"""
HARDENING TESTS - Language Protocol
====================================

Edge cases, error conditions, and stress tests for:
- LanguageProtocol
- CharacterMapping
- MultiLevelWord
- Mahamantra representations

FRACTAL PRINCIPLE: 1:1 mapping must hold under all conditions.
"""

import pytest

from vibe_core.protocols.language import (
    LanguageProtocol,
    LanguageLevel,
    ScriptType,
    CharacterMapping,
    MultiLevelWord,
    VOWEL_MAPPINGS,
    CONSONANT_MAPPINGS,
    SPECIAL_MAPPINGS,
    HOLY_NAME_WORDS,
    MAHAMANTRA,
    MAHAMANTRA_WESTERN,
    MAHAMANTRA_SANSKRIT,
    MAHAMANTRA_DIACRITICS,
)


# =============================================================================
# CHARACTER MAPPING HARDENING
# =============================================================================


class TestCharacterMappingEdgeCases:
    """Edge cases for CharacterMapping."""

    def test_empty_western(self):
        """Empty western representation (for special chars)."""
        mapping = CharacterMapping("", "।", "|")
        assert mapping.western == ""

    def test_multi_char_western(self):
        """Multi-character western representation."""
        mapping = CharacterMapping("shh", "ष", "ṣ")
        assert len(mapping.western) == 3

    def test_unicode_sanskrit(self):
        """Complex Unicode Sanskrit characters."""
        mapping = CharacterMapping("ksha", "क्ष", "kṣa")
        assert "क्ष" == mapping.sanskrit

    def test_diacritics_combined(self):
        """Combined diacritics work."""
        mapping = CharacterMapping("ri", "ऋ", "ṛ")
        assert mapping.diacritics == "ṛ"

    def test_mapping_str_format(self):
        """String format shows all three."""
        mapping = CharacterMapping("k", "क", "k")
        s = str(mapping)
        assert "k" in s
        assert "क" in s

    def test_mapping_equality(self):
        """Equal mappings are equal."""
        m1 = CharacterMapping("k", "क", "k")
        m2 = CharacterMapping("k", "क", "k")
        assert m1 == m2

    def test_mapping_hashable(self):
        """Mappings are hashable."""
        m = CharacterMapping("k", "क", "k")
        d = {m: "velar"}
        assert d[m] == "velar"

    def test_phoneme_field(self):
        """Phoneme field stores IPA."""
        m = CharacterMapping("k", "क", "k", phoneme="k")
        assert m.phoneme == "k"

    def test_category_field(self):
        """Category field stores classification."""
        m = CharacterMapping("k", "क", "k", category="velar")
        assert m.category == "velar"


class TestVowelMappingsComplete:
    """Complete vowel mapping coverage."""

    def test_short_vowels_present(self):
        """All short vowels present."""
        short_vowels = ["a", "i", "u"]
        for v in short_vowels:
            assert any(m.western == v for m in VOWEL_MAPPINGS)

    def test_long_vowels_present(self):
        """All long vowels present."""
        long_vowels = ["aa", "ii", "uu"]
        for v in long_vowels:
            assert any(m.western == v for m in VOWEL_MAPPINGS)

    def test_diphthongs_present(self):
        """Diphthongs present."""
        diphthongs = ["ai", "au"]
        for d in diphthongs:
            assert any(m.western == d for m in VOWEL_MAPPINGS)

    def test_vocalic_r_present(self):
        """Vocalic r (ṛ) present."""
        assert any(m.western == "ri" for m in VOWEL_MAPPINGS)

    def test_all_vowels_have_phonemes(self):
        """All vowels have phoneme info."""
        for m in VOWEL_MAPPINGS:
            assert m.phoneme, f"{m.western} has no phoneme"

    def test_all_vowels_have_category(self):
        """All vowels have category."""
        for m in VOWEL_MAPPINGS:
            assert m.category, f"{m.western} has no category"


