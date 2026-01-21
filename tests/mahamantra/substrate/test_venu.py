"""
TESTS: venu.py - Krishna's Flute (Pure Functions)
=================================================

"venum kvanantam aravinda-dalayataksham"

REAL TESTS for:
1. TickState TypedDict
2. tick_to_* functions
3. position_to_* functions
4. Timing functions
"""

import pytest
from vibe_core.mahamantra.substrate.venu import (
    # Types
    TickState,
    # Tick functions
    tick_to_position,
    tick_to_cycle,
    tick_to_prana,
    tick_to_mala,
    tick_to_quarter,
    tick_to_word,
    is_downbeat,
    is_mala_complete,
    get_tick_state,
    # Position functions
    position_to_quarter,
    position_to_word,
    next_position,
    previous_position,
    # Timing functions
    tick_to_ms,
    ms_to_tick,
    tick_to_seconds,
    mala_duration_seconds,
)
from vibe_core.mahamantra.substrate.seed import Quarter, HolyName


# =============================================================================
# tick_to_position Tests
# =============================================================================


class TestTickToPosition:
    """Test tick_to_position function."""

    def test_tick_0_is_position_0(self):
        """Tick 0 is position 0."""
        assert tick_to_position(0) == 0

    def test_tick_15_is_position_15(self):
        """Tick 15 is position 15."""
        assert tick_to_position(15) == 15

    def test_tick_16_wraps_to_0(self):
        """Tick 16 wraps to position 0."""
        assert tick_to_position(16) == 0

    def test_tick_17_is_position_1(self):
        """Tick 17 is position 1."""
        assert tick_to_position(17) == 1

    def test_tick_100_wraps(self):
        """Tick 100 wraps correctly."""
        assert tick_to_position(100) == 100 % 16  # 4

    def test_large_tick(self):
        """Large tick wraps correctly."""
        assert tick_to_position(1728) == 0  # 1728 % 16 = 0
        assert tick_to_position(1729) == 1


# =============================================================================
# tick_to_cycle Tests
# =============================================================================


class TestTickToCycle:
    """Test tick_to_cycle function."""

    def test_tick_0_is_cycle_0(self):
        """Tick 0 is cycle 0."""
        assert tick_to_cycle(0) == 0

    def test_tick_15_is_cycle_0(self):
        """Tick 15 is still cycle 0."""
        assert tick_to_cycle(15) == 0

    def test_tick_16_is_cycle_1(self):
        """Tick 16 is cycle 1."""
        assert tick_to_cycle(16) == 1

    def test_tick_32_is_cycle_2(self):
        """Tick 32 is cycle 2."""
        assert tick_to_cycle(32) == 2

    def test_tick_1728_is_cycle_108(self):
        """Tick 1728 is cycle 108 (one mala)."""
        assert tick_to_cycle(1728) == 108


# =============================================================================
# tick_to_prana Tests
# =============================================================================


class TestTickToPrana:
    """Test tick_to_prana function."""

    def test_tick_0_is_prana_0(self):
        """Tick 0 is prana 0."""
        assert tick_to_prana(0) == 0

    def test_tick_16_is_prana_1(self):
        """Tick 16 is prana 1."""
        assert tick_to_prana(16) == 1

    def test_tick_1712_is_prana_107(self):
        """Tick 1712 (107 × 16) is prana 107."""
        assert tick_to_prana(107 * 16) == 107

    def test_tick_1728_wraps_to_prana_0(self):
        """Tick 1728 (108 × 16) wraps to prana 0."""
        assert tick_to_prana(1728) == 0

    def test_prana_within_mala(self):
        """Prana is within 0-107 range."""
        for tick in [0, 100, 500, 1000, 1700, 2000, 3456]:
            prana = tick_to_prana(tick)
            assert 0 <= prana < 108


# =============================================================================
# tick_to_mala Tests
# =============================================================================


class TestTickToMala:
    """Test tick_to_mala function."""

    def test_tick_0_is_mala_0(self):
        """Tick 0 is mala 0."""
        assert tick_to_mala(0) == 0

    def test_tick_1727_is_mala_0(self):
        """Tick 1727 is still mala 0."""
        assert tick_to_mala(1727) == 0

    def test_tick_1728_is_mala_1(self):
        """Tick 1728 is mala 1."""
        assert tick_to_mala(1728) == 1

    def test_tick_3456_is_mala_2(self):
        """Tick 3456 (1728 × 2) is mala 2."""
        assert tick_to_mala(3456) == 2


