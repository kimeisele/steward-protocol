"""
VARNA (वर्ण) - The Smallest Unit of Sound
=========================================

"varṇa" = letter, sound, color

The atomic unit of Sanskrit phonetics.
Every syllable, word, and mantra is built from varnas.

STRUCTURE:
- Svara (स्वर) = Vowels (self-sounding)
- Vyanjana (व्यञ्जन) = Consonants (need vowel to sound)
- Anusvara (अनुस्वार) = Nasal sound (ṁ)
- Visarga (विसर्ग) = Aspiration (ḥ)

TRIPLE ENCODING:
- Devanagari: The original script
- IAST: International Alphabet of Sanskrit Transliteration
- Roman: Western approximation
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0x321c4a3e"  # GenesisByte: parampara % 37 == 0

from enum import Enum, auto
from dataclasses import dataclass
from typing import Final, Tuple, Optional, List


class VarnaType(Enum):
    """Classification of varnas."""

    SVARA = auto()  # Vowel
    VYANJANA = auto()  # Consonant
    ANUSVARA = auto()  # Nasal (ṁ)
    VISARGA = auto()  # Aspiration (ḥ)
    VIRAMA = auto()  # Vowel killer (्)
    MATRA = auto()  # Vowel mark (diacritical)


@dataclass(frozen=True)
class Varna:
    """
    A single sound unit - the atom of mantra.

    Attributes:
        devanagari: Original script form
        iast: IAST transliteration
        roman: Western approximation
        varna_type: Classification
        position: Position in alphabet (1-based)
    """

    devanagari: str
    iast: str
    roman: str
    varna_type: VarnaType
    position: int = 0

    def __str__(self) -> str:
        return self.iast

    def __repr__(self) -> str:
        return f"Varna({self.iast!r}, {self.varna_type.name})"


# =============================================================================
# SVARA (Vowels) - 13 basic vowels
# =============================================================================

SVARA: Final[Tuple[Varna, ...]] = (
    Varna("अ", "a", "a", VarnaType.SVARA, 1),
    Varna("आ", "ā", "aa", VarnaType.SVARA, 2),
    Varna("इ", "i", "i", VarnaType.SVARA, 3),
    Varna("ई", "ī", "ee", VarnaType.SVARA, 4),
    Varna("उ", "u", "u", VarnaType.SVARA, 5),
    Varna("ऊ", "ū", "oo", VarnaType.SVARA, 6),
    Varna("ऋ", "ṛ", "ri", VarnaType.SVARA, 7),
    Varna("ॠ", "ṝ", "ree", VarnaType.SVARA, 8),
    Varna("ए", "e", "e", VarnaType.SVARA, 9),
    Varna("ऐ", "ai", "ai", VarnaType.SVARA, 10),
    Varna("ओ", "o", "o", VarnaType.SVARA, 11),
    Varna("औ", "au", "au", VarnaType.SVARA, 12),
    Varna("अं", "aṁ", "am", VarnaType.ANUSVARA, 13),
    Varna("अः", "aḥ", "ah", VarnaType.VISARGA, 14),
)

# =============================================================================
# MATRA (Vowel Marks) - Diacritical forms of vowels
# =============================================================================

MATRA: Final[Tuple[Varna, ...]] = (
    Varna("ा", "ā", "aa", VarnaType.MATRA, 2),
    Varna("ि", "i", "i", VarnaType.MATRA, 3),
    Varna("ी", "ī", "ee", VarnaType.MATRA, 4),
    Varna("ु", "u", "u", VarnaType.MATRA, 5),
    Varna("ू", "ū", "oo", VarnaType.MATRA, 6),
    Varna("ृ", "ṛ", "ri", VarnaType.MATRA, 7),
    Varna("े", "e", "e", VarnaType.MATRA, 9),
    Varna("ै", "ai", "ai", VarnaType.MATRA, 10),
    Varna("ो", "o", "o", VarnaType.MATRA, 11),
    Varna("ौ", "au", "au", VarnaType.MATRA, 12),
    Varna("ं", "ṁ", "m", VarnaType.ANUSVARA, 13),
    Varna("ः", "ḥ", "h", VarnaType.VISARGA, 14),
)

# Virama - the vowel killer
VIRAMA: Final[Varna] = Varna("्", "", "", VarnaType.VIRAMA, 0)

# =============================================================================
# VYANJANA (Consonants) - 33 consonants in 5 vargas + 4 semi-vowels + 3 sibilants + 1 aspirate
# =============================================================================

# =============================================================================
# THE 5 VARGA GROUPS (PANCHA) - Articulation Points
# =============================================================================
# Sanskrit names by articulation point:
# - KANTHYA (कण्ठ्य) = Guttural/Throat = KAVARGA
# - TALAVYA (तालव्य) = Palatal/Palate = CAVARGA
# - MURDHANYA (मूर्धन्य) = Retroflex/Cerebral = TAVARGA (ट-वर्ग)
# - DANTYA (दन्त्य) = Dental/Teeth = DANTYA_VARGA (त-वर्ग)
# - OSHTHYA (ओष्ठ्य) = Labial/Lips = PAVARGA

# Kavarga (guttural - throat) - कवर्ग = KANTHYA
KAVARGA: Final[Tuple[Varna, ...]] = (
    Varna("क", "k", "k", VarnaType.VYANJANA, 1),
    Varna("ख", "kh", "kh", VarnaType.VYANJANA, 2),
    Varna("ग", "g", "g", VarnaType.VYANJANA, 3),
    Varna("घ", "gh", "gh", VarnaType.VYANJANA, 4),
    Varna("ङ", "ṅ", "n", VarnaType.VYANJANA, 5),
)

# Cavarga (palatal - palate)
CAVARGA: Final[Tuple[Varna, ...]] = (
    Varna("च", "c", "ch", VarnaType.VYANJANA, 6),
    Varna("छ", "ch", "chh", VarnaType.VYANJANA, 7),
    Varna("ज", "j", "j", VarnaType.VYANJANA, 8),
    Varna("झ", "jh", "jh", VarnaType.VYANJANA, 9),
    Varna("ञ", "ñ", "n", VarnaType.VYANJANA, 10),
)

# Tavarga (retroflex - tongue curled back)
TAVARGA: Final[Tuple[Varna, ...]] = (
    Varna("ट", "ṭ", "t", VarnaType.VYANJANA, 11),
    Varna("ठ", "ṭh", "th", VarnaType.VYANJANA, 12),
    Varna("ड", "ḍ", "d", VarnaType.VYANJANA, 13),
    Varna("ढ", "ḍh", "dh", VarnaType.VYANJANA, 14),
    Varna("ण", "ṇ", "n", VarnaType.VYANJANA, 15),
)

# Dantya Varga (dental - teeth) - तवर्ग
# NOTE: This is the DENTAL त-varga, distinct from retroflex ट-varga above
# Using DANTYA_VARGA as proper Sanskrit name (TAVARGA2 kept for backward compat)
DANTYA_VARGA: Final[Tuple[Varna, ...]] = (
    Varna("त", "t", "t", VarnaType.VYANJANA, 16),
    Varna("थ", "th", "th", VarnaType.VYANJANA, 17),
    Varna("द", "d", "d", VarnaType.VYANJANA, 18),
    Varna("ध", "dh", "dh", VarnaType.VYANJANA, 19),
    Varna("न", "n", "n", VarnaType.VYANJANA, 20),
)
TAVARGA2 = DANTYA_VARGA  # Backward compatibility alias

# Pavarga (labial - lips)
PAVARGA: Final[Tuple[Varna, ...]] = (
    Varna("प", "p", "p", VarnaType.VYANJANA, 21),
    Varna("फ", "ph", "ph", VarnaType.VYANJANA, 22),
    Varna("ब", "b", "b", VarnaType.VYANJANA, 23),
    Varna("भ", "bh", "bh", VarnaType.VYANJANA, 24),
    Varna("म", "m", "m", VarnaType.VYANJANA, 25),
)

# Antahstha (semi-vowels)
ANTAHSTHA: Final[Tuple[Varna, ...]] = (
    Varna("य", "y", "y", VarnaType.VYANJANA, 26),
    Varna("र", "r", "r", VarnaType.VYANJANA, 27),
    Varna("ल", "l", "l", VarnaType.VYANJANA, 28),
    Varna("व", "v", "v", VarnaType.VYANJANA, 29),
)

# Ushman (sibilants + aspirate)
USHMAN: Final[Tuple[Varna, ...]] = (
    Varna("श", "ś", "sh", VarnaType.VYANJANA, 30),
    Varna("ष", "ṣ", "sh", VarnaType.VYANJANA, 31),
    Varna("स", "s", "s", VarnaType.VYANJANA, 32),
    Varna("ह", "h", "h", VarnaType.VYANJANA, 33),
)

# All consonants combined
VYANJANA: Final[Tuple[Varna, ...]] = KAVARGA + CAVARGA + TAVARGA + DANTYA_VARGA + PAVARGA + ANTAHSTHA + USHMAN

# =============================================================================
# ARTICULATION POINT ALIASES (Proper Sanskrit Names)
# =============================================================================
# These are the canonical names based on WHERE in the mouth the sound originates

KANTHYA_VARGA = KAVARGA      # Throat/Guttural (क-वर्ग)
TALAVYA_VARGA = CAVARGA      # Palate/Palatal (च-वर्ग)
MURDHANYA_VARGA = TAVARGA    # Retroflex/Cerebral (ट-वर्ग)
OSHTHYA_VARGA = PAVARGA      # Lips/Labial (प-वर्ग)
# DANTYA_VARGA already defined above (त-वर्ग)

# =============================================================================
# PANCHA VARGA - The 5 Consonant Groups (SSOT from seed.py PANCHA = 5)
# =============================================================================
# This is THE canonical ordering of the 5 articulation points
# Index 0-4 maps to positions in phonetic analysis

from vibe_core.mahamantra.protocols._seed import PANCHA

PANCHA_VARGA: Final[Tuple[Tuple[Varna, ...], ...]] = (
    KANTHYA_VARGA,   # 0: Throat  → AKASHA (Ether)  → SHABDA (Sound)
    TALAVYA_VARGA,   # 1: Palate  → TEJAS (Fire)    → RUPA (Form)
    MURDHANYA_VARGA, # 2: Cerebral → VAYU (Air)     → SPARSHA (Touch)
    DANTYA_VARGA,    # 3: Teeth   → JALA (Water)    → RASA (Taste)
    OSHTHYA_VARGA,   # 4: Lips    → PRITHVI (Earth) → GANDHA (Smell)
)

# SSOT verification: 5 Vargas = PANCHA Tattvas
assert len(PANCHA_VARGA) == PANCHA, f"PANCHA_VARGA must have exactly {PANCHA} groups"

# =============================================================================
# LOOKUP FUNCTIONS
# =============================================================================


def get_varna_by_devanagari(char: str) -> Optional[Varna]:
    """Find varna by Devanagari character."""
    for v in SVARA + MATRA + VYANJANA + (VIRAMA,):
        if v.devanagari == char:
            return v
    return None


def get_varna_by_iast(char: str) -> Optional[Varna]:
    """Find varna by IAST character."""
    for v in SVARA + MATRA + VYANJANA + (VIRAMA,):
        if v.iast == char:
            return v
    return None


def decompose_devanagari(text: str) -> List[Varna]:
    """Decompose Devanagari text into varnas."""
    result = []
    for char in text:
        v = get_varna_by_devanagari(char)
        if v:
            result.append(v)
    return result


__all__ = [
    # Types
    "VarnaType",
    "Varna",
    # Vowels
    "SVARA",
    "MATRA",
    "VIRAMA",
    # 5 Vargas (original names)
    "KAVARGA",
    "CAVARGA",
    "TAVARGA",
    "TAVARGA2",  # Deprecated, use DANTYA_VARGA
    "DANTYA_VARGA",
    "PAVARGA",
    # Articulation Point Aliases (proper Sanskrit)
    "KANTHYA_VARGA",
    "TALAVYA_VARGA",
    "MURDHANYA_VARGA",
    "OSHTHYA_VARGA",
    # PANCHA VARGA (the 5 groups as tuple)
    "PANCHA_VARGA",
    # Other consonants
    "ANTAHSTHA",
    "USHMAN",
    "VYANJANA",
    # Functions
    "get_varna_by_devanagari",
    "get_varna_by_iast",
    "decompose_devanagari",
]
