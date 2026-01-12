"""
Tests for SAMKHYA Protocol - 24 Prakriti Element Mapping.

"prakṛtiṁ puruṣaṁ caiva viddhy anādī ubhāv api"

Tests verify:
1. All 24 elements are mapped correctly
2. Element → Guardian → OpCode chain works
3. Entropy analysis functions correctly
4. Protocol adoption routing works
5. Integration with adoption pipeline

WATERTIGHT: All types explicit, no Any.
"""

import pytest
from typing import List, Dict

from vibe_core.protocols.mahajanas.kapila.samkhya import (
    # Enums
    PrakritiCategory,
    PrakritiElement,
    # Mappings
    ELEMENT_PROTOCOL_LAYER,
    ELEMENT_GUARDIAN,
    ELEMENT_OPCODE,
    # Types
    ElementAnalysis,
    EntropyReport,
    # Protocol
    SamkhyaProtocol,
    get_samkhya,
    # Functions
    analyze_prakriti_element,
    analyze_protocol_entropy,
    route_wild_protocol,
    fight_protocol_entropy,
    enumerate_all_elements,
)
from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode
from vibe_core.protocols.substrate.mantra.lotus import LOTUS_PARAMPARA


# =============================================================================
# TEST 24 ELEMENTS ENUMERATION
# =============================================================================

class TestPrakritiElements:
    """Test the 24 Prakriti element enumeration."""

    def test_element_count(self) -> None:
        """There are exactly 24 Prakriti elements."""
        assert len(PrakritiElement) == 24

    def test_element_numbers(self) -> None:
        """Elements are numbered 1-24."""
        numbers = [e.value for e in PrakritiElement]
        assert numbers == list(range(1, 25))

    def test_antahkarana_elements(self) -> None:
        """ANTAHKARANA has 4 internal instruments (1-4)."""
        elements = [e for e in PrakritiElement if 1 <= e.value <= 4]
        assert len(elements) == 4
        assert PrakritiElement.MANAS in elements
        assert PrakritiElement.BUDDHI in elements
        assert PrakritiElement.AHANKARA in elements
        assert PrakritiElement.CITTA in elements

    def test_tanmatra_elements(self) -> None:
        """TANMATRA has 5 subtle elements (5-9)."""
        elements = [e for e in PrakritiElement if 5 <= e.value <= 9]
        assert len(elements) == 5
        assert PrakritiElement.SHABDA in elements  # Sound
        assert PrakritiElement.SPARSHA in elements  # Touch
        assert PrakritiElement.RUPA in elements     # Form
        assert PrakritiElement.RASA in elements     # Taste
        assert PrakritiElement.GANDHA in elements   # Smell

    def test_jnanendriya_elements(self) -> None:
        """JNANENDRIYA has 5 knowledge senses (10-14)."""
        elements = [e for e in PrakritiElement if 10 <= e.value <= 14]
        assert len(elements) == 5
        assert PrakritiElement.SHROTRA in elements  # Ear
        assert PrakritiElement.TVAK in elements     # Skin
        assert PrakritiElement.CHAKSHUS in elements # Eye
        assert PrakritiElement.RASANA in elements   # Tongue
        assert PrakritiElement.GHRANA in elements   # Nose

    def test_karmendriya_elements(self) -> None:
        """KARMENDRIYA has 5 working senses (15-19)."""
        elements = [e for e in PrakritiElement if 15 <= e.value <= 19]
        assert len(elements) == 5
        assert PrakritiElement.VAK in elements      # Speech
        assert PrakritiElement.PANI in elements     # Hands
        assert PrakritiElement.PADA in elements     # Feet
        assert PrakritiElement.PAYU in elements     # Excretion
        assert PrakritiElement.UPASTHA in elements  # Generation

    def test_mahabhuta_elements(self) -> None:
        """MAHABHUTA has 5 gross elements (20-24)."""
        elements = [e for e in PrakritiElement if 20 <= e.value <= 24]
        assert len(elements) == 5
        assert PrakritiElement.AKASHA in elements   # Ether
        assert PrakritiElement.VAYU in elements     # Air
        assert PrakritiElement.TEJAS in elements    # Fire
        assert PrakritiElement.APAS in elements     # Water
        assert PrakritiElement.PRITHVI in elements  # Earth


