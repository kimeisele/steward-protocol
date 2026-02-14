"""Incremental keystroke processing for live tick-based language generation.

Each keystroke updates a running buffer. On every Venu tick, the current buffer
state is snapshotted as a TickInputFrame. The rhythm profile is recomputed
incrementally so the sequencer grid stays in sync with the live input.

This is the bridge between "user types a letter" and "the field vibrates".
"""

from __future__ import annotations

from collections import deque
from threading import Lock
from typing import Deque, List, NamedTuple, Optional, Tuple

from .contracts import RuntimeTick


class TickInputFrame(NamedTuple):
    """Snapshot of user input at a specific Venu tick."""

    text: str
    tick: Optional[RuntimeTick]
    syllable_count: int
    stress_pattern: Tuple[int, ...]
    sequencer_steps: Tuple[int, ...]
    dirty: bool  # True if text changed since last frame


class IncrementalBuffer:
    """Thread-safe keystroke buffer that produces TickInputFrames.

    Usage:
        buf = IncrementalBuffer()
        buf.keystroke("d")
        buf.keystroke("e")
        buf.keystroke("v")
        frame = buf.snapshot(tick)  # TickInputFrame for current state
    """

    __slots__ = ("_chars", "_lock", "_last_snapshot_text", "_rhythm_fn")

    def __init__(self, rhythm_fn=None) -> None:
        self._chars: List[str] = []
        self._lock = Lock()
        self._last_snapshot_text: str = ""
        self._rhythm_fn = rhythm_fn or _default_rhythm

    def keystroke(self, char: str) -> None:
        """Append a single character."""
        with self._lock:
            self._chars.append(char)

    def backspace(self) -> None:
        """Remove last character."""
        with self._lock:
            if self._chars:
                self._chars.pop()

    def clear(self) -> None:
        """Clear the buffer."""
        with self._lock:
            self._chars.clear()
            self._last_snapshot_text = ""

    @property
    def text(self) -> str:
        with self._lock:
            return "".join(self._chars)

    def snapshot(self, tick: Optional[RuntimeTick] = None) -> TickInputFrame:
        """Produce a frame for the current buffer state."""
        with self._lock:
            current = "".join(self._chars)
            dirty = current != self._last_snapshot_text
            self._last_snapshot_text = current

        rhythm = self._rhythm_fn(current)
        return TickInputFrame(
            text=current,
            tick=tick,
            syllable_count=rhythm.syllable_count,
            stress_pattern=rhythm.stress_pattern,
            sequencer_steps=rhythm.sequencer_steps,
            dirty=dirty,
        )


class FrameHistory:
    """Bounded ring buffer of TickInputFrames for replay/debug."""

    __slots__ = ("_frames", "_lock")

    def __init__(self, max_frames: int = 256) -> None:
        self._frames: Deque[TickInputFrame] = deque(maxlen=max_frames)
        self._lock = Lock()

    def push(self, frame: TickInputFrame) -> None:
        with self._lock:
            self._frames.append(frame)

    def latest(self) -> Optional[TickInputFrame]:
        with self._lock:
            return self._frames[-1] if self._frames else None

    def all(self) -> Tuple[TickInputFrame, ...]:
        with self._lock:
            return tuple(self._frames)

    def dirty_frames(self) -> Tuple[TickInputFrame, ...]:
        """Return only frames where input changed."""
        with self._lock:
            return tuple(f for f in self._frames if f.dirty)

    def __len__(self) -> int:
        with self._lock:
            return len(self._frames)


def _default_rhythm(text: str):
    """Fallback rhythm computation using engine helpers."""
    from vibe_core.mahamantra.research.maha_language_engine import RhythmProfile, _WORD_TOKEN_RE, _stress_for_word
    from vibe_core.mahamantra.protocols._seed import KSETRAJNA, WORDS

    tokens = _WORD_TOKEN_RE.findall(text)
    stress: List[int] = []
    for token in tokens:
        stress.extend(_stress_for_word(token))

    if not stress:
        return RhythmProfile(syllable_count=0, stress_pattern=(), sequencer_steps=(), signature="-")

    step_count = WORDS * 2
    stress_pattern = tuple(stress)
    steps: List[int] = []
    cursor = 0
    for stress_level in stress_pattern:
        steps.append(cursor % step_count)
        cursor += KSETRAJNA + min(stress_level, 1)

    return RhythmProfile(
        syllable_count=len(stress_pattern),
        stress_pattern=stress_pattern,
        sequencer_steps=tuple(steps),
        signature="".join(str(s) for s in stress_pattern),
    )
