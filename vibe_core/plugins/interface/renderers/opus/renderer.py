"""
OPUS Renderer - AI Workspace Dashboard.

OPUS.md is MY (Claude's) master dashboard for tracking kernel work.

Sections:
- LIVE (auto-updated): status, metrics
- AI (I maintain): current_goal, phase_status, extraction_log, blockers
- HUMAN (user writes): next_actions

The AI sections are PRESERVED between renders - I update them as I work.
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List

from ..base import BaseRenderer

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("RENDERER_OPUS")


class OpusRenderer(BaseRenderer):
    """Renders OPUS.md - the AI workspace dashboard."""

    def __init__(self, kernel: "RealVibeKernel"):
        super().__init__(kernel)
        self._kernel_path = Path("vibe_core/kernel_impl.py")
        self._register_data_sources()

    @property
    def name(self) -> str:
        return "opus"

    def _register_data_sources(self) -> None:
        """Register LIVE data sources only."""
        self.register_data_source("kernel.status", self._get_kernel_status)
        self.register_data_source("opus.metrics", self._get_metrics)

    def render(self) -> None:
        """Render OPUS.md with section preservation."""
        config = self.get_config()
        if config and config.sections:
            content = self.render_sections()
            self.merge_and_write(content)

    # =========================================================================
    # LIVE DATA SOURCES (auto-updated)
    # =========================================================================

    def _get_kernel_status(self) -> str:
        """Kernel status line."""
        status = getattr(self.kernel, "status", "UNKNOWN")
        if hasattr(status, "value"):
            status = status.value

        agent_count = 0
        if hasattr(self.kernel, "agent_registry"):
            try:
                agent_count = len(self.kernel.agent_registry.list_agents())
            except Exception:
                pass

        loc = self._count_kernel_loc()
        return f"**Kernel**: {status} | **Agents**: {agent_count} | **LOC**: {loc}"

    def _get_metrics(self) -> List[Dict[str, Any]]:
        """Kernel metrics table."""
        loc = self._count_kernel_loc()
        target = 1008

        plugin_count = len(self.kernel._plugins) if hasattr(self.kernel, "_plugins") else 0

        return [
            {
                "Metric": "kernel_impl.py LOC",
                "Current": loc,
                "Target": target,
                "Status": "✅" if loc <= target else ("🟡" if loc <= target + 100 else "🔴"),
            },
            {
                "Metric": "Plugins Loaded",
                "Current": plugin_count,
                "Target": "8+",
                "Status": "✅" if plugin_count >= 8 else "🟡",
            },
        ]

    def _count_kernel_loc(self) -> int:
        """Count kernel lines of code."""
        try:
            if self._kernel_path.exists():
                return len(self._kernel_path.read_text().splitlines())
        except Exception:
            pass
        return 0


def create_renderer(kernel: "RealVibeKernel", config: Dict[str, Any]) -> OpusRenderer:
    """Factory function."""
    return OpusRenderer(kernel)