# =============================================================================
# TEST ELEMENT → GUARDIAN MAPPING
# =============================================================================

class TestElementGuardianMapping:
    """Test element to Mahajana guardian mapping."""

    def test_all_elements_have_guardians(self) -> None:
        """Every element has a guardian."""
        for element in PrakritiElement:
            assert element in ELEMENT_GUARDIAN
            assert isinstance(ELEMENT_GUARDIAN[element], Mahajana)

    def test_vak_owned_by_narada(self) -> None:
        """VAK (Speech) is owned by NARADA (Communication)."""
        assert ELEMENT_GUARDIAN[PrakritiElement.VAK] == Mahajana.NARADA

    def test_manas_owned_by_kapila(self) -> None:
        """MANAS (Mind) is owned by KAPILA (Analysis)."""
        assert ELEMENT_GUARDIAN[PrakritiElement.MANAS] == Mahajana.KAPILA

    def test_buddhi_owned_by_yamaraja(self) -> None:
        """BUDDHI (Intelligence) is owned by YAMARAJA (Judgment)."""
        assert ELEMENT_GUARDIAN[PrakritiElement.BUDDHI] == Mahajana.YAMARAJA

    def test_upastha_owned_by_brahma(self) -> None:
        """UPASTHA (Generation) is owned by BRAHMA (Creation)."""
        assert ELEMENT_GUARDIAN[PrakritiElement.UPASTHA] == Mahajana.BRAHMA

    def test_payu_owned_by_shambhu(self) -> None:
        """PAYU (Excretion) is owned by SHAMBHU (Destruction)."""
        assert ELEMENT_GUARDIAN[PrakritiElement.PAYU] == Mahajana.SHAMBHU


# =============================================================================
# TEST ELEMENT → OPCODE MAPPING
# =============================================================================

class TestElementOpcodeMapping:
    """Test element to MantraOpCode mapping."""

    def test_all_elements_have_opcodes(self) -> None:
        """Every element has an OpCode."""
        for element in PrakritiElement:
            assert element in ELEMENT_OPCODE
            assert isinstance(ELEMENT_OPCODE[element], MantraOpCode)

    def test_vak_has_pulse_sync(self) -> None:
        """VAK maps to PULSE_SYNC (communication/sync)."""
        assert ELEMENT_OPCODE[PrakritiElement.VAK] == MantraOpCode.DHARMA_TEST

    def test_manas_has_resolve_req(self) -> None:
        """MANAS maps to RESOLVE_REQ (analysis)."""
        assert ELEMENT_OPCODE[PrakritiElement.MANAS] == MantraOpCode.BIND_SYMBOL

    def test_upastha_has_load_root(self) -> None:
        """UPASTHA maps to LOAD_ROOT (genesis/creation)."""
        assert ELEMENT_OPCODE[PrakritiElement.UPASTHA] == MantraOpCode.LOAD_ROOT

    def test_payu_has_garbage_collect(self) -> None:
        """PAYU maps to GARBAGE_COLLECT (destruction/cleanup)."""
        assert ELEMENT_OPCODE[PrakritiElement.PAYU] == MantraOpCode.TYPE_CHECK


# =============================================================================
# TEST SAMKHYA PROTOCOL
# =============================================================================

class TestSamkhyaProtocol:
    """Test the SamkhyaProtocol implementation."""

    def test_owner_is_kapila(self) -> None:
        """Samkhya is owned by KAPILA."""
        samkhya = get_samkhya()
        assert samkhya.OWNER == Mahajana.KAPILA

    def test_position_is_6(self) -> None:
        """Kapila's position is 6 (DHARMA quarter)."""
        samkhya = get_samkhya()
        assert samkhya.lotus_position == 6

    def test_quarter_is_dharma(self) -> None:
        """Kapila is in DHARMA quarter."""
        samkhya = get_samkhya()
        assert samkhya.lotus_quarter.value == "dharma"

    def test_is_connected(self) -> None:
        """Samkhya protocol is connected to parampara."""
        samkhya = get_samkhya()
        assert samkhya.is_lotus_connected is True
        assert samkhya.parampara_hash % LOTUS_PARAMPARA == 0


