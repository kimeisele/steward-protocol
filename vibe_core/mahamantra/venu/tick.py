"""
MANTRA TICK - The Heartbeat
===========================

The atomic unit of time in the Venu system.
Tracks position (0-15), cycle count, and mala count.

STATEFUL: This class maintains state (tick_count).
For pure calculations, use substrate/venu.py instead.
"""

from __future__ import annotations

from vibe_core.mahamantra.protocols._venu import (
    VENU_POSITIONS,
    VENU_TICKS_PER_MALA,
)


class MantraTick:
    """
    The atomic unit of time in the Venu system.

    A MantraTick tracks the current position in the 16-beat cycle.
    It is the HEARTBEAT of the rhythmic OS.

    Implements MantraTickProtocol.
    """

    __slots__ = ("_tick_count",)

    def __init__(self) -> None:
        """Initialize tick at position 0."""
        self._tick_count: int = 0

    @property
    def tick_count(self) -> int:
        """Total ticks since start (monotonically increasing)."""
        return self._tick_count

    @property
    def position(self) -> int:
        """Current position in the cycle (0-15)."""
        return self._tick_count % VENU_POSITIONS

    @property
    def cycle(self) -> int:
        """Current cycle number (tick_count // 16)."""
        return self._tick_count // VENU_POSITIONS

    @property
    def mala_count(self) -> int:
        """Number of complete Malas (cycles of 108 Pranas)."""
        return self._tick_count // VENU_TICKS_PER_MALA

    def advance(self) -> int:
        """
        Advance the tick by one.

        Returns:
            The new position (0-15)
        """
        self._tick_count += 1
        return self.position

    def __repr__(self) -> str:
        return f"MantraTick(tick={self._tick_count}, pos={self.position}, cycle={self.cycle})"
