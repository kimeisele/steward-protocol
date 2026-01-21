"""
TESTS: byte.py - Packed Ternary Encoding
========================================

"The Word is n-trit, packed into m-bits."

REAL TESTS for:
1. HolyName enum (HARE, KRISHNA, RAMA, VOID)
2. MantraBit flags (16-bit)
3. MantraByte packed encoding
4. GenesisByte validation
"""

import pytest
from vibe_core.mahamantra.substrate.byte import (
    HolyName,
    MantraBit,
    MantraByte,
    GenesisByte,
    MAHAMANTRA_DIMENSION,
    LILA_LIMIT,
    LILA_CYCLES,
    MANTRA_SEQUENCE,
)


# =============================================================================
# HolyName Tests
# =============================================================================


class TestHolyName:
    """Test HolyName IntEnum."""

    def test_hare_is_0(self):
        """HARE = 0 (00 binary)."""
        assert HolyName.HARE.value == 0

    def test_krishna_is_1(self):
        """KRISHNA = 1 (01 binary)."""
        assert HolyName.KRISHNA.value == 1

    def test_rama_is_2(self):
        """RAMA = 2 (10 binary)."""
        assert HolyName.RAMA.value == 2

    def test_void_is_3(self):
        """VOID = 3 (11 binary) - Maya/Error state."""
        assert HolyName.VOID.value == 3

    def test_four_values_for_2_bits(self):
        """Exactly 4 values (2 bits)."""
        assert len(HolyName) == 4


# =============================================================================
# MantraBit Tests
# =============================================================================


class TestMantraBit:
    """Test MantraBit 16-bit flags."""

    def test_16_bits(self):
        """MantraBit has 16 flags (one per word)."""
        assert len(MantraBit) == 16

    def test_first_quarter_positions(self):
        """Quarter 1 (Genesis): positions 0-3."""
        assert MantraBit.HARE_1.value == 1 << 0
        assert MantraBit.KRISHNA_1.value == 1 << 1
        assert MantraBit.HARE_2.value == 1 << 2
        assert MantraBit.KRISHNA_2.value == 1 << 3

    def test_second_quarter_positions(self):
        """Quarter 2 (Dharma): positions 4-7."""
        assert MantraBit.KRISHNA_3.value == 1 << 4
        assert MantraBit.KRISHNA_4.value == 1 << 5
        assert MantraBit.HARE_3.value == 1 << 6
        assert MantraBit.HARE_4.value == 1 << 7

    def test_third_quarter_positions(self):
        """Quarter 3 (Karma): positions 8-11."""
        assert MantraBit.HARE_5.value == 1 << 8
        assert MantraBit.RAMA_1.value == 1 << 9
        assert MantraBit.HARE_6.value == 1 << 10
        assert MantraBit.RAMA_2.value == 1 << 11

    def test_fourth_quarter_positions(self):
        """Quarter 4 (Moksha): positions 12-15."""
        assert MantraBit.RAMA_3.value == 1 << 12
        assert MantraBit.RAMA_4.value == 1 << 13
        assert MantraBit.HARE_7.value == 1 << 14
        assert MantraBit.HARE_8.value == 1 << 15

    def test_full_resonance_is_0xffff(self):
        """full_resonance() returns 0xFFFF (all 16 bits set)."""
        full = MantraBit.full_resonance()
        assert int(full) == 0xFFFF


# =============================================================================
# MantraByte Tests
# =============================================================================


