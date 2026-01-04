#!/usr/bin/env python3
"""
NAGA Federation Status Tool (Tool Protocol).

Read-only monitoring of NAGA Federation health.
Tool Protocol compliant for kernel-managed execution.
"""

import logging
from typing import Any, Dict

from vibe_core.tools.tool_protocol import Tool, ToolResult

logger = logging.getLogger("NAGA.TOOL.STATUS")


class FederationStatusTool(Tool):
    """Read-only NAGA Federation status monitoring (Tool Protocol)."""

    def __init__(self):
        """Initialize status tool."""
        self._federation = None

    @property
    def name(self) -> str:
        return "naga.status"

    @property
    def description(self) -> str:
        return "NAGA Federation health status - check Sesha, Vasuki, Takshaka, FloodManager, CommitWatcher"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action: 'check_all', 'check_component'",
            },
            "component": {
                "type": "string",
                "required": False,
                "description": "Component to check: sesha, vasuki, takshaka, flood, watcher",
            },
        }

    def validate(self, parameters: Dict[str, Any]) -> None:
        """Validate parameters."""
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")

        action = parameters["action"]
        if action not in ["check_all", "check_component"]:
            raise ValueError(f"Invalid action: {action}. Must be 'check_all' or 'check_component'")

        if action == "check_component" and "component" not in parameters:
            raise ValueError("check_component requires 'component' parameter")

    def _get_federation(self):
        """Lazy-load federation from ServiceRegistry."""
        if self._federation is None:
            try:
                from vibe_core.di import ServiceRegistry
                from vibe_core.naga import NagaOrchestrator

                try:
                    self._federation = ServiceRegistry.get("NagaOrchestrator")
                except Exception:
                    self._federation = ServiceRegistry.get(NagaOrchestrator)
            except Exception as e:
                logger.debug(f"NagaOrchestrator not available: {e}")
                return None
        return self._federation

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        """Execute status check."""
        try:
            action = parameters["action"]
            federation = self._get_federation()

            if not federation:
                return ToolResult(
                    success=True,
                    output={
                        "status": "unavailable",
                        "reason": "NagaOrchestrator not registered",
                        "healthy": False,
                    },
                    metadata={"action": action},
                )

            if action == "check_all":
                report = self._check_all(federation)
            else:
                component = parameters["component"]
                report = self._check_component(federation, component)

            return ToolResult(
                success=True,
                output=report,
                metadata={
                    "action": action,
                    "healthy": report.get("healthy", False),
                },
            )

        except Exception as e:
            error_msg = f"Status check failed: {type(e).__name__}: {e!s}"
            return ToolResult(success=False, error=error_msg)

    def _check_all(self, federation) -> Dict[str, Any]:
        """Check all NAGA components."""
        report = {
            "status": "healthy" if federation.is_ready() else "degraded",
            "healthy": federation.is_ready(),
            "components": {},
        }

        # Sesha
        if federation.sesha:
            try:
                sesha_status = federation.sesha.get_status()
                report["components"]["sesha"] = {
                    "healthy": sesha_status.healthy,
                    "details": sesha_status.to_dict() if hasattr(sesha_status, "to_dict") else str(sesha_status),
                }
            except Exception as e:
                report["components"]["sesha"] = {"healthy": False, "error": str(e)}
        else:
            report["components"]["sesha"] = {"healthy": False, "status": "disabled"}

        # Vasuki
        if federation.vasuki:
            try:
                vasuki_status = federation.vasuki.get_status()
                report["components"]["vasuki"] = {
                    "healthy": vasuki_status.healthy,
                    "details": vasuki_status.to_dict() if hasattr(vasuki_status, "to_dict") else str(vasuki_status),
                }
            except Exception as e:
                report["components"]["vasuki"] = {"healthy": False, "error": str(e)}
        else:
            report["components"]["vasuki"] = {"healthy": False, "status": "disabled"}

        # Takshaka
        if federation.takshaka:
            try:
                takshaka_status = federation.takshaka.get_status()
                report["components"]["takshaka"] = {
                    "healthy": takshaka_status.healthy,
                    "trust_mode": takshaka_status.trust_mode if hasattr(takshaka_status, "trust_mode") else "unknown",
                    "details": takshaka_status.to_dict()
                    if hasattr(takshaka_status, "to_dict")
                    else str(takshaka_status),
                }
            except Exception as e:
                report["components"]["takshaka"] = {"healthy": False, "error": str(e)}
        else:
            report["components"]["takshaka"] = {"healthy": False, "status": "disabled"}

        # FloodManager
        if federation.flood_manager:
            try:
                flood_status = federation.flood_manager.get_status()
                report["components"]["flood_manager"] = {
                    "active": flood_status.get("active", False),
                    "observations": flood_status.get("total_observations", 0),
                }
            except Exception as e:
                report["components"]["flood_manager"] = {"active": False, "error": str(e)}
        else:
            report["components"]["flood_manager"] = {"active": False, "status": "disabled"}

        # CommitWatcher
        if federation.commit_watcher:
            try:
                watcher_stats = federation.commit_watcher.get_stats()
                report["components"]["commit_watcher"] = {
                    "enabled": watcher_stats.get("enabled", False),
                    "total_observed": watcher_stats.get("total_observed", 0),
                    "alerts_generated": watcher_stats.get("alerts_generated", 0),
                }
            except Exception as e:
                report["components"]["commit_watcher"] = {"enabled": False, "error": str(e)}
        else:
            report["components"]["commit_watcher"] = {"enabled": False, "status": "disabled"}

        return report

    def _check_component(self, federation, component: str) -> Dict[str, Any]:
        """Check a specific component."""
        component_map = {
            "sesha": federation.sesha,
            "vasuki": federation.vasuki,
            "takshaka": federation.takshaka,
            "flood": federation.flood_manager,
            "watcher": federation.commit_watcher,
        }

        if component not in component_map:
            return {"error": f"Unknown component: {component}", "valid_components": list(component_map.keys())}

        comp = component_map[component]
        if not comp:
            return {"component": component, "status": "disabled", "healthy": False}

        try:
            if hasattr(comp, "get_status"):
                status = comp.get_status()
                return {
                    "component": component,
                    "healthy": getattr(status, "healthy", True),
                    "details": status.to_dict() if hasattr(status, "to_dict") else status,
                }
            elif hasattr(comp, "get_stats"):
                stats = comp.get_stats()
                return {"component": component, "stats": stats}
            else:
                return {"component": component, "status": "available"}
        except Exception as e:
            return {"component": component, "error": str(e), "healthy": False}

    def format_report(self, report: Dict[str, Any]) -> str:
        """Format status report for human reading."""
        lines = []
        lines.append("=" * 70)
        lines.append("    NAGA FEDERATION STATUS")
        lines.append("=" * 70)

        status_emoji = "" if report.get("healthy") else ""
        lines.append(f"\n{status_emoji} Overall: {report.get('status', 'unknown').upper()}")

        if "components" in report:
            lines.append("\nComponents:")
            for name, info in report["components"].items():
                if isinstance(info, dict):
                    healthy = info.get("healthy", info.get("active", info.get("enabled", False)))
                    emoji = "" if healthy else ""
                    lines.append(f"  {emoji} {name}: {'OK' if healthy else 'DEGRADED'}")

        lines.append("\n" + "=" * 70)
        return "\n".join(lines)


__all__ = ["FederationStatusTool"]
