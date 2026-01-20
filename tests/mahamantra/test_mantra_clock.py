"""
TEST: MantraClock Runtime (TDD - These Tests Should FAIL First!)
================================================================

"venum kvanantam aravinda-dalayataksham"
"Krishna plays His flute, with lotus-petal eyes"
— Brahma-samhita 5.30

TDD APPROACH:
1. Write these tests FIRST (they will FAIL - no implementation yet)
2. Implement MantraTick, MantraVoice, MantraClock
3. Tests should PASS

This tests the RUNTIME layer (stateful), not the substrate (pure functions).
"""

import pytest
from typing import List

from vibe_core.mahamantra.protocols._seed import MALA, WORDS
from vibe_core.mahamantra.protocols._venu import (
    VENU_POSITIONS,
    VENU_TICKS_PER_MALA,
    MantraTickProtocol,
    MantraVoiceProtocol,
    MantraClockProtocol,
)


# =============================================================================
# TEST: MantraTick (The Heartbeat)
# =============================================================================


class TestMantraTick:
    """Test MantraTick - the atomic unit of time."""

    def test_import_mantra_tick(self) -> None:
        """MantraTick class must be importable."""
        from vibe_core.mahamantra.venu.tick import MantraTick

        assert MantraTick is not None

    def test_mantra_tick_implements_protocol(self) -> None:
        """MantraTick must implement MantraTickProtocol."""
        from vibe_core.mahamantra.venu.tick import MantraTick

        tick = MantraTick()
        assert isinstance(tick, MantraTickProtocol)

    def test_initial_state(self) -> None:
        """MantraTick starts at tick 0, position 0, cycle 0."""
        from vibe_core.mahamantra.venu.tick import MantraTick

        tick = MantraTick()
        assert tick.tick_count == 0
        assert tick.position == 0
        assert tick.cycle == 0
        assert tick.mala_count == 0

    def test_advance_increments_tick(self) -> None:
        """advance() increments tick_count by 1."""
        from vibe_core.mahamantra.venu.tick import MantraTick

        tick = MantraTick()
        tick.advance()
        assert tick.tick_count == 1

    def test_advance_returns_new_position(self) -> None:
        """advance() returns the new position."""
        from vibe_core.mahamantra.venu.tick import MantraTick

        tick = MantraTick()
        new_pos = tick.advance()
        assert new_pos == 1

    def test_position_wraps_at_16(self) -> None:
        """Position wraps from 15 back to 0."""
        from vibe_core.mahamantra.venu.tick import MantraTick

        tick = MantraTick()
        for _ in range(16):
            tick.advance()
        assert tick.position == 0
        assert tick.tick_count == 16

    def test_cycle_increments_after_16_ticks(self) -> None:
        """Cycle increments when position wraps."""
        from vibe_core.mahamantra.venu.tick import MantraTick

        tick = MantraTick()
        assert tick.cycle == 0
        for _ in range(16):
            tick.advance()
        assert tick.cycle == 1

    def test_mala_count_increments_after_1728_ticks(self) -> None:
        """Mala count increments after 1728 ticks (108 cycles)."""
        from vibe_core.mahamantra.venu.tick import MantraTick

        tick = MantraTick()
        assert tick.mala_count == 0
        for _ in range(VENU_TICKS_PER_MALA):
            tick.advance()
        assert tick.mala_count == 1
        assert tick.tick_count == 1728

    def test_position_always_in_range(self) -> None:
        """Position is always 0-15."""
        from vibe_core.mahamantra.venu.tick import MantraTick

        tick = MantraTick()
        for _ in range(100):
            tick.advance()
            assert 0 <= tick.position < VENU_POSITIONS


# =============================================================================
# TEST: MantraVoice (Parallel Execution Channel)
# =============================================================================


