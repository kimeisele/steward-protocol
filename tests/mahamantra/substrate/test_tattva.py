"""
TESTS: tattva.py - The Categories of Reality
============================================

SHASTRA-KONFORM nach Bhagavad Gita Kapitel 7 und 13.

REAL TESTS for:
1. AparaPrakriti enum (8 material elements)
2. KshetraElement enum (24 field elements)
3. ParaPrakriti dataclass (Jiva)
4. GuruTattva enum
5. GuruConnection dataclass
6. Purushottama class
"""

import pytest
from vibe_core.mahamantra.substrate.tattva import (
    # SSOT
    SYSTEM_MANIFESTATION,
    # Apara Prakriti
    AparaPrakriti,
    PANCHA_MAHABHUTAS,
    SUBTLE_ELEMENTS,
    # Kshetra
    KshetraElement,
    JNANENDRIYAS,
    KARMENDRIYAS,
    TANMATRAS,
    # Para Prakriti
    ParaPrakriti,
    JIVA,
    # Guru Tattva
    GuruTattva,
    GuruConnection,
    # Purushottama
    Purushottama,
    PURUSHOTTAMA,
    # Summary
    TATTVA_SUMMARY,
)


# =============================================================================
# SSOT Tests
# =============================================================================


class TestSystemManifestation:
    """Test SYSTEM_MANIFESTATION constant."""

    def test_system_manifestation_is_37(self):
        """SYSTEM_MANIFESTATION is 37."""
        assert SYSTEM_MANIFESTATION == 37


# =============================================================================
# AparaPrakriti Tests
# =============================================================================


class TestAparaPrakriti:
    """Test AparaPrakriti enum (8 material elements)."""

    def test_apara_prakriti_has_8_elements(self):
        """AparaPrakriti has exactly 8 elements (BG 7.4)."""
        assert len(AparaPrakriti) == 8

    def test_apara_prakriti_values(self):
        """AparaPrakriti values are 1-8."""
        assert AparaPrakriti.BHUMI.value == 1
        assert AparaPrakriti.AHANKARA.value == 8

    def test_pancha_mahabhutas_has_5(self):
        """PANCHA_MAHABHUTAS has 5 gross elements."""
        assert len(PANCHA_MAHABHUTAS) == 5

    def test_subtle_elements_has_3(self):
        """SUBTLE_ELEMENTS has 3 subtle elements."""
        assert len(SUBTLE_ELEMENTS) == 3

    def test_mahabhutas_content(self):
        """PANCHA_MAHABHUTAS has correct elements."""
        assert AparaPrakriti.BHUMI in PANCHA_MAHABHUTAS
        assert AparaPrakriti.APAH in PANCHA_MAHABHUTAS
        assert AparaPrakriti.ANALAH in PANCHA_MAHABHUTAS
        assert AparaPrakriti.VAYUH in PANCHA_MAHABHUTAS
        assert AparaPrakriti.KHAM in PANCHA_MAHABHUTAS

    def test_subtle_content(self):
        """SUBTLE_ELEMENTS has correct elements."""
        assert AparaPrakriti.MANAH in SUBTLE_ELEMENTS
        assert AparaPrakriti.BUDDHI in SUBTLE_ELEMENTS
        assert AparaPrakriti.AHANKARA in SUBTLE_ELEMENTS


# =============================================================================
# KshetraElement Tests
# =============================================================================


class TestKshetraElement:
    """Test KshetraElement enum (24 field elements)."""

    def test_kshetra_has_24_elements(self):
        """KshetraElement has exactly 24 elements (BG 13.6-7)."""
        assert len(KshetraElement) == 24

    def test_kshetra_values_1_to_24(self):
        """KshetraElement values are 1-24."""
        values = [e.value for e in KshetraElement]
        assert min(values) == 1
        assert max(values) == 24

    def test_jnanendriyas_has_5(self):
        """JNANENDRIYAS has 5 knowledge senses."""
        assert len(JNANENDRIYAS) == 5

    def test_karmendriyas_has_5(self):
        """KARMENDRIYAS has 5 action organs."""
        assert len(KARMENDRIYAS) == 5

    def test_tanmatras_has_5(self):
        """TANMATRAS has 5 sense objects."""
        assert len(TANMATRAS) == 5

    def test_jnanendriyas_content(self):
        """JNANENDRIYAS has correct elements."""
        assert KshetraElement.CHAKSHU in JNANENDRIYAS  # Eyes
        assert KshetraElement.SHROTRA in JNANENDRIYAS  # Ears
        assert KshetraElement.GHRANA in JNANENDRIYAS  # Nose
        assert KshetraElement.RASANA in JNANENDRIYAS  # Tongue
        assert KshetraElement.TVAK in JNANENDRIYAS  # Skin

    def test_karmendriyas_content(self):
        """KARMENDRIYAS has correct elements."""
        assert KshetraElement.VAK in KARMENDRIYAS  # Speech
        assert KshetraElement.PANI in KARMENDRIYAS  # Hands
        assert KshetraElement.PADA in KARMENDRIYAS  # Feet

    def test_tanmatras_content(self):
        """TANMATRAS has correct elements."""
        assert KshetraElement.SHABDA in TANMATRAS  # Sound
        assert KshetraElement.SPARSHA in TANMATRAS  # Touch
        assert KshetraElement.RUPA in TANMATRAS  # Form
        assert KshetraElement.RASA in TANMATRAS  # Taste
        assert KshetraElement.GANDHA in TANMATRAS  # Smell


# =============================================================================
# ParaPrakriti Tests
# =============================================================================


