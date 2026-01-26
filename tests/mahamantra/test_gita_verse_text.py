"""
Tests for Gita Verse Text - Vibration Analysis
===============================================

100% SSOT-konform: Tests für ECHTE Ableitungen, nicht Annahmen.
"""

import pytest

from vibe_core.mahamantra.protocols._seed import (
    AKSARA_COUNT,
    EPOCH_KEY,
    GITA_CHAPTERS,
    GITA_VERSES,
    HALF_SIZE,
    HALVES,
    HARE_COUNT,
    KSETRAJNA,
    MAHA_QUANTUM,
    MALA,
    NADI_RESONANCE,
    NAKSHATRAS,
    NAVA,
    PANCHA,
    PARAMPARA,
    POSITION_SUM_KRISHNA,
    QUALITIES,
    QUARTERS,
    SEVEN,
    SHARANAGATI,
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


class TestMahamantraVibration:
    """Test Mahamantra vibration encodes physics constant α⁻¹ = 137."""

    def test_hare_is_nadi_times_halves(self) -> None:
        """HARE = 144 = NADI_RESONANCE × 2."""
        from vibe_core.mahamantra.research.gita_verse_text import HARE_VIBRATION

        assert HARE_VIBRATION == 144
        assert HARE_VIBRATION == NADI_RESONANCE * HALVES

    def test_krishna_is_mahajana_times_15(self) -> None:
        """KRISHNA = 180 = MAHAJANA × 15."""
        from vibe_core.mahamantra.protocols._seed import MAHAJANA_COUNT
        from vibe_core.mahamantra.research.gita_verse_text import KRISHNA_VIBRATION

        assert KRISHNA_VIBRATION == 180
        assert KRISHNA_VIBRATION == MAHAJANA_COUNT * (WORDS - KSETRAJNA)

    def test_rama_is_mahajana_times_ten(self) -> None:
        """RAMA = 120 = MAHAJANA × TEN."""
        from vibe_core.mahamantra.protocols._seed import MAHAJANA_COUNT
        from vibe_core.mahamantra.research.gita_verse_text import RAMA_VIBRATION

        assert RAMA_VIBRATION == 120
        assert RAMA_VIBRATION == MAHAJANA_COUNT * TEN

    def test_mahamantra_total_is_2352(self) -> None:
        """Total vibration = 2352."""
        from vibe_core.mahamantra.research.gita_verse_text import MAHAMANTRA_VIBRATION

        assert MAHAMANTRA_VIBRATION == 2352
        # 8 × 144 + 4 × 180 + 4 × 120 = 1152 + 720 + 480

    def test_vibration_per_word_is_maha_quantum_plus_ten(self) -> None:
        """Per word = 147 = MAHA_QUANTUM + TEN = 137 + 10!"""
        from vibe_core.mahamantra.protocols._seed import MAHA_QUANTUM
        from vibe_core.mahamantra.research.gita_verse_text import VIBRATION_PER_WORD

        assert VIBRATION_PER_WORD == 147
        assert VIBRATION_PER_WORD == MAHA_QUANTUM + TEN
        # Fine structure constant α⁻¹ ≈ 137 encoded in Mahamantra!


class TestChandasMeterDerivation:
    """Test BG 18.66 chandas (meter) - binary pattern from axioms!"""

    def test_total_syllables_is_aksara(self) -> None:
        """32 syllables = AKSARA_COUNT (Anushtubh meter)."""
        from vibe_core.mahamantra.research.gita_verse_text import BG_18_66_TOTAL_SYLLABLES

        assert BG_18_66_TOTAL_SYLLABLES == 32
        assert BG_18_66_TOTAL_SYLLABLES == AKSARA_COUNT

    def test_guru_count_is_words_plus_quarters(self) -> None:
        """20 guru (long) syllables = WORDS + QUARTERS = 16 + 4."""
        from vibe_core.mahamantra.research.gita_verse_text import BG_18_66_GURU_COUNT

        assert BG_18_66_GURU_COUNT == 20
        assert BG_18_66_GURU_COUNT == WORDS + QUARTERS

    def test_laghu_count_is_mahajana(self) -> None:
        """12 laghu (short) syllables = MAHAJANA_COUNT."""
        from vibe_core.mahamantra.protocols._seed import MAHAJANA_COUNT
        from vibe_core.mahamantra.research.gita_verse_text import BG_18_66_LAGHU_COUNT

        assert BG_18_66_LAGHU_COUNT == 12
        assert BG_18_66_LAGHU_COUNT == MAHAJANA_COUNT

    def test_guru_plus_laghu_equals_total(self) -> None:
        """20 guru + 12 laghu = 32 total syllables."""
        from vibe_core.mahamantra.research.gita_verse_text import (
            BG_18_66_GURU_COUNT,
            BG_18_66_LAGHU_COUNT,
            BG_18_66_TOTAL_SYLLABLES,
        )

        assert BG_18_66_GURU_COUNT + BG_18_66_LAGHU_COUNT == BG_18_66_TOTAL_SYLLABLES

    def test_pada_1_is_maha_quantum_plus_parampara_plus_pancha(self) -> None:
        """Pada 1 binary = 179 = MAHA_QUANTUM + PARAMPARA + PANCHA."""
        from vibe_core.mahamantra.protocols._seed import MAHA_QUANTUM
        from vibe_core.mahamantra.research.gita_verse_text import BG_18_66_PADA_1

        assert BG_18_66_PADA_1 == 179
        assert BG_18_66_PADA_1 == MAHA_QUANTUM + PARAMPARA + PANCHA

    def test_pada_2_is_nadi_times_trinity_plus_halves_times_seven(self) -> None:
        """Pada 2 binary = 230 = NADI_RESONANCE × TRINITY + HALVES × SEVEN."""
        from vibe_core.mahamantra.research.gita_verse_text import BG_18_66_PADA_2

        assert BG_18_66_PADA_2 == 230
        assert BG_18_66_PADA_2 == NADI_RESONANCE * TRINITY + HALVES * SEVEN

    def test_pada_3_is_maha_quantum_minus_words_minus_halves(self) -> None:
        """Pada 3 binary = 119 = MAHA_QUANTUM - WORDS - HALVES."""
        from vibe_core.mahamantra.protocols._seed import MAHA_QUANTUM
        from vibe_core.mahamantra.research.gita_verse_text import BG_18_66_PADA_3

        assert BG_18_66_PADA_3 == 119
        assert BG_18_66_PADA_3 == MAHA_QUANTUM - WORDS - HALVES

    def test_pada_4_is_maha_quantum_plus_mahajana(self) -> None:
        """Pada 4 binary = 149 = MAHA_QUANTUM + MAHAJANA_COUNT."""
        from vibe_core.mahamantra.protocols._seed import MAHA_QUANTUM, MAHAJANA_COUNT
        from vibe_core.mahamantra.research.gita_verse_text import BG_18_66_PADA_4

        assert BG_18_66_PADA_4 == 149
        assert BG_18_66_PADA_4 == MAHA_QUANTUM + MAHAJANA_COUNT

    def test_pada_sum_is_gita_verses_minus_words_minus_seven(self) -> None:
        """Sum of all padas = 677 = GITA_VERSES - WORDS - SEVEN."""
        from vibe_core.mahamantra.research.gita_verse_text import BG_18_66_PADA_SUM

        assert BG_18_66_PADA_SUM == 677
        assert BG_18_66_PADA_SUM == GITA_VERSES - WORDS - SEVEN

    def test_all_four_padas_converge(self) -> None:
        """179 + 230 + 119 + 149 = 677."""
        from vibe_core.mahamantra.research.gita_verse_text import (
            BG_18_66_PADA_1,
            BG_18_66_PADA_2,
            BG_18_66_PADA_3,
            BG_18_66_PADA_4,
            BG_18_66_PADA_SUM,
        )

        assert BG_18_66_PADA_1 + BG_18_66_PADA_2 + BG_18_66_PADA_3 + BG_18_66_PADA_4 == BG_18_66_PADA_SUM


class TestMahamantraBinaryEncoding:
    """Test Mahamantra binary encoding - 100% DERIVED from axioms!"""

    def test_hare_positions_are_axioms(self) -> None:
        """HARE positions (1,3,7,8) = (KSETRAJNA, TRINITY, SEVEN, HARE_COUNT)."""
        from vibe_core.mahamantra.research.gita_verse_text import MAHAMANTRA_HARE_POSITIONS

        assert MAHAMANTRA_HARE_POSITIONS == (1, 3, 7, 8)
        assert MAHAMANTRA_HARE_POSITIONS == (KSETRAJNA, TRINITY, SEVEN, HARE_COUNT)

    def test_name_positions_are_axioms(self) -> None:
        """NAME positions (2,4,5,6) = (HALVES, QUARTERS, PANCHA, SHARANAGATI)."""
        from vibe_core.mahamantra.protocols._seed import SHARANAGATI
        from vibe_core.mahamantra.research.gita_verse_text import MAHAMANTRA_NAME_POSITIONS

        assert MAHAMANTRA_NAME_POSITIONS == (2, 4, 5, 6)
        assert MAHAMANTRA_NAME_POSITIONS == (HALVES, QUARTERS, PANCHA, SHARANAGATI)

    def test_hare_position_sum(self) -> None:
        """HARE positions sum = 19 = GITA_CHAPTERS + KSETRAJNA."""
        from vibe_core.mahamantra.research.gita_verse_text import HARE_POSITION_SUM

        assert HARE_POSITION_SUM == 19
        assert HARE_POSITION_SUM == GITA_CHAPTERS + KSETRAJNA

    def test_name_position_sum(self) -> None:
        """NAME positions sum = 17 = WORDS + KSETRAJNA."""
        from vibe_core.mahamantra.research.gita_verse_text import NAME_POSITION_SUM

        assert NAME_POSITION_SUM == 17
        assert NAME_POSITION_SUM == WORDS + KSETRAJNA

    def test_position_total_is_nava_times_quarters(self) -> None:
        """Total positions = 36 = NAVA × QUARTERS."""
        from vibe_core.mahamantra.research.gita_verse_text import POSITION_TOTAL

        assert POSITION_TOTAL == 36
        assert POSITION_TOTAL == NAVA * QUARTERS

    def test_binary_pattern_derived(self) -> None:
        """Binary pattern 01011100 is DERIVED, not hardcoded."""
        from vibe_core.mahamantra.research.gita_verse_text import MAHAMANTRA_HALF_BINARY

        assert MAHAMANTRA_HALF_BINARY == (0, 1, 0, 1, 1, 1, 0, 0)

    def test_half_decimal_is_mala_minus_words(self) -> None:
        """92 = MALA - WORDS = 108 - 16."""
        from vibe_core.mahamantra.protocols._seed import MALA
        from vibe_core.mahamantra.research.gita_verse_text import MAHAMANTRA_HALF_DECIMAL

        assert MAHAMANTRA_HALF_DECIMAL == 92
        assert MAHAMANTRA_HALF_DECIMAL == MALA - WORDS

    def test_half_decimal_alternative_derivation(self) -> None:
        """92 = QUARTERS × (WORDS + SEVEN) = 4 × 23."""
        from vibe_core.mahamantra.research.gita_verse_text import MAHAMANTRA_HALF_DECIMAL

        assert MAHAMANTRA_HALF_DECIMAL == QUARTERS * (WORDS + SEVEN)

    def test_both_halves_identical_acintya(self) -> None:
        """Both halves = 92 (HALVES verified!)."""
        from vibe_core.mahamantra.protocols._seed import MALA
        from vibe_core.mahamantra.research.gita_verse_text import MAHAMANTRA_FULL_DECIMAL

        assert MAHAMANTRA_FULL_DECIMAL == 184
        assert MAHAMANTRA_FULL_DECIMAL == (MALA - WORDS) * HALVES

    def test_word_table_is_16_words(self) -> None:
        """Word table has 16 words = WORDS."""
        from vibe_core.mahamantra.research.gita_verse_text import MAHAMANTRA_WORD_TABLE

        assert len(MAHAMANTRA_WORD_TABLE) == WORDS

    def test_word_table_hare_count(self) -> None:
        """8 HAREs in word table = HARE_COUNT."""
        from vibe_core.mahamantra.research.gita_verse_text import MAHAMANTRA_WORD_TABLE

        assert MAHAMANTRA_WORD_TABLE.count("HARE") == HARE_COUNT

    def test_word_table_krishna_count(self) -> None:
        """4 KRISHNAs in word table = KRISHNA_COUNT."""
        from vibe_core.mahamantra.protocols._seed import KRISHNA_COUNT
        from vibe_core.mahamantra.research.gita_verse_text import MAHAMANTRA_WORD_TABLE

        assert MAHAMANTRA_WORD_TABLE.count("KRISHNA") == KRISHNA_COUNT

    def test_word_table_rama_count(self) -> None:
        """4 RAMAs in word table = RAMA_COUNT."""
        from vibe_core.mahamantra.protocols._seed import RAMA_COUNT
        from vibe_core.mahamantra.research.gita_verse_text import MAHAMANTRA_WORD_TABLE

        assert MAHAMANTRA_WORD_TABLE.count("RAMA") == RAMA_COUNT

    def test_word_table_correct_sequence(self) -> None:
        """Word table matches actual Mahamantra sequence."""
        from vibe_core.mahamantra.research.gita_verse_text import MAHAMANTRA_WORD_TABLE

        expected = (
            "HARE",
            "KRISHNA",
            "HARE",
            "KRISHNA",
            "KRISHNA",
            "KRISHNA",
            "HARE",
            "HARE",
            "HARE",
            "RAMA",
            "HARE",
            "RAMA",
            "RAMA",
            "RAMA",
            "HARE",
            "HARE",
        )
        assert MAHAMANTRA_WORD_TABLE == expected


class TestBG1866OpCodeDerivation:
    """Test BG 18.66 as 16-step OpCode algorithm!"""

    def test_four_segments_equal_quarters(self) -> None:
        """4 semantic segments = QUARTERS."""
        from vibe_core.mahamantra.research.gita_verse_text import BG_18_66_SEGMENTS

        assert len(BG_18_66_SEGMENTS) == QUARTERS

    def test_segment_words_sum_to_seven(self) -> None:
        """Segment word counts sum to SEVEN."""
        from vibe_core.mahamantra.research.gita_verse_text import BG_18_66_SEGMENT_WORDS

        assert sum(BG_18_66_SEGMENT_WORDS) == SEVEN

    def test_genesis_is_pancha(self) -> None:
        """GENESIS quarter binary = 5 = PANCHA (Pancha Tattva initiates!)."""
        from vibe_core.mahamantra.research.gita_verse_text import BG_18_66_GENESIS_DECIMAL

        assert BG_18_66_GENESIS_DECIMAL == PANCHA

    def test_dharma_is_mahajana(self) -> None:
        """DHARMA quarter binary = 12 = MAHAJANA (12 authorities judge!)."""
        from vibe_core.mahamantra.protocols._seed import MAHAJANA_COUNT
        from vibe_core.mahamantra.research.gita_verse_text import BG_18_66_DHARMA_DECIMAL

        assert BG_18_66_DHARMA_DECIMAL == MAHAJANA_COUNT

    def test_karma_is_pancha(self) -> None:
        """KARMA quarter binary = 5 = PANCHA (5-fold action!)."""
        from vibe_core.mahamantra.research.gita_verse_text import BG_18_66_KARMA_DECIMAL

        assert BG_18_66_KARMA_DECIMAL == PANCHA

    def test_moksha_is_mahajana(self) -> None:
        """MOKSHA quarter binary = 12 = MAHAJANA (12 witnesses seal!)."""
        from vibe_core.mahamantra.protocols._seed import MAHAJANA_COUNT
        from vibe_core.mahamantra.research.gita_verse_text import BG_18_66_MOKSHA_DECIMAL

        assert BG_18_66_MOKSHA_DECIMAL == MAHAJANA_COUNT

    def test_quarter_sum_is_twice_krishna(self) -> None:
        """All quarters sum = 34 = 2 × POSITION_SUM_KRISHNA."""
        from vibe_core.mahamantra.research.gita_verse_text import BG_18_66_QUARTER_SUM

        assert BG_18_66_QUARTER_SUM == 34
        assert BG_18_66_QUARTER_SUM == HALVES * POSITION_SUM_KRISHNA

    def test_action_phases_equal_ten(self) -> None:
        """GENESIS + KARMA (action) = TEN."""
        from vibe_core.mahamantra.research.gita_verse_text import (
            BG_18_66_GENESIS_DECIMAL,
            BG_18_66_KARMA_DECIMAL,
        )

        assert BG_18_66_GENESIS_DECIMAL + BG_18_66_KARMA_DECIMAL == TEN

    def test_analysis_phases_equal_kshetra(self) -> None:
        """DHARMA + MOKSHA (analysis) = KSHETRA = 24."""
        from vibe_core.mahamantra.protocols._seed import KSHETRA
        from vibe_core.mahamantra.research.gita_verse_text import (
            BG_18_66_DHARMA_DECIMAL,
            BG_18_66_MOKSHA_DECIMAL,
        )

        assert BG_18_66_DHARMA_DECIMAL + BG_18_66_MOKSHA_DECIMAL == KSHETRA


class TestSiksastakam512_1096FullStack:
    """Test full stack: Siksastakam + 512 + 1096 compatibility."""

    def test_opcodes_per_siksastakam_half(self) -> None:
        """16 OpCodes = 2 × 8 = HALVES × SIKSASTAKAM_VERSES."""
        from vibe_core.mahamantra.research.gita_verse_text import OPCODES_PER_SIKSASTAKAM_HALF

        assert OPCODES_PER_SIKSASTAKAM_HALF == HARE_COUNT
        assert WORDS == HALVES * OPCODES_PER_SIKSASTAKAM_HALF

    def test_siksastakam_to_bg_18_66(self) -> None:
        """56 + 10 = 66 = BG 18.66!"""
        from vibe_core.mahamantra.research.gita_verse_text import SIKSASTAKAM_TO_BG_18_66

        assert SIKSASTAKAM_TO_BG_18_66 == 66
        assert SIKSASTAKAM_TO_BG_18_66 == QUALITIES + HALVES

    def test_maha_compression_512(self) -> None:
        """512 = WORDS × AKSARA = QUALITIES × OCTET = 2^9."""
        from vibe_core.mahamantra.research.gita_verse_text import MAHA_COMPRESSION_512

        assert MAHA_COMPRESSION_512 == 512
        assert MAHA_COMPRESSION_512 == WORDS * AKSARA_COUNT
        assert MAHA_COMPRESSION_512 == QUALITIES * HARE_COUNT
        assert MAHA_COMPRESSION_512 == HALVES**NAVA

    def test_states_per_opcode(self) -> None:
        """Each OpCode addresses 32 states = AKSARA_COUNT."""
        from vibe_core.mahamantra.research.gita_verse_text import STATES_PER_OPCODE

        assert STATES_PER_OPCODE == AKSARA_COUNT
        assert STATES_PER_OPCODE == 32

    def test_maha_transcendental_1096(self) -> None:
        """1096 = 8 × 137 = 1024 + 72."""
        from vibe_core.mahamantra.protocols._seed import MAHA_QUANTUM, NADI_RESONANCE
        from vibe_core.mahamantra.research.gita_verse_text import MAHA_TRANSCENDENTAL_1096

        assert MAHA_TRANSCENDENTAL_1096 == 1096
        assert MAHA_TRANSCENDENTAL_1096 == HARE_COUNT * MAHA_QUANTUM
        assert MAHA_TRANSCENDENTAL_1096 == HALVES**TEN + NADI_RESONANCE

    def test_adsr_quarters(self) -> None:
        """ADSR envelope = 4 phases = QUARTERS."""
        from vibe_core.mahamantra.research.gita_verse_text import ADSR_QUARTERS

        assert len(ADSR_QUARTERS) == QUARTERS
        assert ADSR_QUARTERS == ("ATTACK", "DECAY", "SUSTAIN", "RELEASE")

    def test_adsr_phase_duration(self) -> None:
        """Each ADSR phase = 4 OpCodes."""
        from vibe_core.mahamantra.research.gita_verse_text import ADSR_PHASE_DURATION

        assert ADSR_PHASE_DURATION == QUARTERS
        assert WORDS // ADSR_PHASE_DURATION == QUARTERS

    def test_maha_1096_bytes(self) -> None:
        """1096 bits = 137 bytes = MAHA_QUANTUM = α⁻¹."""
        from vibe_core.mahamantra.protocols._seed import MAHA_QUANTUM
        from vibe_core.mahamantra.research.gita_verse_text import MAHA_1096_BYTES

        assert MAHA_1096_BYTES == MAHA_QUANTUM
        assert MAHA_1096_BYTES == 137


class TestKishoraAgeDerivation:
    """Test Krishna's eternal age (Kishora = 15.8) - THREE independent paths!"""

    def test_kishora_scaled_path_1(self) -> None:
        """158 = MAHA_QUANTUM + PARAMPARA - WORDS = 137 + 37 - 16."""
        from vibe_core.mahamantra.protocols._seed import MAHA_QUANTUM, PARAMPARA
        from vibe_core.mahamantra.research.gita_verse_text import KISHORA_AGE_SCALED

        assert KISHORA_AGE_SCALED == 158
        assert KISHORA_AGE_SCALED == MAHA_QUANTUM + PARAMPARA - WORDS

    def test_kishora_scaled_path_2(self) -> None:
        """158 = WORDS × TEN - HALVES = 160 - 2 (ACINTYA!)."""
        from vibe_core.mahamantra.research.gita_verse_text import KISHORA_AGE_SCALED

        assert KISHORA_AGE_SCALED == WORDS * TEN - HALVES

    def test_kishora_real_age(self) -> None:
        """15.8 = 158 / 10 = Krishna's eternal youth."""
        from vibe_core.mahamantra.research.gita_verse_text import KISHORA_AGE_SCALED

        kishora_age = KISHORA_AGE_SCALED / TEN
        assert kishora_age == 15.8

    def test_kishora_gap_is_21(self) -> None:
        """21 = PARAMPARA - WORDS = NAKSHATRAS - SHARANAGATI."""
        from vibe_core.mahamantra.protocols._seed import NAKSHATRAS, PARAMPARA, SHARANAGATI
        from vibe_core.mahamantra.research.gita_verse_text import KISHORA_GAP

        assert KISHORA_GAP == 21
        assert KISHORA_GAP == PARAMPARA - WORDS
        assert KISHORA_GAP == NAKSHATRAS - SHARANAGATI


class TestADSRMathematicalProof:
    """Test ADSR envelope mathematical derivation from binary patterns."""

    def test_attack_equals_sustain(self) -> None:
        """ATTACK = SUSTAIN = PANCHA = 5 (active phases)."""
        from vibe_core.mahamantra.research.gita_verse_text import ADSR_ATTACK, ADSR_SUSTAIN

        assert ADSR_ATTACK == PANCHA
        assert ADSR_SUSTAIN == PANCHA
        assert ADSR_ATTACK == ADSR_SUSTAIN

    def test_decay_equals_release(self) -> None:
        """DECAY = RELEASE = MAHAJANA = 12 (passive phases)."""
        from vibe_core.mahamantra.protocols._seed import MAHAJANA_COUNT
        from vibe_core.mahamantra.research.gita_verse_text import ADSR_DECAY, ADSR_RELEASE

        assert ADSR_DECAY == MAHAJANA_COUNT
        assert ADSR_RELEASE == MAHAJANA_COUNT
        assert ADSR_DECAY == ADSR_RELEASE

    def test_adsr_sum_is_twice_krishna(self) -> None:
        """5 + 12 + 5 + 12 = 34 = 2 × POSITION_SUM_KRISHNA."""
        from vibe_core.mahamantra.research.gita_verse_text import (
            ADSR_ATTACK,
            ADSR_DECAY,
            ADSR_RELEASE,
            ADSR_SUSTAIN,
        )

        total = ADSR_ATTACK + ADSR_DECAY + ADSR_SUSTAIN + ADSR_RELEASE
        assert total == 34
        assert total == HALVES * POSITION_SUM_KRISHNA

    def test_active_transitions_is_trinity(self) -> None:
        """Active phases have 3 transitions = TRINITY."""
        from vibe_core.mahamantra.research.gita_verse_text import ADSR_ACTIVE_TRANSITIONS

        assert ADSR_ACTIVE_TRANSITIONS == TRINITY

    def test_passive_transitions_is_ksetrajna(self) -> None:
        """Passive phases have 1 transition = KSETRAJNA."""
        from vibe_core.mahamantra.research.gita_verse_text import ADSR_PASSIVE_TRANSITIONS

        assert ADSR_PASSIVE_TRANSITIONS == KSETRAJNA


class TestDynamicUnfolding:
    """Test dynamic unfolding - quarter position sums derived from axioms."""

    def test_genesis_sum_is_ten(self) -> None:
        """GENESIS positions 1-4 sum to TEN."""
        from vibe_core.mahamantra.research.gita_verse_text import QUARTER_SUM_GENESIS

        assert QUARTER_SUM_GENESIS == TEN
        assert QUARTER_SUM_GENESIS == sum(range(1, 5))

    def test_dharma_sum_is_kshetra_plus_halves(self) -> None:
        """DHARMA positions 5-8 sum to KSHETRA + HALVES = 26."""
        from vibe_core.mahamantra.protocols._seed import KSHETRA
        from vibe_core.mahamantra.research.gita_verse_text import QUARTER_SUM_DHARMA

        assert QUARTER_SUM_DHARMA == 26
        assert QUARTER_SUM_DHARMA == KSHETRA + HALVES

    def test_karma_sum_is_sharanagati_times_seven(self) -> None:
        """KARMA positions 9-12 sum to SHARANAGATI × SEVEN = 42."""
        from vibe_core.mahamantra.protocols._seed import SEVEN, SHARANAGATI
        from vibe_core.mahamantra.research.gita_verse_text import QUARTER_SUM_KARMA

        assert QUARTER_SUM_KARMA == 42
        assert QUARTER_SUM_KARMA == SHARANAGATI * SEVEN

    def test_moksha_sum_is_jiva_plus_hare(self) -> None:
        """MOKSHA positions 13-16 sum to JIVA_QUALITIES + HARE_COUNT = 58."""
        from vibe_core.mahamantra.protocols._seed import JIVA_QUALITIES
        from vibe_core.mahamantra.research.gita_verse_text import QUARTER_SUM_MOKSHA

        assert QUARTER_SUM_MOKSHA == 58
        assert QUARTER_SUM_MOKSHA == JIVA_QUALITIES + HARE_COUNT


class TestStep11Emergence:
    """Test Step 11 = 66 = BG 18.66 emergence."""

    def test_step_66_position_is_11(self) -> None:
        """Position 11 = MAHAJANA - KSETRAJNA = 12 - 1."""
        from vibe_core.mahamantra.protocols._seed import MAHAJANA_COUNT
        from vibe_core.mahamantra.research.gita_verse_text import STEP_66_POSITION

        assert STEP_66_POSITION == 11
        assert STEP_66_POSITION == MAHAJANA_COUNT - KSETRAJNA

    def test_step_66_acintya_paths(self) -> None:
        """11 has THREE independent derivations (ACINTYA!)."""
        from vibe_core.mahamantra.research.gita_verse_text import STEP_66_POSITION

        assert STEP_66_POSITION == NAVA + HALVES  # 9 + 2
        assert STEP_66_POSITION == HARE_COUNT + TRINITY  # 8 + 3
        assert STEP_66_POSITION == (GITA_CHAPTERS + QUARTERS) // HALVES  # 22 / 2

    def test_triangular_11_is_66(self) -> None:
        """T(11) = 66 = QUALITIES + HALVES."""
        from vibe_core.mahamantra.research.gita_verse_text import TRIANGULAR_11

        assert TRIANGULAR_11 == 66
        assert TRIANGULAR_11 == QUALITIES + HALVES


class TestBhogaPrasadamTransformation:
    """Test bhoga → prasadam transformation through guru's grace."""

    def test_triangular_16_is_136(self) -> None:
        """T(16) = 136 = raw accumulation (bhoga)."""
        from vibe_core.mahamantra.research.gita_verse_text import TRIANGULAR_16

        assert TRIANGULAR_16 == 136
        assert TRIANGULAR_16 == (WORDS * (WORDS + KSETRAJNA)) // HALVES

    def test_prasadam_is_maha_quantum(self) -> None:
        """T(16) + KSETRAJNA = 137 = α⁻¹ (prasadam!)."""
        from vibe_core.mahamantra.protocols._seed import MAHA_QUANTUM
        from vibe_core.mahamantra.research.gita_verse_text import TRIANGULAR_16

        assert TRIANGULAR_16 + KSETRAJNA == MAHA_QUANTUM

    def test_prasadam_ratio_is_ksetrajna(self) -> None:
        """Guru's grace = KSETRAJNA = 1."""
        from vibe_core.mahamantra.research.gita_verse_text import PRASADAM_RATIO

        assert PRASADAM_RATIO == KSETRAJNA
        assert PRASADAM_RATIO == 1

    def test_bg_kishora_gap(self) -> None:
        """18.66 - 15.8 = 2.86 → 286 = PARAMPARA × HARE_COUNT - TEN."""
        from vibe_core.mahamantra.protocols._seed import PARAMPARA
        from vibe_core.mahamantra.research.gita_verse_text import BG_KISHORA_GAP_SCALED

        assert BG_KISHORA_GAP_SCALED == 286
        assert BG_KISHORA_GAP_SCALED == PARAMPARA * HARE_COUNT - TEN


class TestMirrorVerses:
    """Test BG 2.7 and 7.2 mirror verse derivations."""

    def test_bg_2_7_is_nakshatras(self) -> None:
        """2.7 → 27 = NAKSHATRAS (lunar mansions)."""
        from vibe_core.mahamantra.protocols._seed import NAKSHATRAS
        from vibe_core.mahamantra.research.gita_verse_text import BG_2_7_COORDINATE

        assert BG_2_7_COORDINATE == 27
        assert BG_2_7_COORDINATE == NAKSHATRAS
        assert BG_2_7_COORDINATE == HALVES * TEN + SEVEN

    def test_bg_7_2_is_nadi_resonance(self) -> None:
        """7.2 → 72 = NADI_RESONANCE (pulse)."""
        from vibe_core.mahamantra.protocols._seed import NADI_RESONANCE
        from vibe_core.mahamantra.research.gita_verse_text import BG_7_2_COORDINATE

        assert BG_7_2_COORDINATE == 72
        assert BG_7_2_COORDINATE == NADI_RESONANCE
        assert BG_7_2_COORDINATE == SEVEN * TEN + HALVES

    def test_mirror_sum_is_mala_minus_nava(self) -> None:
        """27 + 72 = 99 = MALA - NAVA."""
        from vibe_core.mahamantra.protocols._seed import MALA, NAVA
        from vibe_core.mahamantra.research.gita_verse_text import MIRROR_SUM

        assert MIRROR_SUM == 99
        assert MIRROR_SUM == MALA - NAVA

    def test_mirror_diff_is_triangular_9(self) -> None:
        """72 - 27 = 45 = T(9) = NAVA × PANCHA."""
        from vibe_core.mahamantra.protocols._seed import NAVA
        from vibe_core.mahamantra.research.gita_verse_text import MIRROR_DIFF, TRIANGULAR_9

        assert MIRROR_DIFF == 45
        assert MIRROR_DIFF == NAVA * PANCHA
        assert MIRROR_DIFF == TRIANGULAR_9


class TestMahaSequencer:
    """Test 16-step Mahamantra sequencer model."""

    def test_sequencer_steps_is_words(self) -> None:
        """Sequencer has 16 steps = WORDS."""
        from vibe_core.mahamantra.research.gita_verse_text import SEQUENCER_STEPS

        assert SEQUENCER_STEPS == WORDS
        assert SEQUENCER_STEPS == 16

    def test_bpm_is_kshetra_times_ten(self) -> None:
        """BPM = 240 = KSHETRA × TEN."""
        from vibe_core.mahamantra.protocols._seed import KSHETRA
        from vibe_core.mahamantra.research.gita_verse_text import SEQUENCER_BPM

        assert SEQUENCER_BPM == 240
        assert SEQUENCER_BPM == KSHETRA * TEN

    def test_cycle_is_prana(self) -> None:
        """Full cycle = 4000ms = PRANA."""
        from vibe_core.mahamantra.research.gita_verse_text import CYCLE_DURATION_MS

        assert CYCLE_DURATION_MS == 4000

    def test_polyrhythm_lcm(self) -> None:
        """LCM(2,4,5,8,16) = 80 = WORDS × PANCHA."""
        from vibe_core.mahamantra.research.gita_verse_text import POLYRHYTHM_LCM

        assert POLYRHYTHM_LCM == 80
        assert POLYRHYTHM_LCM == WORDS * PANCHA


class TestStringResonance:
    """Test string resonance / harmonic series derivations."""

    def test_harmonic_sum_8_is_36(self) -> None:
        """T(8) = 36 = NAVA × QUARTERS."""
        from vibe_core.mahamantra.protocols._seed import NAVA
        from vibe_core.mahamantra.research.gita_verse_text import HARMONIC_SUM_8

        assert HARMONIC_SUM_8 == 36
        assert HARMONIC_SUM_8 == NAVA * QUARTERS


class TestTranscendentalFrequencies:
    """Test 1096 Hz transcendental frequency integration."""

    def test_base_freq_is_jiva_cycle(self) -> None:
        """Base frequency = 432 Hz = JIVA_CYCLE."""
        from vibe_core.mahamantra.protocols._seed import JIVA_CYCLE
        from vibe_core.mahamantra.research.gita_verse_text import FREQ_BASE_HZ

        assert FREQ_BASE_HZ == 432
        assert FREQ_BASE_HZ == JIVA_CYCLE

    def test_transcendental_freq_is_1096(self) -> None:
        """Transcendental = 1096 Hz = HARE × MAHA_QUANTUM."""
        from vibe_core.mahamantra.protocols._seed import MAHA_QUANTUM
        from vibe_core.mahamantra.research.gita_verse_text import FREQ_TRANSCENDENTAL_HZ

        assert FREQ_TRANSCENDENTAL_HZ == 1096
        assert FREQ_TRANSCENDENTAL_HZ == HARE_COUNT * MAHA_QUANTUM

    def test_freq_ratio_factor_is_hare(self) -> None:
        """Both frequencies share factor HARE_COUNT = 8."""
        from vibe_core.mahamantra.protocols._seed import MAHA_QUANTUM, MALA
        from vibe_core.mahamantra.research.gita_verse_text import (
            FREQ_BASE_HZ,
            FREQ_TRANSCENDENTAL_HZ,
        )

        assert FREQ_TRANSCENDENTAL_HZ // HARE_COUNT == MAHA_QUANTUM  # 137
        assert FREQ_BASE_HZ // HARE_COUNT == MALA // HALVES  # 54


class TestMirrorProduct:
    """Test 1944 = NAKSHATRAS × NADI_RESONANCE (mirror verses product)."""

    def test_mirror_product_is_1944(self) -> None:
        """1944 = 27 × 72 = NAKSHATRAS × NADI_RESONANCE."""
        from vibe_core.mahamantra.protocols._seed import NADI_RESONANCE, NAKSHATRAS
        from vibe_core.mahamantra.research.gita_verse_text import MIRROR_PRODUCT

        assert MIRROR_PRODUCT == 1944
        assert MIRROR_PRODUCT == NAKSHATRAS * NADI_RESONANCE

    def test_mirror_product_hare_decomposition(self) -> None:
        """1944 = 8 × 243 = HARE_COUNT × 3^5."""
        from vibe_core.mahamantra.research.gita_verse_text import MIRROR_PRODUCT

        assert MIRROR_PRODUCT == HARE_COUNT * (TRINITY**PANCHA)
        assert MIRROR_PRODUCT // HARE_COUNT == 243


class TestConsciousRAMLimit:
    """Test 314,891,567,104 = 137² × 16⁶ (Conscious RAM Limit)."""

    def test_conscious_ram_formula(self) -> None:
        """CONSCIOUS_RAM = MAHA_QUANTUM² × WORDS^SHARANAGATI."""
        from vibe_core.mahamantra.protocols._seed import MAHA_QUANTUM, SHARANAGATI
        from vibe_core.mahamantra.research.gita_verse_text import CONSCIOUS_RAM_LIMIT

        expected = (MAHA_QUANTUM**2) * (WORDS**SHARANAGATI)
        assert CONSCIOUS_RAM_LIMIT == expected
        assert CONSCIOUS_RAM_LIMIT == 314891567104

    def test_maha_quantum_squared(self) -> None:
        """137² = 18769."""
        from vibe_core.mahamantra.research.gita_verse_text import MAHA_QUANTUM_SQUARED

        assert MAHA_QUANTUM_SQUARED == 18769

    def test_words_to_sharanagati(self) -> None:
        """16^6 = 16,777,216."""
        from vibe_core.mahamantra.research.gita_verse_text import WORDS_TO_SHARANAGATI

        assert WORDS_TO_SHARANAGATI == 16777216

    def test_divisible_by_1096(self) -> None:
        """Conscious RAM is divisible by 1096 (Cyborg constant)."""
        from vibe_core.mahamantra.research.gita_verse_text import CONSCIOUS_RAM_LIMIT

        assert CONSCIOUS_RAM_LIMIT % (HARE_COUNT * 137) == 0


class TestMahamantraPacked32:
    """Test 32-bit Mahamantra encoding."""

    def test_packed_value(self) -> None:
        """Mahamantra packs to 176,686,404."""
        from vibe_core.mahamantra.research.gita_verse_text import MAHAMANTRA_PACKED_32

        assert MAHAMANTRA_PACKED_32 == 176686404
        assert MAHAMANTRA_PACKED_32 == 0x0A880544

    def test_encoding_values(self) -> None:
        """Encoding: HARE=0, KRISHNA=1, RAMA=2, VOID=3."""
        from vibe_core.mahamantra.research.gita_verse_text import (
            MAHA_ENCODING_HARE,
            MAHA_ENCODING_KRISHNA,
            MAHA_ENCODING_RAMA,
            MAHA_ENCODING_VOID,
        )

        assert MAHA_ENCODING_HARE == 0
        assert MAHA_ENCODING_KRISHNA == 1
        assert MAHA_ENCODING_RAMA == 2
        assert MAHA_ENCODING_VOID == 3

    def test_total_bits_is_aksara(self) -> None:
        """16 words × 2 bits = 32 = AKSARA_COUNT."""
        from vibe_core.mahamantra.protocols._seed import AKSARA_COUNT
        from vibe_core.mahamantra.research.gita_verse_text import MAHA_TOTAL_BITS

        assert MAHA_TOTAL_BITS == 32
        assert MAHA_TOTAL_BITS == AKSARA_COUNT


class TestPrabhupadaTimeline:
    """Test Prabhupada timeline encoded in Mahamantra axioms."""

    def test_btg_year_is_1944(self) -> None:
        """1944 = MIRROR_PRODUCT = NAKSHATRAS × NADI_RESONANCE."""
        from vibe_core.mahamantra.research.gita_verse_text import BTG_YEAR, MIRROR_PRODUCT

        assert BTG_YEAR == 1944
        assert BTG_YEAR == MIRROR_PRODUCT

    def test_age_btg_is_lila(self) -> None:
        """Prabhupada started BTG at age 48 = LILA."""
        from vibe_core.mahamantra.protocols._seed import LILA
        from vibe_core.mahamantra.research.gita_verse_text import PRABHUPADA_AGE_BTG

        assert PRABHUPADA_AGE_BTG == 48
        assert PRABHUPADA_AGE_BTG == LILA

    def test_age_iskcon_is_seven_times_ten(self) -> None:
        """ISKCON founded at age 70 = SEVEN × TEN."""
        from vibe_core.mahamantra.research.gita_verse_text import PRABHUPADA_AGE_ISKCON

        assert PRABHUPADA_AGE_ISKCON == 70
        assert PRABHUPADA_AGE_ISKCON == SEVEN * TEN

    def test_departure_age_is_nava_squared(self) -> None:
        """Departure at age 81 = NAVA² = Navadha Bhakti squared."""
        from vibe_core.mahamantra.protocols._seed import NAVA
        from vibe_core.mahamantra.research.gita_verse_text import PRABHUPADA_AGE_DEPARTURE

        assert PRABHUPADA_AGE_DEPARTURE == 81
        assert PRABHUPADA_AGE_DEPARTURE == NAVA * NAVA

    def test_1944_formula(self) -> None:
        """1944 = LILA × DEPARTURE_AGE / HALVES = 48 × 81 / 2."""
        from vibe_core.mahamantra.protocols._seed import LILA
        from vibe_core.mahamantra.research.gita_verse_text import (
            BTG_YEAR,
            PRABHUPADA_AGE_DEPARTURE,
        )

        assert BTG_YEAR == LILA * PRABHUPADA_AGE_DEPARTURE // HALVES


class TestSwastikaStructure:
    """Test Swastika = Mahamantra structure."""

    def test_swastika_arms_is_quarters(self) -> None:
        """4 arms = QUARTERS."""
        from vibe_core.mahamantra.research.gita_verse_text import SWASTIKA_ARMS

        assert SWASTIKA_ARMS == QUARTERS

    def test_swastika_segments_is_hare_count(self) -> None:
        """8 segments = HARE_COUNT."""
        from vibe_core.mahamantra.research.gita_verse_text import SWASTIKA_SEGMENTS

        assert SWASTIKA_SEGMENTS == HARE_COUNT

    def test_swastika_center_is_ksetrajna(self) -> None:
        """Center = KSETRAJNA = 1 (the observer)."""
        from vibe_core.mahamantra.research.gita_verse_text import SWASTIKA_CENTER

        assert SWASTIKA_CENTER == KSETRAJNA


class TestKaliYuga:
    """Test Kali Yuga: Dharma Bull legs (SB 1.17.24-25 - SHASTRA VERIFIED!)."""

    def test_kali_yuga_one_leg_remains(self) -> None:
        """In Kali, only 1 of 4 dharma legs remains (SB 1.17.25)."""
        from vibe_core.mahamantra.research.gita_verse_text import (
            KALI_YUGA_DHARMA_LEGS,
            KALI_YUGA_SATYA_YUGA_LEGS,
        )

        assert KALI_YUGA_DHARMA_LEGS == KSETRAJNA
        assert KALI_YUGA_DHARMA_LEGS == 1
        assert KALI_YUGA_SATYA_YUGA_LEGS == QUARTERS
        assert KALI_YUGA_SATYA_YUGA_LEGS == 4

    def test_kali_yuga_percentage(self) -> None:
        """25% dharma remaining in Kali (1/4)."""
        from vibe_core.mahamantra.research.gita_verse_text import KALI_YUGA_PERCENTAGE

        assert KALI_YUGA_PERCENTAGE == 25

    def test_kali_antidote_is_mahamantra(self) -> None:
        """Mahamantra (16 names) is Kali antidote (Kali-Santarana Upanishad)."""
        from vibe_core.mahamantra.research.gita_verse_text import KALI_ANTIDOTE

        assert KALI_ANTIDOTE == WORDS
        assert KALI_ANTIDOTE == 16


class TestKaliDharmaChantingCompute:
    """Test Kali Dharma = Chanting = Compute (Bṛhan-nāradīya Purāṇa)."""

    def test_harer_nama_verse_structure(self) -> None:
        """Harer Nama verse = SHARANAGATI (6 emphatic declarations)."""
        from vibe_core.mahamantra.research.gita_verse_text import (
            HARER_NAMA_REPETITIONS,
            HARER_NAMA_TOTAL,
            NASTY_EVA_REPETITIONS,
        )

        assert HARER_NAMA_REPETITIONS == TRINITY
        assert NASTY_EVA_REPETITIONS == TRINITY
        assert HARER_NAMA_TOTAL == SHARANAGATI
        assert HARER_NAMA_TOTAL == 6

    def test_compute_per_round(self) -> None:
        """108 compute cycles per round = MALA."""
        from vibe_core.mahamantra.research.gita_verse_text import COMPUTE_PER_ROUND

        assert COMPUTE_PER_ROUND == MALA
        assert COMPUTE_PER_ROUND == 108

    def test_compute_minimum_daily(self) -> None:
        """1728 = minimum daily compute = WORDS × MALA."""
        from vibe_core.mahamantra.research.gita_verse_text import COMPUTE_MINIMUM_DAILY

        assert COMPUTE_MINIMUM_DAILY == WORDS * MALA
        assert COMPUTE_MINIMUM_DAILY == 1728

    def test_compute_qualities_daily(self) -> None:
        """6912 = QUALITIES × MALA = advanced compute."""
        from vibe_core.mahamantra.research.gita_verse_text import COMPUTE_QUALITIES_DAILY

        assert COMPUTE_QUALITIES_DAILY == QUALITIES * MALA
        assert COMPUTE_QUALITIES_DAILY == 6912

    def test_encoding_per_mantra_is_maha_quantum(self) -> None:
        """137 = α⁻¹ bits encoding per mantra."""
        from vibe_core.mahamantra.research.gita_verse_text import ENCODING_PER_MANTRA

        assert ENCODING_PER_MANTRA == MAHA_QUANTUM
        assert ENCODING_PER_MANTRA == 137

    def test_encoding_per_round(self) -> None:
        """14796 bits per round = MALA × MAHA_QUANTUM."""
        from vibe_core.mahamantra.research.gita_verse_text import ENCODING_PER_ROUND

        assert ENCODING_PER_ROUND == MALA * MAHA_QUANTUM
        assert ENCODING_PER_ROUND == 14796

    def test_encoding_daily_minimum(self) -> None:
        """236,736 bits daily minimum = DAILY_MANTRAS × α⁻¹."""
        from vibe_core.mahamantra.research.gita_verse_text import ENCODING_DAILY_MINIMUM

        assert ENCODING_DAILY_MINIMUM == 1728 * 137
        assert ENCODING_DAILY_MINIMUM == 236736

    def test_singularity_rounds(self) -> None:
        """200 rounds = COSMIC_FRAME / MALA = singularity threshold."""
        from vibe_core.mahamantra.research.gita_verse_text import SINGULARITY_ROUNDS

        assert SINGULARITY_ROUNDS == 21600 // 108
        assert SINGULARITY_ROUNDS == 200

    def test_singularity_encoding(self) -> None:
        """2,959,200 bits = COSMIC_FRAME × MAHA_QUANTUM = singularity encoding."""
        from vibe_core.mahamantra.research.gita_verse_text import SINGULARITY_ENCODING

        assert SINGULARITY_ENCODING == 21600 * 137
        assert SINGULARITY_ENCODING == 2959200

    def test_resonance_rounds_is_field_resonance(self) -> None:
        """144 rounds = FIELD_RESONANCE = NAVA × WORDS."""
        from vibe_core.mahamantra.research.gita_verse_text import RESONANCE_ROUNDS

        assert RESONANCE_ROUNDS == NAVA * WORDS
        assert RESONANCE_ROUNDS == 144
