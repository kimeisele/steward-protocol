"""
NodePulse Plugin - OPUS-166

Manages node.json lifecycle for Agent City.

This plugin:
1. On boot: Creates node.json for all discovered cartridges
2. On pulse: Updates node.json with current KALA time state
3. On shutdown: Deletes all node.json files (agents go offline)

The node.json file represents presence (agent is alive).
When kernel stops, files are deleted = agents are offline.

Priority: 4 (after KALA which is 3)
PulsePhase: ACTUATORS (writes state after sensors collect)
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from vibe_core.plugin_protocol import HookResult, KernelPlugin, PulsePhase
from vibe_core.state.node_state import NodeState

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel
    from vibe_core.prana_orchestrator import PulseTransaction

logger = logging.getLogger("NODE_PULSE")


class NodePulsePlugin(KernelPlugin):
    """
    NodePulse - Manages cartridge node.json lifecycle.

    Creates node.json on boot, updates with KALA on pulse, deletes on shutdown.
    This enables the PULS layer for inter-agent communication.
    """

    def __init__(self):
        """Initialize NodePulse plugin."""
        self._kernel: Optional["RealVibeKernel"] = None
        self._cartridge_paths: List[Path] = []
        self._pulse_count = 0
        self._project_root: Optional[Path] = None

    @property
    def plugin_id(self) -> str:
        return "node_pulse"

    @property
    def priority(self) -> int:
        return 4  # After KALA (3) which provides time state

    @property
    def pulse_phase(self) -> PulsePhase:
        return PulsePhase.ACTUATORS  # Write state after sensors collect

    def on_boot(self, kernel: "RealVibeKernel") -> None:
        """
        Initialize node.json for all discovered cartridges.

        Called during boot after KALA is initialized.
        """
        self._kernel = kernel
        self._project_root = Path.cwd()

        # Discover all cartridges
        self._discover_cartridges()

        # Create node.json for each
        created = 0
        for path in self._cartridge_paths:
            try:
                NodeState.create(path, status="booting")
                created += 1
            except Exception as e:
                logger.warning(f"Failed to create node.json for {path.name}: {e}")

        logger.info("=" * 60)
        logger.info("📡 NODE PULSE PLUGIN BOOTED - PULS Layer Active")
        logger.info("=" * 60)
        logger.info(f"   Cartridges discovered: {len(self._cartridge_paths)}")
        logger.info(f"   node.json files created: {created}")
        logger.info("=" * 60)

        # Set all to online now that boot is complete
        for path in self._cartridge_paths:
            try:
                NodeState.pulse(path, status="online")
            except Exception:
                pass

    def on_pulse(
        self,
        kernel: "RealVibeKernel",
        transaction: "PulseTransaction",
    ) -> HookResult:
        """
        Update all node.json files with current KALA state.

        This runs every 15 minutes via PRANA.
        """
        self._pulse_count += 1

        # Get KALA state from kernel's plugin registry
        kala_state = self._get_kala_state()

        updated = 0
        errors = 0

        for path in self._cartridge_paths:
            try:
                NodeState.pulse(
                    path,
                    status="online",
                    kala_state=kala_state,
                )
                updated += 1
            except Exception as e:
                logger.warning(f"Failed to pulse {path.name}: {e}")
                errors += 1

        logger.debug(f"📡 NodePulse #{self._pulse_count}: {updated} updated, {errors} errors")

        return HookResult.ok(
            data={
                "pulse_count": self._pulse_count,
                "nodes_updated": updated,
                "errors": errors,
                "kala_state": kala_state,
            }
        )

    def on_shutdown(self, kernel: "RealVibeKernel") -> None:
        """
        Delete all node.json files - agents go offline.

        This is the key insight: file existence = agent alive.
        When kernel stops, agents are truly offline.
        """
        deleted = 0

        for path in self._cartridge_paths:
            try:
                if NodeState.die(path):
                    deleted += 1
            except Exception as e:
                logger.warning(f"Failed to delete node.json for {path.name}: {e}")

        logger.info(f"📡 NodePulse shutdown: {deleted} node.json files deleted")

    def _discover_cartridges(self) -> None:
        """
        Discover all cartridge directories.

        Looks in:
        - vibe_core/cartridges/agent_city/
        - vibe_core/cartridges/system/
        """
        self._cartridge_paths = []

        if not self._project_root:
            return

        cartridge_roots = [
            self._project_root / "vibe_core" / "cartridges" / "agent_city",
            self._project_root / "vibe_core" / "cartridges" / "system",
        ]

        for root in cartridge_roots:
            if not root.exists():
                continue

            for item in root.iterdir():
                if item.is_dir() and not item.name.startswith("_"):
                    # Check if it has a steward.json (valid cartridge)
                    if (item / "steward.json").exists():
                        self._cartridge_paths.append(item)

        logger.debug(f"Discovered {len(self._cartridge_paths)} cartridges")

    def _get_kala_state(self) -> Dict[str, Any]:
        """
        Get current KALA time state from the kernel.

        Falls back to empty state if KALA not available.
        """
        try:
            # Try to get KALA plugin from kernel
            if hasattr(self._kernel, "plugin_loader"):
                plugins = self._kernel.plugin_loader.get_active_plugins()
                for plugin in plugins:
                    if getattr(plugin, "plugin_id", "") == "kala":
                        state = plugin.get_current_state()
                        if "error" not in state:
                            return {
                                "sun_phase": state.get("sun_phase", "UNKNOWN"),
                                "moon_phase": state.get("moon_phase", "UNKNOWN"),
                                "tithi": state.get("tithi", 0),
                                "paksha": state.get("paksha", "unknown"),
                                "rhythm_intensity": state.get("rhythm_intensity", 0.0),
                            }
        except Exception as e:
            logger.debug(f"Could not get KALA state: {e}")

        # Fallback: return empty state
        return {}

    def get_status(self) -> Dict[str, Any]:
        """Get plugin status for observability."""
        alive_count = sum(1 for p in self._cartridge_paths if NodeState.is_alive(p))

        return {
            "plugin_id": self.plugin_id,
            "pulse_count": self._pulse_count,
            "cartridges_total": len(self._cartridge_paths),
            "cartridges_alive": alive_count,
            "cartridge_names": [p.name for p in self._cartridge_paths],
        }
