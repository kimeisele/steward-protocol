"""
PADA (पद) - The Word Unit
==========================

"pada" = word, foot, quarter

The three transcendental seeds of the Mahamantra:
- HARE (हरे) - Addressing the Energy (Shakti)
- KRISHNA (कृष्ण) - The All-Attractive (Bhagavan)
- RAMA (राम) - The Source of Pleasure (Bhagavan)

"The word Hara is the form of addressing the energy of the Lord,
and the words Krishna and Rama are forms of addressing the Lord Himself."
- Srila Prabhupada

STRUCTURE:
- Each Pada contains Aksaras (syllables)
- Each Aksara contains Varnas (letters)
- The fractal: Varna → Aksara → Pada → Vakya (Mantra)
"""

from dataclasses import dataclass, field
from typing import Final, Tuple, List
from enum import IntEnum

from .aksara import (
    Aksara,
    HARE_AKSARAS,
    KRISHNA_AKSARAS,
    RAMA_AKSARAS,
    join_aksaras,
)


class PadaType(IntEnum):
    """The three types of words in the Mahamantra."""
    HARE = 0      # Addressing Shakti (Energy)
    KRISHNA = 1   # Addressing Bhagavan (All-Attractive)
    RAMA = 2      # Addressing Bhagavan (Pleasure)
    VOID = 3      # Error/Maya


@dataclass(frozen=True)
class Pada:
    """
    A word - the transcendental seed.

    Attributes:
        pada_type: HARE, KRISHNA, or RAMA
        aksaras: Component syllables
        meaning: Philosophical meaning
    """
    pada_type: PadaType
    aksaras: Tuple[Aksara, ...]
    meaning: str = ""

    @property
    def devanagari(self) -> str:
        """Original Sanskrit script."""
        return join_aksaras(self.aksaras, "devanagari")

    @property
    def iast(self) -> str:
        """IAST transliteration."""
        return join_aksaras(self.aksaras, "iast")

    @property
    def roman(self) -> str:
        """Western representation."""
        return join_aksaras(self.aksaras, "roman")

    @property
    def syllable_count(self) -> int:
        """Number of syllables."""
        return len(self.aksaras)

    def __str__(self) -> str:
        return self.iast

    def __repr__(self) -> str:
        return f"Pada({self.iast!r}, {self.pada_type.name})"


# =============================================================================
# THE THREE TRANSCENDENTAL SEEDS
# =============================================================================

PADA_HARE: Final[Pada] = Pada(
    pada_type=PadaType.HARE,
    aksaras=HARE_AKSARAS,
    meaning="O Energy of the Lord! Please engage me in service.",
)

PADA_KRISHNA: Final[Pada] = Pada(
    pada_type=PadaType.KRISHNA,
    aksaras=KRISHNA_AKSARAS,
    meaning="O All-Attractive One! You are the source of all pleasure.",
)

PADA_RAMA: Final[Pada] = Pada(
    pada_type=PadaType.RAMA,
    aksaras=RAMA_AKSARAS,
    meaning="O Source of Pleasure! Give me strength to serve.",
)

# Lookup by type
PADA_BY_TYPE: Final[dict] = {
    PadaType.HARE: PADA_HARE,
    PadaType.KRISHNA: PADA_KRISHNA,
    PadaType.RAMA: PADA_RAMA,
}


# =============================================================================
# THE MAHAMANTRA SEQUENCE (16 words)
# =============================================================================

# Hare Krishna Hare Krishna Krishna Krishna Hare Hare
# Hare Rama Hare Rama Rama Rama Hare Hare

MAHAMANTRA_SEQUENCE: Final[Tuple[Pada, ...]] = (
    # Quarter 1: Hare Krishna Hare Krishna
    PADA_HARE, PADA_KRISHNA, PADA_HARE, PADA_KRISHNA,
    # Quarter 2: Krishna Krishna Hare Hare
    PADA_KRISHNA, PADA_KRISHNA, PADA_HARE, PADA_HARE,
    # Quarter 3: Hare Rama Hare Rama
    PADA_HARE, PADA_RAMA, PADA_HARE, PADA_RAMA,
    # Quarter 4: Rama Rama Hare Hare
    PADA_RAMA, PADA_RAMA, PADA_HARE, PADA_HARE,
)


def get_pada(pada_type: PadaType) -> Pada:
    """Get a Pada by type."""
    return PADA_BY_TYPE.get(pada_type, PADA_HARE)


def mahamantra_to_string(encoding: str = "iast", separator: str = " ") -> str:
    """Convert the full Mahamantra to string."""
    if encoding == "devanagari":
        return separator.join(p.devanagari for p in MAHAMANTRA_SEQUENCE)
    elif encoding == "iast":
        return separator.join(p.iast for p in MAHAMANTRA_SEQUENCE)
    elif encoding == "roman":
        return separator.join(p.roman for p in MAHAMANTRA_SEQUENCE)
    else:
        raise ValueError(f"Unknown encoding: {encoding}")


def count_padas() -> dict:
    """Count occurrences of each pada in the Mahamantra."""
    return {
        "hare": sum(1 for p in MAHAMANTRA_SEQUENCE if p.pada_type == PadaType.HARE),
        "krishna": sum(1 for p in MAHAMANTRA_SEQUENCE if p.pada_type == PadaType.KRISHNA),
        "rama": sum(1 for p in MAHAMANTRA_SEQUENCE if p.pada_type == PadaType.RAMA),
    }


__all__ = [
    "PadaType",
    "Pada",
    # The three seeds
    "PADA_HARE",
    "PADA_KRISHNA",
    "PADA_RAMA",
    "PADA_BY_TYPE",
    # Full mantra
    "MAHAMANTRA_SEQUENCE",
    # Functions
    "get_pada",
    "mahamantra_to_string",
    "count_padas",
]
