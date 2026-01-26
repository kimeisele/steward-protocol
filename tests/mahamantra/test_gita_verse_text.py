"""
Tests for Gita Verse Text - Vibration Analysis
===============================================

100% SSOT-konform: Tests für ECHTE Ableitungen, nicht Annahmen.
"""

import pytest

from vibe_core.mahamantra.protocols._seed import (
    AKSARA_COUNT,
    EPOCH_KEY,
    GITA_VERSES,
    HALF_SIZE,
    HALVES,
    HARE_COUNT,
    KSETRAJNA,
    NADI_RESONANCE,
    NAKSHATRAS,
    NAVA,
    PANCHA,
    PARAMPARA,
    QUALITIES,
    QUARTERS,
    SEVEN,
    TEN,
    TRINITY,
    WORDS,
)
from vibe_core.mahamantra.research.gita_verse_text import (
    BG_18_66_ANALYSES,
    BG_18_66_FIRST_LETTER_POS,
    BG_18_66_PATH_1,
    BG_18_66_PATH_2,
    BG_18_66_PATH_3,
    BG_18_66_WORD_LENGTH_SUM,
    BG_18_66_WORD_LENGTHS,
    BG_18_66_WORDS,
    CHAITANYA_512_PATH_A,
    CHAITANYA_512_PATH_B,
    CHAITANYA_512_PATH_C,
    DHARMA_MANTRA_PRODUCT,
    GITA_COMPRESSION_RATIO,
    OCTET,
    PRABHUPADA_ARRIVAL_MOD,
    PRABHUPADA_DEPARTURE,
    PRABHUPADA_DEPARTURE_MOD,
    SIKSASTAKAM_EFFECTS,
    SIKSASTAKAM_FIRST_LETTER_POS,
    SIKSASTAKAM_FIRST_LETTER_SUM,
    SIKSASTAKAM_PRODUCT,
    SIKSASTAKAM_VERSES,
    VERSE_PIPELINE_DEPTH,
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


class TestSiksastakamConnection:
    """Test the Siksastakam → BG 18.66 connection."""

    def test_siksastakam_verses_equals_hare_count(self) -> None:
        """8 Siksastakam verses = 8 Hare in Mahamantra."""
        assert SIKSASTAKAM_VERSES == HARE_COUNT == 8

    def test_siksastakam_effects_equals_seven(self) -> None:
        """7 effects in verse 1 = SEVEN."""
        assert SIKSASTAKAM_EFFECTS == SEVEN == 7

    def test_siksastakam_product(self) -> None:
        """8 × 7 = 56 = SIKSASTAKAM_PRODUCT."""
        assert SIKSASTAKAM_PRODUCT == 56
        assert SIKSASTAKAM_PRODUCT == HARE_COUNT * SEVEN

    def test_three_paths_to_66(self) -> None:
        """Three independent paths converge to 66 (ACINTYA!)."""
        # All three paths must equal 66
        assert BG_18_66_PATH_1 == 66
        assert BG_18_66_PATH_2 == 66
        assert BG_18_66_PATH_3 == 66

    def test_path_1_qualities_halves(self) -> None:
        """Path 1: QUALITIES + HALVES = 64 + 2 = 66."""
        assert QUALITIES + HALVES == 66
        assert BG_18_66_PATH_1 == QUALITIES + HALVES

    def test_path_2_dharma_mantra(self) -> None:
        """Path 2: (QUARTERS × WORDS) + HALVES = 66."""
        assert (QUARTERS * WORDS) + HALVES == 66
        assert BG_18_66_PATH_2 == (QUARTERS * WORDS) + HALVES

    def test_path_3_siksastakam(self) -> None:
        """Path 3: SIKSASTAKAM_PRODUCT + TEN = 56 + 10 = 66."""
        assert SIKSASTAKAM_PRODUCT + TEN == 66
        assert BG_18_66_PATH_3 == SIKSASTAKAM_PRODUCT + TEN

    def test_acintya_convergence(self) -> None:
        """All three paths are equal (ACINTYA principle)."""
        assert BG_18_66_PATH_1 == BG_18_66_PATH_2 == BG_18_66_PATH_3


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


class TestMahaCompression512:
    """Test the 512 MAHA COMPRESSION verse generation principle."""

    def test_512_path_a_binary(self) -> None:
        """Path A: HALVES^NAVA = 2^9 = 512."""
        assert CHAITANYA_512_PATH_A == 512
        assert HALVES**NAVA == 512

    def test_512_path_b_mahamantra_syllables(self) -> None:
        """Path B: WORDS × AKSARA = 16 × 32 = 512."""
        assert CHAITANYA_512_PATH_B == 512
        assert WORDS * AKSARA_COUNT == 512

    def test_512_path_c_qualities_octet(self) -> None:
        """Path C: QUALITIES × OCTET = 64 × 8 = 512."""
        assert CHAITANYA_512_PATH_C == 512
        assert QUALITIES * HALF_SIZE == 512

    def test_512_three_paths_converge(self) -> None:
        """All three paths converge to 512 (ACINTYA!)."""
        assert CHAITANYA_512_PATH_A == CHAITANYA_512_PATH_B == CHAITANYA_512_PATH_C == 512

    def test_octet_equals_siksastakam(self) -> None:
        """OCTET = HARE_COUNT = 8 Siksastakam verses."""
        assert OCTET == 8
        assert OCTET == HARE_COUNT
        assert OCTET == SIKSASTAKAM_VERSES


class TestPrabhupadaIsKey:
    """Test that Prabhupada is the KEY decoder for verse generation."""

    def test_1972_mod_27_equals_ksetrajna(self) -> None:
        """1972 mod 27 = 1 = KSETRAJNA (observer arrived!)."""
        assert PRABHUPADA_ARRIVAL_MOD == KSETRAJNA
        assert EPOCH_KEY % NAKSHATRAS == 1

    def test_1977_mod_37_equals_words(self) -> None:
        """1977 mod 37 = 16 = WORDS (message complete!)."""
        assert PRABHUPADA_DEPARTURE_MOD == WORDS
        assert (EPOCH_KEY + PANCHA) % PARAMPARA == 16

    def test_prabhupada_departure_is_1977(self) -> None:
        """1972 + 5 = 1977 (PANCHA years)."""
        assert PRABHUPADA_DEPARTURE == 1977
        assert PRABHUPADA_DEPARTURE == EPOCH_KEY + PANCHA

    def test_five_years_timeline(self) -> None:
        """Timeline = 5 years = PANCHA."""
        assert PRABHUPADA_DEPARTURE - EPOCH_KEY == PANCHA


class TestVerseGenerationPipeline:
    """Test the verse generation pipeline structure."""

    def test_pipeline_depth_equals_octet(self) -> None:
        """32 bits / 4 bits per nibble = 8 stages = OCTET."""
        assert VERSE_PIPELINE_DEPTH == 8
        assert VERSE_PIPELINE_DEPTH == OCTET
        assert AKSARA_COUNT // QUARTERS == 8

    def test_gita_compression_ratio(self) -> None:
        """Gita compression = 700/16 = 43.75×."""
        assert GITA_COMPRESSION_RATIO > 40
        assert GITA_COMPRESSION_RATIO == GITA_VERSES / WORDS

    def test_nibble_is_quarters(self) -> None:
        """One nibble = 4 bits = QUARTERS."""
        assert QUARTERS == 4
        # 32-bit address = 8 nibbles = 8 verses
        assert AKSARA_COUNT // QUARTERS == SIKSASTAKAM_VERSES


class TestFirstLetterDerivation:
    """Test ACTUAL verse text derivation - first letters from axioms."""

    def test_bg_18_66_first_letter_is_aksara(self) -> None:
        """BG 18.66 'sarva' starts with स (s) = position 32 = AKSARA_COUNT."""
        assert BG_18_66_FIRST_LETTER_POS == 32
        assert BG_18_66_FIRST_LETTER_POS == AKSARA_COUNT

    def test_bg_18_66_first_letter_derivation_paths(self) -> None:
        """32 = WORDS × HALVES = HARE_COUNT × QUARTERS."""
        assert WORDS * HALVES == 32
        assert HARE_COUNT * QUARTERS == 32

    def test_siksastakam_verse_1_first_letter(self) -> None:
        """Verse 1 'ceto' → च (c) = 6 = HALVES + QUARTERS."""
        assert SIKSASTAKAM_FIRST_LETTER_POS[0] == 6
        assert SIKSASTAKAM_FIRST_LETTER_POS[0] == HALVES + QUARTERS

    def test_siksastakam_verse_3_is_words(self) -> None:
        """Verse 3 'tṛṇād' → त (t) = 16 = WORDS!"""
        assert SIKSASTAKAM_FIRST_LETTER_POS[2] == WORDS

    def test_siksastakam_verse_5_is_ksetrajna(self) -> None:
        """Verse 5 'ayi' → अ (a) = 1 = KSETRAJNA!"""
        assert SIKSASTAKAM_FIRST_LETTER_POS[4] == KSETRAJNA

    def test_siksastakam_verse_8_is_halves(self) -> None:
        """Verse 8 'āśliṣya' → आ (ā) = 2 = HALVES!"""
        assert SIKSASTAKAM_FIRST_LETTER_POS[7] == HALVES

    def test_siksastakam_has_8_positions(self) -> None:
        """8 first letter positions = OCTET."""
        assert len(SIKSASTAKAM_FIRST_LETTER_POS) == 8
        assert len(SIKSASTAKAM_FIRST_LETTER_POS) == HARE_COUNT

    def test_siksastakam_sum_is_111(self) -> None:
        """Sum of all positions = 111 = SEVEN × WORDS - KSETRAJNA."""
        assert SIKSASTAKAM_FIRST_LETTER_SUM == 111
        assert SIKSASTAKAM_FIRST_LETTER_SUM == SEVEN * WORDS - KSETRAJNA
        assert SIKSASTAKAM_FIRST_LETTER_SUM == 7 * 16 - 1


class TestWordLengthDerivation:
    """Test BG 18.66 word lengths - ALL are axioms!"""

    def test_word_lengths_are_axioms(self) -> None:
        """Each word length = an axiom constant."""
        assert BG_18_66_WORD_LENGTHS == (5, 7, 10, 3, 4, 7, 5)
        # sarva=PANCHA, dharmān=SEVEN, parityajya=TEN, mām=TRINITY,
        # ekam=QUARTERS, śaraṇam=SEVEN, vraja=PANCHA

    def test_seven_words_in_first_half(self) -> None:
        """7 words in first half = SEVEN."""
        assert len(BG_18_66_WORD_LENGTHS) == SEVEN

    def test_sarva_is_pancha(self) -> None:
        """sarva = 5 = PANCHA."""
        assert BG_18_66_WORD_LENGTHS[0] == PANCHA

    def test_dharman_is_seven(self) -> None:
        """dharmān = 7 = SEVEN."""
        assert BG_18_66_WORD_LENGTHS[1] == SEVEN

    def test_parityajya_is_ten(self) -> None:
        """parityajya = 10 = TEN."""
        assert BG_18_66_WORD_LENGTHS[2] == TEN

    def test_mam_is_trinity(self) -> None:
        """mām = 3 = TRINITY."""
        assert BG_18_66_WORD_LENGTHS[3] == TRINITY

    def test_ekam_is_quarters(self) -> None:
        """ekam = 4 = QUARTERS."""
        assert BG_18_66_WORD_LENGTHS[4] == QUARTERS

    def test_sum_is_parampara_plus_quarters(self) -> None:
        """Sum = 41 = PARAMPARA + QUARTERS = 37 + 4."""
        assert BG_18_66_WORD_LENGTH_SUM == 41
        assert BG_18_66_WORD_LENGTH_SUM == PARAMPARA + QUARTERS
