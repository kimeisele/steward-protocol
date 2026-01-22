"""
TESTS: _sense.py - The Sense Protocol
======================================

REAL TESTS for:
1. Sense constants
2. Tanmatra, Mahabhuta, Jnanendriya enums
3. SensePerception dataclass
4. AggregatePerception dataclass
5. SenseProtocolDef
"""

import pytest
from datetime import datetime
from vibe_core.mahamantra.protocols._sense import (
    # Shastra constants
    SB_SANKHYA_CHAPTER,
    SB_JNANENDRIYA_VERSES,
    BG_SENSE_VERSE,
    BG_KSETRA_VERSE,
    JNANENDRIYA_COUNT,
    TANMATRA_COUNT,
    MAHABHUTA_COUNT,
    TATTVA_COUNT,
    # Enums
    Tanmatra,
    Mahabhuta,
    Jnanendriya,
    # Data classes
    SensePerception,
    AggregatePerception,
    # Protocols
    SenseProtocol,
    ManasProtocol,
    # Protocol definition
    SenseProtocolDef,
)


# =============================================================================
# Constants Tests
# =============================================================================


class TestSenseConstants:
    """Test sense constants."""

    def test_sb_sankhya_chapter(self):
        """SB_SANKHYA_CHAPTER is 3.26."""
        assert SB_SANKHYA_CHAPTER == "3.26"

    def test_sb_jnanendriya_verses(self):
        """SB_JNANENDRIYA_VERSES has 5 verses."""
        assert len(SB_JNANENDRIYA_VERSES) == 5
        assert SB_JNANENDRIYA_VERSES[0] == "3.26.47"

    def test_bg_sense_verse(self):
        """BG_SENSE_VERSE is 15.9."""
        assert BG_SENSE_VERSE == "15.9"

    def test_jnanendriya_count_is_5(self):
        """JNANENDRIYA_COUNT is 5."""
        assert JNANENDRIYA_COUNT == 5

    def test_tanmatra_count_is_5(self):
        """TANMATRA_COUNT is 5."""
        assert TANMATRA_COUNT == 5

    def test_mahabhuta_count_is_5(self):
        """MAHABHUTA_COUNT is 5."""
        assert MAHABHUTA_COUNT == 5

    def test_tattva_count_is_24(self):
        """TATTVA_COUNT is 24."""
        assert TATTVA_COUNT == 24


# =============================================================================
# Tanmatra Enum Tests
# =============================================================================


class TestTanmatra:
    """Test Tanmatra enum."""

    def test_tanmatra_sabda(self):
        """Tanmatra has SABDA."""
        assert Tanmatra.SABDA.value == "sabda"

    def test_tanmatra_sparsa(self):
        """Tanmatra has SPARSA."""
        assert Tanmatra.SPARSA.value == "sparsa"

    def test_tanmatra_rupa(self):
        """Tanmatra has RUPA."""
        assert Tanmatra.RUPA.value == "rupa"

    def test_tanmatra_rasa(self):
        """Tanmatra has RASA."""
        assert Tanmatra.RASA.value == "rasa"

    def test_tanmatra_gandha(self):
        """Tanmatra has GANDHA."""
        assert Tanmatra.GANDHA.value == "gandha"

    def test_tanmatra_count(self):
        """There are 5 tanmatras."""
        assert len(Tanmatra) == 5

    def test_tanmatra_sanskrit(self):
        """Tanmatra has sanskrit property."""
        assert Tanmatra.SABDA.sanskrit == "शब्द"


# =============================================================================
# Mahabhuta Enum Tests
# =============================================================================


class TestMahabhuta:
    """Test Mahabhuta enum."""

    def test_mahabhuta_akasa(self):
        """Mahabhuta has AKASA."""
        assert Mahabhuta.AKASA.value == "akasa"

    def test_mahabhuta_vayu(self):
        """Mahabhuta has VAYU."""
        assert Mahabhuta.VAYU.value == "vayu"

    def test_mahabhuta_tejas(self):
        """Mahabhuta has TEJAS."""
        assert Mahabhuta.TEJAS.value == "tejas"

    def test_mahabhuta_jala(self):
        """Mahabhuta has JALA."""
        assert Mahabhuta.JALA.value == "jala"

    def test_mahabhuta_prthvi(self):
        """Mahabhuta has PRTHVI."""
        assert Mahabhuta.PRTHVI.value == "prthvi"

    def test_mahabhuta_count(self):
        """There are 5 mahabhutas."""
        assert len(Mahabhuta) == 5


