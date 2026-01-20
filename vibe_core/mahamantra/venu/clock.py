"""
MANTRA CLOCK - The Master Scheduler
===================================

The MantraClock orchestrates MantraVoices, ticking through
positions and executing tasks at each beat.

This is the DRUMMER of the Venu system.

STATEFUL: This class maintains the tick counter and voices.
"""

from __future__ import annotations

from typing import Callable, List

from vibe_core.mahamantra.protocols._venu import (
    VENU_POSITIONS,
    VENU_TICKS_PER_MALA,
    MantraTickProtocol,
    MantraVoiceProtocol,
)
from vibe_core.mahamantra.venu.tick import MantraTick
from vibe_core.mahamantra.venu.voice import MantraVoice


class MantraClock:
    """
    The Master Clock - The Drummer of the Venu system.

    The MantraClock orchestrates MantraVoices, ticking through
    positions and executing tasks at each beat.

    Implements MantraClockProtocol.
    """

    __slots__ = (
        "_tick",
        "_voices",
        "_next_voice_id",
        "_position_callbacks",
        "_mala_callbacks",
    )

    def __init__(self) -> None:
        """Initialize the clock with no voices."""
        self._tick = MantraTick()
        self._voices: List[MantraVoice] = []
        self._next_voice_id = 0
        # Callbacks per position
        self._position_callbacks: List[List[Callable[[], None]]] = [
            [] for _ in range(VENU_POSITIONS)
        ]
        # Mala completion callbacks
        self._mala_callbacks: List[Callable[[int], None]] = []

    @property
    def tick(self) -> MantraTickProtocol:
        """The underlying tick counter."""
        return self._tick

    @property
    def voices(self) -> List[MantraVoiceProtocol]:
        """All registered voices."""
        return list(self._voices)  # Return a copy

    @property
    def position(self) -> int:
        """Current position (delegated to tick)."""
        return self._tick.position

    def add_voice(self) -> MantraVoiceProtocol:
        """Create and register a new voice."""
        voice = MantraVoice(voice_id=self._next_voice_id)
        self._next_voice_id += 1
        self._voices.append(voice)
        return voice

    def on_position(self, position: int, callback: Callable[[], None]) -> None:
        """
        Register a callback to be called when reaching a position.

        Args:
            position: The position (0-15) to trigger on
            callback: The function to call
        """
        if not 0 <= position < VENU_POSITIONS:
            raise ValueError(f"Position must be 0-{VENU_POSITIONS - 1}, got {position}")
        self._position_callbacks[position].append(callback)

    def on_mala(self, callback: Callable[[int], None]) -> None:
        """
        Register a callback for Mala completion.

        Args:
            callback: Function called with mala_count when a Mala completes
        """
        self._mala_callbacks.append(callback)

    def tick_once(self) -> int:
        """
        Execute one tick: run all tasks at current position, then advance.

        Returns:
            The new position after advancing
        """
        current_pos = self._tick.position

        # 1. Execute position callbacks
        for callback in self._position_callbacks[current_pos]:
            callback()

        # 2. Execute tasks from all voices at current position
        for voice in self._voices:
            tasks = voice.get_tasks(current_pos)
            for task in tasks:
                task()
            voice.clear(current_pos)

        # 3. Advance the tick
        new_pos = self._tick.advance()

        # 4. Check for Mala completion (after advancing)
        if self._tick.tick_count > 0 and self._tick.tick_count % VENU_TICKS_PER_MALA == 0:
            mala_count = self._tick.mala_count
            for callback in self._mala_callbacks:
                callback(mala_count)

        return new_pos

    def __repr__(self) -> str:
        return f"MantraClock(pos={self.position}, voices={len(self._voices)})"
