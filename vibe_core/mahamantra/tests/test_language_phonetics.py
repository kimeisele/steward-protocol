"""
Tests for substrate/language/phonetics.py — 3D Syllable Vectors from CMU ARPAbet.

Tests what is DERIVED from the protocol, not invented.
"""

import pytest

from vibe_core.mahamantra.protocols._seed import HALVES, KSETRAJNA, QUARTERS
from vibe_core.mahamantra.substrate.language.types import RhythmProfile, SyllableVector
from vibe_core.mahamantra.substrate.language.phonetics import (
    _VOWEL_GROUP_RE,
    _WORD_TOKEN_RE,
    _fallback_vectors,
    _parse_arpabet,
    _varga_height,
    scan_syllable_rhythm,
    stress_for_word,
    syllable_vectors_for_word,
)
from vibe_core.mahamantra.substrate.phonetic_bridge import VargaIndex


# =============================================================================
# _varga_height: VargaIndex → 1-5 (PANCHA scale)
# =============================================================================

class TestVargaHeight:
    """_varga_height maps articulatory position to PANCHA height scale."""

    def test_kanthya_is_lowest(self):
        assert _varga_height(VargaIndex.KANTHYA) == KSETRAJNA  # 0 + 1 = 1

    def test_oshthya_is_highest(self):
        assert _varga_height(VargaIndex.OSHTHYA) == 5  # 4 + 1 = 5

    def test_all_five_vargas(self):
        heights = [_varga_height(v) for v in VargaIndex]
        assert heights == [1, 2, 3, 4, 5]

    def test_monotonically_increasing(self):
        heights = [_varga_height(v) for v in VargaIndex]
        for i in range(len(heights) - 1):
            assert heights[i] < heights[i + 1]


# =============================================================================
# _parse_arpabet: ARPAbet phoneme list → SyllableVector tuple
# =============================================================================

class TestParseArpabet:
    """_parse_arpabet converts CMU phoneme sequences to 3D vectors."""

    def test_single_vowel(self):
        # "AH0" = unstressed vowel, no onset consonants
        result = _parse_arpabet(["AH0"])
        assert len(result) == 1
        assert result[0].stress == 0
        assert result[0].weight == KSETRAJNA  # 0 onset + 1

    def test_stressed_vowel(self):
        result = _parse_arpabet(["AH1"])
        assert result[0].stress == 1

    def test_secondary_stress(self):
        result = _parse_arpabet(["AH2"])
        assert result[0].stress == 2

    def test_consonant_onset_adds_weight(self):
        # "K AH1" = one onset consonant
        result = _parse_arpabet(["K", "AH1"])
        assert len(result) == 1
        assert result[0].weight == KSETRAJNA + KSETRAJNA  # 1 onset + 1

    def test_cluster_onset(self):
        # "S T R AH1" = 3 onset consonants
        result = _parse_arpabet(["S", "T", "R", "AH1"])
        assert len(result) == 1
        assert result[0].weight == 3 + KSETRAJNA  # 3 onset + 1

    def test_coda_adds_to_last_syllable(self):
        # "AH1 N" = vowel + coda consonant
        result = _parse_arpabet(["AH1", "N"])
        assert len(result) == 1
        assert result[0].weight == KSETRAJNA + KSETRAJNA  # 0 onset + 1 + 1 coda

    def test_two_syllables(self):
        # "D AH0 V OW1 SH AH0 N" = de-vo-tion (simplified)
        result = _parse_arpabet(["D", "AH0", "V", "OW1", "SH", "AH0", "N"])
        assert len(result) == 3

    def test_empty_input(self):
        result = _parse_arpabet([])
        assert result == ()

    def test_all_consonants_no_syllable(self):
        # No vowel nucleus → no syllables
        result = _parse_arpabet(["K", "S", "T"])
        assert result == ()

    def test_returns_tuple(self):
        result = _parse_arpabet(["AH1"])
        assert isinstance(result, tuple)
        assert isinstance(result[0], SyllableVector)


# =============================================================================
# _fallback_vectors: vowel-group approximation when CMU unavailable
# =============================================================================

class TestFallbackVectors:
    """_fallback_vectors uses vowel groups for approximate vectors."""

    def test_no_vowels_returns_empty(self):
        assert _fallback_vectors("bcd") == ()

    def test_single_syllable_word(self):
        # 'cat' has one vowel group 'a' → 1 syllable
        result = _fallback_vectors("cat")
        assert len(result) == 1
        assert result[0].stress == KSETRAJNA  # single syllable gets primary stress
        assert result[0].height == 3  # default mid height

    def test_multi_syllable_first_stressed(self):
        result = _fallback_vectors("devotion")
        assert len(result) >= 2
        assert result[0].stress == KSETRAJNA  # first syllable stressed
        if len(result) > 1:
            assert result[1].stress == 0  # subsequent unstressed

    def test_returns_tuple_of_syllable_vectors(self):
        result = _fallback_vectors("hello")
        assert isinstance(result, tuple)
        for sv in result:
            assert isinstance(sv, SyllableVector)


