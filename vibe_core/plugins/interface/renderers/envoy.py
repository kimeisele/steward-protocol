"""
Envoy Renderer (Terminal Interface).

Renders ENVOY.md and handles bidirectional terminal commands.
Uses EnvoyPlugin (kernel.envoy) for routing when available.
"""

import logging
from typing import TYPE_CHECKING, Any, Dict

from vibe_core.envoy_sync import EnvoySync, EnvoySyncState

from .base import BaseRenderer

if TYPE_CHECKING:
    from vibe_core import Task

logger = logging.getLogger("RENDERER_ENVOY")


class EnvoyRenderer(BaseRenderer):
    """Renders ENVOY.md and handles terminal commands."""

    def __init__(self, kernel):
        super().__init__(kernel)
        self.sync = EnvoySync()
        self.state = EnvoySyncState()

    @property
    def name(self) -> str:
        return "envoy"

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

    def render(self) -> None:
        """Render ENVOY.md with bidirectional sync."""
        # 0. Check for completed tasks
        if hasattr(self.kernel, "scheduler") and hasattr(self.kernel.scheduler, "completed"):
            completed_tasks = self.kernel.scheduler.completed
            for task_id in list(self.state.pending_tasks.keys()):
                if task_id in completed_tasks:
                    task = completed_tasks[task_id]
                    error = getattr(task, "error", None)
                    result_val = getattr(task, "result", None)

                    status = "COMPLETED" if not error else "FAILED"
                    response = str(result_val) if not error else str(error)

                    self.sync.update_task_status(
                        task_id, status, response, self.state.pending_tasks, self.state.request_history
                    )

        # 1. Sync to reality (Render + Read Commands)
        try:
            # Use EnvoyPlugin if available (the proper way)
            if hasattr(self.kernel, "envoy"):
                router_callback = self._envoy_route_adapter
            else:
                # Fallback to legacy _playbook_router
                router_callback = self.kernel._playbook_router.route

            result = self.sync.sync_to_reality(
                self.state,
                router_callback=router_callback,
                submit_callback=self.kernel.scheduler.submit_task,
                task_factory=lambda payload: self._create_task(payload),
            )

            # Update state from result
            if result:
                self.state.last_modified = result.new_mtime
                self.state.pending_tasks = result.pending_tasks
                self.state.request_history = result.history_entries

        except Exception as e:
            logger.error(f"Error syncing ENVOY.md: {e}")

        # 2. Generate and Write Document
        try:
            content = self._generate_content()
            self.sync.render_document(content)
        except Exception as e:
            logger.error(f"Error generating ENVOY.md: {e}")

    def _generate_content(self) -> str:
        """Generate ENVOY.md content."""
        lines = ["# ENVOY TERMINAL", ""]

        # Request Section
        lines.extend(
            [
                "## Request",
                "",
                "> Write your request here.",
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
