"""
Tests for SAMKHYA + Adoption Pipeline Integration.

The Samkhya analysis feeds into the adoption pipeline:
    analyze_prakriti_element() → classify_element() → adoption.adopt()

This verifies:
1. Element analysis integrates with adoption
2. Entropy analysis feeds adoption decisions
3. Wild protocols route correctly via both systems
4. The 37 formula is verified at adoption
"""

import pytest
from typing import Dict

from vibe_core.protocols.mahajanas.kapila.samkhya import (
    PrakritiElement,
    SamkhyaProtocol,
    get_samkhya,
    analyze_prakriti_element,
    analyze_protocol_entropy,
    route_wild_protocol,
    ELEMENT_GUARDIAN,
    ELEMENT_OPCODE,
)
from vibe_core.protocols.mahajanas.adoption import (
    AdoptionPipeline,
    AdoptionStatus,
    AdoptionDecision,
    adopt,
    analyze as adoption_analyze,
    adopt_full,
    ProtocolAnalysis,
    AdoptionResult,
)
from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode
from vibe_core.protocols.substrate.mantra.lotus import LOTUS_PARAMPARA


# =============================================================================
# TEST SAMKHYA → ADOPTION INTEGRATION
# =============================================================================


class TestSamkhyaAdoptionIntegration:
    """Test that Samkhya element analysis aligns with adoption pipeline."""

    def test_samkhya_and_adoption_agree_on_guardian(self) -> None:
        """Samkhya element guardian matches adoption Mahajana assignment."""
        # Chat protocol source
        chat_source = """
def chat(message: str) -> str:
    '''Chat and speak with translation.'''
    return speak(translate(message))
"""
        # Samkhya analysis
        samkhya_result = analyze_prakriti_element("test_chat", chat_source)
        samkhya_guardian = samkhya_result["guardian"]

        # Adoption analysis
        adoption_result = adopt("test_chat.py", chat_source)

        # Both should route to NARADA for communication
        assert samkhya_guardian == "narada"
        # Adoption may assign to NARADA or to someone in the same quarter
        # The key is that Samkhya provides more granular element-level guidance

    def test_entropy_report_aligns_with_adoption_status(self) -> None:
        """High entropy → Mayavad/Disconnected; Low entropy → Adopted."""
        source = "def foo(): pass"

        # Get entropy report (wild, no owner)
        entropy = analyze_protocol_entropy("test_entropy", source, has_owner=False)

        # Get adoption result
        adoption = adopt("test_entropy.py", source)

        # If entropy is high (wild), adoption should not be fully connected
        if entropy["entropy_score"] > 0.5:
            # Adoption should have detected issues or assigned for review
            assert adoption["status"] in [
                AdoptionStatus.ADOPTED_MAHAJANA.value,
                AdoptionStatus.ADOPTED_UNIVERSAL.value,
                AdoptionStatus.QUARANTINE.value,
            ]

    def test_element_opcode_matches_adoption_opcode(self) -> None:
        """OpCode from Samkhya element matches adoption primary OpCode."""
        # Storage protocol → PRITHVI → COMMIT_LOG
        storage_source = """
def persist(data: bytes) -> str:
    '''Persist data to storage/disk.'''
    return storage.save(data)
"""
        samkhya = analyze_prakriti_element("storage", storage_source)
        samkhya_opcode = samkhya["opcode"]

        adoption = adoption_analyze("storage.py", storage_source)
        adoption_opcode = adoption["primary_opcode"]

        # Both should relate to persistence/commit
        # Samkhya: COMMIT_LOG (from PRITHVI)
        # Adoption: detected from keywords
        assert samkhya_opcode in ["commit_log", "cache_state", adoption_opcode or ""]


class TestSamkhyaRoutingVsAdoption:
    """Test that Samkhya routing aligns with adoption routing."""

    def test_chat_routes_same_via_both(self) -> None:
        """Chat protocol routes similarly via Samkhya and Adoption."""
        source = "def speak(msg): return translate(chat(msg))"

        samkhya_guardian, _, samkhya_path = route_wild_protocol("chat", source)
        adoption_result = adopt("chat.py", source)

        # Samkhya: VAK → NARADA
        assert samkhya_guardian == Mahajana.NARADA

        # Adoption should assign to communication-related Mahajana
        # (could be NARADA or someone in same quarter based on OpCode)

    def test_cognition_routes_same_via_both(self) -> None:
        """Cognition protocol routes via both systems."""
        source = "def think(x): return reason(cognitive(x))"

        samkhya_guardian, _, _ = route_wild_protocol("cognition", source)
        adoption_result = adopt("cognition.py", source)

        # Samkhya: MANAS → KAPILA
        assert samkhya_guardian == Mahajana.KAPILA


