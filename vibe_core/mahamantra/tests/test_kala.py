"""
KALA — TimeKeeper Tests
========================

Tests the Wheel of Time:
- 16 Ticks = 1 Mantra
- 48 Ticks = 1 Lila
- 1728 Ticks = 1 Mala
"""

import pytest

from vibe_core.mahamantra.substrate.time.kala import (
    TimeKeeper,
    LILA_TICKS,
    MALA_MANTRAS,
    MALA_TICKS,
)
from vibe_core.mahamantra.protocols._seed import WORDS, TRINITY, MALA


class TestKalaConstants:
    """Kala constants derive from seed."""

    def test_lila_ticks(self):
        assert LILA_TICKS == WORDS * TRINITY == 48

    def test_mala_mantras(self):
        assert MALA_MANTRAS == MALA == 108

    def test_mala_ticks(self):
        assert MALA_TICKS == WORDS * MALA == 1728


class TestTimeKeeper:
    """TimeKeeper tracks cosmic time."""

    def test_initial_state(self):
        tk = TimeKeeper()
        time = tk.get_time()
        assert time.total_ticks == 0
        assert time.tick_in_mantra == 0
        assert time.mantra_in_mala == 0
        assert time.lila_position == 0
        assert time.mala_count == 0

    def test_initial_state_with_offset(self):
        tk = TimeKeeper(start_ticks=100)
        time = tk.get_time()
        assert time.total_ticks == 100

    def test_advance_single_tick(self):
        tk = TimeKeeper()
        time = tk.advance()
        assert time.total_ticks == 1
        assert time.tick_in_mantra == 1

    def test_advance_full_mantra(self):
        """16 ticks = 1 mantra cycle."""
        tk = TimeKeeper()
        for _ in range(WORDS):
            time = tk.advance()

        assert time.total_ticks == WORDS  # 16
        assert time.tick_in_mantra == 0  # wrapped
        assert time.mantra_in_mala == 1  # 1 mantra done

    def test_advance_full_lila(self):
        """48 ticks = 1 lila cycle."""
        tk = TimeKeeper()
        for _ in range(LILA_TICKS):
            time = tk.advance()

        assert time.total_ticks == LILA_TICKS  # 48
        assert time.lila_position == 0  # wrapped
        assert time.mantra_in_mala == 3  # 3 mantras in 48 ticks

    def test_advance_full_mala(self):
        """1728 ticks = 1 mala cycle."""
        tk = TimeKeeper()
        for _ in range(MALA_TICKS):
            time = tk.advance()

        assert time.total_ticks == MALA_TICKS  # 1728
        assert time.tick_in_mantra == 0
        assert time.mantra_in_mala == 0  # wrapped
        assert time.mala_count == 1

    def test_multiple_malas(self):
        tk = TimeKeeper()
        for _ in range(MALA_TICKS * 3):
            time = tk.advance()

        assert time.mala_count == 3

    def test_set_ticks(self):
        tk = TimeKeeper()
        tk.set_ticks(MALA_TICKS * 5 + 42)
        time = tk.get_time()
        assert time.total_ticks == MALA_TICKS * 5 + 42
        assert time.mala_count == 5

    def test_time_consistency(self):
        """All time components must be consistent with total ticks."""
        tk = TimeKeeper()
        for i in range(200):
            time = tk.advance()

            # Reconstruct total from components
            t = time.total_ticks
            assert time.tick_in_mantra == t % WORDS
            assert time.mantra_in_mala == (t // WORDS) % MALA_MANTRAS
            assert time.lila_position == t % LILA_TICKS
            assert time.mala_count == t // MALA_TICKS

    def test_tick_in_mantra_range(self):
        """tick_in_mantra must always be 0-15."""
        tk = TimeKeeper()
        for _ in range(100):
            time = tk.advance()
            assert 0 <= time.tick_in_mantra < WORDS

    def test_mantra_in_mala_range(self):
        """mantra_in_mala must always be 0-107."""
        tk = TimeKeeper()
        for _ in range(MALA_TICKS + 100):
            time = tk.advance()
            assert 0 <= time.mantra_in_mala < MALA_MANTRAS

    def test_lila_position_range(self):
        """lila_position must always be 0-47."""
        tk = TimeKeeper()
        for _ in range(100):
            time = tk.advance()
            assert 0 <= time.lila_position < LILA_TICKS

