"""
TEST LANGUAGE PROTOCOL
======================

Verifies the three-level language representation:
    Level 1: WESTERN   - "Hare Krishna"
    Level 2: SANSKRIT  - हरे कृष्ण
    Level 3: DIACRITICS - "Hare Kṛṣṇa"

FRACTAL PRINCIPLE:
Each character maps 1:1 across levels.
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
    HOLY_NAME_WORDS,
    MAHAMANTRA,
    MAHAMANTRA_WESTERN,
    MAHAMANTRA_SANSKRIT,
    MAHAMANTRA_DIACRITICS,
)


class TestLanguageLevels:
    """Test the three language levels."""

    def test_three_levels_exist(self):
        """Three levels are defined."""
        assert len(LanguageLevel) == 3

    def test_western_level(self):
        """Western level is ASCII/English."""
        assert LanguageLevel.WESTERN.value == "western"

    def test_sanskrit_level(self):
        """Sanskrit level is Devanagari."""
        assert LanguageLevel.SANSKRIT.value == "sanskrit"

    def test_diacritics_level(self):
        """Diacritics level is IAST."""
        assert LanguageLevel.DIACRITICS.value == "diacritics"


class TestScriptTypes:
    """Test script encoding types."""

    def test_ascii_type(self):
        """ASCII script type."""
        assert ScriptType.ASCII.value == "ascii"

    def test_devanagari_type(self):
        """Devanagari script type."""
        assert ScriptType.DEVANAGARI.value == "devanagari"

    def test_iast_type(self):
        """IAST script type."""
        assert ScriptType.IAST.value == "iast"


class TestCharacterMapping:
    """Test 1:1 character mappings."""

    def test_mapping_is_frozen(self):
        """CharacterMapping is immutable."""
        mapping = CharacterMapping("k", "क", "k")
        with pytest.raises(Exception):
            mapping.western = "changed"

    def test_mapping_has_all_three_levels(self):
        """Each mapping has western, sanskrit, diacritics."""
        mapping = CharacterMapping("k", "क", "k")
        assert mapping.western == "k"
        assert mapping.sanskrit == "क"
        assert mapping.diacritics == "k"

    def test_vowel_a_mapping(self):
        """Vowel 'a' maps correctly."""
        a_mapping = next(m for m in VOWEL_MAPPINGS if m.western == "a")
        assert a_mapping.sanskrit == "अ"
        assert a_mapping.diacritics == "a"

    def test_vowel_long_a_mapping(self):
        """Long vowel 'ā' maps correctly."""
        aa_mapping = next(m for m in VOWEL_MAPPINGS if m.western == "aa")
        assert aa_mapping.sanskrit == "आ"
        assert aa_mapping.diacritics == "ā"

    def test_vowel_ri_mapping(self):
        """Vowel 'ṛ' (as in Kṛṣṇa) maps correctly."""
        ri_mapping = next(m for m in VOWEL_MAPPINGS if m.western == "ri")
        assert ri_mapping.sanskrit == "ऋ"
        assert ri_mapping.diacritics == "ṛ"


class TestConsonantMappings:
    """Test consonant mappings."""

    def test_k_mapping(self):
        """Consonant 'k' maps correctly."""
        k = next(m for m in CONSONANT_MAPPINGS if m.western == "k")
        assert k.sanskrit == "क"
        assert k.diacritics == "k"

    def test_sh_mapping(self):
        """Consonant 'ś' maps correctly."""
        sh = next(m for m in CONSONANT_MAPPINGS if m.western == "sh")
        assert sh.sanskrit == "श"
        assert sh.diacritics == "ś"

    def test_retroflex_sh_mapping(self):
        """Retroflex 'ṣ' maps correctly."""
        shh = next(m for m in CONSONANT_MAPPINGS if m.western == "shh")
        assert shh.sanskrit == "ष"
        assert shh.diacritics == "ṣ"

    def test_n_mapping(self):
        """Consonant 'n' maps correctly."""
        n = next(m for m in CONSONANT_MAPPINGS if m.western == "n")
        assert n.sanskrit == "न"
        assert n.diacritics == "n"


class TestMultiLevelWord:
    """Test multi-level word representation."""

    def test_word_is_frozen(self):
        """MultiLevelWord is immutable."""
        word = MultiLevelWord("Test", "टेस्ट", "Test")
        with pytest.raises(Exception):
            word.western = "changed"

    def test_word_at_level(self):
        """Can get word at specific level."""
        word = MultiLevelWord("Krishna", "कृष्ण", "Kṛṣṇa")
        assert word.at_level(LanguageLevel.WESTERN) == "Krishna"
        assert word.at_level(LanguageLevel.SANSKRIT) == "कृष्ण"
        assert word.at_level(LanguageLevel.DIACRITICS) == "Kṛṣṇa"


class TestHolyNames:
    """Test the Holy Name word mappings."""

    def test_hare_word(self):
        """'Hare' word is correctly mapped."""
        hare = HOLY_NAME_WORDS["hare"]
        assert hare.western == "Hare"
        assert hare.sanskrit == "हरे"
        assert hare.diacritics == "Hare"

    def test_krishna_word(self):
        """'Krishna' word is correctly mapped."""
        krishna = HOLY_NAME_WORDS["krishna"]
        assert krishna.western == "Krishna"
        assert krishna.sanskrit == "कृष्ण"
        assert krishna.diacritics == "Kṛṣṇa"

    def test_rama_word(self):
        """'Rama' word is correctly mapped."""
        rama = HOLY_NAME_WORDS["rama"]
        assert rama.western == "Rama"
        assert rama.sanskrit == "राम"
        assert rama.diacritics == "Rāma"

    def test_krishna_has_meaning(self):
        """Krishna word has meaning defined."""
        krishna = HOLY_NAME_WORDS["krishna"]
        assert "Attractive" in krishna.meaning

    def test_rama_has_meaning(self):
        """Rama word has meaning defined."""
        rama = HOLY_NAME_WORDS["rama"]
        assert "Pleasure" in rama.meaning


class TestMahamantra:
    """Test the Mahamantra in three levels."""

    def test_mahamantra_western(self):
        """Mahamantra western version."""
        assert "Hare Krishna" in MAHAMANTRA_WESTERN
        assert "Hare Rama" in MAHAMANTRA_WESTERN

    def test_mahamantra_sanskrit(self):
        """Mahamantra Sanskrit version."""
        assert "हरे कृष्ण" in MAHAMANTRA_SANSKRIT
        assert "हरे राम" in MAHAMANTRA_SANSKRIT

    def test_mahamantra_diacritics(self):
        """Mahamantra IAST version."""
        assert "Hare Kṛṣṇa" in MAHAMANTRA_DIACRITICS
        assert "Hare Rāma" in MAHAMANTRA_DIACRITICS

    def test_mahamantra_multilevel_word(self):
        """MAHAMANTRA is a MultiLevelWord."""
        assert isinstance(MAHAMANTRA, MultiLevelWord)
        assert MAHAMANTRA.western == MAHAMANTRA_WESTERN
        assert MAHAMANTRA.sanskrit == MAHAMANTRA_SANSKRIT
        assert MAHAMANTRA.diacritics == MAHAMANTRA_DIACRITICS

    def test_mahamantra_has_meaning(self):
        """Mahamantra has meaning defined."""
        assert "Great Mantra" in MAHAMANTRA.meaning or "Deliverance" in MAHAMANTRA.meaning


class TestMahamantraWordCount:
    """Test the 16-word structure of Mahamantra."""

    def test_western_has_16_words(self):
        """Western Mahamantra has 16 words."""
        words = MAHAMANTRA_WESTERN.split()
        assert len(words) == 16

    def test_sanskrit_has_16_words(self):
        """Sanskrit Mahamantra has 16 words."""
        words = MAHAMANTRA_SANSKRIT.split()
        assert len(words) == 16

    def test_diacritics_has_16_words(self):
        """Diacritics Mahamantra has 16 words."""
        words = MAHAMANTRA_DIACRITICS.split()
        assert len(words) == 16


class TestLanguageProtocolContract:
    """Test the LanguageProtocol contract."""

    def test_protocol_is_runtime_checkable(self):
        """LanguageProtocol can be checked at runtime."""
        assert hasattr(LanguageProtocol, "__protocol_attrs__") or hasattr(LanguageProtocol, "_is_protocol")

    def test_protocol_has_translate(self):
        """Protocol requires translate method."""
        assert "translate" in dir(LanguageProtocol)

    def test_protocol_has_detect_level(self):
        """Protocol requires detect_level method."""
        assert "detect_level" in dir(LanguageProtocol)

    def test_protocol_has_validate_mapping(self):
        """Protocol requires validate_mapping method."""
        assert "validate_mapping" in dir(LanguageProtocol)

    def test_protocol_has_get_word(self):
        """Protocol requires get_word method."""
        assert "get_word" in dir(LanguageProtocol)


class TestStrictTyping:
    """Test that no Any types are used."""

    def test_character_mapping_no_any(self):
        """CharacterMapping has no Any types."""
        from typing import get_type_hints, Any

        hints = get_type_hints(CharacterMapping)
        for field_name, field_type in hints.items():
            assert field_type is not Any, f"CharacterMapping.{field_name} uses Any"

    def test_multilevel_word_no_any(self):
        """MultiLevelWord has no Any types."""
        from typing import get_type_hints, Any

        hints = get_type_hints(MultiLevelWord)
        for field_name, field_type in hints.items():
            assert field_type is not Any, f"MultiLevelWord.{field_name} uses Any"


class TestFractalMapping:
    """Test the 1:1 fractal mapping principle."""

    def test_all_vowels_have_three_forms(self):
        """Every vowel has western, sanskrit, diacritics."""
        for mapping in VOWEL_MAPPINGS:
            assert mapping.western, "Missing western"
            assert mapping.sanskrit, "Missing sanskrit"
            assert mapping.diacritics, "Missing diacritics"

    def test_all_consonants_have_three_forms(self):
        """Every consonant has western, sanskrit, diacritics."""
        for mapping in CONSONANT_MAPPINGS:
            assert mapping.western, "Missing western"
            assert mapping.sanskrit, "Missing sanskrit"
            assert mapping.diacritics, "Missing diacritics"

    def test_holy_names_have_three_forms(self):
        """Every holy name has western, sanskrit, diacritics."""
        for key, word in HOLY_NAME_WORDS.items():
            assert word.western, f"{key} missing western"
            assert word.sanskrit, f"{key} missing sanskrit"
            assert word.diacritics, f"{key} missing diacritics"
