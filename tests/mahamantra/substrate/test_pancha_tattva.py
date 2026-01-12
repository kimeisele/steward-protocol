"""
TEST PANCHA TATTVA - substrate/pancha_tattva.py
================================================

Tests for the Pancha Tattva (Die 5 Absoluten Wahrheiten).

"sri-krsna-caitanya prabhu-nityananda
 sri-advaita gadadhara srivasadi-gaura-bhakta-vrnda"

Die Essenz des Mahamantra offenbart sich nur durch die Pancha Tattva.
"""

import pytest

from vibe_core.mahamantra.substrate import (
    # Main Enum
    PanchaTattva,
    TattvaIndex,
    # Aspect
    TattvaAspect,
    PANCHA_TATTVA_ASPECTS,
    # Lookup
    get_tattva_aspect,
    get_tattva_by_index,
    get_tattva_by_capability,
    get_tattva_by_protocol,
    # Byte Mapping
    TATTVA_TO_HOLYNAME,
    tattva_to_trit,
    # Gates
    TattvaGate,
    GATE_TO_TATTVA,
    # Protocol
    PanchaTattvaAware,
    # Position Mapping
    get_tattva_for_position,
    # Parampara
    PANCHA_TATTVA_COUNT,
    PANCHA_TATTVA_VECTOR,
    verify_pancha_tattva_parampara,
    # Prayer
    PANCHA_TATTVA_MANTRA,
    PANCHA_TATTVA_MEANING,
    # Byte for comparison
    HolyName,
)


class TestPanchaTattvaEnum:
    """Test the Pancha Tattva enum."""

    def test_has_5_members(self) -> None:
        """Must have exactly 5 members (Pancha = 5)."""
        assert len(PanchaTattva) == 5

    def test_correct_values(self) -> None:
        """Verify correct string values."""
        assert PanchaTattva.CHAITANYA.value == "chaitanya"
        assert PanchaTattva.NITYANANDA.value == "nityananda"
        assert PanchaTattva.ADVAITA.value == "advaita"
        assert PanchaTattva.GADADHARA.value == "gadadhara"
        assert PanchaTattva.SRIVASA.value == "srivasa"

    def test_tattva_index_matches_order(self) -> None:
        """TattvaIndex must match Pancha Tattva order."""
        assert TattvaIndex.CHAITANYA == 0
        assert TattvaIndex.NITYANANDA == 1
        assert TattvaIndex.ADVAITA == 2
        assert TattvaIndex.GADADHARA == 3
        assert TattvaIndex.SRIVASA == 4


class TestPanchaTattvaAspects:
    """Test the 5 Tattva Aspects."""

    def test_has_5_aspects(self) -> None:
        """Must have exactly 5 aspects."""
        assert len(PANCHA_TATTVA_ASPECTS) == 5

    def test_aspects_indexed_0_to_4(self) -> None:
        """Aspect indices match their index in tuple."""
        for i, aspect in enumerate(PANCHA_TATTVA_ASPECTS):
            assert aspect.index == i

    def test_aspects_have_all_fields(self) -> None:
        """Each aspect has all required fields."""
        for aspect in PANCHA_TATTVA_ASPECTS:
            assert aspect.tattva is not None
            assert isinstance(aspect.index, int)
            assert aspect.sanskrit_name
            assert aspect.essence
            assert aspect.capability
            assert aspect.protocol
            assert isinstance(aspect.primary_word, HolyName)

    def test_chaitanya_is_first(self) -> None:
        """Chaitanya (Krishna Himself) must be first."""
        first = PANCHA_TATTVA_ASPECTS[0]
        assert first.tattva == PanchaTattva.CHAITANYA
        assert "Krishna" in first.essence

    def test_each_has_unique_protocol(self) -> None:
        """Each aspect maps to a unique protocol."""
        protocols = [a.protocol for a in PANCHA_TATTVA_ASPECTS]
        # Each should be distinct
        assert len(protocols) == len(set(protocols))


class TestPanchaTattvaLookup:
    """Test lookup functions."""

    def test_get_tattva_aspect(self) -> None:
        """get_tattva_aspect returns correct aspect."""
        aspect = get_tattva_aspect(PanchaTattva.NITYANANDA)
        assert aspect.index == 1
        assert "Ananta" in aspect.essence

    def test_get_tattva_by_index(self) -> None:
        """get_tattva_by_index returns correct aspect."""
        aspect = get_tattva_by_index(2)
        assert aspect.tattva == PanchaTattva.ADVAITA

    def test_get_tattva_by_index_invalid(self) -> None:
        """get_tattva_by_index raises for invalid index."""
        with pytest.raises(ValueError):
            get_tattva_by_index(5)
        with pytest.raises(ValueError):
            get_tattva_by_index(-1)

    def test_get_tattva_by_capability(self) -> None:
        """get_tattva_by_capability finds by keyword."""
        aspect = get_tattva_by_capability("IDENTITY")
        assert aspect.tattva == PanchaTattva.CHAITANYA

        aspect = get_tattva_by_capability("storage")
        assert aspect.tattva == PanchaTattva.NITYANANDA

    def test_get_tattva_by_protocol(self) -> None:
        """get_tattva_by_protocol finds by protocol name."""
        aspect = get_tattva_by_protocol("MantraProtocol")
        assert aspect.tattva == PanchaTattva.CHAITANYA

        aspect = get_tattva_by_protocol("Sync")
        assert aspect.tattva == PanchaTattva.GADADHARA


