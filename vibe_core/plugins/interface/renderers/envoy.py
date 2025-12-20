"""
Envoy Renderer (Terminal Interface).

OPUS-152: Refactored to use render_sections() pattern.

Renders ENVOY.md and handles bidirectional terminal commands.
Uses EnvoyPlugin (kernel.envoy) for routing when available.

Architecture:
- INPUT: EnvoySync parses user commands from "## Request" section
- OUTPUT: render_sections() uses config-driven sections from interface.yaml
- BIDIRECTIONAL: Preserves user sections on each render
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from vibe_core.envoy_sync import EnvoySync, EnvoySyncState
from vibe_core.io_service import DocumentType

from .base import BaseRenderer

if TYPE_CHECKING:
    from vibe_core import Task

logger = logging.getLogger("RENDERER_ENVOY")


class EnvoyRenderer(BaseRenderer):
    """Renders ENVOY.md and handles terminal commands.

    OPUS-152: Uses render_sections() for config-driven output.
    """

    def __init__(self, kernel):
        super().__init__(kernel)
        self.sync = EnvoySync()
        self.state = EnvoySyncState()
        self._register_data_sources()

    def _register_data_sources(self) -> None:
        """Register data sources for config-driven sections.

        Maps interface.yaml section sources to actual data.
        """
        self.register_data_source("envoy.pending_tasks", self._get_pending_tasks)
        self.register_data_source("envoy.history", self._get_history)
        self.register_data_source("envoy.routes", self._get_routes)

    @property
    def name(self) -> str:
        return "envoy"

    @property
    def output_file(self) -> str:
        return "ENVOY.md"

    @property
    def doc_type(self) -> DocumentType:
        return DocumentType.BIDIRECTIONAL

    def _envoy_route_adapter(self, request: str, context: dict):
        """Adapter to convert EnvoyPlugin.route() to PlaybookRoute format."""
        from dataclasses import dataclass

        @dataclass
        class RouteResult:
            task: str
            description: str
            confidence: str
            source: str

        result = self.kernel.envoy.route(request, context)
        return RouteResult(
            task=result.get("task", "fallback"),
            description=result.get("description", ""),
            confidence=result.get("confidence", "none"),
            source=result.get("source", "envoy_plugin"),
        )

    # =========================================================================
    # DATA SOURCES (for render_sections)
    # =========================================================================

    def _get_pending_tasks(self) -> List[Dict[str, Any]]:
        """Get pending tasks for status section."""
        if not self.state.pending_tasks:
            return []
        return [
            {
                "Task ID": f"`{task_id}`",
                "Status": f"**{meta.get('status', 'UNKNOWN')}**",
                "Request": meta.get("request", ""),
            }
            for task_id, meta in self.state.pending_tasks.items()
        ]

    def _get_history(self) -> List[Dict[str, Any]]:
        """Get request history for history section."""
        history = []
        for entry in reversed(self.state.request_history[-5:]):
            response = entry.get("response", "") or entry.get("error", "")
            if len(response) > 50:
                response = response[:47] + "..."
            history.append(
                {
                    "Time": entry.get("timestamp", ""),
                    "Request": entry.get("request", ""),
                    "Status": entry.get("status", ""),
                    "Response": response,
                }
            )
        return history

    def _get_routes(self) -> List[Dict[str, Any]]:
        """Get available routes for routes section."""
        routes = []
        if hasattr(self.kernel, "envoy"):
            try:
                kernel_routes = self.kernel.envoy.get_routes()
                for route in kernel_routes[:20]:
                    routes.append(
                        {
                            "Route": f"`{route.get('name', '')}`",
                            "Description": route.get("description", "")[:50],
                        }
                    )
            except Exception as e:
                logger.debug(f"Could not get routes: {e}")
        if not routes:
            routes = [
                {"Route": "`bootstrap`", "Description": "System Bootstrap"},
                {"Route": "`status`", "Description": "System Status"},
            ]
        return routes

    # =========================================================================
    # RENDER (OPUS-152: Config-driven with bidirectional support)
    # =========================================================================

    def render(self) -> None:
        """Render ENVOY.md with bidirectional support.

        OPUS-152: Uses render_sections() for output when config available.

        Flow:
        1. Process INPUT (user commands from file)
        2. Process completed tasks
        3. Generate OUTPUT (config-driven or fallback)
        """
        # DEFENSIVE CHECK: Verify EnvoyPlugin loaded
        if not hasattr(self.kernel, "envoy") or self.kernel.envoy is None:
            logger.warning("EnvoyPlugin not available - returning offline message")
            content = self._generate_offline_content()
            self.merge_and_write(content)
            return

        # INPUT: Process user commands FIRST
        self._sync_from_file()

        # Process completed tasks
        self._process_completed_tasks()

        # OUTPUT: Use config-driven sections if available
        config = self.get_config()
        if config and config.sections:
            content = self.render_sections()
            self.merge_and_write(content)
        else:
            # Fallback to hardcoded content
            content = self._generate_content()
            if content:
                self.merge_and_write(content)

    def generate_content(self) -> Optional[str]:
        """
        Legacy generate_content for compatibility.

        DEPRECATED: Use render() instead which calls render_sections().
        This method is kept for backwards compatibility only.
        """
        # DEFENSIVE CHECK: Verify EnvoyPlugin loaded (Fix 2 from OPUS-004)
        # If EnvoyPlugin failed to boot, show offline message instead of crashing
        if not hasattr(self.kernel, "envoy") or self.kernel.envoy is None:
            logger.warning("EnvoyPlugin not available - returning offline message")
            return self._generate_offline_content()

        # Process user input from ENVOY.md FIRST
        # This may add new tasks to pending_tasks
        self._sync_from_file()

        # THEN process completed tasks
        # This moves completed tasks from pending to history
        self._process_completed_tasks()

        # Return content for KING to write
        return self._generate_content()

    def _process_completed_tasks(self) -> None:
        """Process completed tasks and update state.

        Uses the kernel ledger to check for task completion events,
        since the kernel writes to ledger (not scheduler.completed).
        """
        if not hasattr(self.kernel, "ledger"):
            return

        for task_id in list(self.state.pending_tasks.keys()):
            # Query ledger for task status
            event = self.kernel.ledger.get_task(task_id)
            if not event:
                continue

            event_type = event.get("event_type", "")

            if event_type == "task_completed":
                result_val = event.get("result", {})
                # FIX 7: Extract response from result dict
                # Check circuit result structure first (phases_executed)
                response = ""
                if isinstance(result_val, dict):
                    # Try circuit result structure first
                    if "phases_executed" in result_val:
                        for phase in result_val.get("phases_executed", []):
                            if phase.get("phase_id") == "render_output":
                                response = phase.get("result", {}).get("rendered", "")
                                break
                    # Then try standard response field
                    if not response:
                        response = result_val.get("response", "")
                    # Then try other common fields
                    if not response:
                        response = (
                            result_val.get("message")
                            or result_val.get("summary")
                            or result_val.get("output")
                            or result_val.get("status")
                            or "Done"
                        )
                else:
                    response = str(result_val) if result_val else "Done"

                self.sync.update_task_status(
                    task_id, "COMPLETED", response, self.state.pending_tasks, self.state.request_history
                )

            elif event_type == "task_failed":
                error = event.get("error", "Unknown error")
                self.sync.update_task_status(
                    task_id, "FAILED", str(error), self.state.pending_tasks, self.state.request_history
                )

    def _sync_from_file(self) -> None:
        """Read and process user commands from ENVOY.md."""
        try:
            # FIX 1: Use EnvoyPlugin's UnifiedRouter (the ONLY way)
            # Legacy _playbook_router removed - UnifiedRouter is always available
            if not hasattr(self.kernel, "envoy"):
                logger.warning("EnvoyPlugin not loaded - cannot process requests")
                return
            router_callback = self._envoy_route_adapter

            result = self.sync.sync_to_reality(
                self.state,
                router_callback=router_callback,
                submit_callback=self.kernel.scheduler.submit_task,
                task_factory=lambda payload: self._create_task(payload),
            )

            if result:
                self.state.last_modified = result.new_mtime
                self.state.pending_tasks = result.pending_tasks
                self.state.request_history = result.history_entries
        except Exception as e:
            logger.error(f"Error syncing ENVOY.md: {e}")

    def _generate_content(self) -> str:
        """Generate ENVOY.md content."""
        lines = ["# ENVOY TERMINAL", ""]

        # Request Section - MUST match envoy_sync.py pattern "## 💬 Request"
        lines.extend(
            [
                "## 💬 Request",
                "",
                "> Write your request here (one per line).",
                "",
                "_No pending request. Write your request above this line._",
                "",
                "---",
                "",
            ]
        )

        # Status Section
        lines.extend(["## Status", "", "| Task ID | Status | Request |", "| :--- | :--- | :--- |"])

        if not self.state.pending_tasks:
            lines.append("_No active tasks_")
        else:
            for task_id, meta in self.state.pending_tasks.items():
                lines.append(f"| `{task_id}` | **{meta.get('status', 'UNKNOWN')}** | {meta.get('request', '')} |")

        lines.append("")

        # Response History
        lines.extend(
            ["## Response History", "", "| Time | Request | Status | Response |", "| :--- | :--- | :--- | :--- |"]
        )

        # Show last 5 entries
        for entry in reversed(self.state.request_history[-5:]):
            response = entry.get("response", "") or entry.get("error", "")
            if len(response) > 50:
                response = response[:47] + "..."
            lines.append(
                f"| {entry.get('timestamp', '')} | {entry.get('request', '')} | {entry.get('status', '')} | {response} |"
            )

        lines.append("")

        # Available Routes
        lines.extend(["## Available Routes", "", "| Route | Description |", "| :--- | :--- |"])

        # Get routes from EnvoyPlugin (the proper way)
        if hasattr(self.kernel, "envoy"):
            try:
                routes = self.kernel.envoy.get_routes()
                for route in routes[:20]:  # Limit display
                    name = route.get("name", "")
                    desc = route.get("description", "")[:50]
                    lines.append(f"| `{name}` | {desc} |")
                if not routes:
                    lines.append("| _No routes discovered_ | |")
            except Exception as e:
                logger.debug(f"Could not get routes: {e}")
                lines.append("| `bootstrap` | System Bootstrap |")
                lines.append("| `status` | System Status |")
        else:
            # Fallback if EnvoyPlugin not loaded
            lines.append("| `bootstrap` | System Bootstrap |")
            lines.append("| `status` | System Status |")
            lines.append("| _EnvoyPlugin not loaded_ | |")

        return "\n".join(lines)

    def _create_task(self, payload: Dict[str, Any]) -> "Task":
        """Helper to create a Task object from payload."""
        from vibe_core import Task

        return Task(**payload)

    def _generate_offline_content(self) -> str:
        """
        Generate ENVOY.md content when EnvoyPlugin is offline/failed.

        This is a defensive fallback that displays a helpful error message
        instead of crashing when the EnvoyPlugin boot fails.

        See: docs/architecture/OPUS/004-BOOT-SEQUENCE-AUDIT.md (Fix 2)
        """
        return """# ENVOY TERMINAL

## System Status

**ENVOY System Offline (Boot Failure)**

The ENVOY routing system failed to initialize. This typically means:
- ToolsPlugin failed to load before EnvoyPlugin
- Plugin priority order is misconfigured
- A critical boot dependency is missing

Check kernel logs for: `CRITICAL: ToolsPlugin (priority=5) must boot before EnvoyPlugin`

---

## Troubleshooting

1. Verify plugin priorities in `manifest.json`
2. Check that ToolsPlugin (priority=5) boots before EnvoyPlugin (priority=15)
3. Review `docs/architecture/OPUS/004-BOOT-SEQUENCE-AUDIT.md`

---

_This message generated by EnvoyRenderer defensive fallback._
"""