class TestConsonantMappingsComplete:
    """Complete consonant mapping coverage."""

    def test_velar_consonants(self):
        """Velar consonants (k, kh, g, gh)."""
        velars = ["k", "kh", "g", "gh"]
        for c in velars:
            assert any(m.western == c for m in CONSONANT_MAPPINGS)

    def test_palatal_consonants(self):
        """Palatal consonants (c/ch, j)."""
        palatals = ["ch", "j"]
        for c in palatals:
            assert any(m.western == c for m in CONSONANT_MAPPINGS)

    def test_dental_consonants(self):
        """Dental consonants (t, th, d, dh, n)."""
        dentals = ["t", "th", "d", "dh", "n"]
        for c in dentals:
            assert any(m.western == c for m in CONSONANT_MAPPINGS)

    def test_labial_consonants(self):
        """Labial consonants (p, ph, b, bh, m)."""
        labials = ["p", "ph", "b", "bh", "m"]
        for c in labials:
            assert any(m.western == c for m in CONSONANT_MAPPINGS)

    def test_semivowels(self):
        """Semivowels (y, r, l, v)."""
        semivowels = ["y", "r", "l", "v"]
        for s in semivowels:
            assert any(m.western == s for m in CONSONANT_MAPPINGS)

    def test_sibilants(self):
        """Sibilants (ś, ṣ, s)."""
        sibilants = ["sh", "shh", "s"]
        for s in sibilants:
            assert any(m.western == s for m in CONSONANT_MAPPINGS)

    def test_glottal(self):
        """Glottal (h)."""
        assert any(m.western == "h" for m in CONSONANT_MAPPINGS)

    def test_all_consonants_have_phonemes(self):
        """All consonants have phoneme info."""
        for m in CONSONANT_MAPPINGS:
            assert m.phoneme, f"{m.western} has no phoneme"


# =============================================================================
# MULTI-LEVEL WORD HARDENING
# =============================================================================


class TestMultiLevelWordEdgeCases:
    """Edge cases for MultiLevelWord."""

    def test_empty_strings(self):
        """Empty strings in all levels."""
        word = MultiLevelWord("", "", "")
        assert word.western == ""

    def test_at_level_western(self):
        """at_level returns western."""
        word = MultiLevelWord("Test", "टेस्ट", "Test")
        assert word.at_level(LanguageLevel.WESTERN) == "Test"

    def test_at_level_sanskrit(self):
        """at_level returns sanskrit."""
        word = MultiLevelWord("Test", "टेस्ट", "Test")
        assert word.at_level(LanguageLevel.SANSKRIT) == "टेस्ट"

    def test_at_level_diacritics(self):
        """at_level returns diacritics."""
        word = MultiLevelWord("Krishna", "कृष्ण", "Kṛṣṇa")
        assert word.at_level(LanguageLevel.DIACRITICS) == "Kṛṣṇa"

    def test_word_str_format(self):
        """String format shows diacritics and western."""
        word = MultiLevelWord("Krishna", "कृष्ण", "Kṛṣṇa")
        s = str(word)
        assert "Kṛṣṇa" in s
        assert "Krishna" in s

    def test_word_with_meaning(self):
        """Word with meaning field."""
        word = MultiLevelWord("Krishna", "कृष्ण", "Kṛṣṇa", meaning="The All-Attractive One")
        assert "Attractive" in word.meaning

    def test_word_with_etymology(self):
        """Word with etymology field."""
        word = MultiLevelWord("Krishna", "कृष्ण", "Kṛṣṇa", etymology="kṛṣ (to attract) + ṇa")
        assert "kṛṣ" in word.etymology

    def test_word_equality(self):
        """Equal words are equal."""
        w1 = MultiLevelWord("Hare", "हरे", "Hare")
        w2 = MultiLevelWord("Hare", "हरे", "Hare")
        assert w1 == w2

    def test_word_hashable(self):
        """Words are hashable."""
        word = MultiLevelWord("Hare", "हरे", "Hare")
        d = {word: "vocative"}
        assert d[word] == "vocative"


# =============================================================================
# HOLY NAME HARDENING
# =============================================================================