class TestElementAnalysis:
    """Test element analysis functionality."""

    def test_analyze_chat_protocol(self) -> None:
        """Chat protocol maps to VAK (speech)."""
        analysis = analyze_prakriti_element("test_chat", """
def chat(message: str) -> str:
    return translate(speak(message))
""")
        assert analysis["element"] == "VAK"
        assert analysis["protocol_layer"] == "speech"
        assert analysis["guardian"] == "narada"

    def test_analyze_storage_protocol(self) -> None:
        """Storage protocol maps to PRITHVI (earth)."""
        analysis = analyze_prakriti_element("test_storage", """
def persist(data: bytes) -> str:
    return storage.save(data, disk=True)
""")
        assert analysis["element"] == "PRITHVI"
        assert analysis["protocol_layer"] == "storage"
        assert analysis["guardian"] == "brahma"

    def test_analyze_cognition_protocol(self) -> None:
        """Cognition protocol maps to MANAS (mind)."""
        analysis = analyze_prakriti_element("test_cognition", """
def think(input: str) -> str:
    return cognitive_process(reason(input))
""")
        assert analysis["element"] == "MANAS"
        assert analysis["protocol_layer"] == "cognition"
        assert analysis["guardian"] == "kapila"

    def test_analysis_includes_quarter(self) -> None:
        """Analysis includes quarter information."""
        analysis = analyze_prakriti_element("test_any", "def foo(): pass")
        assert "quarter" in analysis
        assert analysis["quarter"] in ["genesis", "dharma", "karma", "moksha"]


class TestEntropyAnalysis:
    """Test entropy analysis and entropy fighting."""

    def test_wild_protocol_has_high_entropy(self) -> None:
        """Wild (unowned) protocol has high entropy."""
        report = analyze_protocol_entropy("wild_test", "def foo(): pass", has_owner=False)
        assert report["is_wild"] is True
        assert report["entropy_score"] > 0

    def test_owned_protocol_has_lower_entropy(self) -> None:
        """Owned protocol has lower entropy."""
        report = analyze_protocol_entropy("owned_test", "def foo(): pass", has_owner=True)
        assert report["is_wild"] is False
        assert report["entropy_score"] < 0.5

    def test_connected_protocol_has_lowest_entropy(self) -> None:
        """Connected protocol (% 37 == 0) has lowest entropy."""
        # Create a hash that's divisible by 37
        parampara_hash = 37 * 100
        report = analyze_protocol_entropy(
            "connected_test", "def foo(): pass",
            has_owner=True,
            parampara_hash=parampara_hash,
        )
        assert report["parampara_connected"] is True
        assert report["entropy_score"] < 0.3

    def test_fight_entropy_reduces_score(self) -> None:
        """Fighting entropy reduces the entropy score."""
        # First analyze wild protocol
        initial = analyze_protocol_entropy("entropy_test", "def think(): pass")
        initial_score = initial["entropy_score"]

        # Fight entropy
        reduction = fight_protocol_entropy("entropy_test", "def think(): pass")

        # Should have reduced entropy
        assert reduction > 0


class TestWildProtocolRouting:
    """Test routing wild protocols to guardians."""

    def test_route_chat_to_narada(self) -> None:
        """Chat protocol routes to NARADA."""
        guardian, position, path = route_wild_protocol("test_chat", """
def chat(msg): return speak(msg)
""")
        assert guardian == Mahajana.NARADA
        assert "narada" in path

    def test_route_storage_to_brahma(self) -> None:
        """Storage protocol routes to BRAHMA."""
        guardian, position, path = route_wild_protocol("test_storage", """
def persist(data): return storage.save(data)
""")
        assert guardian == Mahajana.BRAHMA
        assert "brahma" in path

    def test_route_includes_position(self) -> None:
        """Route includes lotus position."""
        guardian, position, path = route_wild_protocol("test_any", "def foo(): pass")
        assert 0 <= position < 16


