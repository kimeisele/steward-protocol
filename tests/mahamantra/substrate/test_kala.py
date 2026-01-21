"""
TESTS: kala.py - TimeKeeper Implementation
==========================================

"kāla-cakra" - The Wheel of Time.

REAL TESTS for:
1. TimeKeeper class
2. KalaTime TypedDict
3. Time constants (LILA_TICKS, MALA_TICKS)
"""

import pytest
from vibe_core.mahamantra.substrate.kala import (
    TimeKeeper,
    LILA_TICKS,
    MALA_MANTRAS,
    MALA_TICKS,
)


# =============================================================================
# Constants Tests
# =============================================================================


class TestKalaConstants:
    """Test Kala constants."""

    def test_lila_ticks_is_48(self):
        """LILA_TICKS is 48 (16 × 3)."""
        assert LILA_TICKS == 48

    def test_mala_mantras_is_108(self):
        """MALA_MANTRAS is 108."""
        assert MALA_MANTRAS == 108

    def test_mala_ticks_is_1728(self):
        """MALA_TICKS is 1728 (16 × 108)."""
        assert MALA_TICKS == 1728


# =============================================================================
# TimeKeeper Initialization Tests
# =============================================================================


class TestTimeKeeperInit:
    """Test TimeKeeper initialization."""

    def test_default_start_at_0(self):
        """Default TimeKeeper starts at tick 0."""
        tk = TimeKeeper()
        time = tk.get_time()
        assert time.total_ticks == 0

    def test_custom_start_ticks(self):
        """TimeKeeper can start at custom tick count."""
        tk = TimeKeeper(start_ticks=100)
        time = tk.get_time()
        assert time.total_ticks == 100


# =============================================================================
# TimeKeeper.get_time Tests
# =============================================================================


class TestTimeKeeperGetTime:
    """Test TimeKeeper.get_time method."""

    def test_get_time_tick_0(self):
        """get_time at tick 0."""
        tk = TimeKeeper()
        time = tk.get_time()
        assert time.total_ticks == 0
        assert time.tick_in_mantra == 0
        assert time.mantra_in_mala == 0
        assert time.lila_position == 0
        assert time.mala_count == 0

    def test_get_time_tick_15(self):
        """get_time at tick 15."""
        tk = TimeKeeper(start_ticks=15)
        time = tk.get_time()
        assert time.tick_in_mantra == 15
        assert time.mantra_in_mala == 0  # Still in first mantra
        assert time.lila_position == 15

    def test_get_time_tick_16(self):
        """get_time at tick 16 (start of second mantra)."""
        tk = TimeKeeper(start_ticks=16)
        time = tk.get_time()
        assert time.tick_in_mantra == 0
        assert time.mantra_in_mala == 1
        assert time.lila_position == 16

    def test_get_time_tick_48(self):
        """get_time at tick 48 (start of second lila cycle)."""
        tk = TimeKeeper(start_ticks=48)
        time = tk.get_time()
        assert time.tick_in_mantra == 0
        assert time.mantra_in_mala == 3  # 48 // 16 = 3
        assert time.lila_position == 0  # 48 % 48 = 0

    def test_get_time_tick_1728(self):
        """get_time at tick 1728 (start of second mala)."""
        tk = TimeKeeper(start_ticks=1728)
        time = tk.get_time()
        assert time.tick_in_mantra == 0
        assert time.mantra_in_mala == 0  # 108 % 108 = 0
        assert time.mala_count == 1

    def test_get_time_tick_1729(self):
        """get_time at tick 1729."""
        tk = TimeKeeper(start_ticks=1729)
        time = tk.get_time()
        assert time.tick_in_mantra == 1
        assert time.mala_count == 1


# =============================================================================
# TimeKeeper.advance Tests
# =============================================================================