class TestHolyNamesComplete:
    """Complete Holy Name coverage."""

    def test_hare_complete(self):
        """Hare has all fields."""
        hare = HOLY_NAME_WORDS["hare"]
        assert hare.western == "Hare"
        assert hare.sanskrit == "हरे"
        assert hare.diacritics == "Hare"
        assert hare.meaning
        assert hare.etymology

    def test_krishna_complete(self):
        """Krishna has all fields."""
        krishna = HOLY_NAME_WORDS["krishna"]
        assert krishna.western == "Krishna"
        assert krishna.sanskrit == "कृष्ण"
        assert krishna.diacritics == "Kṛṣṇa"
        assert krishna.meaning
        assert krishna.etymology

    def test_rama_complete(self):
        """Rama has all fields."""
        rama = HOLY_NAME_WORDS["rama"]
        assert rama.western == "Rama"
        assert rama.sanskrit == "राम"
        assert rama.diacritics == "Rāma"
        assert rama.meaning
        assert rama.etymology

    def test_hare_meaning_contains_hari(self):
        """Hare meaning references Hari."""
        hare = HOLY_NAME_WORDS["hare"]
        assert "Hari" in hare.meaning or "energy" in hare.meaning.lower()

    def test_krishna_meaning_attractive(self):
        """Krishna meaning references attraction."""
        krishna = HOLY_NAME_WORDS["krishna"]
        assert "Attractive" in krishna.meaning or "attract" in krishna.meaning.lower()

    def test_rama_meaning_pleasure(self):
        """Rama meaning references pleasure."""
        rama = HOLY_NAME_WORDS["rama"]
        assert "Pleasure" in rama.meaning or "enjoy" in rama.meaning.lower()


# =============================================================================
# MAHAMANTRA HARDENING
# =============================================================================


class TestMahamantraStructure:
    """Mahamantra structure validation."""

    def test_16_words_western(self):
        """Western has exactly 16 words."""
        words = MAHAMANTRA_WESTERN.split()
        assert len(words) == 16

    def test_16_words_sanskrit(self):
        """Sanskrit has exactly 16 words."""
        words = MAHAMANTRA_SANSKRIT.split()
        assert len(words) == 16

    def test_16_words_diacritics(self):
        """Diacritics has exactly 16 words."""
        words = MAHAMANTRA_DIACRITICS.split()
        assert len(words) == 16

    def test_word_sequence_western(self):
        """Western word sequence is correct."""
        words = MAHAMANTRA_WESTERN.split()
        # First four: Hare Krishna Hare Krishna
        assert words[0] == "Hare"
        assert words[1] == "Krishna"
        assert words[2] == "Hare"
        assert words[3] == "Krishna"
        # Last two: Hare Hare
        assert words[14] == "Hare"
        assert words[15] == "Hare"

    def test_word_sequence_sanskrit(self):
        """Sanskrit word sequence is correct."""
        words = MAHAMANTRA_SANSKRIT.split()
        assert words[0] == "हरे"
        assert words[1] == "कृष्ण"
        assert words[8] == "हरे"
        assert words[9] == "राम"

    def test_word_sequence_diacritics(self):
        """Diacritics word sequence is correct."""
        words = MAHAMANTRA_DIACRITICS.split()
        assert words[0] == "Hare"
        assert words[1] == "Kṛṣṇa"
        assert words[8] == "Hare"
        assert words[9] == "Rāma"

    def test_mahamantra_multilevel_consistent(self):
        """MAHAMANTRA MultiLevelWord matches constants."""
        assert MAHAMANTRA.western == MAHAMANTRA_WESTERN
        assert MAHAMANTRA.sanskrit == MAHAMANTRA_SANSKRIT
        assert MAHAMANTRA.diacritics == MAHAMANTRA_DIACRITICS

    def test_mahamantra_has_meaning(self):
        """MAHAMANTRA has meaning."""
        assert MAHAMANTRA.meaning
        assert "Mantra" in MAHAMANTRA.meaning or "mantra" in MAHAMANTRA.meaning.lower()

    def test_mahamantra_has_etymology(self):
        """MAHAMANTRA has etymology."""
        assert MAHAMANTRA.etymology
        assert "mahā" in MAHAMANTRA.etymology or "great" in MAHAMANTRA.etymology.lower()


