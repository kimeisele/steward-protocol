"""
Envoy Renderer (Terminal Interface).
"""

import logging
from typing import TYPE_CHECKING, Any, Dict

from vibe_core.envoy_sync import EnvoySync

from .base import BaseRenderer

if TYPE_CHECKING:
    from vibe_core import Task

logger = logging.getLogger("RENDERER_ENVOY")


class EnvoyRenderer(BaseRenderer):
    """Renders ENVOY.md and handles terminal commands."""

    def __init__(self, kernel):
        super().__init__(kernel)
        self.sync = EnvoySync()

    @property
    def name(self) -> str:
        return "envoy"

    def render(self) -> None:
        # Prepare state for rendering
        state = {
            "agents": self.kernel.agent_registry,
            "scheduler": {
                "queue_size": self.kernel.scheduler.queue_size(),
                "active_tasks": len(self.kernel.scheduler.active_tasks),
            },
            "status": self.kernel.get_status(),
        }

        # Sync to reality (Render + Read Commands)
        try:
            result = self.sync.sync_to_reality(
                state,
                router_callback=self.kernel._playbook_router.route,
                submit_callback=self.kernel.scheduler.submit_task,
                task_factory=lambda payload: self._create_task(payload),
            )

            # Log if commands were executed
            if result and result.get("commands_executed"):
                logger.info(f"Executed {result['commands_executed']} commands from ENVOY.md")

        except Exception as e:
            logger.error(f"Error rendering ENVOY.md: {e}")

    def _create_task(self, payload: Dict[str, Any]) -> "Task":
        """Helper to create a Task object from payload."""
        from vibe_core import Task

        return Task(**payload)