class TestByteMapping:
    """Test Pancha Tattva to byte.py mapping."""

    def test_tattva_to_holyname_complete(self) -> None:
        """All 5 Tattvas map to HolyNames."""
        for tattva in PanchaTattva:
            assert tattva in TATTVA_TO_HOLYNAME

    def test_chaitanya_is_krishna(self) -> None:
        """Chaitanya IS Krishna (HolyName.KRISHNA)."""
        assert TATTVA_TO_HOLYNAME[PanchaTattva.CHAITANYA] == HolyName.KRISHNA

    def test_nityananda_is_hare(self) -> None:
        """Nityananda carries energy (HolyName.HARE)."""
        assert TATTVA_TO_HOLYNAME[PanchaTattva.NITYANANDA] == HolyName.HARE

    def test_srivasa_is_rama(self) -> None:
        """Srivasa serves (HolyName.RAMA = strength/service)."""
        assert TATTVA_TO_HOLYNAME[PanchaTattva.SRIVASA] == HolyName.RAMA

    def test_tattva_to_trit(self) -> None:
        """tattva_to_trit returns correct trit values."""
        assert tattva_to_trit(PanchaTattva.CHAITANYA) == HolyName.KRISHNA.value  # 1
        assert tattva_to_trit(PanchaTattva.NITYANANDA) == HolyName.HARE.value    # 0
        assert tattva_to_trit(PanchaTattva.SRIVASA) == HolyName.RAMA.value       # 2


class TestTattvaGates:
    """Test the 5 Gates mapping."""

    def test_has_5_gates(self) -> None:
        """Must have exactly 5 gates."""
        assert len(TattvaGate) == 5

    def test_gates_map_to_tattva(self) -> None:
        """Each gate maps to a Pancha Tattva."""
        for gate in TattvaGate:
            assert gate in GATE_TO_TATTVA
            assert isinstance(GATE_TO_TATTVA[gate], PanchaTattva)

    def test_parse_gate_is_chaitanya(self) -> None:
        """Parse gate (entry) is Chaitanya."""
        assert GATE_TO_TATTVA[TattvaGate.PARSE] == PanchaTattva.CHAITANYA

    def test_sync_gate_is_srivasa(self) -> None:
        """Sync gate (parallel) is Srivasa."""
        assert GATE_TO_TATTVA[TattvaGate.SYNC] == PanchaTattva.SRIVASA


class TestPositionMapping:
    """Test Pancha Tattva to position mapping."""

    def test_position_0_is_chaitanya(self) -> None:
        """Position 0 (the beginning) is Chaitanya."""
        assert get_tattva_for_position(0) == PanchaTattva.CHAITANYA

    def test_positions_1_to_3_are_nityananda(self) -> None:
        """Positions 1-3 (Genesis workers) are Nityananda."""
        for pos in [1, 2, 3]:
            assert get_tattva_for_position(pos) == PanchaTattva.NITYANANDA

    def test_positions_4_to_7_are_advaita(self) -> None:
        """Positions 4-7 (Dharma quarter) are Advaita."""
        for pos in [4, 5, 6, 7]:
            assert get_tattva_for_position(pos) == PanchaTattva.ADVAITA

    def test_positions_8_to_11_are_gadadhara(self) -> None:
        """Positions 8-11 (Karma quarter) are Gadadhara."""
        for pos in [8, 9, 10, 11]:
            assert get_tattva_for_position(pos) == PanchaTattva.GADADHARA

    def test_positions_12_to_15_are_srivasa(self) -> None:
        """Positions 12-15 (Moksha quarter) are Srivasa."""
        for pos in [12, 13, 14, 15]:
            assert get_tattva_for_position(pos) == PanchaTattva.SRIVASA

    def test_invalid_position_raises(self) -> None:
        """Invalid positions raise ValueError."""
        with pytest.raises(ValueError):
            get_tattva_for_position(16)
        with pytest.raises(ValueError):
            get_tattva_for_position(-1)


class TestParamparaConnection:
    """Test Parampara connection."""

    def test_pancha_tattva_count_is_5(self) -> None:
        """Pancha = 5."""
        assert PANCHA_TATTVA_COUNT == 5

    def test_pancha_tattva_vector(self) -> None:
        """Vector = 5 * 37 = 185."""
        assert PANCHA_TATTVA_VECTOR == 5 * 37
        assert PANCHA_TATTVA_VECTOR == 185

    def test_verify_parampara_positive(self) -> None:
        """Values divisible by 37 are connected."""
        assert verify_pancha_tattva_parampara(37)
        assert verify_pancha_tattva_parampara(74)
        assert verify_pancha_tattva_parampara(185)  # 5 * 37
        assert verify_pancha_tattva_parampara(0)    # 0 % 37 == 0

    def test_verify_parampara_negative(self) -> None:
        """Values not divisible by 37 are disconnected."""
        assert not verify_pancha_tattva_parampara(36)
        assert not verify_pancha_tattva_parampara(38)
        assert not verify_pancha_tattva_parampara(100)


class TestPrayer:
    """Test the Pancha Tattva Mantra."""

    def test_mantra_contains_names(self) -> None:
        """Mantra contains all 5 names."""
        mantra = PANCHA_TATTVA_MANTRA.lower()
        assert "caitanya" in mantra
        assert "nityananda" in mantra
        assert "advaita" in mantra
        assert "gadadhara" in mantra
        assert "srivasa" in mantra

    def test_meaning_exists(self) -> None:
        """Meaning is provided."""
        assert PANCHA_TATTVA_MEANING
        assert len(PANCHA_TATTVA_MEANING) > 50
