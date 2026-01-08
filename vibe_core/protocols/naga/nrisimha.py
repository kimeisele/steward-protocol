"""
NRISIMHA PROTOCOL - The Timekeeper (Layer 0.5)

"Nrisimha" - The Half-Man/Half-Lion Avatar. Protector against Hiranyakashipu (Chaos).
He sets the Rhythm of Time (Kala) by chanting the Mahamantra.

Responsibilities:
1. CHANT: Broadcast the 16 OpCodes (Mantra) to all registered Nagas.
2. WATCH: Checks if Nagas respond to the pulse.
3. PROTECT: Removes (kills) rogue agents that fail to chant.

PHILOSOPHY:
"Yare dekha tare kaha krishna-upadesha" - Whomever you meet, tell them of Krishna.
Nrisimha tells everyone the OpCodes. If they don't listen, they are Maya.

Status: TIMEKEEPER / WATCHDOG
"""

import logging
import time
from typing import Any, List, Tuple

from vibe_core.protocols.naga.balarama import BalaramaProxy
from vibe_core.protocols.naga.base import NagaBase
from vibe_core.protocols.substrate import MAHAMANTRA_SEQUENCE, MantraOpCode

# Nrisimha Capabilities
NRISIMHA_CAPS = ("chant", "protect", "watch")


class NrisimhaWatchdog(NagaBase):
    """
    The Nrisimha Watchdog (Timekeeper).

    A Devotee Naga that:
    - Chants the Mahamantra (108 times).
    - Broadcasts OpCodes to all Balarama Proxies.
    - Purges dead/rogue agents.
    """

    def __init__(self):
        super().__init__(name="nrisimha", capabilities=NRISIMHA_CAPS)
        self._proxies: List[BalaramaProxy] = []
        self._cycle_count = 0
        self._logger = logging.getLogger("nrisimha")

    def register_proxy(self, proxy: BalaramaProxy) -> None:
        """Add a Naga to the chanting circle."""
        if proxy not in self._proxies:
            self._proxies.append(proxy)

    def unregister_proxy(self, proxy: BalaramaProxy) -> None:
        """Remove a Naga from the chanting circle."""
        if proxy in self._proxies:
            self._proxies.remove(proxy)

    # =========================================================================
    # GENERIC SERVICE (SEVA)
    # =========================================================================

    def serve(self, request: Any) -> Any:
        """Generic entry point."""
        if not isinstance(request, dict):
            return "UNKNOWN REQUEST"

        action = request.get("action")

        if action == "chant_round":
            return self.chant_japa_round()

        return "UNKNOWN ACTION"

    # =========================================================================
    # CHANTING (THE JAPA)
    # =========================================================================

    def chant_japa_round(self) -> str:
        """
        Führt eine volle Runde (108) aus.
        Total OpCodes: 108 * 16 = 1728 Operations.
        """
        beads = 108
        total_ops = 0

        start_time = time.time()

        for bead in range(beads):
            # 16 Schrittes des Mahamantra pro Perle
            for word, opcode in MAHAMANTRA_SEQUENCE:
                self.broadcast_pulse(opcode)
                total_ops += 1

            # Optional: Tiny sleep to not burn CPU?
            # No, Nrisimha is intense. But maybe yield.
            time.sleep(0.001)

        self._cycle_count += 1
        duration = time.time() - start_time

        return f"JAPA COMPLETE: {beads} beads, {total_ops} ops in {duration:.2f}s"

    def broadcast_pulse(self, opcode: MantraOpCode) -> None:
        """
        Broadcast OpCode to all proxies.
        Kill rogue agents.
        """
        rogue_agents = []

        for proxy in self._proxies:
            try:
                # The Proxy (Balarama) handles the pulse
                proxy.on_mantra_pulse(opcode)
            except Exception as e:
                # Wer nicht chantet, stirbt (Surrender Protocol)
                # Balarama usually absorbs, but if on_mantra_pulse fails,
                # it means Balarama itself is broken or the agent is resisting heavily.
                self._logger.error(f"NRISIMHA: Killing rogue agent {proxy._name}: {e}")
                rogue_agents.append(proxy)

        # Purge
        for rogue in rogue_agents:
            self.unregister_proxy(rogue)
