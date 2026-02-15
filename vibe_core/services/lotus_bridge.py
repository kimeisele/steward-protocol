"""
LOTUS BRIDGE - RETIRED (VenuService now calls Singularity.tick() directly)
==========================================================================

"sarvasya cāhaṁ hṛdi sanniviṣṭo"
"I am seated in everyone's heart"
— Bhagavad Gita 15.15

HISTORY:
    This subscriber was a workaround for the disconnected heartbeat problem.
    VenuService used to call orchestrator.step() directly, bypassing
    Singularity._broadcast(). LotusBridgeSubscriber bridged the gap.

RETIRED:
    VenuService now calls Singularity.tick() directly (EKAMEVADVITIYAM).
    This subscriber is no longer needed. on_beat_tick() is a no-op.
    Kept for backward compatibility (beat_discovery.py lists it).
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
        """RETIRED: No-op. VenuService now calls Singularity.tick() directly.

        Previously this bridged VenuService → Singularity._broadcast().
        Now VenuService calls Singularity.tick() which does step() + broadcast.
        Calling lotus.tick() here would DOUBLE-TICK. So: no-op.
        """
        self._broadcast_count += 1

    @property
    def broadcast_count(self) -> int:
        """Total ticks bridged from VenuService to listeners."""
        return self._broadcast_count


__all__ = ["LotusBridgeSubscriber"]