class TestMantraByte:
    """Test MantraByte packed encoding."""

    def test_empty_mantra_byte(self):
        """Empty MantraByte has length 0."""
        mb = MantraByte()
        assert len(mb) == 0

    def test_from_trits(self):
        """from_trits packs HolyNames into integer."""
        trits = [HolyName.HARE, HolyName.KRISHNA, HolyName.RAMA]
        mb = MantraByte.from_trits(trits)
        assert len(mb) == 3
        assert mb.get_trit(0) == HolyName.HARE
        assert mb.get_trit(1) == HolyName.KRISHNA
        assert mb.get_trit(2) == HolyName.RAMA

    def test_from_trits_void_raises(self):
        """from_trits raises on VOID."""
        with pytest.raises(ValueError, match="Cannot pack VOID"):
            MantraByte.from_trits([HolyName.VOID])

    def test_from_string(self):
        """from_string parses 'H K R' format."""
        mb = MantraByte.from_string("H K R H")
        assert len(mb) == 4
        assert mb.get_trit(0) == HolyName.HARE
        assert mb.get_trit(1) == HolyName.KRISHNA
        assert mb.get_trit(2) == HolyName.RAMA
        assert mb.get_trit(3) == HolyName.HARE

    def test_standard_16_length(self):
        """standard_16() returns 16-word sequence."""
        std = MantraByte.standard_16()
        assert len(std) == 16
        assert std.dimension == 16

    def test_standard_16_first_quarter(self):
        """First quarter is Hare Krishna Hare Krishna."""
        std = MantraByte.standard_16()
        assert std.get_trit(0) == HolyName.HARE
        assert std.get_trit(1) == HolyName.KRISHNA
        assert std.get_trit(2) == HolyName.HARE
        assert std.get_trit(3) == HolyName.KRISHNA

    def test_standard_16_second_quarter(self):
        """Second quarter is Krishna Krishna Hare Hare."""
        std = MantraByte.standard_16()
        assert std.get_trit(4) == HolyName.KRISHNA
        assert std.get_trit(5) == HolyName.KRISHNA
        assert std.get_trit(6) == HolyName.HARE
        assert std.get_trit(7) == HolyName.HARE

    def test_standard_16_third_quarter(self):
        """Third quarter is Hare Rama Hare Rama."""
        std = MantraByte.standard_16()
        assert std.get_trit(8) == HolyName.HARE
        assert std.get_trit(9) == HolyName.RAMA
        assert std.get_trit(10) == HolyName.HARE
        assert std.get_trit(11) == HolyName.RAMA

    def test_standard_16_fourth_quarter(self):
        """Fourth quarter is Rama Rama Hare Hare."""
        std = MantraByte.standard_16()
        assert std.get_trit(12) == HolyName.RAMA
        assert std.get_trit(13) == HolyName.RAMA
        assert std.get_trit(14) == HolyName.HARE
        assert std.get_trit(15) == HolyName.HARE

    def test_get_trit_out_of_bounds_returns_void(self):
        """get_trit returns VOID for out of bounds."""
        mb = MantraByte.from_trits([HolyName.HARE])
        assert mb.get_trit(99) == HolyName.VOID
        assert mb.get_trit(-1) == HolyName.VOID

    def test_sequence_property(self):
        """sequence property returns list of HolyNames."""
        mb = MantraByte.from_trits([HolyName.HARE, HolyName.KRISHNA])
        seq = mb.sequence
        assert seq == [HolyName.HARE, HolyName.KRISHNA]

    def test_coherence_perfect_match(self):
        """Perfect match has high coherence."""
        std = MantraByte.standard_16()
        assert std.coherence > 0.9

    def test_coherence_empty_is_zero(self):
        """Empty MantraByte has 0 coherence."""
        mb = MantraByte()
        assert mb.coherence == 0.0

    def test_iteration(self):
        """MantraByte is iterable."""
        mb = MantraByte.from_trits([HolyName.HARE, HolyName.KRISHNA, HolyName.RAMA])
        names = list(mb)
        assert names == [HolyName.HARE, HolyName.KRISHNA, HolyName.RAMA]

    def test_equality(self):
        """MantraByte equality."""
        mb1 = MantraByte.from_trits([HolyName.HARE, HolyName.KRISHNA])
        mb2 = MantraByte.from_trits([HolyName.HARE, HolyName.KRISHNA])
        mb3 = MantraByte.from_trits([HolyName.KRISHNA, HolyName.HARE])
        assert mb1 == mb2
        assert mb1 != mb3


# =============================================================================
# GenesisByte Tests
# =============================================================================


