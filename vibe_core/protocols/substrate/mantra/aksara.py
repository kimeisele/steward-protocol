"""
AKSARA (अक्षर) - The Syllable Unit
===================================

"akṣara" = imperishable, syllable

A syllable is the smallest pronounceable unit.
Built from varnas (consonant + vowel or just vowel).

STRUCTURE:
- Consonant + inherent 'a': क = ka
- Consonant + matra: के = ke, की = kī
- Consonant + virama + consonant: क्र = kra
- Pure vowel: अ = a, आ = ā

MAHAMANTRA SYLLABLES:
- हरे (hare): ह (ha) + रे (re)
- कृष्ण (kṛṣṇa): कृ (kṛ) + ष्ण (ṣṇa)
- राम (rāma): रा (rā) + म (ma)
"""

from dataclasses import dataclass, field
from typing import Final, Tuple, List, Optional
from .varna import Varna, VarnaType, VYANJANA, SVARA, MATRA, VIRAMA


@dataclass(frozen=True)
class Aksara:
    """
    A syllable - the smallest pronounceable unit.

    Attributes:
        devanagari: Original script form
        iast: IAST transliteration
        roman: Western approximation
        varnas: Component varnas (letters)
    """
    devanagari: str
    iast: str
    roman: str
    varnas: Tuple[Varna, ...] = field(default_factory=tuple)

    def __str__(self) -> str:
        return self.iast

    def __repr__(self) -> str:
        return f"Aksara({self.iast!r})"

    @property
    def is_pure_vowel(self) -> bool:
        """True if this is just a vowel (no consonant)."""
        return len(self.varnas) == 1 and self.varnas[0].varna_type == VarnaType.SVARA

    @property
    def has_consonant(self) -> bool:
        """True if starts with a consonant."""
        return len(self.varnas) > 0 and self.varnas[0].varna_type == VarnaType.VYANJANA


# =============================================================================
# MAHAMANTRA SYLLABLES - The building blocks of the Holy Names
# =============================================================================

# HARE (हरे) = ha + re
AKSARA_HA = Aksara("ह", "ha", "ha")
AKSARA_RE = Aksara("रे", "re", "re")

# KRISHNA (कृष्ण) = kṛ + ṣṇa
AKSARA_KRI = Aksara("कृ", "kṛ", "kri")
AKSARA_SHNA = Aksara("ष्ण", "ṣṇa", "shna")

# RAMA (राम) = rā + ma
AKSARA_RAA = Aksara("रा", "rā", "raa")
AKSARA_MA = Aksara("म", "ma", "ma")

# Collection of Mahamantra syllables
MAHAMANTRA_AKSARAS: Final[Tuple[Aksara, ...]] = (
    AKSARA_HA,
    AKSARA_RE,
    AKSARA_KRI,
    AKSARA_SHNA,
    AKSARA_RAA,
    AKSARA_MA,
)


# =============================================================================
# DECOMPOSITION: Word -> Syllables
# =============================================================================

# HARE decomposition
HARE_AKSARAS: Final[Tuple[Aksara, ...]] = (AKSARA_HA, AKSARA_RE)

# KRISHNA decomposition
KRISHNA_AKSARAS: Final[Tuple[Aksara, ...]] = (AKSARA_KRI, AKSARA_SHNA)

# RAMA decomposition
RAMA_AKSARAS: Final[Tuple[Aksara, ...]] = (AKSARA_RAA, AKSARA_MA)


def join_aksaras(aksaras: Tuple[Aksara, ...], encoding: str = "iast") -> str:
    """Join syllables into a word."""
    if encoding == "devanagari":
        return "".join(a.devanagari for a in aksaras)
    elif encoding == "iast":
        return "".join(a.iast for a in aksaras)
    elif encoding == "roman":
        return "".join(a.roman for a in aksaras)
    else:
        raise ValueError(f"Unknown encoding: {encoding}")


def get_aksara_count(word: str) -> int:
    """
    Count syllables in a word (approximate).
    Sanskrit syllable = consonant cluster + vowel
    """
    # Simple heuristic: count vowels
    vowels = "aāiīuūṛṝeoai"
    return sum(1 for c in word.lower() if c in vowels)


__all__ = [
    "Aksara",
    # Mahamantra syllables
    "AKSARA_HA",
    "AKSARA_RE",
    "AKSARA_KRI",
    "AKSARA_SHNA",
    "AKSARA_RAA",
    "AKSARA_MA",
    "MAHAMANTRA_AKSARAS",
    # Word decompositions
    "HARE_AKSARAS",
    "KRISHNA_AKSARAS",
    "RAMA_AKSARAS",
    # Functions
    "join_aksaras",
    "get_aksara_count",
]
