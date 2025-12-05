"""
Envoy Renderer (Terminal Interface).
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

    def render(self) -> None:
        # 0. Check for completed tasks
        if hasattr(self.kernel, "scheduler") and hasattr(self.kernel.scheduler, "completed"):
            completed_tasks = self.kernel.scheduler.completed
            # Create a copy of keys to avoid runtime error during iteration if modified
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
            result = self.sync.sync_to_reality(
                self.state,
                router_callback=self.kernel._playbook_router.route,
                submit_callback=self.kernel.scheduler.submit_task,
                task_factory=lambda payload: self._create_task(payload),
            )

            # Update state from result
            if result:
                self.state.last_modified = result.new_mtime
                self.state.pending_tasks = result.pending_tasks
                self.state.request_history = result.history_entries

                # Log if commands were executed
                # if result.commands_executed:
                #    logger.info(f"Executed {result.commands_executed} commands from ENVOY.md")

        except Exception as e:
            logger.error(f"Error rendering ENVOY.md: {e}")

        # 2. Generate and Write Document
        try:
            content = self._generate_content()
            self.sync.render_document(content)
        except Exception as e:
            logger.error(f"Error generating ENVOY.md: {e}")

    def _generate_content(self) -> str:
        """Generate ENVOY.md content."""
        lines = ["# 📬 ENVOY TERMINAL", ""]

        # Request Section
        lines.extend(
            [
                "## 💬 Request",
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
        lines.extend(["## 📊 Status", "", "| Task ID | Status | Request |", "| :--- | :--- | :--- |"])

        if not self.state.pending_tasks:
            lines.append("_No active tasks_")
        else:
            for task_id, meta in self.state.pending_tasks.items():
                lines.append(f"| `{task_id}` | **{meta.get('status', 'UNKNOWN')}** | {meta.get('request', '')} |")

        lines.append("")

        # Response History
        lines.extend(
            ["## 📜 Response History", "", "| Time | Request | Status | Response |", "| :--- | :--- | :--- | :--- |"]
        )

        # Show last 5 entries
        for entry in reversed(self.state.request_history[-5:]):
            response = entry.get("response", "") or entry.get("error", "")
            # Truncate response
            if len(response) > 50:
                response = response[:47] + "..."
            lines.append(
                f"| {entry.get('timestamp', '')} | {entry.get('request', '')} | {entry.get('status', '')} | {response} |"
            )

        lines.append("")

        # Available Routes
        lines.extend(["## 🎯 Available Routes", "", "| Route | Description |", "| :--- | :--- |"])

        # Get routes from router if possible
        if hasattr(self.kernel, "_playbook_router"):
            # This is a bit hacky, accessing private registry
            try:
                registry = self.kernel._playbook_router.registry
                for name, playbook in registry.items():
                    desc = playbook.description if hasattr(playbook, "description") else ""
                    lines.append(f"| `{name}` | {desc} |")
            except Exception:
                lines.append("| `bootstrap` | System Bootstrap |")
                lines.append("| `status` | System Status |")
        else:
            lines.append("| `bootstrap` | System Bootstrap |")
            lines.append("| `status` | System Status |")

        return "\n".join(lines)

    def _create_task(self, payload: Dict[str, Any]) -> "Task":
        """Helper to create a Task object from payload."""
        from vibe_core import Task

        return Task(**payload)
