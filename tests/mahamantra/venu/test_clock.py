"""
TESTS: venu/clock.py - MantraClock Master Scheduler
====================================================

REAL TESTS for:
1. MantraClock class
2. tick property
3. voices property
4. position property
5. add_voice method
6. on_position method
7. on_mala method
8. tick_once method
"""

import pytest
from vibe_core.mahamantra.venu.clock import MantraClock
from vibe_core.mahamantra.venu.tick import MantraTick
from vibe_core.mahamantra.venu.voice import MantraVoice
from vibe_core.mahamantra.protocols._venu import (
    VENU_POSITIONS,
    VENU_TICKS_PER_MALA,
)


# =============================================================================
# MantraClock Tests
# =============================================================================


class TestMantraClock:
    """Test MantraClock class."""

    def test_mantra_clock_creation(self):
        """MantraClock can be created."""
        clock = MantraClock()
        assert clock is not None

    def test_mantra_clock_has_tick(self):
        """MantraClock has tick property."""
        clock = MantraClock()
        assert clock.tick is not None

    def test_mantra_clock_tick_is_mantra_tick(self):
        """Clock's tick is a MantraTick instance."""
        clock = MantraClock()
        assert isinstance(clock.tick, MantraTick)

    def test_mantra_clock_initial_position(self):
        """MantraClock starts at position 0."""
        clock = MantraClock()
        assert clock.position == 0

    def test_mantra_clock_initial_voices_empty(self):
        """MantraClock starts with no voices."""
        clock = MantraClock()
        assert clock.voices == []

    def test_mantra_clock_add_voice(self):
        """add_voice creates and registers a voice."""
        clock = MantraClock()
        voice = clock.add_voice()
        assert voice is not None
        assert isinstance(voice, MantraVoice)

    def test_mantra_clock_add_voice_registered(self):
        """add_voice registers voice in clock."""
        clock = MantraClock()
        voice = clock.add_voice()
        assert voice in clock.voices

    def test_mantra_clock_add_multiple_voices(self):
        """add_voice can add multiple voices."""
        clock = MantraClock()
        v1 = clock.add_voice()
        v2 = clock.add_voice()
        v3 = clock.add_voice()

        assert len(clock.voices) == 3
        assert v1 in clock.voices
        assert v2 in clock.voices
        assert v3 in clock.voices

    def test_mantra_clock_voices_unique_ids(self):
        """Added voices have unique IDs."""
        clock = MantraClock()
        v1 = clock.add_voice()
        v2 = clock.add_voice()
        v3 = clock.add_voice()

        ids = [v1.voice_id, v2.voice_id, v3.voice_id]
        assert len(ids) == len(set(ids))  # All unique

    def test_mantra_clock_voices_returns_copy(self):
        """voices property returns a copy."""
        clock = MantraClock()
        clock.add_voice()
        voices1 = clock.voices
        voices2 = clock.voices
        assert voices1 == voices2
        assert voices1 is not voices2

    def test_mantra_clock_tick_once(self):
        """tick_once advances the clock."""
        clock = MantraClock()
        assert clock.position == 0
        new_pos = clock.tick_once()
        assert new_pos == 1
        assert clock.position == 1

    def test_mantra_clock_tick_once_returns_new_position(self):
        """tick_once returns new position."""
        clock = MantraClock()
        for expected in range(1, VENU_POSITIONS + 1):
            new_pos = clock.tick_once()
            assert new_pos == expected % VENU_POSITIONS

    def test_mantra_clock_tick_once_executes_tasks(self):
        """tick_once executes tasks at current position."""
        clock = MantraClock()
        voice = clock.add_voice()
        results = []

        voice.submit(lambda: results.append(1), position=0)
        clock.tick_once()

        assert results == [1]

    def test_mantra_clock_tick_once_clears_tasks(self):
        """tick_once clears tasks after execution."""
        clock = MantraClock()
        voice = clock.add_voice()
        results = []

        voice.submit(lambda: results.append(1), position=0)
        clock.tick_once()

        # Tick again - should not re-execute
        clock.tick_once()
        assert results == [1]  # Still just 1

    def test_mantra_clock_tick_once_executes_multiple_voices(self):
        """tick_once executes tasks from all voices."""
        clock = MantraClock()
        voice1 = clock.add_voice()
        voice2 = clock.add_voice()
        results = []

        voice1.submit(lambda: results.append("v1"), position=0)
        voice2.submit(lambda: results.append("v2"), position=0)
        clock.tick_once()

        assert "v1" in results
        assert "v2" in results

    def test_mantra_clock_repr(self):
        """MantraClock has string representation."""
        clock = MantraClock()
        rep = repr(clock)
        assert "MantraClock" in rep
        assert "pos=" in rep
        assert "voices=" in rep

    def test_mantra_clock_repr_shows_voice_count(self):
        """repr shows voice count."""
        clock = MantraClock()
        clock.add_voice()
        clock.add_voice()
        rep = repr(clock)
        assert "voices=2" in rep


# =============================================================================
# on_position Tests
# =============================================================================


