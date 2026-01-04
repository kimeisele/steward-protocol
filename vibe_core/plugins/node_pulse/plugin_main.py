"""
NodePulse Plugin - OPUS-166

Manages node.json lifecycle for registered agents.

ARCHITECTURE (Lasagne Layers):
1. AgentLoader - discovers agents (Layer 1)
2. Discoverer - registers with kernel (Layer 2)
3. CIVIC/Registry - legitimizes (Layer 3)
4. NodePulse - manages presence (Layer 4) ← THIS PLUGIN

This plugin:
1. On boot: Agents already call ensure_presence() via set_kernel()
2. On pulse: Updates all registered agents with KALA state
3. On shutdown: Calls release_presence() on all registered agents

The node.json file represents presence (agent is alive).
When kernel stops, files are deleted = agents are offline.

SELF-HEALING: If node.json is deleted, next pulse recreates it.

Priority: 4 (after KALA which is 3)
PulsePhase: ACTUATORS (writes state after sensors collect)
"""

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from vibe_core.plugin_protocol import HookResult, KernelPlugin, PulsePhase
from vibe_core.state.node_state import NodeState

if TYPE_CHECKING:
    from vibe_core.protocols.kernel_protocol import KernelProtocol
    from vibe_core.prana_orchestrator import PulseTransaction

logger = logging.getLogger("NODE_PULSE")


class NodePulsePlugin(KernelPlugin):
    """
    NodePulse - Manages agent node.json lifecycle via kernel registry.

    Uses kernel.agent_registry (proper registration) instead of
    scanning directories (spaghetti).

    Each pulse:
    1. Gets KALA state
    2. Iterates registered agents
    3. Calls agent.ensure_presence() with KALA state
    4. If node.json was deleted, it gets recreated (self-healing)
    """

    def __init__(self):
        """Initialize NodePulse plugin."""
        self._kernel: Optional["KernelProtocol"] = None
        self._pulse_count = 0
        self._agents_updated = 0

    @property
    def plugin_id(self) -> str:
        return "node_pulse"

    @property
    def priority(self) -> int:
        return 4  # After KALA (3) which provides time state

    @property
    def pulse_phase(self) -> PulsePhase:
        return PulsePhase.ACTUATORS  # Write state after sensors collect

    def on_boot(self, kernel: "KernelProtocol") -> None:
        """
        Initialize on kernel boot.

        Note: Agents already call ensure_presence() in set_kernel().
        This plugin just tracks state and provides pulse updates.
        """
        self._kernel = kernel

        # Count registered agents
        agent_count = len(self._get_registered_agents())

        logger.info("=" * 60)
        logger.info("📡 NODE PULSE PLUGIN BOOTED - PULS Layer Active")
        logger.info("=" * 60)
        logger.info(f"   Registered agents: {agent_count}")
        logger.info("   Agents manage their own presence via ensure_presence()")
        logger.info("   This plugin provides KALA state on each pulse")
        logger.info("=" * 60)

    def on_pulse(
        self,
        kernel: "KernelProtocol",
        transaction: "PulseTransaction",
    ) -> HookResult:
        """
        Update all registered agents with current KALA state.

        This runs every pulse (15 minutes).
        Each agent's ensure_presence() is called, which:
        - Updates node.json with KALA state
        - Recreates node.json if deleted (self-healing)
        """
        self._pulse_count += 1

        # Get KALA state from kernel's plugin registry
        kala_state = self._get_kala_state()

        updated = 0
        errors = 0

        for agent in self._get_registered_agents():
            try:
                # Call agent's ensure_presence with KALA state
                if hasattr(agent, "ensure_presence"):
                    if agent.ensure_presence(status="online", kala_state=kala_state):
                        updated += 1
                    else:
                        # Agent couldn't determine its path (e.g., dynamic agent)
                        pass
            except Exception as e:
                agent_id = getattr(agent, "agent_id", "unknown")
                logger.warning(f"Failed to pulse {agent_id}: {e}")
                errors += 1

        self._agents_updated = updated

        logger.debug(f"📡 NodePulse #{self._pulse_count}: {updated} updated, {errors} errors")

        return HookResult.ok(
            data={
                "pulse_count": self._pulse_count,
                "agents_updated": updated,
                "errors": errors,
                "kala_state": kala_state,
            }
        )

    def on_shutdown(self, kernel: "KernelProtocol") -> None:
        """
        Release presence for all registered agents.

        This is the key insight: file existence = agent alive.
        When kernel stops, agents are truly offline.
        """
        released = 0

        for agent in self._get_registered_agents():
            try:
                if hasattr(agent, "release_presence"):
                    if agent.release_presence():
                        released += 1
            except Exception as e:
                agent_id = getattr(agent, "agent_id", "unknown")
                logger.warning(f"Failed to release presence for {agent_id}: {e}")

        logger.info(f"📡 NodePulse shutdown: {released} agents released")

    def _get_registered_agents(self) -> List[Any]:
        """
        Get all registered agents from kernel.

        Uses kernel.agent_registry (proper registration mechanism).
        """
        if not self._kernel:
            return []

        try:
            if hasattr(self._kernel, "agent_registry"):
                return list(self._kernel.agent_registry.values())
        except Exception as e:
            logger.debug(f"Could not get agents from registry: {e}")

        return []

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
        agents = self._get_registered_agents()
        alive_count = 0

        for agent in agents:
            if hasattr(agent, "get_cartridge_path"):
                path = agent.get_cartridge_path()
                if path and NodeState.is_alive(path):
                    alive_count += 1

        return {
            "plugin_id": self.plugin_id,
            "pulse_count": self._pulse_count,
            "agents_registered": len(agents),
            "agents_alive": alive_count,
            "last_update_count": self._agents_updated,
        }