# =============================================================================
# syllable_vectors_for_word: CMU lookup with fallback
# =============================================================================

class TestSyllableVectorsForWord:
    """syllable_vectors_for_word: CMU → 3D vectors, fallback if unavailable."""

    def test_returns_tuple(self):
        result = syllable_vectors_for_word("love")
        assert isinstance(result, tuple)

    def test_nonempty_for_english_word(self):
        result = syllable_vectors_for_word("devotion")
        assert len(result) >= 1

    def test_all_elements_are_syllable_vectors(self):
        for sv in syllable_vectors_for_word("Krishna"):
            assert isinstance(sv, SyllableVector)
            assert sv.stress >= 0
            assert sv.height >= 1
            assert sv.weight >= KSETRAJNA

    def test_deterministic(self):
        a = syllable_vectors_for_word("surrender")
        b = syllable_vectors_for_word("surrender")
        assert a == b

    def test_empty_string(self):
        result = syllable_vectors_for_word("")
        assert result == ()


# =============================================================================
# stress_for_word: backward compat wrapper
# =============================================================================

class TestStressForWord:
    """stress_for_word extracts stress digits from syllable vectors."""

    def test_returns_tuple_of_ints(self):
        result = stress_for_word("love")
        assert isinstance(result, tuple)
        for s in result:
            assert isinstance(s, int)
            assert s in (0, 1, 2)

    def test_matches_syllable_vectors(self):
        word = "devotion"
        vectors = syllable_vectors_for_word(word)
        stress = stress_for_word(word)
        assert len(stress) == len(vectors)
        for sv, s in zip(vectors, stress):
            assert sv.stress == s


# =============================================================================
# scan_syllable_rhythm: text → RhythmProfile on mantra grid
# =============================================================================

class TestScanSyllableRhythm:
    """scan_syllable_rhythm: full text → RhythmProfile with grid alignment."""

    def test_empty_text(self):
        rp = scan_syllable_rhythm("")
        assert rp.syllable_count == 0
        assert rp.stress_pattern == ()
        assert rp.sequencer_steps == ()
        assert rp.signature == "-"

    def test_single_word(self):
        rp = scan_syllable_rhythm("love")
        assert rp.syllable_count >= 1
        assert len(rp.stress_pattern) == rp.syllable_count
        assert len(rp.sequencer_steps) == rp.syllable_count
        assert rp.signature != "-"

    def test_multi_word(self):
        rp = scan_syllable_rhythm("fire and wisdom")
        assert rp.syllable_count >= 3

    def test_returns_rhythm_profile(self):
        rp = scan_syllable_rhythm("devotion")
        assert isinstance(rp, RhythmProfile)

    def test_vectors_populated(self):
        rp = scan_syllable_rhythm("surrender everything")
        assert len(rp.vectors) == rp.syllable_count
        for sv in rp.vectors:
            assert isinstance(sv, SyllableVector)

    def test_grid_modes_populated(self):
        rp = scan_syllable_rhythm("what is devotion")
        if rp.syllable_count > 0:
            assert len(rp.grid_modes) == rp.syllable_count
            for mode in rp.grid_modes:
                assert mode in ("DHARMA", "GENESIS", "KARMA")

    def test_sequencer_steps_within_grid(self):
        rp = scan_syllable_rhythm("tell me about dharma")
        for step in rp.sequencer_steps:
            assert 0 <= step < 32  # 32-step grid

    def test_deterministic(self):
        a = scan_syllable_rhythm("Hare Krishna")
        b = scan_syllable_rhythm("Hare Krishna")
        assert a == b

    def test_signature_matches_stress(self):
        rp = scan_syllable_rhythm("love")
        expected = "".join(str(s) for s in rp.stress_pattern)
        assert rp.signature == expected


# =============================================================================
# Regex patterns
# =============================================================================

class TestRegexPatterns:
    """_WORD_TOKEN_RE and _VOWEL_GROUP_RE patterns."""

    def test_word_token_re(self):
        tokens = _WORD_TOKEN_RE.findall("What is devotion?")
        assert tokens == ["What", "is", "devotion"]

    def test_word_token_re_apostrophe(self):
        tokens = _WORD_TOKEN_RE.findall("don't stop")
        assert "don't" in tokens

    def test_vowel_group_re(self):
        groups = _VOWEL_GROUP_RE.findall("devotion")
        assert len(groups) >= 2  # e, o, io

    def test_vowel_group_no_vowels(self):
        # y is a vowel in the regex, so use consonants-only
        groups = _VOWEL_GROUP_RE.findall("bcd")
        assert groups == []
