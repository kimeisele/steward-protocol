"""
Envoy Renderer (Terminal Interface).

Renders ENVOY.md and handles bidirectional terminal commands.
Uses EnvoyPlugin (kernel.envoy) for routing when available.
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, Optional

from vibe_core.envoy_sync import EnvoySync, EnvoySyncState
from vibe_core.io_service import DocumentType

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

    def generate_content(self) -> Optional[str]:
        """
        Generate ENVOY.md content (UNIFIED UI pattern).

        Note: This renderer is BIDIRECTIONAL. Input processing
        happens in on_tick_pre via render(). This method only
        generates the output content for the KING to write.
        """
        # Process any completed tasks first
        self._process_completed_tasks()

        # Process user input from ENVOY.md
        self._sync_from_file()

        # Return content for KING to write
        return self._generate_content()

    def _process_completed_tasks(self) -> None:
        """Process completed tasks and update state."""
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

    def _sync_from_file(self) -> None:
        """Read and process user commands from ENVOY.md."""
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

            if result:
                self.state.last_modified = result.new_mtime
                self.state.pending_tasks = result.pending_tasks
                self.state.request_history = result.history_entries
        except Exception as e:
            logger.error(f"Error syncing ENVOY.md: {e}")

    def render(self) -> None:
        """Legacy render - DEPRECATED. Use generate_content()."""
        # Process completed tasks
        self._process_completed_tasks()

        # Sync from file (read user commands)
        self._sync_from_file()

        # Generate and Write Document (legacy - sync writes directly)
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
