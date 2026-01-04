"""
Treasury - OPUS-031 Layer 1.5 Resource Tracking

Tracks API token usage and enforces budget limits.
Acts as a kill-switch for autonomous loops.

Architecture:
    ┌─────────────────────────────────────────────────────────────┐
    │                   Treasury                                   │
    │   record_usage(input_tokens, output_tokens)                 │
    │   check_budget(limit) → bool (False = KILL SWITCH)          │
    │   get_daily_spend() → DailySpend                            │
    └────────────────────────┬────────────────────────────────────┘
                             │ persists to
                             ▼
    ┌─────────────────────────────────────────────────────────────┐
    │               .opus_state/treasury.json                     │
    │   { "date": "2025-01-15", "tokens_input": 5000, ... }       │
    └─────────────────────────────────────────────────────────────┘

Design Decisions (OPUS-031):
- DD6: Resource Awareness - Track token usage and costs
- Budget limits with kill-switch prevent runaway autonomous loops
- Daily reset to allow next day's work

Integration:
- Called by any LLM-using component that wants to track costs
- Treasury.check_budget() should be called BEFORE expensive operations
- If returns False, the Autonomous Conductor MUST stop
"""

import json
import logging
import os
import tempfile
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("TREASURY")

# File name within .opus_state/
TREASURY_FILE = "treasury.json"
TREASURY_HISTORY_FILE = "treasury_history.jsonl"


@dataclass
class DailySpend:
    """Track daily token usage and costs."""

    date: str  # YYYY-MM-DD format
    tokens_input: int = 0
    tokens_output: int = 0
    estimated_cost: float = 0.0
    api_calls: int = 0
    budget_warnings: int = 0  # Times we hit 80% budget

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DailySpend":
        return cls(
            date=data.get("date", datetime.now().strftime("%Y-%m-%d")),
            tokens_input=data.get("tokens_input", 0),
            tokens_output=data.get("tokens_output", 0),
            estimated_cost=data.get("estimated_cost", 0.0),
            api_calls=data.get("api_calls", 0),
            budget_warnings=data.get("budget_warnings", 0),
        )