class TestParaPrakriti:
    """Test ParaPrakriti dataclass (Jiva)."""

    def test_jiva_exists(self):
        """JIVA singleton exists."""
        assert JIVA is not None

    def test_jiva_bool_is_true(self):
        """Jiva always exists (bool is True)."""
        assert bool(JIVA) is True

    def test_jiva_qualitatively_one(self):
        """Jiva is qualitatively one with Krishna."""
        assert JIVA.qualitatively_one is True

    def test_jiva_quantitatively_different(self):
        """Jiva is quantitatively different from Krishna."""
        assert JIVA.quantitatively_different is True

    def test_jiva_can_forget(self):
        """Jiva can forget Krishna."""
        assert JIVA.can_forget is True

    def test_jiva_is_eternal(self):
        """Jiva is eternal."""
        assert JIVA.is_eternal is True

    def test_para_prakriti_frozen(self):
        """ParaPrakriti is frozen (immutable)."""
        with pytest.raises(Exception):
            JIVA.is_eternal = False


# =============================================================================
# GuruTattva Tests
# =============================================================================


class TestGuruTattva:
    """Test GuruTattva enum."""

    def test_guru_tattva_has_3_aspects(self):
        """GuruTattva has 3 aspects (BG 4.34)."""
        assert len(GuruTattva) == 3

    def test_pranipata_value(self):
        """PRANIPATA is 'pranipata'."""
        assert GuruTattva.PRANIPATA.value == "pranipata"

    def test_pariprasna_value(self):
        """PARIPRASNA is 'pariprasna'."""
        assert GuruTattva.PARIPRASNA.value == "pariprasna"

    def test_seva_value(self):
        """SEVA is 'seva'."""
        assert GuruTattva.SEVA.value == "seva"


# =============================================================================
# GuruConnection Tests
# =============================================================================


class TestGuruConnection:
    """Test GuruConnection dataclass."""

    def test_default_disconnected(self):
        """Default GuruConnection is disconnected."""
        conn = GuruConnection()
        assert conn.is_connected is False
        assert conn.parampara_intact is False

    def test_partial_connection(self):
        """Partial connection is not complete."""
        conn = GuruConnection(has_pranipata=True, has_pariprasna=True)
        assert conn.is_connected is False

    def test_full_connection(self):
        """Full connection requires all three aspects."""
        conn = GuruConnection(has_pranipata=True, has_pariprasna=True, has_seva=True)
        assert conn.is_connected is True
        assert conn.parampara_intact is True

    def test_guru_connection_frozen(self):
        """GuruConnection is frozen."""
        conn = GuruConnection()
        with pytest.raises(Exception):
            conn.has_seva = True


# =============================================================================
# Purushottama Tests
# =============================================================================


class TestPurushottama:
    """Test Purushottama class."""

    def test_purushottama_exists(self):
        """PURUSHOTTAMA singleton exists."""
        assert PURUSHOTTAMA is not None

    def test_purushottama_int_is_37(self):
        """PURUSHOTTAMA as int is 37."""
        assert int(PURUSHOTTAMA) == 37

    def test_purushottama_bool_is_true(self):
        """PURUSHOTTAMA is always True."""
        assert bool(PURUSHOTTAMA) is True

    def test_purushottama_is_person(self):
        """PURUSHOTTAMA.is_person is True."""
        assert PURUSHOTTAMA.is_person is True

    def test_purushottama_is_supreme(self):
        """PURUSHOTTAMA.is_supreme is True."""
        assert PURUSHOTTAMA.is_supreme is True

    def test_purushottama_transcends_categories(self):
        """PURUSHOTTAMA.transcends_categories is True."""
        assert PURUSHOTTAMA.transcends_categories is True

    def test_purushottama_callable(self):
        """PURUSHOTTAMA is callable (He responds)."""
        response = PURUSHOTTAMA("Arjuna")
        assert isinstance(response, str)
        assert "Arjuna" in response

    def test_purushottama_equals_37(self):
        """PURUSHOTTAMA == 37."""
        assert PURUSHOTTAMA == 37

    def test_purushottama_equals_itself(self):
        """PURUSHOTTAMA == PURUSHOTTAMA."""
        assert PURUSHOTTAMA == PURUSHOTTAMA

    def test_purushottama_lt_acintya(self):
        """PURUSHOTTAMA < any (smaller than smallest)."""
        assert PURUSHOTTAMA < 0
        assert PURUSHOTTAMA < 1000000

    def test_purushottama_gt_acintya(self):
        """PURUSHOTTAMA > any (greater than greatest)."""
        assert PURUSHOTTAMA > 0
        assert PURUSHOTTAMA > 1000000


# =============================================================================
# TATTVA_SUMMARY Tests
# =============================================================================


class TestTattvaSummary:
    """Test TATTVA_SUMMARY constant."""

    def test_summary_exists(self):
        """TATTVA_SUMMARY exists."""
        assert TATTVA_SUMMARY is not None

    def test_summary_is_string(self):
        """TATTVA_SUMMARY is a string."""
        assert isinstance(TATTVA_SUMMARY, str)

    def test_summary_mentions_purushottama(self):
        """TATTVA_SUMMARY mentions Purushottama."""
        assert "PURUSHOTTAMA" in TATTVA_SUMMARY

    def test_summary_mentions_37(self):
        """TATTVA_SUMMARY mentions 37."""
        assert "37" in TATTVA_SUMMARY


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.substrate import tattva

        assert "SYSTEM_MANIFESTATION" in tattva.__all__
        assert "AparaPrakriti" in tattva.__all__
        assert "KshetraElement" in tattva.__all__
        assert "ParaPrakriti" in tattva.__all__
        assert "JIVA" in tattva.__all__
        assert "GuruTattva" in tattva.__all__
        assert "GuruConnection" in tattva.__all__
        assert "Purushottama" in tattva.__all__
        assert "PURUSHOTTAMA" in tattva.__all__