# =============================================================================
# tick_to_quarter Tests
# =============================================================================


class TestTickToQuarter:
    """Test tick_to_quarter function."""

    def test_tick_0_is_genesis(self):
        """Tick 0 (position 0) is GENESIS."""
        assert tick_to_quarter(0) == Quarter.GENESIS

    def test_tick_4_is_dharma(self):
        """Tick 4 (position 4) is DHARMA."""
        assert tick_to_quarter(4) == Quarter.DHARMA

    def test_tick_8_is_karma(self):
        """Tick 8 (position 8) is KARMA."""
        assert tick_to_quarter(8) == Quarter.KARMA

    def test_tick_12_is_moksha(self):
        """Tick 12 (position 12) is MOKSHA."""
        assert tick_to_quarter(12) == Quarter.MOKSHA

    def test_tick_20_wraps_to_dharma(self):
        """Tick 20 (position 4) is DHARMA."""
        assert tick_to_quarter(20) == Quarter.DHARMA


# =============================================================================
# tick_to_word Tests
# =============================================================================


class TestTickToWord:
    """Test tick_to_word function."""

    def test_tick_0_is_hare(self):
        """Tick 0 (position 0) is HARE."""
        assert tick_to_word(0) == HolyName.HARE

    def test_tick_1_is_krishna(self):
        """Tick 1 (position 1) is KRISHNA."""
        assert tick_to_word(1) == HolyName.KRISHNA

    def test_tick_9_is_rama(self):
        """Tick 9 (position 9) is RAMA."""
        assert tick_to_word(9) == HolyName.RAMA

    def test_tick_16_is_hare(self):
        """Tick 16 (position 0) is HARE."""
        assert tick_to_word(16) == HolyName.HARE


# =============================================================================
# is_downbeat Tests
# =============================================================================


class TestIsDownbeat:
    """Test is_downbeat function."""

    def test_tick_0_is_downbeat(self):
        """Tick 0 is downbeat."""
        assert is_downbeat(0) is True

    def test_tick_16_is_downbeat(self):
        """Tick 16 is downbeat."""
        assert is_downbeat(16) is True

    def test_tick_1_is_not_downbeat(self):
        """Tick 1 is not downbeat."""
        assert is_downbeat(1) is False

    def test_tick_15_is_not_downbeat(self):
        """Tick 15 is not downbeat."""
        assert is_downbeat(15) is False


# =============================================================================
# is_mala_complete Tests
# =============================================================================


class TestIsMalaComplete:
    """Test is_mala_complete function."""

    def test_tick_0_not_complete(self):
        """Tick 0 is not mala complete (tick must be > 0)."""
        assert is_mala_complete(0) is False

    def test_tick_1728_is_complete(self):
        """Tick 1728 is mala complete."""
        assert is_mala_complete(1728) is True

    def test_tick_3456_is_complete(self):
        """Tick 3456 is mala complete."""
        assert is_mala_complete(3456) is True

    def test_tick_1727_not_complete(self):
        """Tick 1727 is not mala complete."""
        assert is_mala_complete(1727) is False


# =============================================================================
# get_tick_state Tests
# =============================================================================


class TestGetTickState:
    """Test get_tick_state function."""

    def test_get_tick_state_tick_0(self):
        """get_tick_state for tick 0."""
        state = get_tick_state(0)
        assert state["tick"] == 0
        assert state["position"] == 0
        assert state["cycle"] == 0
        assert state["prana"] == 0
        assert state["mala"] == 0
        assert state["quarter"] == "genesis"
        assert state["word"] == "HARE"
        assert state["is_downbeat"] is True
        assert state["is_mala_complete"] is False

    def test_get_tick_state_tick_17(self):
        """get_tick_state for tick 17."""
        state = get_tick_state(17)
        assert state["tick"] == 17
        assert state["position"] == 1
        assert state["cycle"] == 1
        assert state["word"] == "KRISHNA"
        assert state["is_downbeat"] is False

    def test_get_tick_state_tick_1728(self):
        """get_tick_state for tick 1728."""
        state = get_tick_state(1728)
        assert state["tick"] == 1728
        assert state["position"] == 0
        assert state["cycle"] == 108
        assert state["mala"] == 1
        assert state["is_mala_complete"] is True

    def test_get_tick_state_returns_typed_dict(self):
        """get_tick_state returns TickState TypedDict."""
        state = get_tick_state(0)
        assert "tick" in state
        assert "position" in state
        assert "cycle" in state
        assert "prana" in state
        assert "mala" in state
        assert "quarter" in state
        assert "word" in state
        assert "is_downbeat" in state
        assert "is_mala_complete" in state


