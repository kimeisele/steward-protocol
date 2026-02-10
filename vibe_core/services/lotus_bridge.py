"""
LOTUS BRIDGE - Connecting MahamantraLotus to VenuService
========================================================

"sarvasya cāhaṁ hṛdi sanniviṣṭo"
"I am seated in everyone's heart"
— Bhagavad Gita 15.15

PROBLEM:
    VenuService calls orchestrator.step() — bit-level heartbeat.
    Singularity._listeners (Nrisimha, MahaCompute, DriftAuditor, Proxy)
    need semantic-level TickState broadcasts via tick().

SOLUTION:
    LotusBridgeSubscriber fires every VenuService tick and calls
    lotus.tick(). The _owned guard on VenuOrchestrator prevents
    double-stepping — tick() reads _prev_state instead of calling step().
    Kala advances correctly, full TickState is broadcast to all listeners.

    One flute, one dance. No manual state construction.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "nityananda"
__position__ = 1
__genesis__ = "0x4b8e2d5a"

import logging

logger = logging.getLogger("LOTUS.BRIDGE")


class LotusBridgeSubscriber:
    """
    Bridges VenuService heartbeat → Singularity._listeners.

    Fires every tick (250ms). Calls lotus.tick() which:
    - Advances Kala (time) — correct, VenuService IS the heartbeat
    - Reads _prev_state via _owned guard (no double step())
    - Broadcasts full TickState to all Singularity._listeners

    Beat interval: 1 tick (every 250ms) — in sync with VenuService.
    """

    def __init__(self) -> None:
        self._lotus = None  # Lazy
        self._broadcast_count: int = 0

    @property
    def beat_name(self) -> str:
        return "lotus_bridge"

    @property
    def beat_interval(self) -> int:
        return 1  # Every tick — listeners need position-level granularity

    def _get_lotus(self):
        """Lazy access to MahamantraLotus singleton."""
        if self._lotus is None:
            try:
                from vibe_core.mahamantra import mahamantra
                self._lotus = mahamantra
            except Exception as e:
                logger.debug("MahamantraLotus not available: %s", e)
        return self._lotus

    def on_beat_tick(self, tick_count: int, position: int) -> None:
        """Called by VenuService every tick.

        Delegates to lotus.tick() which advances Kala and broadcasts
        the full TickState to all Singularity._listeners. The _owned
        guard ensures step() is not called again — just reads _prev_state.
        """
        lotus = self._get_lotus()
        if lotus is None:
            return

        try:
            lotus.tick()
            self._broadcast_count += 1
        except Exception as e:
            logger.debug("Lotus bridge tick failed: %s", e)

    @property
    def broadcast_count(self) -> int:
        """Total ticks bridged from VenuService to listeners."""
        return self._broadcast_count


__all__ = ["LotusBridgeSubscriber"]
