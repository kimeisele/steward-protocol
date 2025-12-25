"""
Git Analysis Tool - Temporal patterns and velocity analysis.

Implements Tool Protocol (vibe_core.tools.tool_protocol.Tool).

Provides:
- Velocity trends (accelerating/decelerating/steady)
- Day-of-week patterns
- Hour-of-day patterns (work style detection)
- Activity bursts and quiet periods
- Commit classification (feature/fix/refactor/etc)
"""

import logging
import re
import subprocess
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import TYPE_CHECKING, Any, Optional

from vibe_core.tools.tool_protocol import Tool, ToolResult

if TYPE_CHECKING:
    from vibe_core.di import ServiceRegistry

logger = logging.getLogger("ANALYST_GIT_TOOL")


class GitAnalysisTool(Tool):
    """
    Tool for analyzing git history and temporal patterns.

    This is the TEMPORAL dimension of ANALYST.
    Git is truth - but it's ONE source, not the ONLY source.
    """

    def __init__(self, services: Optional["ServiceRegistry"] = None, root_dir: str = "."):
        """
        Initialize git analysis tool.

        Args:
            services: Service registry for DI
            root_dir: Repository root directory
        """
        super().__init__(services)
        self.root_dir = Path(root_dir).resolve()
        # ⚡ VAJRA: Core kernel reference for ledger binding
        self._vibe_kernel = None

    def inject_kernel(self, kernel) -> None:
        """
        ⚡ VAJRA: Inject the core VibeKernel for ledger access.

        OPUS-070: Analyst tools MUST have kernel access for full context.
        Without kernel injection, they operate in "file-only mode" (limited).
        """
        self._vibe_kernel = kernel
        logger.info(f"⚡ {self.name}: Kernel injected - ledger binding ACTIVE")

    def _get_ledger(self):
        """Get kernel.ledger via VAJRA binding."""
        if self._vibe_kernel is None:
            return None
        if not hasattr(self._vibe_kernel, "ledger"):
            return None
        return self._vibe_kernel.ledger

    @property
    def name(self) -> str:
        return "analyst.git"

    @property
    def description(self) -> str:
        return "Analyze git history for temporal patterns, velocity trends, and commit classification"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Analysis action: 'velocity', 'patterns', 'classify', 'full'",
            },
            "days": {
                "type": "integer",
                "required": False,
                "description": "Number of days to analyze (default: 30)",
            },
            "periods": {
                "type": "integer",
                "required": False,
                "description": "Number of periods for velocity trend (default: 4 weeks)",
            },
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate parameters."""
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")

        valid_actions = ["velocity", "patterns", "classify", "full"]
        if parameters["action"] not in valid_actions:
            raise ValueError(f"Invalid action: {parameters['action']}. Must be one of {valid_actions}")

        if "days" in parameters:
            days = parameters["days"]
            if not isinstance(days, int) or days < 1 or days > 365:
                raise ValueError("days must be an integer between 1 and 365")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """Execute git analysis."""
        try:
            action = parameters["action"]
            days = parameters.get("days", 30)
            periods = parameters.get("periods", 4)

            # Verify git access
            if not self._verify_git():
                return ToolResult(success=False, error="Not a git repository or git not accessible")

            if action == "velocity":
                result = self._analyze_velocity(periods)
            elif action == "patterns":
                result = self._analyze_patterns(days)
            elif action == "classify":
                result = self._classify_commits(days)
            elif action == "full":
                result = {
                    "velocity": self._analyze_velocity(periods),
                    "patterns": self._analyze_patterns(days),
                    "commits": self._classify_commits(days),
                    "metadata": {
                        "analyzed_at": datetime.utcnow().isoformat(),
                        "days": days,
                        "periods": periods,
                    },
                }
            else:
                return ToolResult(success=False, error=f"Unknown action: {action}")

            logger.info(f"analyst.git: {action} analysis complete")

            return ToolResult(
                success=True,
                output=result,
                metadata={"action": action, "days": days},
            )

        except Exception as e:
            error_msg = f"Git analysis failed: {type(e).__name__}: {e!s}"
            logger.error(f"GitAnalysisTool: {error_msg}", exc_info=True)
            return ToolResult(success=False, error=error_msg)

    # -------------------------------------------------------------------------
    # Internal Methods
    # -------------------------------------------------------------------------

    def _run_git(self, cmd: str) -> str:
        """Run git command and return output."""
        result = subprocess.run(
            ["git"] + cmd.split(),
            capture_output=True,
            text=True,
            cwd=str(self.root_dir),
        )
        return result.stdout.strip()

    def _verify_git(self) -> bool:
        """Verify git is accessible."""
        try:
            self._run_git("status")
            return True
        except Exception:
            return False

    def _analyze_velocity(self, periods: int = 4) -> dict[str, Any]:
        """Analyze velocity trends over weekly periods."""
        week_counts = []
        for i in range(periods):
            start = (datetime.now() - timedelta(weeks=i + 1)).strftime("%Y-%m-%d")
            end = (datetime.now() - timedelta(weeks=i)).strftime("%Y-%m-%d")

            cmd = f"rev-list --count HEAD --since={start} --until={end}"
            count = int(self._run_git(cmd) or "0")
            week_counts.append(count)

        # Calculate trend
        if len(week_counts) >= 2:
            recent = sum(week_counts[:2]) / 2
            older = sum(week_counts[2:]) / 2 if len(week_counts) > 2 else week_counts[0]

            if older == 0:
                trend_ratio = float("inf") if recent > 0 else 1.0
            else:
                trend_ratio = recent / older

            if trend_ratio > 1.3:
                trend = "ACCELERATING"
                momentum = "HIGH"
            elif trend_ratio > 1.1:
                trend = "GROWING"
                momentum = "POSITIVE"
            elif trend_ratio < 0.7:
                trend = "DECELERATING"
                momentum = "LOW"
            elif trend_ratio < 0.9:
                trend = "SLOWING"
                momentum = "NEGATIVE"
            else:
                trend = "STEADY"
                momentum = "STABLE"
        else:
            trend = "INSUFFICIENT_DATA"
            momentum = "UNKNOWN"
            trend_ratio = 1.0

        # Total commits
        total = int(self._run_git("rev-list --count HEAD") or "0")

        return {
            "weekly_counts": week_counts,
            "trend": trend,
            "momentum": momentum,
            "trend_ratio": round(trend_ratio, 2) if trend_ratio != float("inf") else None,
            "average_weekly": round(sum(week_counts) / len(week_counts), 1) if week_counts else 0,
            "total_commits": total,
        }

    def _analyze_patterns(self, days: int = 30) -> dict[str, Any]:
        """Analyze day/hour commit patterns."""
        since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        # Day patterns
        day_output = self._run_git(f"log --pretty=format:%ad --date=format:%A --since={since}")
        day_counts = defaultdict(int)
        for line in day_output.split("\n"):
            if line.strip():
                day_counts[line.strip()] += 1

        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        day_distribution = {day: day_counts.get(day, 0) for day in day_order}

        # Hour patterns
        hour_output = self._run_git(f"log --pretty=format:%ad --date=format:%H --since={since}")
        hour_counts = defaultdict(int)
        for line in hour_output.split("\n"):
            if line.strip():
                try:
                    hour = int(line.strip())
                    hour_counts[hour] += 1
                except ValueError:
                    pass

        # Categorize hours
        morning = sum(hour_counts.get(h, 0) for h in range(6, 12))
        afternoon = sum(hour_counts.get(h, 0) for h in range(12, 18))
        evening = sum(hour_counts.get(h, 0) for h in range(18, 24))
        night = sum(hour_counts.get(h, 0) for h in range(0, 6))

        total = morning + afternoon + evening + night
        if total > 0:
            if night > total * 0.3:
                work_style = "NIGHT_OWL"
            elif morning > afternoon:
                work_style = "EARLY_BIRD"
            elif evening > afternoon:
                work_style = "EVENING_CODER"
            else:
                work_style = "BUSINESS_HOURS"
        else:
            work_style = "UNKNOWN"

        # Peak analysis
        peak_day = max(day_distribution.items(), key=lambda x: x[1]) if day_distribution else ("Unknown", 0)
        peak_hour = max(hour_counts.items(), key=lambda x: x[1]) if hour_counts else (12, 0)

        weekday_total = sum(day_distribution.get(d, 0) for d in day_order[:5])
        weekend_total = sum(day_distribution.get(d, 0) for d in day_order[5:])

        return {
            "day_distribution": day_distribution,
            "hour_distribution": dict(sorted(hour_counts.items())),
            "peak_day": peak_day[0],
            "peak_hour": f"{peak_hour[0]:02d}:00",
            "work_style": work_style,
            "morning_commits": morning,
            "afternoon_commits": afternoon,
            "evening_commits": evening,
            "night_commits": night,
            "weekday_commits": weekday_total,
            "weekend_commits": weekend_total,
            "weekend_ratio": round(weekend_total / weekday_total, 2) if weekday_total > 0 else 0,
        }

    def _classify_commits(self, days: int = 30) -> dict[str, Any]:
        """Classify commits by type."""
        since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        output = self._run_git(f"log --pretty=format:%s --since={since}")

        # Patterns for classification
        patterns = {
            "feature": [r"^feat", r"^add", r"^implement", r"^new", r"^create"],
            "fix": [r"^fix", r"^bug", r"^resolve", r"^patch", r"^correct"],
            "refactor": [r"^refactor", r"^clean", r"^simplify", r"^extract", r"^move"],
            "docs": [r"^doc", r"^readme", r"^comment", r"^update.*doc"],
            "test": [r"^test", r"^spec", r"^coverage"],
            "chore": [r"^chore", r"^config", r"^ci", r"^build", r"^deps", r"^merge"],
            "style": [r"^style", r"^format", r"^lint"],
        }

        classifications = defaultdict(int)
        for line in output.split("\n"):
            if not line.strip():
                continue

            msg = line.strip().lower()
            classified = False

            for category, category_patterns in patterns.items():
                for pattern in category_patterns:
                    if re.search(pattern, msg, re.IGNORECASE):
                        classifications[category] += 1
                        classified = True
                        break
                if classified:
                    break

            if not classified:
                classifications["other"] += 1

        total = sum(classifications.values())
        percentages = {k: round(v / total * 100, 1) if total > 0 else 0 for k, v in classifications.items()}

        dominant = max(classifications.items(), key=lambda x: x[1]) if classifications else ("unknown", 0)

        return {
            "distribution": dict(classifications),
            "percentages": percentages,
            "total_commits": total,
            "dominant_type": dominant[0],
            "dominant_count": dominant[1],
        }
