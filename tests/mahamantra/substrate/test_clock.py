"""
TESTS: clock.py - Stateless Mantra Clock Functions
===================================================

"kālo 'smi loka-kṣaya-kṛt pravṛddho"

REAL TESTS for:
1. get_tick_info - mantra position info (0-15)
2. get_lila_info - lila position info (0-47)
3. next/previous position functions
4. lila_to_mantra conversion
5. verify_parampara
"""

import pytest
from vibe_core.mahamantra.substrate.clock import (
    # Types
    TickInfo,
    LilaInfo,
    # Mantra functions
    get_tick_info,
    get_position_by_index,
    get_position_by_guardian,
    next_position,
    previous_position,
    # Lila functions
    get_lila_info,
    next_lila_position,
    previous_lila_position,
    lila_to_mantra,
    # Constants
    MANTRA_LENGTH,
    LILA_LENGTH,
    NAVADVIP_END,
    PURI_START,
    # Utilities
    get_chant,
    verify_parampara,
)


# =============================================================================
# Constants Tests
# =============================================================================


class TestClockConstants:
    """Test clock constants."""

    def test_mantra_length_is_16(self):
        """MANTRA_LENGTH = 16."""
        assert MANTRA_LENGTH == 16

    def test_lila_length_is_48(self):
        """LILA_LENGTH = 48."""
        assert LILA_LENGTH == 48

    def test_navadvip_end_is_24(self):
        """NAVADVIP_END = 24 (exclusive)."""
        assert NAVADVIP_END == 24

    def test_puri_start_is_24(self):
        """PURI_START = 24 (inclusive)."""
        assert PURI_START == 24


# =============================================================================
# get_tick_info Tests
# =============================================================================


class TestGetTickInfo:
    """Test get_tick_info function."""

    def test_position_0_vyasa(self):
        """Position 0 is Vyasa (GENESIS HEAD)."""
        info = get_tick_info(0)
        assert info["position"] == 0
        assert info["guardian"] == "vyasa"
        assert info["quarter"] == "genesis"

    def test_position_4_prithu(self):
        """Position 4 is Prithu (DHARMA HEAD)."""
        info = get_tick_info(4)
        assert info["position"] == 4
        assert info["guardian"] == "prithu"
        assert info["quarter"] == "dharma"

    def test_position_8_parashurama(self):
        """Position 8 is Parashurama (KARMA HEAD)."""
        info = get_tick_info(8)
        assert info["position"] == 8
        assert info["guardian"] == "parashurama"
        assert info["quarter"] == "karma"

    def test_position_12_nrisimha(self):
        """Position 12 is Nrisimha (MOKSHA HEAD)."""
        info = get_tick_info(12)
        assert info["position"] == 12
        assert info["guardian"] == "nrisimha"
        assert info["quarter"] == "moksha"

    def test_position_15_yamaraja(self):
        """Position 15 is Yamaraja (last position)."""
        info = get_tick_info(15)
        assert info["position"] == 15
        assert info["guardian"] == "yamaraja"
        assert info["quarter"] == "moksha"

    def test_all_positions_have_word(self):
        """All positions have a word (HARE/KRISHNA/RAMA)."""
        for pos in range(16):
            info = get_tick_info(pos)
            assert info["word"] in ("HARE", "KRISHNA", "RAMA")

    def test_invalid_position_raises(self):
        """Invalid position raises ValueError."""
        with pytest.raises(ValueError):
            get_tick_info(16)
        with pytest.raises(ValueError):
            get_tick_info(-1)


# =============================================================================
# get_lila_info Tests
# =============================================================================


class TestGetLilaInfo:
    """Test get_lila_info function."""

    def test_lila_0_is_navadvipa_cycle_1(self):
        """Lila position 0 is Navadvipa, cycle 1."""
        info = get_lila_info(0)
        assert info["lila_position"] == 0
        assert info["phase"] == "navadvipa"
        assert info["cycle"] == 1
        assert info["is_navadvip"] is True
        assert info["is_puri"] is False

    def test_lila_23_is_navadvipa_cycle_2(self):
        """Lila position 23 is Navadvipa, cycle 2."""
        info = get_lila_info(23)
        assert info["lila_position"] == 23
        assert info["phase"] == "navadvipa"
        assert info["cycle"] == 2
        assert info["is_navadvip"] is True

    def test_lila_24_is_puri_cycle_2(self):
        """Lila position 24 is Puri, cycle 2."""
        info = get_lila_info(24)
        assert info["lila_position"] == 24
        assert info["phase"] == "puri"
        assert info["cycle"] == 2
        assert info["is_navadvip"] is False
        assert info["is_puri"] is True

    def test_lila_47_is_puri_cycle_3(self):
        """Lila position 47 is Puri, cycle 3."""
        info = get_lila_info(47)
        assert info["lila_position"] == 47
        assert info["phase"] == "puri"
        assert info["cycle"] == 3
        assert info["is_puri"] is True

    def test_lila_position_maps_to_mantra(self):
        """Lila position maps to correct mantra position."""
        # Position 0 -> mantra 0
        assert get_lila_info(0)["position"] == 0
        # Position 16 -> mantra 0 (cycle 2)
        assert get_lila_info(16)["position"] == 0
        # Position 17 -> mantra 1 (cycle 2)
        assert get_lila_info(17)["position"] == 1
        # Position 47 -> mantra 15 (cycle 3)
        assert get_lila_info(47)["position"] == 15

    def test_invalid_lila_position_raises(self):
        """Invalid lila position raises ValueError."""
        with pytest.raises(ValueError):
            get_lila_info(48)
        with pytest.raises(ValueError):
            get_lila_info(-1)


