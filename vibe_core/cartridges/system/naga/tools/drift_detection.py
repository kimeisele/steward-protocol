#!/usr/bin/env python3
"""
NAGA Drift Detection Tool (Tool Protocol).

Detect drifts and violations using CommitWatcher patterns.
Tool Protocol compliant for kernel-managed execution.

"Der Wächter-Pattern" - NAGAs notice when things go wrong.
"""

import logging
from typing import Any, Dict

from vibe_core.tools.tool_protocol import Tool, ToolResult

logger = logging.getLogger("NAGA.TOOL.DETECT")


class DriftDetectionTool(Tool):
    """Drift and violation detection using CommitWatcher (Tool Protocol)."""

    def __init__(self):
        """Initialize drift detector."""
        self._federation = None

    @property
    def name(self) -> str:
        return "naga.detect"

    @property
    def description(self) -> str:
        return "Detect drifts and violations using CommitWatcher pattern analysis"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action: 'detect_all', 'get_stats', 'check_patterns'",
            },
            "pattern_type": {
                "type": "string",
                "required": False,
                "description": "Pattern to check: 'panic', 'stagnation', 'deferral', 'conflict'",
            },
        }

    def validate(self, parameters: Dict[str, Any]) -> None:
        """Validate parameters."""
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")

        action = parameters["action"]
        if action not in ["detect_all", "get_stats", "check_patterns"]:
            raise ValueError(f"Invalid action: {action}")

        if action == "check_patterns" and "pattern_type" in parameters:
            valid_patterns = ["panic", "stagnation", "deferral", "conflict"]
            if parameters["pattern_type"] not in valid_patterns:
                raise ValueError(f"Invalid pattern_type. Must be one of: {valid_patterns}")

    def _get_federation(self):
        """Lazy-load federation from ServiceRegistry."""
        if self._federation is None:
            try:
                from vibe_core.di import ServiceRegistry
                from vibe_core.protocols.naga import NagaFederationProtocol

                self._federation = ServiceRegistry.get(NagaFederationProtocol)
            except Exception as e:
                logger.debug(f"NagaFederation not available: {e}")
                return None
        return self._federation

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute drift detection."""
        try:
            action = parameters["action"]
            federation = self._get_federation()

            if not federation:
                return ToolResult(
                    success=True,
                    output={
                        "detections": [],
                        "warning": "NagaOrchestrator not available",
                    },
                    metadata={"action": action, "available": False},
                )

            if action == "detect_all":
                report = self._detect_all(federation)
            elif action == "get_stats":
                report = self._get_stats(federation)
            else:  # check_patterns
                pattern_type = parameters.get("pattern_type")
                report = self._check_patterns(federation, pattern_type)

            return ToolResult(
                success=True,
                output=report,
                metadata={
                    "action": action,
                    "alerts_count": report.get("alerts_count", 0),
                },
            )

        except Exception as e:
            error_msg = f"Drift detection failed: {type(e).__name__}: {e!s}"
            logger.error(error_msg)
            return ToolResult(success=False, error=error_msg)

    def _detect_all(self, federation) -> Dict[str, Any]:
        """Run comprehensive drift detection."""
        report = {
            "status": "clean",
            "detections": [],
            "alerts_count": 0,
            "stats": {},
        }

        # CommitWatcher stats
        if federation.commit_watcher:
            stats = federation.commit_watcher.get_stats()
            report["stats"]["commit_watcher"] = stats

            # Check for concerning patterns
            if stats.get("panic_count", 0) > 0:
                report["detections"].append(
                    {
                        "type": "PANIC_PATTERN",
                        "severity": "CRITICAL",
                        "count": stats["panic_count"],
                        "message": f"{stats['panic_count']} panic dump(s) detected",
                    }
                )

            if stats.get("consecutive_deferrals", 0) >= 3:
                report["detections"].append(
                    {
                        "type": "DEFERRAL_LOOP",
                        "severity": "WARNING",
                        "count": stats["consecutive_deferrals"],
                        "message": f"{stats['consecutive_deferrals']} consecutive deferrals",
                    }
                )

            if stats.get("alerts_generated", 0) > 0:
                report["alerts_count"] = stats["alerts_generated"]

        # FloodManager observations
        if federation.flood_manager:
            flood_status = federation.flood_manager.get_status()
            report["stats"]["flood_manager"] = {
                "active": flood_status.get("active", False),
                "observations": flood_status.get("total_observations", 0),
            }

        # Determine overall status
        if any(d.get("severity") == "CRITICAL" for d in report["detections"]):
            report["status"] = "critical"
        elif report["detections"]:
            report["status"] = "warning"

        return report

    def _get_stats(self, federation) -> Dict[str, Any]:
        """Get raw statistics from all watchers."""
        stats = {}

        if federation.commit_watcher:
            stats["commit_watcher"] = federation.commit_watcher.get_stats()

        if federation.flood_manager:
            stats["flood_manager"] = federation.flood_manager.get_status()

        if federation.sesha:
            try:
                sesha_status = federation.sesha.get_status()
                stats["sesha"] = sesha_status.to_dict() if hasattr(sesha_status, "to_dict") else {"status": "active"}
            except Exception:
                stats["sesha"] = {"status": "unknown"}

        if federation.takshaka:
            try:
                takshaka_status = federation.takshaka.get_status()
                stats["takshaka"] = (
                    takshaka_status.to_dict() if hasattr(takshaka_status, "to_dict") else {"status": "active"}
                )
            except Exception:
                stats["takshaka"] = {"status": "unknown"}

        return {"stats": stats, "timestamp": "now"}

    def _check_patterns(self, federation, pattern_type: str = None) -> Dict[str, Any]:
        """Check for specific drift patterns."""
        patterns = {
            "panic": {
                "description": "Panic dumps in commit window",
                "threshold": 3,
                "window": "5 minutes",
                "severity": "CRITICAL",
            },
            "stagnation": {
                "description": "No successful commits",
                "threshold": "10 minutes",
                "severity": "WARNING",
            },
            "deferral": {
                "description": "Consecutive commit deferrals",
                "threshold": 5,
                "severity": "WARNING",
            },
            "conflict": {
                "description": "High conflict/healing rate",
                "threshold": "50%",
                "severity": "WARNING",
            },
        }

        if pattern_type:
            if pattern_type not in patterns:
                return {"error": f"Unknown pattern: {pattern_type}"}
            return {
                "pattern": pattern_type,
                "config": patterns[pattern_type],
                "current_status": self._check_single_pattern(federation, pattern_type),
            }

        # Check all patterns
        results = {}
        for name in patterns:
            results[name] = {
                "config": patterns[name],
                "status": self._check_single_pattern(federation, name),
            }

        return {"patterns": results}

    def _check_single_pattern(self, federation, pattern_type: str) -> Dict[str, Any]:
        """Check a single pattern's current status."""
        if not federation.commit_watcher:
            return {"checked": False, "reason": "CommitWatcher not available"}

        stats = federation.commit_watcher.get_stats()

        if pattern_type == "panic":
            count = stats.get("panic_count", 0)
            return {
                "checked": True,
                "triggered": count >= 3,
                "current_value": count,
                "threshold": 3,
            }
        elif pattern_type == "stagnation":
            last_success = stats.get("last_success_ago")
            triggered = last_success is not None and last_success > 600
            return {
                "checked": True,
                "triggered": triggered,
                "current_value": last_success,
                "threshold": 600,
            }
        elif pattern_type == "deferral":
            count = stats.get("consecutive_deferrals", 0)
            return {
                "checked": True,
                "triggered": count >= 5,
                "current_value": count,
                "threshold": 5,
            }
        elif pattern_type == "conflict":
            total = stats.get("total_observed", 0)
            healed = stats.get("healed_count", 0)
            rate = healed / total if total > 0 else 0
            return {
                "checked": True,
                "triggered": rate >= 0.5,
                "current_value": f"{rate:.1%}",
                "threshold": "50%",
            }

        return {"checked": False, "reason": "Unknown pattern"}

    def format_report(self, output: Dict[str, Any]) -> str:
        """Format detection report for human reading."""
        lines = []
        lines.append("=" * 60)
        lines.append("    NAGA DRIFT DETECTION REPORT")
        lines.append("=" * 60)

        status = output.get("status", "unknown")
        status_emoji = "" if status == "clean" else ("" if status == "critical" else "")
        lines.append(f"\n{status_emoji} Status: {status.upper()}")

        detections = output.get("detections", [])
        if detections:
            lines.append(f"\n   Detections: {len(detections)}")
            for d in detections:
                sev = d.get("severity", "INFO")
                sev_emoji = "" if sev == "CRITICAL" else ""
                lines.append(f"     {sev_emoji} [{sev}] {d.get('type')}: {d.get('message')}")

        if "stats" in output:
            lines.append("\n   Statistics:")
            stats = output["stats"]
            if "commit_watcher" in stats:
                cw = stats["commit_watcher"]
                lines.append(
                    f"     CommitWatcher: {cw.get('total_observed', 0)} observed, {cw.get('success_count', 0)} success"
                )

        lines.append("\n" + "=" * 60)
        return "\n".join(lines)


__all__ = ["DriftDetectionTool"]