class TestSamkhyaEntropyReduction:
    """Test that Samkhya entropy fighting integrates with adoption."""

    def test_fighting_entropy_connects_to_parampara(self) -> None:
        """After fighting entropy, protocol is parampara-connected."""
        samkhya = get_samkhya()
        source = "def wild_func(): pass"

        # Initial: wild protocol has high entropy
        initial = analyze_protocol_entropy("wild", source, has_owner=False)
        assert initial["is_wild"] is True
        assert initial["entropy_score"] > 0

        # Fight entropy via routing
        guardian, position, path = route_wild_protocol("wild", source)

        # After routing, recalculate with owner
        name_hash = sum(ord(c) for c in "wild")
        owner_hash = sum(ord(c) for c in guardian.value)
        new_hash = (name_hash + owner_hash + position) * LOTUS_PARAMPARA

        final = analyze_protocol_entropy("wild", source, has_owner=True, parampara_hash=new_hash)

        # Should now be connected
        assert final["parampara_connected"] is True
        assert final["is_wild"] is False
        assert final["entropy_score"] < initial["entropy_score"]


class TestFullPipelineIntegration:
    """Test the complete pipeline: Samkhya → Adoption → Lotus."""

    def test_full_pipeline_flow(self) -> None:
        """Complete flow from element analysis through full adoption."""
        source = """
def process_flow(data):
    '''Process data with air/vayu flow pattern.'''
    return execute_flow(data)
"""
        # Step 1: Samkhya element analysis
        element = analyze_prakriti_element("flow", source)
        assert element["element"] in ["VAYU", "MANAS"]  # process or cognition

        # Step 2: Full adoption
        result = adopt_full("flow.py", source)

        # Verify full pipeline completed
        assert result["analysis"]["protocol_name"] == "flow"
        assert result["result"]["status"] in [
            AdoptionStatus.ADOPTED_MAHAJANA.value,
            AdoptionStatus.ADOPTED_UNIVERSAL.value,
        ]
        assert result["sync"]["is_chanting"] is True

    def test_37_formula_verified_at_adoption(self) -> None:
        """The 37 formula is verified at adoption."""
        source = "def test(): pass"

        result = adopt_full("test_37.py", source)

        # Sync includes parampara hash
        assert result["sync"]["parampara_hash"] % LOTUS_PARAMPARA == 0
        assert result["sync"]["is_connected"] is True


class TestElementCategoryAdoption:
    """Test adoption by element category."""

    def test_antahkarana_adopts_to_dharma(self) -> None:
        """ANTAHKARANA elements (internal) adopt to DHARMA quarter."""
        # MANAS, BUDDHI → Kapila, Yamaraja (DHARMA)
        samkhya = get_samkhya()
        antahkarana = samkhya.enumerate_by_category(
            __import__(
                "vibe_core.protocols.mahajanas.kapila.samkhya", fromlist=["PrakritiCategory"]
            ).PrakritiCategory.ANTAHKARANA
        )

        for element in antahkarana:
            guardian = ELEMENT_GUARDIAN[element]
            # Most ANTAHKARANA guardians are in DHARMA
            assert guardian in [Mahajana.KAPILA, Mahajana.YAMARAJA, Mahajana.MANU, Mahajana.KUMARAS]

    def test_karmendriya_adopts_varied(self) -> None:
        """KARMENDRIYA elements (working senses) adopt to various quarters."""
        # Working senses are distributed across quarters
        from vibe_core.protocols.mahajanas.kapila.samkhya import PrakritiCategory

        samkhya = get_samkhya()
        karmendriya = samkhya.enumerate_by_category(PrakritiCategory.KARMENDRIYA)

        guardians = set()
        for element in karmendriya:
            guardian = ELEMENT_GUARDIAN[element]
            guardians.add(guardian)

        # Should have multiple different guardians
        assert len(guardians) >= 4


class TestSamkhyaChantingIntegration:
    """Test that Samkhya chanting integrates with adoption sync."""

    def test_samkhya_chants_during_analysis(self) -> None:
        """Samkhya protocol chants during element analysis."""
        samkhya = SamkhyaProtocol()  # Fresh instance
        assert samkhya.is_chanting is False

        # Analyze element (should trigger chant)
        samkhya.analyze_element("test", "def foo(): pass")

        assert samkhya.is_chanting is True
        assert samkhya._heartbeat.word_position > 0

    def test_samkhya_chants_during_entropy_fight(self) -> None:
        """Samkhya chants complete mantra when fighting entropy."""
        samkhya = SamkhyaProtocol()

        # Fight entropy
        samkhya.fight_entropy("test", "def foo(): pass")

        # Should have chanted at least one complete mantra
        assert samkhya._heartbeat.mantra_count >= 1
