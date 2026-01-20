"""
MANTRA VOICE - Parallel Execution Channel
=========================================

A voice is a parallel execution channel.
Like voices in music, multiple MantraVoices can play simultaneously,
each with their own queue of tasks per position.

STATEFUL: This class maintains task queues.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 4
__genesis__ = "0x6a00189f"  # GenesisByte: parampara % 37 == 0

from typing import Callable, List, TypeVar

from vibe_core.mahamantra.protocols._venu import VENU_POSITIONS

T = TypeVar("T")


class MantraVoice:
    """
    A voice is a parallel execution channel.

    Like voices in music, multiple MantraVoices can play simultaneously,
    each with their own queue of tasks per position.

    Implements MantraVoiceProtocol.
    """

    __slots__ = ("_voice_id", "_tasks")

    def __init__(self, voice_id: int) -> None:
        """
        Initialize a voice with a unique ID.

        Args:
            voice_id: Unique identifier for this voice
        """
        self._voice_id = voice_id
        # Tasks per position: 16 lists (one per position)
        self._tasks: List[List[Callable[[], object]]] = [[] for _ in range(VENU_POSITIONS)]

    @property
    def voice_id(self) -> int:
        """Unique identifier for this voice."""
        return self._voice_id

    def submit(self, task: Callable[[], T], position: int | None = None) -> None:
        """
        Submit a task to be executed at a specific position.

        Args:
            task: The callable to execute
            position: The position (0-15) to execute at, or None for position 0
        """
        if position is None:
            position = 0  # Default to next downbeat
        if not 0 <= position < VENU_POSITIONS:
            raise ValueError(f"Position must be 0-{VENU_POSITIONS - 1}, got {position}")
        self._tasks[position].append(task)

    def get_tasks(self, position: int) -> List[Callable[[], object]]:
        """
        Get all tasks queued for a specific position.

        Args:
            position: The position (0-15)

        Returns:
            List of tasks queued for that position
        """
        if not 0 <= position < VENU_POSITIONS:
            raise ValueError(f"Position must be 0-{VENU_POSITIONS - 1}, got {position}")
        return list(self._tasks[position])  # Return a copy

    def clear(self, position: int) -> None:
        """Clear all tasks at a specific position after execution."""
        if not 0 <= position < VENU_POSITIONS:
            raise ValueError(f"Position must be 0-{VENU_POSITIONS - 1}, got {position}")
        self._tasks[position].clear()

    def __repr__(self) -> str:
        total_tasks = sum(len(t) for t in self._tasks)
        return f"MantraVoice(id={self._voice_id}, tasks={total_tasks})"