# =============================================================================
# position_to_quarter Tests
# =============================================================================


class TestPositionToQuarter:
    """Test position_to_quarter function."""

    def test_position_0_is_genesis(self):
        """Position 0 is GENESIS."""
        assert position_to_quarter(0) == Quarter.GENESIS

    def test_position_3_is_genesis(self):
        """Position 3 is GENESIS."""
        assert position_to_quarter(3) == Quarter.GENESIS

    def test_position_4_is_dharma(self):
        """Position 4 is DHARMA."""
        assert position_to_quarter(4) == Quarter.DHARMA

    def test_position_8_is_karma(self):
        """Position 8 is KARMA."""
        assert position_to_quarter(8) == Quarter.KARMA

    def test_position_12_is_moksha(self):
        """Position 12 is MOKSHA."""
        assert position_to_quarter(12) == Quarter.MOKSHA

    def test_invalid_position_raises(self):
        """Invalid position raises ValueError."""
        with pytest.raises(ValueError):
            position_to_quarter(16)
        with pytest.raises(ValueError):
            position_to_quarter(-1)


# =============================================================================
# position_to_word Tests
# =============================================================================


class TestPositionToWord:
    """Test position_to_word function."""

    def test_position_0_is_hare(self):
        """Position 0 is HARE."""
        assert position_to_word(0) == HolyName.HARE

    def test_position_1_is_krishna(self):
        """Position 1 is KRISHNA."""
        assert position_to_word(1) == HolyName.KRISHNA

    def test_position_9_is_rama(self):
        """Position 9 is RAMA."""
        assert position_to_word(9) == HolyName.RAMA

    def test_invalid_position_raises(self):
        """Invalid position raises ValueError."""
        with pytest.raises(ValueError):
            position_to_word(16)


# =============================================================================
# next_position / previous_position Tests
# =============================================================================


class TestPositionNavigation:
    """Test next_position and previous_position functions."""

    def test_next_position_normal(self):
        """next_position advances by 1."""
        assert next_position(0) == 1
        assert next_position(5) == 6
        assert next_position(14) == 15

    def test_next_position_wraps(self):
        """next_position wraps at 16."""
        assert next_position(15) == 0

    def test_previous_position_normal(self):
        """previous_position goes back by 1."""
        assert previous_position(1) == 0
        assert previous_position(5) == 4
        assert previous_position(15) == 14

    def test_previous_position_wraps(self):
        """previous_position wraps at 0."""
        assert previous_position(0) == 15


# =============================================================================
# Timing Functions Tests
# =============================================================================


class TestTimingFunctions:
    """Test timing conversion functions."""

    def test_tick_to_ms(self):
        """tick_to_ms converts correctly."""
        assert tick_to_ms(0) == 0
        assert tick_to_ms(1) == 250
        assert tick_to_ms(4) == 1000
        assert tick_to_ms(16) == 4000

    def test_ms_to_tick(self):
        """ms_to_tick converts correctly."""
        assert ms_to_tick(0) == 0
        assert ms_to_tick(250) == 1
        assert ms_to_tick(1000) == 4
        assert ms_to_tick(4000) == 16

    def test_ms_to_tick_floors(self):
        """ms_to_tick floors non-exact values."""
        assert ms_to_tick(249) == 0
        assert ms_to_tick(251) == 1
        assert ms_to_tick(500) == 2

    def test_tick_to_seconds(self):
        """tick_to_seconds converts correctly."""
        assert tick_to_seconds(0) == 0.0
        assert tick_to_seconds(4) == 1.0
        assert tick_to_seconds(16) == 4.0

    def test_mala_duration_seconds(self):
        """mala_duration_seconds returns 432."""
        assert mala_duration_seconds() == 432  # 108 × 4


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.substrate import venu

        assert "TickState" in venu.__all__
        assert "tick_to_position" in venu.__all__
        assert "tick_to_cycle" in venu.__all__
        assert "tick_to_prana" in venu.__all__
        assert "tick_to_mala" in venu.__all__
        assert "get_tick_state" in venu.__all__
        assert "tick_to_ms" in venu.__all__
        assert "mala_duration_seconds" in venu.__all__
