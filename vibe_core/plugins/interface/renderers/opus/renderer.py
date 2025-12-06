"""
OPUS Renderer - Master AI Dashboard.

Extends ArchitectureRenderer with AI/Human sections.
"""

from typing import TYPE_CHECKING, Any, Dict, List

from ..architecture.renderer import ArchitectureRenderer

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel


class OpusRenderer(ArchitectureRenderer):
    """Master AI Dashboard - extends Architecture with AI sections."""

    @property
    def name(self) -> str:
        return "opus"

    def _register_data_sources(self) -> None:
        """Register arch.* sources + opus-specific."""
        super()._register_data_sources()
        self.register_data_source("kernel.status", self._get_kernel_status)
        self.register_data_source("opus.metrics", self._get_metrics)

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

        loc = self._count_loc("vibe_core/kernel_impl.py")
        return f"**Kernel**: {status} | **Agents**: {agent_count} | **LOC**: {loc}"

    def _get_metrics(self) -> List[Dict[str, Any]]:
        """Kernel metrics table."""
        loc = self._count_loc("vibe_core/kernel_impl.py")
        target = 1008
        plugin_count = len(self.kernel._plugins) if hasattr(self.kernel, "_plugins") else 0

        return [
            {
                "Metric": "kernel_impl.py LOC",
                "Current": loc,
                "Target": target,
                "Delta": loc - target,
                "Status": "✅" if loc <= target else ("🟡" if loc <= target + 100 else "🔴"),
            },
            {
                "Metric": "Plugins Loaded",
                "Current": plugin_count,
                "Target": "8+",
                "Delta": "-",
                "Status": "✅" if plugin_count >= 8 else "🟡",
            },
        ]


def create_renderer(kernel: "RealVibeKernel", config: Dict[str, Any]) -> OpusRenderer:
    """Factory function."""
    return OpusRenderer(kernel)
