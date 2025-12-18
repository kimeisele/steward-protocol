"""
OPUS-106: UntotbarMergeEngine - Organic Conflict Healing

"Merge conflicts are NOT fatal. They are HEALABLE."

The Untotbar ("unkillable") strategy ensures state files NEVER break
the system. Conflicts are healed, not rejected.

Strategy per file type:
- JSON state files: Deep merge with conflict markers
- YAML config: Ours wins (config is human-controlled)
- SQLite/DB: Ledger replay via event sourcing
- Binary: Ours wins (regenerate from source)

This implements the UntotbarMergeEngine from OPUS-009 philosophy.
"""

import json
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("MERGE_ENGINE")


# =============================================================================
# Enums and Data Classes
# =============================================================================


class MergeStrategy(Enum):
    """Available merge strategies."""

    DEEP_MERGE = "deep_merge"  # JSON: Merge objects, concat arrays
    OURS_WINS = "ours_wins"  # Config: Human-controlled wins
    THEIRS_WINS = "theirs_wins"  # Rare: Remote wins
    LEDGER_REPLAY = "ledger_replay"  # DB: Replay missing events
    LATEST_TIMESTAMP = "latest"  # Use most recent by mtime


@dataclass
class HealedConflict:
    """Result of healing a merge conflict."""

    path: Path
    strategy: MergeStrategy
    healed_content: bytes
    ours_preserved: bool = True
    theirs_preserved: bool = False
    conflicts_found: int = 0
    merge_timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for logging/ledger."""
        return {
            "path": str(self.path),
            "strategy": self.strategy.value,
            "ours_preserved": self.ours_preserved,
            "theirs_preserved": self.theirs_preserved,
            "conflicts_found": self.conflicts_found,
            "merge_timestamp": self.merge_timestamp,
            "metadata": self.metadata,
        }


# =============================================================================
# Main Class: UntotbarMergeEngine
# =============================================================================


class UntotbarMergeEngine:
    """
    The Untotbar Merge Engine - Conflicts are healed, not rejected.

    "The untotbar is not the invincible.
     The untotbar is that which heals."

    This engine ensures state files NEVER break the system by providing
    per-type healing strategies that always produce valid output.
    """

    # Default strategies by file pattern
    STRATEGIES: Dict[str, MergeStrategy] = {
        "*.json": MergeStrategy.DEEP_MERGE,
        "*.yaml": MergeStrategy.OURS_WINS,
        "*.yml": MergeStrategy.OURS_WINS,
        "*.db": MergeStrategy.LEDGER_REPLAY,
        "*.sqlite": MergeStrategy.LEDGER_REPLAY,
        "*.md": MergeStrategy.OURS_WINS,
        "*": MergeStrategy.OURS_WINS,  # Safe default
    }

    def __init__(self, custom_strategies: Optional[Dict[str, MergeStrategy]] = None):
        """
        Initialize the merge engine.

        Args:
            custom_strategies: Override default strategies for specific patterns
        """
        self.strategies = dict(self.STRATEGIES)
        if custom_strategies:
            self.strategies.update(custom_strategies)
        logger.info("[MERGE_ENGINE] Untotbar initialized")

    # =========================================================================
    # Main API
    # =========================================================================

    def heal_conflict(
        self, path: Path, ours: bytes, theirs: bytes, strategy: Optional[MergeStrategy] = None
    ) -> HealedConflict:
        """
        Heal a merge conflict. NEVER returns None. ALWAYS produces valid state.

        Args:
            path: Conflicting file path
            ours: Our version of the content
            theirs: Their version of the content
            strategy: Override automatic strategy selection

        Returns:
            HealedConflict with healed content (always valid)
        """
        if strategy is None:
            strategy = self.get_strategy(path)

        logger.debug(f"[MERGE_ENGINE] Healing {path} with strategy {strategy.value}")

        try:
            if strategy == MergeStrategy.DEEP_MERGE:
                return self._deep_merge_json(path, ours, theirs)
            elif strategy == MergeStrategy.OURS_WINS:
                return self._ours_wins(path, ours, theirs)
            elif strategy == MergeStrategy.THEIRS_WINS:
                return self._theirs_wins(path, ours, theirs)
            elif strategy == MergeStrategy.LEDGER_REPLAY:
                return self._ledger_replay(path, ours, theirs)
            elif strategy == MergeStrategy.LATEST_TIMESTAMP:
                return self._latest_timestamp(path, ours, theirs)
            else:
                # Fallback: ours wins (safe default)
                return self._ours_wins(path, ours, theirs)
        except Exception as e:
            # UNTOTBAR: Even on error, produce valid output
            logger.warning(f"[MERGE_ENGINE] Strategy {strategy.value} failed for {path}: {e}")
            logger.warning("[MERGE_ENGINE] Falling back to OURS_WINS")
            return self._ours_wins(path, ours, theirs)

    def get_strategy(self, path: Path) -> MergeStrategy:
        """
        Get the appropriate merge strategy for a file path.

        Args:
            path: File path to check

        Returns:
            MergeStrategy to use
        """
        path_str = str(path)

        # Check specific patterns first
        for pattern, strategy in self.strategies.items():
            if pattern == "*":
                continue
            # Simple glob matching
            if pattern.startswith("*"):
                suffix = pattern[1:]
                if path_str.endswith(suffix):
                    return strategy
            elif pattern in path_str:
                return strategy

        # Default fallback
        return self.strategies.get("*", MergeStrategy.OURS_WINS)

    # =========================================================================
    # Strategy Implementations
    # =========================================================================

    def _ours_wins(self, path: Path, ours: bytes, theirs: bytes) -> HealedConflict:
        """Strategy: Our version wins completely."""
        return HealedConflict(
            path=path,
            strategy=MergeStrategy.OURS_WINS,
            healed_content=ours,
            ours_preserved=True,
            theirs_preserved=False,
            conflicts_found=1 if ours != theirs else 0,
        )

    def _theirs_wins(self, path: Path, ours: bytes, theirs: bytes) -> HealedConflict:
        """Strategy: Their version wins completely."""
        return HealedConflict(
            path=path,
            strategy=MergeStrategy.THEIRS_WINS,
            healed_content=theirs,
            ours_preserved=False,
            theirs_preserved=True,
            conflicts_found=1 if ours != theirs else 0,
        )

    def _deep_merge_json(self, path: Path, ours: bytes, theirs: bytes) -> HealedConflict:
        """
        Strategy: Deep merge two JSON objects.

        Rules:
        - Objects: Recursive merge, ours wins on key conflict
        - Arrays: Concatenate, dedupe by 'id' if present
        - Primitives: Ours wins
        - Conflict markers preserved in _merge_conflicts key
        """
        conflicts_found = 0

        try:
            ours_data = json.loads(ours.decode("utf-8"))
            theirs_data = json.loads(theirs.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            # Can't parse as JSON, fall back to ours wins
            logger.warning(f"[MERGE_ENGINE] JSON parse failed for {path}: {e}")
            return self._ours_wins(path, ours, theirs)

        merged, conflicts = self._recursive_merge(ours_data, theirs_data, [])
        conflicts_found = len(conflicts)

        # Add merge metadata
        if isinstance(merged, dict):
            merged["_merge_timestamp"] = time.time()
            merged["_merge_strategy"] = "deep_merge"
            if conflicts:
                merged["_merge_conflicts"] = conflicts

        healed_content = json.dumps(merged, indent=2).encode("utf-8")

        return HealedConflict(
            path=path,
            strategy=MergeStrategy.DEEP_MERGE,
            healed_content=healed_content,
            ours_preserved=True,
            theirs_preserved=True,  # Both contributed
            conflicts_found=conflicts_found,
            metadata={"conflicts": conflicts},
        )

    def _recursive_merge(self, ours: Any, theirs: Any, path: List[str]) -> tuple[Any, List[str]]:
        """
        Recursively merge two values.

        Returns:
            Tuple of (merged_value, list_of_conflict_paths)
        """
        conflicts: List[str] = []
        path_str = ".".join(path) if path else "root"

        # Both are dicts - recursive merge
        if isinstance(ours, dict) and isinstance(theirs, dict):
            result = dict(theirs)  # Start with theirs
            for key, value in ours.items():
                if key in result:
                    merged_val, sub_conflicts = self._recursive_merge(value, result[key], path + [key])
                    result[key] = merged_val
                    conflicts.extend(sub_conflicts)
                else:
                    result[key] = value
            return result, conflicts

        # Both are lists - concatenate and dedupe
        elif isinstance(ours, list) and isinstance(theirs, list):
            # Try to dedupe by 'id' field if present
            seen_ids = set()
            result = []

            for item in theirs + ours:
                if isinstance(item, dict) and "id" in item:
                    item_id = item["id"]
                    if item_id not in seen_ids:
                        seen_ids.add(item_id)
                        result.append(item)
                elif item not in result:
                    result.append(item)

            return result, conflicts

        # Different types or primitives - ours wins
        elif ours != theirs:
            conflicts.append(f"{path_str}: ours={type(ours).__name__}, theirs={type(theirs).__name__}")
            return ours, conflicts

        # Same value
        return ours, conflicts

    def _ledger_replay(self, path: Path, ours: bytes, theirs: bytes) -> HealedConflict:
        """
        Strategy: Merge databases by replaying ledger events.

        For SQLite databases, we can't just merge bytes. Instead:
        1. Open both databases
        2. Find events in theirs that are not in ours
        3. Replay missing events into ours

        NOTE: This is a simplified implementation. Full implementation
        would require access to the LedgerState to replay events.
        """
        # For now, fall back to ours wins for DB files
        # Full implementation would integrate with LedgerState
        logger.info(f"[MERGE_ENGINE] Ledger replay not fully implemented for {path}")
        logger.info("[MERGE_ENGINE] Using OURS_WINS for database merge")

        return HealedConflict(
            path=path,
            strategy=MergeStrategy.LEDGER_REPLAY,
            healed_content=ours,
            ours_preserved=True,
            theirs_preserved=False,
            conflicts_found=1,
            metadata={"note": "Simplified implementation - ours wins"},
        )

    def _latest_timestamp(self, path: Path, ours: bytes, theirs: bytes) -> HealedConflict:
        """
        Strategy: Use content with latest embedded timestamp.

        Works for JSON files with _updated or timestamp field.
        Falls back to ours wins if no timestamps found.
        """
        try:
            ours_data = json.loads(ours.decode("utf-8"))
            theirs_data = json.loads(theirs.decode("utf-8"))

            # Look for timestamp fields
            ours_ts = ours_data.get("_updated") or ours_data.get("timestamp") or 0
            theirs_ts = theirs_data.get("_updated") or theirs_data.get("timestamp") or 0

            if theirs_ts > ours_ts:
                return self._theirs_wins(path, ours, theirs)
            else:
                return self._ours_wins(path, ours, theirs)

        except (json.JSONDecodeError, UnicodeDecodeError):
            return self._ours_wins(path, ours, theirs)

    # =========================================================================
    # Utilities
    # =========================================================================

    def detect_conflicts(self, path: Path) -> bool:
        """
        Check if a file has Git merge conflict markers.

        Args:
            path: Path to check

        Returns:
            True if conflict markers found
        """
        if not path.exists():
            return False

        try:
            content = path.read_text()
            return "<<<<<<< " in content or "=======" in content or ">>>>>>> " in content
        except Exception:
            return False

    def auto_heal_file(self, path: Path) -> Optional[HealedConflict]:
        """
        Automatically heal a file with conflict markers.

        Args:
            path: File with conflict markers

        Returns:
            HealedConflict if healed, None if no conflicts
        """
        if not self.detect_conflicts(path):
            return None

        try:
            content = path.read_text()

            # Parse conflict markers
            ours_parts = []
            theirs_parts = []
            current_section = "common"

            for line in content.split("\n"):
                if line.startswith("<<<<<<< "):
                    current_section = "ours"
                elif line.startswith("======="):
                    current_section = "theirs"
                elif line.startswith(">>>>>>> "):
                    current_section = "common"
                else:
                    if current_section == "ours":
                        ours_parts.append(line)
                    elif current_section == "theirs":
                        theirs_parts.append(line)

            ours = "\n".join(ours_parts).encode("utf-8")
            theirs = "\n".join(theirs_parts).encode("utf-8")

            return self.heal_conflict(path, ours, theirs)

        except Exception as e:
            logger.error(f"[MERGE_ENGINE] Auto-heal failed for {path}: {e}")
            return None


# =============================================================================
# Public API Exports
# =============================================================================

__all__ = [
    "UntotbarMergeEngine",
    "MergeStrategy",
    "HealedConflict",
]
