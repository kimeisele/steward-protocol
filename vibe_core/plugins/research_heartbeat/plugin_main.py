"""
Research Heartbeat Plugin - Connects Research to Kernel Heartbeat
==================================================================

"yad yad ācarati śreṣṭhas tat tad evetaro janaḥ"
"Whatever action a great man performs, common men follow."
— Bhagavad Gita 3.21

This plugin bridges the research folder to production via the kernel heartbeat.
Uses the plugin architecture to avoid Ring 0 (kernel_impl.py) modification.

ARCHITECTURE:
=============

    Kernel Boot → PluginLoader → ResearchHeartbeatPlugin.on_boot()
                                        ↓
                              connect_research(kernel.chaitanya)
                                        ↓
                              RolloutTracker.register_proxy()
                                        ↓
                              Nrisimha → on_mantra_pulse() → RolloutTracker

ROLLOUT STAGES (from _rollout.py):
==================================

    RESEARCH → PROVEN → INTEGRATING → PRODUCTION

Each stage requires 64 heartbeat pulses (WORDS × QUARTERS) to advance.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x6e44c339"  # GenesisByte: parampara % 37 == 0

import logging
from typing import TYPE_CHECKING, Any, Dict, Optional

from vibe_core.mahamantra.protocols._seed import PARAMPARA
from vibe_core.plugin_protocol import HookResult, KernelPlugin

# Verify genesis
assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"

if TYPE_CHECKING:
    from vibe_core.protocols.kernel_protocol import KernelProtocol as VibeKernel
else:
    VibeKernel = Any

logger = logging.getLogger("RESEARCH_HEARTBEAT")


class ResearchHeartbeatPlugin(KernelPlugin):
    """
    Plugin that connects research modules to kernel heartbeat.

    Registers RolloutTracker with Nrisimha watchdog to receive
    heartbeat pulses and track module rollout stages.
    """

    @property
    def plugin_id(self) -> str:
        return "research_heartbeat"

    def on_boot(self, kernel: VibeKernel, config: Optional[Dict[str, Any]] = None) -> HookResult:
        """
        Connect research modules to heartbeat on kernel boot.

        This is the PARAMPARA bridge - research hears the kernel's heartbeat.
        """
        try:
            from vibe_core.mahamantra.research_gateway import connect_research

            # Get NrisimhaWatchdog (kernel.chaitanya)
            if not hasattr(kernel, "chaitanya") or kernel.chaitanya is None:
                logger.warning("⚠️ Kernel has no chaitanya (NrisimhaWatchdog)")
                return HookResult.ok()  # Non-fatal

            # Connect research modules to heartbeat
            result = connect_research(kernel.chaitanya)

            logger.info(f"🔬 RESEARCH_HEARTBEAT: {result['modules_tracked']} modules connected")
            return HookResult.ok()

        except Exception as e:
            logger.warning(f"⚠️ Research gateway connection failed: {e}")
            return HookResult.ok()  # Non-fatal - kernel should boot anyway

    def on_pulse(self, kernel: VibeKernel, transaction: Any) -> Dict[str, Any]:
        """
        Called on each kernel pulse - report research status.
        """
        try:
            from vibe_core.mahamantra.research_gateway import get_research_status

            status = get_research_status()
            return {
                "success": True,
                "research_modules": status.get("modules", 0),
                "total_pulses": status.get("total_pulses", 0),
                "by_stage": status.get("by_stage", {}),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# Entry point for PluginLoader
def get_plugin():
    """Factory function for PluginLoader."""
    return ResearchHeartbeatPlugin()