class TestMahamantraWordMapping:
    """Mahamantra word-level consistency."""

    def test_hare_count_western(self):
        """8 Hare in western."""
        words = MAHAMANTRA_WESTERN.split()
        assert words.count("Hare") == 8

    def test_krishna_count_western(self):
        """4 Krishna in western."""
        words = MAHAMANTRA_WESTERN.split()
        assert words.count("Krishna") == 4

    def test_rama_count_western(self):
        """4 Rama in western."""
        words = MAHAMANTRA_WESTERN.split()
        assert words.count("Rama") == 4

    def test_hare_count_sanskrit(self):
        """8 हरे in sanskrit."""
        words = MAHAMANTRA_SANSKRIT.split()
        assert words.count("हरे") == 8

    def test_krishna_count_sanskrit(self):
        """4 कृष्ण in sanskrit."""
        words = MAHAMANTRA_SANSKRIT.split()
        assert words.count("कृष्ण") == 4

    def test_rama_count_sanskrit(self):
        """4 राम in sanskrit."""
        words = MAHAMANTRA_SANSKRIT.split()
        assert words.count("राम") == 4

    def test_word_positions_match(self):
        """Word positions match across levels."""
        western = MAHAMANTRA_WESTERN.split()
        sanskrit = MAHAMANTRA_SANSKRIT.split()
        diacritics = MAHAMANTRA_DIACRITICS.split()

        for i in range(16):
            # If western is Hare, sanskrit should be हरे
            if western[i] == "Hare":
                assert sanskrit[i] == "हरे"
                assert diacritics[i] == "Hare"
            elif western[i] == "Krishna":
                assert sanskrit[i] == "कृष्ण"
                assert diacritics[i] == "Kṛṣṇa"
            elif western[i] == "Rama":
                assert sanskrit[i] == "राम"
                assert diacritics[i] == "Rāma"


# =============================================================================
# LANGUAGE LEVEL HARDENING
# =============================================================================


class TestLanguageLevelCompleteness:
    """Language level completeness."""

    def test_exactly_three_levels(self):
        """Exactly three levels exist."""
        assert len(LanguageLevel) == 3

    def test_level_values_unique(self):
        """Level values are unique."""
        values = [level.value for level in LanguageLevel]
        assert len(values) == len(set(values))

    def test_all_levels_are_strings(self):
        """All level values are strings."""
        for level in LanguageLevel:
            assert isinstance(level.value, str)


class TestScriptTypeCompleteness:
    """Script type completeness."""

    def test_ascii_exists(self):
        """ASCII script type exists."""
        assert ScriptType.ASCII.value == "ascii"

    def test_devanagari_exists(self):
        """Devanagari script type exists."""
        assert ScriptType.DEVANAGARI.value == "devanagari"

    def test_iast_exists(self):
        """IAST script type exists."""
        assert ScriptType.IAST.value == "iast"


# =============================================================================
# PROTOCOL CONTRACT HARDENING
# =============================================================================


class TestLanguageProtocolContract:
    """LanguageProtocol contract enforcement."""

    def test_protocol_has_translate(self):
        """Protocol has translate method."""
        assert hasattr(LanguageProtocol, "translate")

    def test_protocol_has_detect_level(self):
        """Protocol has detect_level method."""
        assert hasattr(LanguageProtocol, "detect_level")

    def test_protocol_has_validate_mapping(self):
        """Protocol has validate_mapping method."""
        assert hasattr(LanguageProtocol, "validate_mapping")

    def test_protocol_has_get_word(self):
        """Protocol has get_word method."""
        assert hasattr(LanguageProtocol, "get_word")

    def test_protocol_is_runtime_checkable(self):
        """Protocol is runtime checkable."""
        assert hasattr(LanguageProtocol, "__protocol_attrs__") or hasattr(LanguageProtocol, "_is_protocol")


# =============================================================================
# IMMUTABILITY HARDENING
# =============================================================================


