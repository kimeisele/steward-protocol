"""
Dashboard Renderer.
Renders DASHBOARD.md (Simplified Status).

UNIFIED UI: Implements generate_content() pattern.
"""

import logging
from typing import Optional

from vibe_core.io_service import DocumentType

from .base import BaseRenderer

logger = logging.getLogger("RENDERER_DASHBOARD")


class DashboardRenderer(BaseRenderer):
    """Renders DASHBOARD.md."""

    @property
    def name(self) -> str:
        return "dashboard"

    @property
    def output_file(self) -> str:
        return "DASHBOARD.md"

    @property
    def doc_type(self) -> DocumentType:
        return DocumentType.READONLY

    def generate_content(self) -> Optional[str]:
        """Generate DASHBOARD.md content (UNIFIED UI pattern)."""
        try:
            status = self.kernel.get_status()
            queue_size = 0
            if hasattr(self.kernel, "scheduler"):
                if hasattr(self.kernel.scheduler, "queue_size"):
                    queue_size = self.kernel.scheduler.queue_size()
                elif hasattr(self.kernel.scheduler, "_queue"):
                    queue_size = len(self.kernel.scheduler._queue)

            lines = [
                "# 📊 Live Dashboard",
                "",
                f"**Status**: {status.get('status', 'UNKNOWN')}",
                f"**Time**: {status.get('timestamp', '')}",
                f"**Agents**: {len(self.kernel.agent_registry)}",
                f"**Tasks**: {queue_size}",
                "",
                "See [OPERATIONS.md](OPERATIONS.md) for detailed metrics.",
            ]
            return "\n".join(lines)
        except Exception as e:
            logger.error(f"Error generating DASHBOARD content: {e}")
            return None
