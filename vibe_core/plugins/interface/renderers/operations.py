"""
Operations Renderer.
Renders OPERATIONS.md (Dashboard).
"""

import logging
from typing import TYPE_CHECKING

from vibe_core.doc_renderer import DocRenderer

from .base import BaseRenderer

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("RENDERER_OPERATIONS")


class OperationsRenderer(BaseRenderer):
    """Renders OPERATIONS.md using DocRenderer logic."""

    def __init__(self, kernel: "RealVibeKernel"):
        super().__init__(kernel)
        self.doc_renderer = DocRenderer(io_service=kernel.io)

    @property
    def name(self) -> str:
        return "operations"

    def render(self) -> None:
        # Gather snapshot
        snapshot = {
            "timestamp": self.kernel.get_status().get("timestamp", ""),
            "kernel_status": self.kernel.get_status().get("status", "UNKNOWN"),
            "agents": self.kernel.agent_registry,
            "scheduler": {
                "queue_length": self.kernel.scheduler.queue_size(),
                "completed": self.kernel.scheduler.completed_count,
            },
            "ledger_stats": {
                "total_events": self.kernel.ledger.get_event_count()
                if hasattr(self.kernel.ledger, "get_event_count")
                else 0
            },
        }

        try:
            self.doc_renderer.render_operations(snapshot)
        except Exception as e:
            logger.error(f"Error rendering OPERATIONS.md: {e}")
