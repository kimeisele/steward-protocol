"""
TESTS: venu/tick.py - MantraTick Heartbeat
==========================================

REAL TESTS for:
1. MantraTick class
2. tick_count property
3. position property
4. cycle property
5. mala_count property
6. advance method
"""

import pytest
from vibe_core.mahamantra.venu.tick import MantraTick
from vibe_core.mahamantra.protocols._venu import (
    VENU_POSITIONS,
    VENU_TICKS_PER_MALA,
)


# =============================================================================
# MantraTick Tests
# =============================================================================


class TestMantraTick:
    """Test MantraTick class."""

    def test_mantra_tick_creation(self):
        """MantraTick can be created."""
        tick = MantraTick()
        assert tick is not None

    def test_mantra_tick_initial_tick_count(self):
        """MantraTick starts at tick_count 0."""
        tick = MantraTick()
        assert tick.tick_count == 0

    def test_mantra_tick_initial_position(self):
        """MantraTick starts at position 0."""
        tick = MantraTick()
        assert tick.position == 0

    def test_mantra_tick_initial_cycle(self):
        """MantraTick starts at cycle 0."""
        tick = MantraTick()
        assert tick.cycle == 0

    def test_mantra_tick_initial_mala_count(self):
        """MantraTick starts at mala_count 0."""
        tick = MantraTick()
        assert tick.mala_count == 0

    def test_mantra_tick_advance(self):
        """advance increases tick_count."""
        tick = MantraTick()
        initial = tick.tick_count
        tick.advance()
        assert tick.tick_count == initial + 1

    def test_mantra_tick_advance_returns_position(self):
        """advance returns new position."""
        tick = MantraTick()
        new_pos = tick.advance()
        assert new_pos == tick.position

    def test_mantra_tick_position_wraps(self):
        """position wraps at VENU_POSITIONS (16)."""
        tick = MantraTick()
        for _ in range(VENU_POSITIONS):
            tick.advance()
        assert tick.position == 0
        assert tick.tick_count == VENU_POSITIONS

    def test_mantra_tick_position_sequence(self):
        """position cycles through 0-15."""
        tick = MantraTick()
        for expected in range(VENU_POSITIONS):
            assert tick.position == expected
            tick.advance()
        # Back to 0
        assert tick.position == 0

    def test_mantra_tick_cycle_increments(self):
        """cycle increments every 16 ticks."""
        tick = MantraTick()
        assert tick.cycle == 0

        for _ in range(VENU_POSITIONS):
            tick.advance()
        assert tick.cycle == 1

        for _ in range(VENU_POSITIONS):
            tick.advance()
        assert tick.cycle == 2

    def test_mantra_tick_mala_count_increments(self):
        """mala_count increments every VENU_TICKS_PER_MALA ticks."""
        tick = MantraTick()
        assert tick.mala_count == 0

        for _ in range(VENU_TICKS_PER_MALA):
            tick.advance()
        assert tick.mala_count == 1

    def test_mantra_tick_repr(self):
        """MantraTick has string representation."""
        tick = MantraTick()
        rep = repr(tick)
        assert "MantraTick" in rep
        assert "tick=" in rep
        assert "pos=" in rep
        assert "cycle=" in rep

    def test_mantra_tick_repr_updates(self):
        """repr shows updated values."""
        tick = MantraTick()
        tick.advance()
        tick.advance()
        rep = repr(tick)
        assert "tick=2" in rep
        assert "pos=2" in rep

    def test_mantra_tick_multiple_advances(self):
        """Multiple advances work correctly."""
        tick = MantraTick()
        for i in range(100):
            tick.advance()

        assert tick.tick_count == 100
        assert tick.position == 100 % VENU_POSITIONS
        assert tick.cycle == 100 // VENU_POSITIONS


# =============================================================================
# Constants Tests
# =============================================================================


class TestVenuConstants:
    """Test Venu constants used by MantraTick."""

    def test_venu_positions_is_16(self):
        """VENU_POSITIONS is 16."""
        assert VENU_POSITIONS == 16

    def test_venu_ticks_per_mala_is_positive(self):
        """VENU_TICKS_PER_MALA is positive."""
        assert VENU_TICKS_PER_MALA > 0

    def test_venu_ticks_per_mala_is_divisible_by_positions(self):
        """VENU_TICKS_PER_MALA is divisible by VENU_POSITIONS."""
        assert VENU_TICKS_PER_MALA % VENU_POSITIONS == 0