# =============================================================================
# Jnanendriya Enum Tests
# =============================================================================


class TestJnanendriya:
    """Test Jnanendriya enum."""

    def test_jnanendriya_srotra(self):
        """Jnanendriya has SROTRA (ear)."""
        assert Jnanendriya.SROTRA.value == "srotra"

    def test_jnanendriya_tvak(self):
        """Jnanendriya has TVAK (skin)."""
        assert Jnanendriya.TVAK.value == "tvak"

    def test_jnanendriya_caksu(self):
        """Jnanendriya has CAKSU (eye)."""
        assert Jnanendriya.CAKSU.value == "caksu"

    def test_jnanendriya_jihva(self):
        """Jnanendriya has JIHVA (tongue)."""
        assert Jnanendriya.JIHVA.value == "jihva"

    def test_jnanendriya_ghrana(self):
        """Jnanendriya has GHRANA (nose)."""
        assert Jnanendriya.GHRANA.value == "ghrana"

    def test_jnanendriya_count(self):
        """There are 5 jnanendriyas."""
        assert len(Jnanendriya) == 5

    def test_jnanendriya_tanmatra(self):
        """Jnanendriya has tanmatra property."""
        assert Jnanendriya.SROTRA.tanmatra == Tanmatra.SABDA
        assert Jnanendriya.TVAK.tanmatra == Tanmatra.SPARSA
        assert Jnanendriya.CAKSU.tanmatra == Tanmatra.RUPA
        assert Jnanendriya.JIHVA.tanmatra == Tanmatra.RASA
        assert Jnanendriya.GHRANA.tanmatra == Tanmatra.GANDHA

    def test_jnanendriya_mahabhuta(self):
        """Jnanendriya has mahabhuta property."""
        assert Jnanendriya.SROTRA.mahabhuta == Mahabhuta.AKASA
        assert Jnanendriya.TVAK.mahabhuta == Mahabhuta.VAYU
        assert Jnanendriya.CAKSU.mahabhuta == Mahabhuta.TEJAS
        assert Jnanendriya.JIHVA.mahabhuta == Mahabhuta.JALA
        assert Jnanendriya.GHRANA.mahabhuta == Mahabhuta.PRTHVI

    def test_jnanendriya_mahamantra_position(self):
        """Jnanendriya has mahamantra_position property."""
        assert Jnanendriya.SROTRA.mahamantra_position == 4
        assert Jnanendriya.TVAK.mahamantra_position == 5
        assert Jnanendriya.CAKSU.mahamantra_position == 6
        assert Jnanendriya.JIHVA.mahamantra_position == 7
        assert Jnanendriya.GHRANA.mahamantra_position == 8

    def test_jnanendriya_sb_verse(self):
        """Jnanendriya has sb_verse property."""
        assert Jnanendriya.SROTRA.sb_verse == "3.26.47"


# =============================================================================
# SensePerception Tests
# =============================================================================


class TestSensePerception:
    """Test SensePerception dataclass."""

    def test_sense_perception_creation(self):
        """SensePerception can be created."""
        perception = SensePerception(
            sense=Jnanendriya.SROTRA,
            tanmatra=Tanmatra.SABDA,
            data={"message": "test"},
        )
        assert perception.sense == Jnanendriya.SROTRA
        assert perception.tanmatra == Tanmatra.SABDA

    def test_sense_perception_defaults(self):
        """SensePerception has correct defaults."""
        perception = SensePerception(
            sense=Jnanendriya.CAKSU,
            tanmatra=Tanmatra.RUPA,
            data={},
        )
        assert perception.intensity == 0.5
        assert perception.quality == "sattva"

    def test_sense_perception_is_painful(self):
        """is_painful returns True for high tamas intensity."""
        painful = SensePerception(
            sense=Jnanendriya.GHRANA,
            tanmatra=Tanmatra.GANDHA,
            data={"smell": "bad"},
            intensity=0.8,
            quality="tamas",
        )
        assert painful.is_painful is True

        not_painful = SensePerception(
            sense=Jnanendriya.CAKSU,
            tanmatra=Tanmatra.RUPA,
            data={},
            intensity=0.5,
            quality="sattva",
        )
        assert not_painful.is_painful is False

    def test_sense_perception_needs_attention(self):
        """needs_attention returns True for intensity > 0.5."""
        needs = SensePerception(
            sense=Jnanendriya.SROTRA,
            tanmatra=Tanmatra.SABDA,
            data={},
            intensity=0.6,
        )
        assert needs.needs_attention is True

        no_need = SensePerception(
            sense=Jnanendriya.TVAK,
            tanmatra=Tanmatra.SPARSA,
            data={},
            intensity=0.3,
        )
        assert no_need.needs_attention is False