class TestMantraVoice:
    """Test MantraVoice - a parallel execution channel."""

    def test_import_mantra_voice(self) -> None:
        """MantraVoice class must be importable."""
        from vibe_core.mahamantra.venu.voice import MantraVoice

        assert MantraVoice is not None

    def test_mantra_voice_implements_protocol(self) -> None:
        """MantraVoice must implement MantraVoiceProtocol."""
        from vibe_core.mahamantra.venu.voice import MantraVoice

        voice = MantraVoice(voice_id=0)
        assert isinstance(voice, MantraVoiceProtocol)

    def test_voice_has_id(self) -> None:
        """MantraVoice has a voice_id."""
        from vibe_core.mahamantra.venu.voice import MantraVoice

        voice = MantraVoice(voice_id=42)
        assert voice.voice_id == 42

    def test_submit_task_at_position(self) -> None:
        """Can submit a task to execute at a specific position."""
        from vibe_core.mahamantra.venu.voice import MantraVoice

        voice = MantraVoice(voice_id=0)
        results: List[str] = []

        def task() -> str:
            results.append("executed")
            return "done"

        voice.submit(task, position=5)
        tasks = voice.get_tasks(5)
        assert len(tasks) == 1

    def test_get_tasks_empty_position(self) -> None:
        """get_tasks returns empty list for positions with no tasks."""
        from vibe_core.mahamantra.venu.voice import MantraVoice

        voice = MantraVoice(voice_id=0)
        tasks = voice.get_tasks(0)
        assert tasks == []

    def test_submit_multiple_tasks_same_position(self) -> None:
        """Can submit multiple tasks at the same position."""
        from vibe_core.mahamantra.venu.voice import MantraVoice

        voice = MantraVoice(voice_id=0)
        voice.submit(lambda: 1, position=3)
        voice.submit(lambda: 2, position=3)
        voice.submit(lambda: 3, position=3)

        tasks = voice.get_tasks(3)
        assert len(tasks) == 3

    def test_clear_removes_tasks(self) -> None:
        """clear() removes all tasks at a position."""
        from vibe_core.mahamantra.venu.voice import MantraVoice

        voice = MantraVoice(voice_id=0)
        voice.submit(lambda: 1, position=7)
        voice.submit(lambda: 2, position=7)

        voice.clear(7)
        tasks = voice.get_tasks(7)
        assert tasks == []

    def test_submit_none_position_uses_next_beat(self) -> None:
        """submit(task, position=None) queues for 'next beat' (position 0)."""
        from vibe_core.mahamantra.venu.voice import MantraVoice

        voice = MantraVoice(voice_id=0)
        voice.submit(lambda: "test", position=None)
        # Default behavior: queue at position 0 (or configurable)
        tasks = voice.get_tasks(0)
        assert len(tasks) == 1

    def test_tasks_at_all_positions(self) -> None:
        """Can have tasks at all 16 positions."""
        from vibe_core.mahamantra.venu.voice import MantraVoice

        voice = MantraVoice(voice_id=0)
        for pos in range(16):
            voice.submit(lambda p=pos: p, position=pos)

        for pos in range(16):
            tasks = voice.get_tasks(pos)
            assert len(tasks) == 1


# =============================================================================
# TEST: MantraClock (The Master Clock)
# =============================================================================