class TestTimeKeeperAdvance:
    """Test TimeKeeper.advance method."""

    def test_advance_increments_tick(self):
        """advance increments total ticks by 1."""
        tk = TimeKeeper()
        time = tk.advance()
        assert time.total_ticks == 1

    def test_advance_returns_time(self):
        """advance returns KalaTime dataclass."""
        tk = TimeKeeper()
        time = tk.advance()
        assert hasattr(time, "total_ticks")
        assert hasattr(time, "tick_in_mantra")
        assert hasattr(time, "mantra_in_mala")
        assert hasattr(time, "lila_position")
        assert hasattr(time, "mala_count")

    def test_multiple_advances(self):
        """Multiple advances increment correctly."""
        tk = TimeKeeper()
        for i in range(16):
            time = tk.advance()
        assert time.total_ticks == 16
        assert time.tick_in_mantra == 0
        assert time.mantra_in_mala == 1

    def test_advance_through_mala(self):
        """Advance through complete mala."""
        tk = TimeKeeper()
        for _ in range(1728):
            time = tk.advance()
        assert time.total_ticks == 1728
        assert time.mala_count == 1


# =============================================================================
# TimeKeeper.set_ticks Tests
# =============================================================================


class TestTimeKeeperSetTicks:
    """Test TimeKeeper.set_ticks method."""

    def test_set_ticks_updates_time(self):
        """set_ticks updates internal time."""
        tk = TimeKeeper()
        tk.set_ticks(100)
        time = tk.get_time()
        assert time.total_ticks == 100

    def test_set_ticks_can_go_backward(self):
        """set_ticks can set time backward."""
        tk = TimeKeeper(start_ticks=1000)
        tk.set_ticks(50)
        time = tk.get_time()
        assert time.total_ticks == 50

    def test_set_ticks_from_persistence(self):
        """set_ticks can restore from persistence."""
        tk = TimeKeeper()
        # Simulate loading from persistence
        persisted_ticks = 3456  # 2 malas
        tk.set_ticks(persisted_ticks)
        time = tk.get_time()
        assert time.total_ticks == 3456
        assert time.mala_count == 2


# =============================================================================
# TimeKeeper Integration Tests
# =============================================================================


class TestTimeKeeperIntegration:
    """Integration tests for TimeKeeper."""

    def test_tick_in_mantra_cycles(self):
        """tick_in_mantra cycles 0-15."""
        tk = TimeKeeper()
        for expected in range(16):
            time = tk.get_time()
            assert time.tick_in_mantra == expected
            tk.advance()
        # Should wrap back to 0
        time = tk.get_time()
        assert time.tick_in_mantra == 0

    def test_lila_position_cycles(self):
        """lila_position cycles 0-47."""
        tk = TimeKeeper()
        for expected in range(48):
            time = tk.get_time()
            assert time.lila_position == expected
            tk.advance()
        # Should wrap back to 0
        time = tk.get_time()
        assert time.lila_position == 0

    def test_mantra_in_mala_cycles(self):
        """mantra_in_mala cycles 0-107."""
        tk = TimeKeeper()
        for _ in range(108 * 16):
            tk.advance()
        time = tk.get_time()
        assert time.mantra_in_mala == 0
        assert time.mala_count == 1

    def test_time_calculations_consistent(self):
        """All time calculations are consistent."""
        tk = TimeKeeper(start_ticks=1729)  # 1 mala + 1 tick
        time = tk.get_time()

        # Verify consistency
        assert time.total_ticks == 1729
        assert time.tick_in_mantra == 1729 % 16  # 1
        assert time.mantra_in_mala == (1729 // 16) % 108  # 0
        assert time.lila_position == 1729 % 48  # 1
        assert time.mala_count == 1729 // 1728  # 1


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_timekeeper_exists(self):
        """TimeKeeper is importable."""
        assert TimeKeeper is not None

    def test_constants_exist(self):
        """Constants are importable."""
        assert LILA_TICKS is not None
        assert MALA_MANTRAS is not None
        assert MALA_TICKS is not None
