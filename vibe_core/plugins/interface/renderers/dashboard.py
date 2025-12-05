"""
Dashboard Renderer.
Renders DASHBOARD.md (Simplified Status).
"""

import logging

from .base import BaseRenderer

logger = logging.getLogger("RENDERER_DASHBOARD")


class DashboardRenderer(BaseRenderer):
    """Renders DASHBOARD.md."""

    @property
    def name(self) -> str:
        return "dashboard"

    def render(self) -> None:
        # For now, we'll just mirror OPERATIONS.md or keep it simple
        # The user's grep showed DASHBOARD.md is used.
        # Let's create a simple dashboard if DocRenderer doesn't support it directly.

        status = self.kernel.get_status()

        content = [
            "# 📊 Live Dashboard",
            "",
            f"**Status**: {status.get('status', 'UNKNOWN')}",
            f"**Time**: {status.get('timestamp', '')}",
            f"**Agents**: {len(self.kernel.agent_registry)}",
            f"**Tasks**: {self.kernel.scheduler.queue_size()}",
            "",
            "See [OPERATIONS.md](OPERATIONS.md) for detailed metrics.",
        ]

        try:
            self.kernel.io.write_document(
                name="DASHBOARD.md", content="\n".join(content), writer_id="RENDERER_DASHBOARD"
            )
        except Exception as e:
            logger.error(f"Error rendering DASHBOARD.md: {e}")
