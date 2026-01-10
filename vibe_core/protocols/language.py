"""
LANGUAGE PROTOCOL - The Three Realities of Text
================================================

"One meaning, three expressions."

THE THREE LEVELS:
    Level 1: WESTERN   - ASCII/English ("Hare Krishna")
    Level 2: SANSKRIT  - Devanagari (हरे कृष्ण)
    Level 3: DIACRITICS - IAST precise ("Hare Kṛṣṇa")

WHY THREE LEVELS?
- Western: Machine-friendly, universal encoding
- Sanskrit: Original script, spiritual potency
- Diacritics: Scholarly precision, pronunciation guide

FRACTAL MAPPING:
    Each character maps 1:1 across levels.
    "Kṛṣṇa" (IAST) ↔ "कृष्ण" (Devanagari) ↔ "Krishna" (ASCII)

This enables:
- Proper translation without loss
- Bit-for-bit character mapping
- Spiritual precision in technical systems

STRICT TYPING (NO ANY):
Per PROMPT.md §IV.1 - All types explicit.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Protocol, Tuple, Union, runtime_checkable


# =============================================================================
# LANGUAGE LEVELS
# =============================================================================

class LanguageLevel(str, Enum):
    """The three levels of text reality."""
    WESTERN = "western"        # ASCII/English (Level 1)
    SANSKRIT = "sanskrit"      # Devanagari script (Level 2)
    DIACRITICS = "diacritics"  # IAST transliteration (Level 3)


class ScriptType(str, Enum):
    """Script encoding types."""
    ASCII = "ascii"            # Basic ASCII (A-Z, a-z)
    DEVANAGARI = "devanagari"  # Sanskrit script (Unicode block)
    IAST = "iast"              # International Alphabet of Sanskrit Transliteration


# =============================================================================
# CHARACTER MAPPING (1:1 Fractal)
# =============================================================================

@dataclass(frozen=True)
class CharacterMapping:
    """
    A single character across all three levels.

    FRACTAL PRINCIPLE:
    One meaning, three expressions.
    Each maps 1:1 to the others.
    """
    western: str       # ASCII representation
    sanskrit: str      # Devanagari character
    diacritics: str    # IAST character

    # Phonetic info
    phoneme: str = ""  # IPA or simplified phonetic
    category: str = "" # vowel, consonant, etc.

    def __str__(self) -> str:
        return f"{self.western}/{self.sanskrit}/{self.diacritics}"


# Core Sanskrit vowels
VOWEL_MAPPINGS: List[CharacterMapping] = [
    CharacterMapping("a", "अ", "a", phoneme="ə", category="short_vowel"),
    CharacterMapping("aa", "आ", "ā", phoneme="aː", category="long_vowel"),
    CharacterMapping("i", "इ", "i", phoneme="ɪ", category="short_vowel"),
    CharacterMapping("ii", "ई", "ī", phoneme="iː", category="long_vowel"),
    CharacterMapping("u", "उ", "u", phoneme="ʊ", category="short_vowel"),
    CharacterMapping("uu", "ऊ", "ū", phoneme="uː", category="long_vowel"),
    CharacterMapping("ri", "ऋ", "ṛ", phoneme="rɪ", category="vowel_r"),
    CharacterMapping("e", "ए", "e", phoneme="eː", category="long_vowel"),
    CharacterMapping("ai", "ऐ", "ai", phoneme="aɪ", category="diphthong"),
    CharacterMapping("o", "ओ", "o", phoneme="oː", category="long_vowel"),
    CharacterMapping("au", "औ", "au", phoneme="aʊ", category="diphthong"),
]

# Core consonants (partial - commonly used)
CONSONANT_MAPPINGS: List[CharacterMapping] = [
    CharacterMapping("k", "क", "k", phoneme="k", category="velar"),
    CharacterMapping("kh", "ख", "kh", phoneme="kʰ", category="velar_aspirated"),
    CharacterMapping("g", "ग", "g", phoneme="g", category="velar"),
    CharacterMapping("gh", "घ", "gh", phoneme="gʱ", category="velar_aspirated"),
    CharacterMapping("ch", "च", "c", phoneme="tʃ", category="palatal"),
    CharacterMapping("j", "ज", "j", phoneme="dʒ", category="palatal"),
    CharacterMapping("t", "त", "t", phoneme="t̪", category="dental"),
    CharacterMapping("th", "थ", "th", phoneme="t̪ʰ", category="dental_aspirated"),
    CharacterMapping("d", "द", "d", phoneme="d̪", category="dental"),
    CharacterMapping("dh", "ध", "dh", phoneme="d̪ʱ", category="dental_aspirated"),
    CharacterMapping("n", "न", "n", phoneme="n", category="dental_nasal"),
    CharacterMapping("p", "प", "p", phoneme="p", category="labial"),
    CharacterMapping("ph", "फ", "ph", phoneme="pʰ", category="labial_aspirated"),
    CharacterMapping("b", "ब", "b", phoneme="b", category="labial"),
    CharacterMapping("bh", "भ", "bh", phoneme="bʱ", category="labial_aspirated"),
    CharacterMapping("m", "म", "m", phoneme="m", category="labial_nasal"),
    CharacterMapping("y", "य", "y", phoneme="j", category="semivowel"),
    CharacterMapping("r", "र", "r", phoneme="r", category="semivowel"),
    CharacterMapping("l", "ल", "l", phoneme="l", category="semivowel"),
    CharacterMapping("v", "व", "v", phoneme="ʋ", category="semivowel"),
    CharacterMapping("sh", "श", "ś", phoneme="ʃ", category="sibilant"),
    CharacterMapping("shh", "ष", "ṣ", phoneme="ʂ", category="retroflex_sibilant"),
    CharacterMapping("s", "स", "s", phoneme="s", category="sibilant"),
    CharacterMapping("h", "ह", "h", phoneme="ɦ", category="glottal"),
]

# Special characters
SPECIAL_MAPPINGS: List[CharacterMapping] = [
    CharacterMapping("m", "ं", "ṁ", phoneme="ŋ", category="anusvara"),
    CharacterMapping("h", "ः", "ḥ", phoneme="h", category="visarga"),
]


# =============================================================================
# WORD REPRESENTATION
# =============================================================================

@dataclass(frozen=True)
class MultiLevelWord:
    """
    A word represented in all three levels.

    Example:
        western="Krishna", sanskrit="कृष्ण", diacritics="Kṛṣṇa"
    """
    western: str
    sanskrit: str
    diacritics: str

    # Meaning
    meaning: str = ""
    etymology: str = ""

    def at_level(self, level: LanguageLevel) -> str:
        """Get representation at specific level."""
        if level == LanguageLevel.WESTERN:
            return self.western
        elif level == LanguageLevel.SANSKRIT:
            return self.sanskrit
        elif level == LanguageLevel.DIACRITICS:
            return self.diacritics
        return self.western  # Default

    def __str__(self) -> str:
        return f"{self.diacritics} ({self.western})"


# Core words - the Holy Names
HOLY_NAME_WORDS: Dict[str, MultiLevelWord] = {
    "hare": MultiLevelWord(
        western="Hare",
        sanskrit="हरे",
        diacritics="Hare",
        meaning="O Hari (energy of the Lord)",
        etymology="vocative of Harā (Rādhā)"
    ),
    "krishna": MultiLevelWord(
        western="Krishna",
        sanskrit="कृष्ण",
        diacritics="Kṛṣṇa",
        meaning="The All-Attractive One",
        etymology="kṛṣ (to attract) + ṇa (suffix)"
    ),
    "rama": MultiLevelWord(
        western="Rama",
        sanskrit="राम",
        diacritics="Rāma",
        meaning="The Source of All Pleasure",
        etymology="ram (to enjoy) + a (suffix)"
    ),
}


# =============================================================================
# LANGUAGE PROTOCOL
# =============================================================================

@runtime_checkable
class LanguageProtocol(Protocol):
    """
    Protocol for language operations across three levels.

    FRACTAL REQUIREMENT:
    Every translation must maintain 1:1 mapping.
    No information loss between levels.
    """

    def translate(
        self,
        text: str,
        from_level: LanguageLevel,
        to_level: LanguageLevel
    ) -> str:
        """
        Translate text between levels.

        Args:
            text: Input text
            from_level: Source level
            to_level: Target level

        Returns:
            Translated text (1:1 character mapping where possible)
        """
        ...

    def detect_level(self, text: str) -> LanguageLevel:
        """
        Detect which level the text is in.

        Checks for:
        - Devanagari characters → SANSKRIT
        - IAST diacritics → DIACRITICS
        - ASCII only → WESTERN
        """
        ...

    def validate_mapping(self, text: str) -> bool:
        """
        Validate that text can be mapped across all levels.

        Returns True if text uses only mapped characters.
        """
        ...

    def get_word(self, key: str) -> Optional[MultiLevelWord]:
        """
        Get a multi-level word by key.

        Keys: "hare", "krishna", "rama", etc.
        """
        ...


# =============================================================================
# MAHAMANTRA IN THREE LEVELS
# =============================================================================

MAHAMANTRA_WESTERN = (
    "Hare Krishna Hare Krishna Krishna Krishna Hare Hare "
    "Hare Rama Hare Rama Rama Rama Hare Hare"
)

MAHAMANTRA_SANSKRIT = (
    "हरे कृष्ण हरे कृष्ण कृष्ण कृष्ण हरे हरे "
    "हरे राम हरे राम राम राम हरे हरे"
)

MAHAMANTRA_DIACRITICS = (
    "Hare Kṛṣṇa Hare Kṛṣṇa Kṛṣṇa Kṛṣṇa Hare Hare "
    "Hare Rāma Hare Rāma Rāma Rāma Hare Hare"
)

MAHAMANTRA = MultiLevelWord(
    western=MAHAMANTRA_WESTERN,
    sanskrit=MAHAMANTRA_SANSKRIT,
    diacritics=MAHAMANTRA_DIACRITICS,
    meaning="The Great Mantra for Deliverance",
    etymology="mahā (great) + mantra (sacred utterance)"
)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Protocol
    "LanguageProtocol",
    # Enums
    "LanguageLevel",
    "ScriptType",
    # Types
    "CharacterMapping",
    "MultiLevelWord",
    # Mappings
    "VOWEL_MAPPINGS",
    "CONSONANT_MAPPINGS",
    "SPECIAL_MAPPINGS",
    "HOLY_NAME_WORDS",
    # Mahamantra
    "MAHAMANTRA",
    "MAHAMANTRA_WESTERN",
    "MAHAMANTRA_SANSKRIT",
    "MAHAMANTRA_DIACRITICS",
]