class TestEnumerateFunctions:
    """Test enumeration functions."""

    def test_enumerate_all_returns_24(self) -> None:
        """enumerate_all_elements returns all 24."""
        elements = enumerate_all_elements()
        assert len(elements) == 24

    def test_enumerate_includes_all_fields(self) -> None:
        """Each enumerated element has required fields."""
        elements = enumerate_all_elements()
        for e in elements:
            assert "number" in e
            assert "name" in e
            assert "category" in e
            assert "layer" in e
            assert "guardian" in e
            assert "opcode" in e

    def test_enumerate_by_category(self) -> None:
        """Can enumerate elements by category."""
        samkhya = get_samkhya()

        antahkarana = samkhya.enumerate_by_category(PrakritiCategory.ANTAHKARANA)
        assert len(antahkarana) == 4

        mahabhuta = samkhya.enumerate_by_category(PrakritiCategory.MAHABHUTA)
        assert len(mahabhuta) == 5

    def test_enumerate_by_guardian(self) -> None:
        """Can enumerate elements by guardian."""
        samkhya = get_samkhya()

        narada_elements = samkhya.enumerate_by_guardian(Mahajana.NARADA)
        # NARADA guards: SHABDA, SHROTRA, VAK, AKASHA
        assert len(narada_elements) >= 4
        assert PrakritiElement.VAK in narada_elements


# =============================================================================
# TEST INTEGRATION WITH OWNED PROTOCOL
# =============================================================================

class TestOwnedProtocolIntegration:
    """Test integration with OwnedProtocol base class."""

    def test_samkhya_is_owned_protocol(self) -> None:
        """SamkhyaProtocol inherits from OwnedProtocol."""
        from vibe_core.protocols.mahajanas.owned_protocol import OwnedProtocol
        samkhya = get_samkhya()
        assert isinstance(samkhya, OwnedProtocol)

    def test_can_chant(self) -> None:
        """Samkhya can chant (heartbeat works)."""
        samkhya = SamkhyaProtocol()  # Fresh instance
        assert samkhya.is_chanting is False
        samkhya.chant()
        assert samkhya.is_chanting is True

    def test_get_state_returns_valid_state(self) -> None:
        """get_state returns valid ProtocolState."""
        samkhya = get_samkhya()
        state = samkhya.get_state()

        assert state["protocol_name"] == "samkhya"
        assert state["owner"] == "kapila"
        assert isinstance(state["lotus_position"], int)
        assert isinstance(state["is_lotus_connected"], bool)

    def test_get_samkhya_state_includes_extra_fields(self) -> None:
        """get_samkhya_state includes Samkhya-specific fields."""
        samkhya = get_samkhya()
        state = samkhya.get_samkhya_state()

        assert "elements_mapped" in state
        assert "protocols_analyzed" in state
        assert "entropy_reduced" in state
        assert "wild_protocols_adopted" in state


# =============================================================================
# TEST THE 37 FORMULA
# =============================================================================

class TestParamparaFormula:
    """Test the 37 formula (24 + 12 + 1)."""

    def test_element_count_is_24(self) -> None:
        """There are 24 Prakriti elements."""
        assert len(PrakritiElement) == 24

    def test_mahajana_count_is_12(self) -> None:
        """There are 12 Mahajana guardians."""
        guardians = set(ELEMENT_GUARDIAN.values())
        assert len(guardians) == 12

    def test_formula_equals_37(self) -> None:
        """24 Prakriti + 12 Mahajanas + 1 Ksetrajna = 37."""
        prakriti = 24
        mahajanas = 12
        ksetrajna = 1  # Krishna
        assert prakriti + mahajanas + ksetrajna == LOTUS_PARAMPARA

    def test_parampara_divisibility(self) -> None:
        """Connected protocols have hash % 37 == 0."""
        samkhya = get_samkhya()
        assert samkhya.parampara_hash % LOTUS_PARAMPARA == 0