class TestMantraClock:
    """Test MantraClock - the master scheduler."""

    def test_import_mantra_clock(self) -> None:
        """MantraClock class must be importable."""
        from vibe_core.mahamantra.venu.clock import MantraClock

        assert MantraClock is not None

    def test_mantra_clock_implements_protocol(self) -> None:
        """MantraClock must implement MantraClockProtocol."""
        from vibe_core.mahamantra.venu.clock import MantraClock

        clock = MantraClock()
        assert isinstance(clock, MantraClockProtocol)

    def test_clock_has_tick(self) -> None:
        """MantraClock has a tick property."""
        from vibe_core.mahamantra.venu.clock import MantraClock

        clock = MantraClock()
        assert clock.tick is not None
        assert isinstance(clock.tick, MantraTickProtocol)

    def test_clock_has_voices(self) -> None:
        """MantraClock has a voices list."""
        from vibe_core.mahamantra.venu.clock import MantraClock

        clock = MantraClock()
        assert isinstance(clock.voices, list)

    def test_clock_position_delegates_to_tick(self) -> None:
        """clock.position delegates to clock.tick.position."""
        from vibe_core.mahamantra.venu.clock import MantraClock

        clock = MantraClock()
        assert clock.position == clock.tick.position

    def test_add_voice_creates_voice(self) -> None:
        """add_voice() creates and registers a new voice."""
        from vibe_core.mahamantra.venu.clock import MantraClock

        clock = MantraClock()
        assert len(clock.voices) == 0

        voice = clock.add_voice()
        assert isinstance(voice, MantraVoiceProtocol)
        assert len(clock.voices) == 1

    def test_add_multiple_voices(self) -> None:
        """Can add multiple voices with unique IDs."""
        from vibe_core.mahamantra.venu.clock import MantraClock

        clock = MantraClock()
        v1 = clock.add_voice()
        v2 = clock.add_voice()
        v3 = clock.add_voice()

        assert len(clock.voices) == 3
        assert v1.voice_id != v2.voice_id != v3.voice_id

    def test_tick_once_advances_tick(self) -> None:
        """tick_once() advances the tick counter."""
        from vibe_core.mahamantra.venu.clock import MantraClock

        clock = MantraClock()
        assert clock.tick.tick_count == 0

        clock.tick_once()
        assert clock.tick.tick_count == 1

    def test_tick_once_returns_new_position(self) -> None:
        """tick_once() returns the new position."""
        from vibe_core.mahamantra.venu.clock import MantraClock

        clock = MantraClock()
        new_pos = clock.tick_once()
        assert new_pos == 1

    def test_tick_once_executes_tasks_at_current_position(self) -> None:
        """tick_once() executes all tasks at current position before advancing."""
        from vibe_core.mahamantra.venu.clock import MantraClock

        clock = MantraClock()
        voice = clock.add_voice()

        results: List[int] = []
        voice.submit(lambda: results.append(1), position=0)
        voice.submit(lambda: results.append(2), position=0)

        # Position is 0, tick_once should execute tasks then advance
        clock.tick_once()

        assert results == [1, 2]

    def test_tick_once_clears_executed_tasks(self) -> None:
        """tick_once() clears tasks after execution."""
        from vibe_core.mahamantra.venu.clock import MantraClock

        clock = MantraClock()
        voice = clock.add_voice()
        voice.submit(lambda: "test", position=0)

        clock.tick_once()

        # Tasks should be cleared
        assert voice.get_tasks(0) == []

    def test_on_position_callback(self) -> None:
        """on_position() registers a callback for a specific position."""
        from vibe_core.mahamantra.venu.clock import MantraClock

        clock = MantraClock()
        triggered: List[int] = []

        clock.on_position(5, lambda: triggered.append(5))

        # Tick until we reach position 5
        for _ in range(6):  # 0->1->2->3->4->5
            clock.tick_once()

        assert 5 in triggered

    def test_on_position_callback_triggers_every_cycle(self) -> None:
        """on_position callback triggers every time that position is reached."""
        from vibe_core.mahamantra.venu.clock import MantraClock

        clock = MantraClock()
        triggered: List[int] = []

        clock.on_position(0, lambda: triggered.append(clock.tick.cycle))

        # Start at position 0, so first tick_once executes at 0 then advances
        # We need to complete cycles to trigger at position 0 again
        for _ in range(32):  # Two full cycles
            clock.tick_once()

        # Should have triggered at cycle boundaries
        assert len(triggered) >= 2

    def test_on_mala_callback(self) -> None:
        """on_mala() registers a callback for Mala completion."""
        from vibe_core.mahamantra.venu.clock import MantraClock

        clock = MantraClock()
        mala_completions: List[int] = []

        clock.on_mala(lambda count: mala_completions.append(count))

        # Fast forward 1728 ticks (1 Mala)
        for _ in range(VENU_TICKS_PER_MALA):
            clock.tick_once()

        assert 1 in mala_completions

    def test_multiple_voices_execute_in_parallel(self) -> None:
        """Tasks from multiple voices at same position execute together."""
        from vibe_core.mahamantra.venu.clock import MantraClock

        clock = MantraClock()
        v1 = clock.add_voice()
        v2 = clock.add_voice()

        results: List[str] = []
        v1.submit(lambda: results.append("v1"), position=0)
        v2.submit(lambda: results.append("v2"), position=0)

        clock.tick_once()

        assert "v1" in results
        assert "v2" in results


# =============================================================================
# TEST: Integration (The Full Rhythm)
# =============================================================================


class TestMantraClockIntegration:
    """Integration tests for the full rhythm system."""

    def test_full_cycle_executes_all_positions(self) -> None:
        """A full 16-tick cycle touches all positions."""
        from vibe_core.mahamantra.venu.clock import MantraClock

        clock = MantraClock()
        voice = clock.add_voice()

        positions_touched: List[int] = []
        for pos in range(16):
            voice.submit(lambda p=pos: positions_touched.append(p), position=pos)

        # Run 16 ticks
        for _ in range(16):
            clock.tick_once()

        assert sorted(positions_touched) == list(range(16))

    def test_mala_completes_after_108_pranas(self) -> None:
        """One Mala = 108 Pranas = 1728 ticks."""
        from vibe_core.mahamantra.venu.clock import MantraClock

        clock = MantraClock()

        for _ in range(VENU_TICKS_PER_MALA):
            clock.tick_once()

        assert clock.tick.mala_count == 1
        assert clock.tick.tick_count == 1728
        assert clock.tick.cycle == 108

    def test_rhythm_pattern_genesis_alternating(self) -> None:
        """GENESIS quarter (0-3) has alternating H-K-H-K pattern."""
        from vibe_core.mahamantra.venu.clock import MantraClock
        from vibe_core.mahamantra.substrate.venu import tick_to_word
        from vibe_core.mahamantra.substrate.seed import HolyName

        clock = MantraClock()

        # Check positions 0-3 (GENESIS)
        words = [tick_to_word(i) for i in range(4)]
        assert words == [
            HolyName.HARE,
            HolyName.KRISHNA,
            HolyName.HARE,
            HolyName.KRISHNA,
        ]