class TestImmutabilityEnforced:
    """All dataclasses are properly frozen."""

    def test_character_mapping_immutable(self):
        """CharacterMapping is truly immutable."""
        m = CharacterMapping("k", "क", "k")
        with pytest.raises(Exception):
            m.western = "g"

    def test_multilevel_word_immutable(self):
        """MultiLevelWord is truly immutable."""
        word = MultiLevelWord("Test", "टेस्ट", "Test")
        with pytest.raises(Exception):
            word.western = "Changed"


# =============================================================================
# NO ANY TYPE HARDENING
# =============================================================================


class TestNoAnyTypes:
    """Verify no Any types are used."""

    def test_character_mapping_no_any(self):
        """CharacterMapping uses strict types."""
        from typing import get_type_hints, Any

        hints = get_type_hints(CharacterMapping)
        for field_name, field_type in hints.items():
            assert field_type is not Any

    def test_multilevel_word_no_any(self):
        """MultiLevelWord uses strict types."""
        from typing import get_type_hints, Any

        hints = get_type_hints(MultiLevelWord)
        for field_name, field_type in hints.items():
            assert field_type is not Any


# =============================================================================
# UNICODE HANDLING HARDENING
# =============================================================================


class TestUnicodeHandling:
    """Unicode edge cases."""

    def test_devanagari_conjuncts(self):
        """Devanagari conjunct consonants work."""
        # क्ष = kṣa (conjunct of क + ष)
        word = MultiLevelWord("ksha", "क्ष", "kṣa")
        assert word.sanskrit == "क्ष"

    def test_devanagari_with_matras(self):
        """Devanagari with vowel matras work."""
        # कृ = kṛ (with vocalic r matra)
        assert "कृ" in HOLY_NAME_WORDS["krishna"].sanskrit

    def test_iast_with_macrons(self):
        """IAST with macrons work."""
        # ā = long a
        assert "ā" in HOLY_NAME_WORDS["rama"].diacritics

    def test_iast_with_underdots(self):
        """IAST with underdots work."""
        # ṛ, ṣ, ṇ
        assert "ṛ" in HOLY_NAME_WORDS["krishna"].diacritics
        assert "ṣ" in HOLY_NAME_WORDS["krishna"].diacritics

    def test_mixed_scripts_in_word(self):
        """Mixed scripts should be avoided."""
        # A proper word should not mix scripts
        for key, word in HOLY_NAME_WORDS.items():
            # Western should be ASCII only
            assert word.western.isascii(), f"{key} western has non-ASCII"
            # Sanskrit should have Devanagari
            assert not word.sanskrit.isascii(), f"{key} sanskrit is ASCII"


# =============================================================================
# FRACTAL MAPPING HARDENING
# =============================================================================


class TestFractalMappingConsistency:
    """1:1 fractal mapping consistency."""

    def test_vowel_mappings_bidirectional(self):
        """Vowel mappings work both ways."""
        for m in VOWEL_MAPPINGS:
            # Each mapping should have all three
            assert m.western
            assert m.sanskrit
            assert m.diacritics

    def test_consonant_mappings_bidirectional(self):
        """Consonant mappings work both ways."""
        for m in CONSONANT_MAPPINGS:
            assert m.western
            assert m.sanskrit
            assert m.diacritics

    def test_holy_names_level_consistent(self):
        """Holy names consistent at all levels."""
        for key, word in HOLY_NAME_WORDS.items():
            # at_level should work for all levels
            for level in LanguageLevel:
                result = word.at_level(level)
                assert result, f"{key} empty at {level}"

    def test_mahamantra_character_count_related(self):
        """Mahamantra character counts are related."""
        # Sanskrit uses more bytes but fewer visible characters
        # Western and diacritics should have similar character counts
        west_chars = len(MAHAMANTRA_WESTERN.replace(" ", ""))
        diac_chars = len(MAHAMANTRA_DIACRITICS.replace(" ", ""))
        # Should be within 20% of each other
        assert abs(west_chars - diac_chars) / west_chars < 0.2
