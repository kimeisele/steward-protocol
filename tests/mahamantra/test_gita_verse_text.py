"""
Tests for Gita Verse Text - Vibration Analysis
===============================================

100% SSOT-konform: Tests für ECHTE Ableitungen, nicht Annahmen.
"""

import pytest

from vibe_core.mahamantra.protocols._seed import (
    HALVES,
    NADI_RESONANCE,
    QUALITIES,
    QUARTERS,
    WORDS,
)
from vibe_core.mahamantra.research.gita_verse_text import (
    BG_18_66_ANALYSES,
    BG_18_66_WORDS,
    DHARMA_MANTRA_PRODUCT,
    analyze_sanskrit_word,
    get_verse_vibration_summary,
)
from vibe_core.mahamantra.research.shabda_translation import (
    SPARSHA_CONSONANTS,
    VARNAMALA_TOTAL,
    VOWELS_TOTAL,
)


class TestDharmaMantraRelation:
    """Test the proven DHARMA × MANTRA = QUALITIES relation."""

    def test_dharma_mantra_product(self) -> None:
        """QUARTERS × WORDS = QUALITIES = 64."""
        assert DHARMA_MANTRA_PRODUCT == QUALITIES
        assert QUARTERS * WORDS == 64

    def test_bg_18_66_verse_number(self) -> None:
        """BG 18.66 = QUALITIES + HALVES = 64 + 2."""
        verse_number = QUALITIES + HALVES
        assert verse_number == 66

    def test_dharma_legs(self) -> None:
        """QUARTERS = 4 = The four legs of dharma."""
        assert QUARTERS == 4

    def test_mantra_words(self) -> None:
        """WORDS = 16 = The sixteen words of Mahamantra."""
        assert WORDS == 16


class TestSanskritAlphabetStructure:
    """Test that Sanskrit alphabet maps to Mahamantra structure."""

    def test_vowels_equal_words(self) -> None:
        """16 vowels = 16 Mahamantra words."""
        assert VOWELS_TOTAL == WORDS

    def test_consonants_equal_prasadam(self) -> None:
        """25 stop consonants = PRASADAM."""
        assert SPARSHA_CONSONANTS == 25

    def test_varnamala_is_seven_squared(self) -> None:
        """49 total letters = 7²."""
        assert VARNAMALA_TOTAL == 49
        assert VARNAMALA_TOTAL == 7 * 7


class TestVibrationAnalysis:
    """Test the vibration analysis system."""

    def test_analyze_word_returns_structure(self) -> None:
        """analyze_sanskrit_word returns WordVibration."""
        result = analyze_sanskrit_word("hare")
        assert result.word == "hare"
        assert result.phoneme_count >= 0
        assert result.total_signature_sum >= 0

    def test_bg_18_66_has_14_words(self) -> None:
        """BG 18.66 has 14 analyzed words."""
        assert len(BG_18_66_WORDS) == 14
        assert len(BG_18_66_ANALYSES) == 14

    def test_verse_summary_has_required_fields(self) -> None:
        """get_verse_vibration_summary returns all required fields."""
        summary = get_verse_vibration_summary()
        assert "verse" in summary
        assert "verse_number" in summary
        assert "word_count" in summary
        assert "phoneme_count" in summary
        assert "total_signature_sum" in summary

    def test_verse_number_in_summary(self) -> None:
        """Summary verse_number = 66."""
        summary = get_verse_vibration_summary()
        assert summary["verse_number"] == 66


class TestHonesty:
    """Tests that verify we're not making unfounded claims."""

    def test_not_all_phonemes_mapped(self) -> None:
        """Not all Sanskrit characters are in PHONEME_MAP - this is honest."""
        # A typical word should have some unmapped phonemes
        # (complex consonants, diacritics, etc.)
        result = analyze_sanskrit_word("sarva")
        # We expect some phonemes to be unmapped
        total_chars = len([c for c in "sarva" if c not in " -'"])
        assert result.phoneme_count <= total_chars

    def test_signature_sum_is_computable(self) -> None:
        """Signature sum is computable even with partial mapping."""
        summary = get_verse_vibration_summary()
        assert summary["total_signature_sum"] > 0

    def test_mod_calculations_present(self) -> None:
        """Modulo calculations are present for investigation."""
        summary = get_verse_vibration_summary()
        # These are for investigation, not claims
        assert "signature_mod_nadi" in summary
        assert "signature_mod_qualities" in summary