class Treasury:
    """
    Resource tracking with kill-switch.

    If check_budget() returns False, the caller MUST stop.
    This prevents runaway autonomous loops from burning $$$$.
    """

    # Default cost estimates (OpenRouter blended rates)
    # Override via set_cost_rates() for specific models
    DEFAULT_COST_INPUT_1K: float = 0.001  # $1 per 1M input tokens
    DEFAULT_COST_OUTPUT_1K: float = 0.005  # $5 per 1M output tokens

    def __init__(self, state_dir: Optional[Path] = None):
        """
        Initialize Treasury.

        Args:
            state_dir: Path to state directory (auto-detected if None)
        """
        if state_dir is None:
            # Use new state path helper
            from vibe_core.plugins.opus_assistant.core.state_paths import get_opus_state_path

            state_dir = get_opus_state_path(Path.cwd()).parent

        self._state_dir = Path(state_dir)
        self._state_dir.mkdir(parents=True, exist_ok=True)

        self._file_path = self._state_dir / TREASURY_FILE
        self._history_path = self._state_dir / TREASURY_HISTORY_FILE

        # Cost rates (can be overridden)
        self._cost_input_1k = self.DEFAULT_COST_INPUT_1K
        self._cost_output_1k = self.DEFAULT_COST_OUTPUT_1K

        # Load current spend
        self._current = self._load()

    def _load(self) -> DailySpend:
        """Load current daily spend from file."""
        today = datetime.now().strftime("%Y-%m-%d")

        if not self._file_path.exists():
            return DailySpend(date=today)

        try:
            with open(self._file_path, "r") as f:
                data = json.load(f)
                spend = DailySpend.from_dict(data)

                # Check if new day - archive and reset
                if spend.date != today:
                    self._archive_day(spend)
                    return DailySpend(date=today)

                return spend
        except Exception as e:
            logger.warning(f"Failed to load treasury: {e}")
            return DailySpend(date=today)

    def _save(self) -> bool:
        """Save current spend to file (atomic write)."""
        try:
            content = json.dumps(self._current.to_dict(), indent=2)
            self._atomic_write(self._file_path, content)
            return True
        except Exception as e:
            logger.error(f"Failed to save treasury: {e}")
            return False

    def _atomic_write(self, file_path: Path, content: str) -> None:
        """Atomic write to prevent corruption on crash."""
        fd, tmp_path = tempfile.mkstemp(
            dir=file_path.parent,
            prefix=f".{file_path.name}.",
            suffix=".tmp",
        )
        try:
            with os.fdopen(fd, "w") as f:
                f.write(content)
                f.flush()
                os.fsync(f.fileno())
            os.rename(tmp_path, file_path)
        except Exception:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise

    def _archive_day(self, day_spend: DailySpend) -> None:
        """Archive completed day's spend to history file."""
        try:
            with open(self._history_path, "a") as f:
                f.write(json.dumps(day_spend.to_dict()) + "\n")
            logger.debug(f"Archived treasury for {day_spend.date}")
        except Exception as e:
            logger.warning(f"Failed to archive treasury: {e}")

    def record_usage(self, input_tokens: int, output_tokens: int, model: Optional[str] = None) -> float:
        """
        Record token usage and update cost estimate.

        Args:
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens generated
            model: Optional model name (for model-specific pricing)

        Returns:
            Estimated cost of this API call
        """
        # Calculate cost for this call
        cost = (input_tokens / 1000 * self._cost_input_1k) + (output_tokens / 1000 * self._cost_output_1k)

        # Update current spend
        self._current.tokens_input += input_tokens
        self._current.tokens_output += output_tokens
        self._current.estimated_cost += cost
        self._current.api_calls += 1

        self._save()

        logger.debug(
            f"💰 Treasury: +{input_tokens}in/{output_tokens}out = ${cost:.4f} "
            f"(total: ${self._current.estimated_cost:.4f})"
        )

        return cost

    def check_budget(self, limit: Optional[float] = None) -> bool:
        """
        Check if budget is OK.

        THIS IS THE KILL-SWITCH.
        If this returns False, autonomous operations MUST stop.

        Args:
            limit: Budget limit in USD (uses preference if None)

        Returns:
            True if budget OK, False if EXHAUSTED
        """
        if limit is None:
            # Try to get from preferences
            try:
                from vibe_core.plugins.opus_assistant.core.state_manager import get_state_manager

                state_mgr = get_state_manager()
                limit = state_mgr.get_preference("budget_limit", 5.0)
            except Exception:
                limit = 5.0

        current_cost = self._current.estimated_cost

        # Budget exhausted - KILL SWITCH
        if current_cost >= limit:
            logger.critical(
                f"💸 BUDGET EXHAUSTED: ${current_cost:.4f} >= ${limit:.2f} - Autonomous operations MUST stop!"
            )
            return False

        # 80% warning
        if current_cost >= (limit * 0.8):
            self._current.budget_warnings += 1
            self._save()
            logger.warning(
                f"⚠️ BUDGET WARNING: ${current_cost:.4f} / ${limit:.2f} ({(current_cost / limit) * 100:.0f}% used)"
            )

        return True

    def get_daily_spend(self) -> DailySpend:
        """Get current daily spend."""
        return self._current

    def get_remaining_budget(self, limit: Optional[float] = None) -> float:
        """
        Get remaining budget in USD.

        Args:
            limit: Budget limit (uses preference if None)

        Returns:
            Remaining budget (can be negative if over budget)
        """
        if limit is None:
            try:
                from vibe_core.plugins.opus_assistant.core.state_manager import get_state_manager

                state_mgr = get_state_manager()
                limit = state_mgr.get_preference("budget_limit", 5.0)
            except Exception:
                limit = 5.0

        return limit - self._current.estimated_cost

    def get_history(self, days: int = 7) -> List[DailySpend]:
        """
        Get spending history for the last N days.

        Args:
            days: Number of days to retrieve

        Returns:
            List of DailySpend entries (newest first)
        """
        history = []

        if not self._history_path.exists():
            return history

        try:
            with open(self._history_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            data = json.loads(line)
                            history.append(DailySpend.from_dict(data))
                        except json.JSONDecodeError:
                            continue

            # Reverse (newest first) and limit
            history.reverse()
            return history[:days]
        except Exception as e:
            logger.warning(f"Failed to read treasury history: {e}")
            return []

    def set_cost_rates(self, input_per_1k: float, output_per_1k: float) -> None:
        """
        Override default cost rates.

        Use this for model-specific pricing.

        Args:
            input_per_1k: Cost per 1000 input tokens
            output_per_1k: Cost per 1000 output tokens
        """
        self._cost_input_1k = input_per_1k
        self._cost_output_1k = output_per_1k
        logger.debug(f"Treasury cost rates set: ${input_per_1k}/1k in, ${output_per_1k}/1k out")

    def reset_daily(self) -> None:
        """
        Force reset daily spend (for testing).

        Archives current day and starts fresh.
        """
        self._archive_day(self._current)
        self._current = DailySpend(date=datetime.now().strftime("%Y-%m-%d"))
        self._save()
        logger.info("🔄 Treasury reset for new day")


def get_treasury(state_dir: Optional[Path] = None) -> Treasury:
    """
    Get a Treasury instance.

    Args:
        state_dir: Path to .opus_state/ (auto-detected if None)

    Returns:
        Treasury instance
    """
    return Treasury(state_dir=state_dir)