# =============================================================================
# Position Navigation Tests
# =============================================================================


class TestPositionNavigation:
    """Test next/previous position functions."""

    def test_next_position(self):
        """next_position advances by 1."""
        assert next_position(0) == 1
        assert next_position(5) == 6
        assert next_position(14) == 15

    def test_next_position_wraps(self):
        """next_position wraps at 16."""
        assert next_position(15) == 0

    def test_previous_position(self):
        """previous_position goes back by 1."""
        assert previous_position(1) == 0
        assert previous_position(5) == 4
        assert previous_position(15) == 14

    def test_previous_position_wraps(self):
        """previous_position wraps at 0."""
        assert previous_position(0) == 15


class TestLilaNavigation:
    """Test next/previous lila position functions."""

    def test_next_lila_position(self):
        """next_lila_position advances by 1."""
        assert next_lila_position(0) == 1
        assert next_lila_position(23) == 24
        assert next_lila_position(46) == 47

    def test_next_lila_position_wraps(self):
        """next_lila_position wraps at 48."""
        assert next_lila_position(47) == 0

    def test_previous_lila_position(self):
        """previous_lila_position goes back by 1."""
        assert previous_lila_position(1) == 0
        assert previous_lila_position(24) == 23
        assert previous_lila_position(47) == 46

    def test_previous_lila_position_wraps(self):
        """previous_lila_position wraps at 0."""
        assert previous_lila_position(0) == 47


# =============================================================================
# lila_to_mantra Tests
# =============================================================================


class TestLilaToMantra:
    """Test lila_to_mantra conversion."""

    def test_lila_0_to_mantra(self):
        """Lila 0 -> mantra 0, cycle 1, navadvipa."""
        pos, cycle, phase = lila_to_mantra(0)
        assert pos == 0
        assert cycle == 1
        assert phase == "navadvipa"

    def test_lila_16_to_mantra(self):
        """Lila 16 -> mantra 0, cycle 2, navadvipa."""
        pos, cycle, phase = lila_to_mantra(16)
        assert pos == 0
        assert cycle == 2
        assert phase == "navadvipa"

    def test_lila_32_to_mantra(self):
        """Lila 32 -> mantra 0, cycle 3, puri."""
        pos, cycle, phase = lila_to_mantra(32)
        assert pos == 0
        assert cycle == 3
        assert phase == "puri"

    def test_lila_47_to_mantra(self):
        """Lila 47 -> mantra 15, cycle 3, puri."""
        pos, cycle, phase = lila_to_mantra(47)
        assert pos == 15
        assert cycle == 3
        assert phase == "puri"


# =============================================================================
# get_position_by Tests
# =============================================================================


class TestGetPositionBy:
    """Test get_position_by_* functions."""

    def test_get_position_by_index(self):
        """get_position_by_index returns MantraPosition."""
        pos = get_position_by_index(0)
        assert pos.index == 0

    def test_get_position_by_guardian(self):
        """get_position_by_guardian finds position."""
        pos = get_position_by_guardian("vyasa")
        assert pos.index == 0

        pos = get_position_by_guardian("yamaraja")
        assert pos.index == 15

    def test_get_position_by_unknown_guardian_raises(self):
        """get_position_by_guardian raises for unknown."""
        with pytest.raises(ValueError):
            get_position_by_guardian("nonexistent")


# =============================================================================
# Utility Function Tests
# =============================================================================


class TestUtilities:
    """Test utility functions."""

    def test_get_chant(self):
        """get_chant returns full mahamantra."""
        chant = get_chant()
        assert "Hare" in chant
        assert "Krishna" in chant
        assert "Rama" in chant
        # Should have 16 words
        words = chant.split()
        assert len(words) == 16

    def test_get_chant_custom_separator(self):
        """get_chant accepts custom separator."""
        chant = get_chant(separator="-")
        assert "-" in chant

    def test_verify_parampara_37(self):
        """verify_parampara returns True for multiples of 37."""
        assert verify_parampara(37) is True
        assert verify_parampara(74) is True
        assert verify_parampara(111) is True

    def test_verify_parampara_not_37(self):
        """verify_parampara returns False for non-multiples of 37."""
        assert verify_parampara(36) is False
        assert verify_parampara(38) is False
        assert verify_parampara(100) is False

    def test_verify_parampara_zero(self):
        """verify_parampara returns True for 0."""
        assert verify_parampara(0) is True