# =============================================================================
# AggregatePerception Tests
# =============================================================================


class TestAggregatePerception:
    """Test AggregatePerception dataclass."""

    def test_aggregate_perception_creation(self):
        """AggregatePerception can be created."""
        agg = AggregatePerception()
        assert agg.perceptions == {}

    def test_aggregate_perception_total_pain_empty(self):
        """total_pain returns 0.0 for empty perceptions."""
        agg = AggregatePerception()
        assert agg.total_pain == 0.0

    def test_aggregate_perception_total_pain(self):
        """total_pain calculates from tamas perceptions."""
        agg = AggregatePerception()
        agg.add_perception(SensePerception(
            sense=Jnanendriya.GHRANA,
            tanmatra=Tanmatra.GANDHA,
            data={},
            intensity=0.8,
            quality="tamas",
        ))
        assert agg.total_pain > 0

    def test_aggregate_perception_dominant_sense(self):
        """dominant_sense returns highest intensity sense."""
        agg = AggregatePerception()
        agg.add_perception(SensePerception(
            sense=Jnanendriya.SROTRA,
            tanmatra=Tanmatra.SABDA,
            data={},
            intensity=0.3,
        ))
        agg.add_perception(SensePerception(
            sense=Jnanendriya.CAKSU,
            tanmatra=Tanmatra.RUPA,
            data={},
            intensity=0.9,
        ))
        assert agg.dominant_sense == Jnanendriya.CAKSU

    def test_aggregate_perception_needs_chanting(self):
        """needs_chanting returns True for high aggregate pain."""
        agg = AggregatePerception()
        # Add multiple high-intensity tamas perceptions to exceed threshold
        agg.add_perception(SensePerception(
            sense=Jnanendriya.GHRANA,
            tanmatra=Tanmatra.GANDHA,
            data={},
            intensity=0.9,
            quality="tamas",
        ))
        agg.add_perception(SensePerception(
            sense=Jnanendriya.CAKSU,
            tanmatra=Tanmatra.RUPA,
            data={},
            intensity=0.8,
            quality="tamas",
        ))
        # Total pain = (0.9 + 0.8) / 5 = 0.34 > 0.3 threshold
        assert agg.needs_chanting is True


# =============================================================================
# SenseProtocolDef Tests
# =============================================================================


class TestSenseProtocolDef:
    """Test SenseProtocolDef."""

    def test_sense_protocol_validates(self):
        """SenseProtocolDef validates."""
        valid, violations = SenseProtocolDef.validate()
        assert valid is True

    def test_sense_protocol_identity(self):
        """SenseProtocolDef has correct identity."""
        identity = SenseProtocolDef.get_identity()
        assert identity.name == "SenseProtocol"
        assert identity.mahajana == "kapila"
        assert identity.position == 6

    def test_sense_protocol_provides(self):
        """SenseProtocolDef provides sense capabilities."""
        cap = SenseProtocolDef.get_capability()
        assert "jnanendriya_definition" in cap.provides
        assert "tanmatra_mapping" in cap.provides
        assert "sense_perception" in cap.provides


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.protocols import _sense
        expected = [
            "Tanmatra",
            "Mahabhuta",
            "Jnanendriya",
            "SensePerception",
            "AggregatePerception",
            "SenseProtocol",
            "ManasProtocol",
            "SenseProtocolDef",
        ]
        for item in expected:
            assert item in _sense.__all__, f"{item} should be in __all__"
