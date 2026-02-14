"""Tests for incremental keystroke processing."""

from __future__ import annotations

from vibe_core.mahamantra.research.language_runtime.contracts import RuntimeTick
from vibe_core.mahamantra.research.language_runtime.incremental import (
    FrameHistory,
    IncrementalBuffer,
    TickInputFrame,
)


def _tick(n: int = 0) -> RuntimeTick:
    return RuntimeTick(tick=n, position=n % 16, phase=n // 4, mode=0, diw=99, venu=1, vamsi=2, murali=0)


class TestIncrementalBuffer:
    def test_keystroke_builds_text(self):
        buf = IncrementalBuffer()
        for ch in "dev":
            buf.keystroke(ch)
        assert buf.text == "dev"

    def test_backspace_removes_last(self):
        buf = IncrementalBuffer()
        for ch in "abc":
            buf.keystroke(ch)
        buf.backspace()
        assert buf.text == "ab"

    def test_clear_empties(self):
        buf = IncrementalBuffer()
        buf.keystroke("x")
        buf.clear()
        assert buf.text == ""

    def test_snapshot_marks_dirty_on_change(self):
        buf = IncrementalBuffer()
        buf.keystroke("a")
        f1 = buf.snapshot(_tick(0))
        assert f1.dirty is True
        assert f1.text == "a"

        f2 = buf.snapshot(_tick(1))
        assert f2.dirty is False

        buf.keystroke("b")
        f3 = buf.snapshot(_tick(2))
        assert f3.dirty is True
        assert f3.text == "ab"

    def test_snapshot_has_rhythm_for_real_word(self):
        buf = IncrementalBuffer()
        for ch in "devotion":
            buf.keystroke(ch)
        frame = buf.snapshot(_tick(5))
        assert frame.syllable_count > 0
        assert len(frame.stress_pattern) == frame.syllable_count
        assert len(frame.sequencer_steps) == frame.syllable_count

    def test_snapshot_empty_buffer_has_zero_rhythm(self):
        buf = IncrementalBuffer()
        frame = buf.snapshot()
        assert frame.syllable_count == 0
        assert frame.stress_pattern == ()
        assert frame.sequencer_steps == ()
        assert frame.dirty is False

    def test_tick_is_attached_to_frame(self):
        buf = IncrementalBuffer()
        buf.keystroke("x")
        t = _tick(42)
        frame = buf.snapshot(t)
        assert frame.tick is not None
        assert frame.tick.tick == 42


class TestFrameHistory:
    def test_push_and_latest(self):
        hist = FrameHistory(max_frames=4)
        buf = IncrementalBuffer()
        buf.keystroke("a")
        f = buf.snapshot(_tick(0))
        hist.push(f)
        assert hist.latest() == f
        assert len(hist) == 1

    def test_bounded_capacity(self):
        hist = FrameHistory(max_frames=3)
        buf = IncrementalBuffer()
        for i in range(5):
            buf.keystroke(str(i))
            hist.push(buf.snapshot(_tick(i)))
        assert len(hist) == 3

    def test_dirty_frames_filters(self):
        hist = FrameHistory()
        buf = IncrementalBuffer()
        buf.keystroke("a")
        hist.push(buf.snapshot(_tick(0)))  # dirty
        hist.push(buf.snapshot(_tick(1)))  # not dirty
        buf.keystroke("b")
        hist.push(buf.snapshot(_tick(2)))  # dirty

        dirty = hist.dirty_frames()
        assert len(dirty) == 2
        assert all(f.dirty for f in dirty)

    def test_all_returns_ordered(self):
        hist = FrameHistory()
        buf = IncrementalBuffer()
        for i in range(3):
            buf.keystroke(chr(ord("a") + i))
            hist.push(buf.snapshot(_tick(i)))
        frames = hist.all()
        assert len(frames) == 3
        assert frames[0].text == "a"
        assert frames[2].text == "abc"
