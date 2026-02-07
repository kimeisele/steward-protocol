"""
LOTUS BRIDGE - Connecting MahamantraLotus to VenuService
========================================================

"sarvasya cāhaṁ hṛdi sanniviṣṭo"
"I am seated in everyone's heart"
— Bhagavad Gita 15.15

PROBLEM:
    MahamantraLotus.tick() uses time.time() % 16 — wall clock.
    VenuService uses monotonic time with drift compensation.
    BalaramaProxy gated listeners depend on Lotus tick().
    These are TWO INDEPENDENT heartbeats.

SOLUTION:
    LotusBridgeSubscriber is a BeatSubscriberProtocol that fires
    every tick (interval=1) and calls MahamantraLotus._broadcast()
    with the VenuService-derived position. This unifies the heartbeats.

    The Lotus listeners now dance to Krishna's flute, not the wall clock.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "nityananda"
__position__ = 1
__genesis__ = "0x4b8e2d5a"

import logging

from vibe_core.mahamantra.protocols._seed import WORDS

logger = logging.getLogger("LOTUS.BRIDGE")


class LotusBridgeSubscriber:
    """
    Bridges VenuService heartbeat → MahamantraLotus listeners.

    Fires every tick (250ms). On each tick, constructs the tick state
    that MahamantraLotus would produce and broadcasts it to all
    registered Lotus listeners.

    This means BalaramaProxy gated listeners now fire on VenuService
    timing instead of wall-clock timing. One drummer, one dance.

    Beat interval: 1 tick (every 250ms) — must be in sync with VenuService.
    """

    def __init__(self) -> None:
        self._lotus = None  # Lazy
        self._broadcast_count: int = 0

    @property
    def beat_name(self) -> str:
        return "lotus_bridge"

    @property
    def beat_interval(self) -> int:
        return 1  # Every tick — Lotus needs position-level granularity

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

        Constructs the Lotus tick state from VenuService position
        and broadcasts to all Lotus listeners. This replaces the
        wall-clock-based tick() with VenuService-driven timing.
        """
        lotus = self._get_lotus()
        if lotus is None:
            return

        # Only broadcast if Lotus has listeners
        listeners = getattr(lotus, '_listeners', [])
        if not listeners:
            return

        # Construct tick state matching MahamantraLotus.tick() format
        try:
            from vibe_core.mahamantra.substrate.opcode import MAHAMANTRA_SEQUENCE
            from vibe_core.mahamantra.substrate.seed import ALL_GUARDIANS, get_quarter_name

            pos = position % WORDS
            guardian = ALL_GUARDIANS[pos]
            word, opcode = MAHAMANTRA_SEQUENCE[pos]

            state = {
                "quarter": get_quarter_name(pos),
                "guardian": guardian,
                "word": word,
                "opcode": opcode.name,
                "position": pos,
                "tick": tick_count,
            }

            # Use Lotus's own broadcast mechanism
            lotus._broadcast(state)
            self._broadcast_count += 1

        except Exception as e:
            logger.debug("Lotus bridge broadcast failed: %s", e)

    @property
    def broadcast_count(self) -> int:
        """Total broadcasts sent to Lotus listeners."""
        return self._broadcast_count


__all__ = ["LotusBridgeSubscriber"]