class TestMantraClockOnPosition:
    """Test on_position callbacks."""

    def test_on_position_registers_callback(self):
        """on_position registers a callback."""
        clock = MantraClock()
        called = []
        clock.on_position(5, lambda: called.append(True))
        # No exception = success

    def test_on_position_callback_fires(self):
        """on_position callback fires at correct position."""
        clock = MantraClock()
        called = []
        clock.on_position(3, lambda: called.append(True))

        # Tick to reach position 3 and execute it
        # tick_once executes current position, then advances
        # pos 0 -> execute pos 0 -> advance to 1
        # pos 1 -> execute pos 1 -> advance to 2
        # pos 2 -> execute pos 2 -> advance to 3
        # pos 3 -> execute pos 3 -> advance to 4
        for _ in range(4):
            clock.tick_once()

        # Position 3 callback should have fired
        assert len(called) == 1

    def test_on_position_callback_fires_only_once(self):
        """on_position callback fires only at that position."""
        clock = MantraClock()
        called = []
        clock.on_position(0, lambda: called.append(True))

        # First tick (pos 0 -> 1)
        clock.tick_once()
        assert len(called) == 1

        # More ticks (not at pos 0)
        for _ in range(VENU_POSITIONS - 1):
            clock.tick_once()

        # Back at position 0, tick again
        clock.tick_once()
        assert len(called) == 2

    def test_on_position_multiple_callbacks(self):
        """on_position can register multiple callbacks."""
        clock = MantraClock()
        called = []
        clock.on_position(0, lambda: called.append(1))
        clock.on_position(0, lambda: called.append(2))

        clock.tick_once()

        assert 1 in called
        assert 2 in called

    def test_on_position_invalid_position(self):
        """on_position raises for invalid position."""
        clock = MantraClock()
        with pytest.raises(ValueError):
            clock.on_position(-1, lambda: None)
        with pytest.raises(ValueError):
            clock.on_position(VENU_POSITIONS, lambda: None)


# =============================================================================
# on_mala Tests
# =============================================================================


class TestMantraClockOnMala:
    """Test on_mala callbacks."""

    def test_on_mala_registers_callback(self):
        """on_mala registers a callback."""
        clock = MantraClock()
        called = []
        clock.on_mala(lambda mala: called.append(mala))
        # No exception = success

    def test_on_mala_callback_fires(self):
        """on_mala callback fires after VENU_TICKS_PER_MALA ticks."""
        clock = MantraClock()
        mala_counts = []
        clock.on_mala(lambda mala: mala_counts.append(mala))

        # Tick VENU_TICKS_PER_MALA times
        for _ in range(VENU_TICKS_PER_MALA):
            clock.tick_once()

        assert len(mala_counts) == 1
        assert mala_counts[0] == 1

    def test_on_mala_callback_fires_multiple(self):
        """on_mala callback fires multiple times."""
        clock = MantraClock()
        mala_counts = []
        clock.on_mala(lambda mala: mala_counts.append(mala))

        # Tick 2 * VENU_TICKS_PER_MALA times
        for _ in range(2 * VENU_TICKS_PER_MALA):
            clock.tick_once()

        assert len(mala_counts) == 2
        assert mala_counts[0] == 1
        assert mala_counts[1] == 2


# =============================================================================
# Integration Tests
# =============================================================================


class TestMantraClockIntegration:
    """Integration tests for MantraClock."""

    def test_full_cycle(self):
        """Clock can complete a full 16-position cycle."""
        clock = MantraClock()
        voice = clock.add_voice()
        executed = []

        # Submit task at each position
        for pos in range(VENU_POSITIONS):
            voice.submit(lambda p=pos: executed.append(p), position=pos)

        # Run full cycle
        for _ in range(VENU_POSITIONS):
            clock.tick_once()

        # All positions should have been executed
        assert len(executed) == VENU_POSITIONS
        assert set(executed) == set(range(VENU_POSITIONS))

    def test_position_callback_with_task(self):
        """Position callback and voice task both execute."""
        clock = MantraClock()
        voice = clock.add_voice()
        executed = []

        clock.on_position(0, lambda: executed.append("callback"))
        voice.submit(lambda: executed.append("task"), position=0)

        clock.tick_once()

        assert "callback" in executed
        assert "task" in executed

    def test_multiple_voices_all_positions(self):
        """Multiple voices work at all positions."""
        clock = MantraClock()
        voice1 = clock.add_voice()
        voice2 = clock.add_voice()
        results = {0: [], 5: [], 15: []}

        voice1.submit(lambda: results[0].append("v1"), position=0)
        voice2.submit(lambda: results[0].append("v2"), position=0)
        voice1.submit(lambda: results[5].append("v1"), position=5)
        voice2.submit(lambda: results[5].append("v2"), position=5)
        voice1.submit(lambda: results[15].append("v1"), position=15)
        voice2.submit(lambda: results[15].append("v2"), position=15)

        # Run full cycle
        for _ in range(VENU_POSITIONS):
            clock.tick_once()

        assert results[0] == ["v1", "v2"]
        assert results[5] == ["v1", "v2"]
        assert results[15] == ["v1", "v2"]


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra import venu

        expected = [
            "MantraTick",
            "MantraVoice",
            "MantraClock",
        ]
        for item in expected:
            assert item in venu.__all__, f"{item} should be in __all__"