class TestGenesisByte:
    """Test GenesisByte validation."""

    def test_genesis_byte_defaults(self):
        """GenesisByte has correct defaults."""
        gb = GenesisByte(signature="test")
        assert gb.dimension == MAHAMANTRA_DIMENSION  # 16
        assert gb.lila_limit == LILA_LIMIT  # 48

    def test_validate_requires_signature(self):
        """Validation requires non-empty signature."""
        gb = GenesisByte(signature="")
        with pytest.raises(PermissionError, match="Voidist"):
            gb.validate()

    def test_validate_requires_parampara(self):
        """Validation requires valid parampara hash."""
        gb = GenesisByte(signature="test", parampara_hash="0x99")  # 153 % 37 != 0
        with pytest.raises(ConnectionError, match="Sahajiya"):
            gb.validate()

    def test_validate_lila_limit_must_be_dimension_times_3(self):
        """lila_limit must equal dimension × 3."""
        gb = GenesisByte(signature="test", lila_limit=50)  # Not 16 × 3
        with pytest.raises(ValueError, match="Chaitanya Lila Violation"):
            gb.validate()

    def test_valid_genesis_byte(self):
        """Valid GenesisByte passes validation."""
        gb = GenesisByte(
            signature="valid",
            parampara_hash="0x25",  # 37 % 37 == 0
            dimension=16,
            lila_limit=48,
        )
        assert gb.validate() is True

    def test_is_valid_property(self):
        """is_valid returns False for invalid, True for valid."""
        invalid = GenesisByte(signature="")
        assert invalid.is_valid is False

        valid = GenesisByte(signature="valid", parampara_hash="0x25")
        assert valid.is_valid is True

    def test_get_lila_phase_navadvipa(self):
        """Phase is navadvipa for ticks 0-23."""
        gb = GenesisByte(signature="test")
        assert gb.get_lila_phase(0) == "navadvipa"
        assert gb.get_lila_phase(10) == "navadvipa"
        assert gb.get_lila_phase(23) == "navadvipa"

    def test_get_lila_phase_puri(self):
        """Phase is puri for ticks 24-47."""
        gb = GenesisByte(signature="test")
        assert gb.get_lila_phase(24) == "puri"
        assert gb.get_lila_phase(35) == "puri"
        assert gb.get_lila_phase(47) == "puri"

    def test_get_lila_phase_out_of_bounds(self):
        """get_lila_phase raises for invalid tick."""
        gb = GenesisByte(signature="test")
        with pytest.raises(ValueError):
            gb.get_lila_phase(48)
        with pytest.raises(ValueError):
            gb.get_lila_phase(-1)

    def test_get_mantra_position(self):
        """get_mantra_position returns 0-15."""
        gb = GenesisByte(signature="test")
        assert gb.get_mantra_position(0) == 0
        assert gb.get_mantra_position(15) == 15
        assert gb.get_mantra_position(16) == 0  # Wraps
        assert gb.get_mantra_position(17) == 1
        assert gb.get_mantra_position(47) == 15

    def test_get_mantra_cycle(self):
        """get_mantra_cycle returns 1, 2, or 3."""
        gb = GenesisByte(signature="test")
        # Cycle 1: ticks 0-15
        assert gb.get_mantra_cycle(0) == 1
        assert gb.get_mantra_cycle(15) == 1
        # Cycle 2: ticks 16-31
        assert gb.get_mantra_cycle(16) == 2
        assert gb.get_mantra_cycle(31) == 2
        # Cycle 3: ticks 32-47
        assert gb.get_mantra_cycle(32) == 3
        assert gb.get_mantra_cycle(47) == 3


# =============================================================================
# Constants Tests
# =============================================================================


class TestByteConstants:
    """Test module-level constants."""

    def test_mahamantra_dimension_is_16(self):
        """MAHAMANTRA_DIMENSION = 16."""
        assert MAHAMANTRA_DIMENSION == 16

    def test_lila_limit_is_48(self):
        """LILA_LIMIT = 48."""
        assert LILA_LIMIT == 48

    def test_lila_cycles_is_3(self):
        """LILA_CYCLES = 3."""
        assert LILA_CYCLES == 3

    def test_lila_limit_formula(self):
        """LILA_LIMIT = MAHAMANTRA_DIMENSION × LILA_CYCLES."""
        assert LILA_LIMIT == MAHAMANTRA_DIMENSION * LILA_CYCLES

    def test_mantra_sequence_is_standard(self):
        """MANTRA_SEQUENCE is the standard 16-word sequence."""
        assert len(MANTRA_SEQUENCE) == 16
        assert MANTRA_SEQUENCE == MantraByte.standard_16()
