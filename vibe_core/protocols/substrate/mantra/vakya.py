"""
VAKYA (वाक्य) - The Mantra Level
================================

"vakya" = sentence, statement, utterance

One complete Mahamantra = 16 words (padas)

STRUCTURE:
    4 quarters × 4 words = 16 words

QUARTER PATTERN:
    Q1: Hare Krishna Hare Krishna  (addressing Krishna)
    Q2: Krishna Krishna Hare Hare  (glorifying Krishna)
    Q3: Hare Rama Hare Rama        (addressing Rama)
    Q4: Rama Rama Hare Hare        (glorifying Rama)

COMPUTATIONAL MAPPING:
    Vakya = Instruction (16 opcodes = one complete instruction set)
"""

from dataclasses import dataclass, field
from typing import Final, Tuple, List, Iterator, Optional
from enum import IntEnum

from .pada import Pada, PadaType, MAHAMANTRA_SEQUENCE, PADA_BY_TYPE
from .aksara import Aksara


class QuarterType(IntEnum):
    """The four quarters of the Mahamantra."""
    KRISHNA_ADDRESS = 0   # Q1: Hare Krishna Hare Krishna
    KRISHNA_GLORIFY = 1   # Q2: Krishna Krishna Hare Hare
    RAMA_ADDRESS = 2      # Q3: Hare Rama Hare Rama
    RAMA_GLORIFY = 3      # Q4: Rama Rama Hare Hare


@dataclass(frozen=True)
class Quarter:
    """
    One quarter of the Mahamantra (4 words).

    Attributes:
        quarter_type: Which quarter (0-3)
        padas: The 4 words in this quarter
    """
    quarter_type: QuarterType
    padas: Tuple[Pada, Pada, Pada, Pada]

    @property
    def devanagari(self) -> str:
        """Original Sanskrit script."""
        return " ".join(p.devanagari for p in self.padas)

    @property
    def iast(self) -> str:
        """IAST transliteration."""
        return " ".join(p.iast for p in self.padas)

    @property
    def roman(self) -> str:
        """Western representation."""
        return " ".join(p.roman for p in self.padas)

    @property
    def aksaras(self) -> Tuple[Aksara, ...]:
        """All syllables in this quarter."""
        result = []
        for pada in self.padas:
            result.extend(pada.aksaras)
        return tuple(result)

    def __str__(self) -> str:
        return self.iast

    def __iter__(self) -> Iterator[Pada]:
        return iter(self.padas)

    def __len__(self) -> int:
        return 4


# =============================================================================
# THE FOUR QUARTERS
# =============================================================================

QUARTER_1: Final[Quarter] = Quarter(
    quarter_type=QuarterType.KRISHNA_ADDRESS,
    padas=(MAHAMANTRA_SEQUENCE[0], MAHAMANTRA_SEQUENCE[1],
           MAHAMANTRA_SEQUENCE[2], MAHAMANTRA_SEQUENCE[3]),
)

QUARTER_2: Final[Quarter] = Quarter(
    quarter_type=QuarterType.KRISHNA_GLORIFY,
    padas=(MAHAMANTRA_SEQUENCE[4], MAHAMANTRA_SEQUENCE[5],
           MAHAMANTRA_SEQUENCE[6], MAHAMANTRA_SEQUENCE[7]),
)

QUARTER_3: Final[Quarter] = Quarter(
    quarter_type=QuarterType.RAMA_ADDRESS,
    padas=(MAHAMANTRA_SEQUENCE[8], MAHAMANTRA_SEQUENCE[9],
           MAHAMANTRA_SEQUENCE[10], MAHAMANTRA_SEQUENCE[11]),
)

QUARTER_4: Final[Quarter] = Quarter(
    quarter_type=QuarterType.RAMA_GLORIFY,
    padas=(MAHAMANTRA_SEQUENCE[12], MAHAMANTRA_SEQUENCE[13],
           MAHAMANTRA_SEQUENCE[14], MAHAMANTRA_SEQUENCE[15]),
)

QUARTERS: Final[Tuple[Quarter, ...]] = (QUARTER_1, QUARTER_2, QUARTER_3, QUARTER_4)


@dataclass(frozen=True)
class Vakya:
    """
    One complete Mahamantra (16 words).

    The atomic unit of japa (chanting meditation).
    One bead on the mala = one vakya.

    Attributes:
        quarters: The 4 quarters (each with 4 words)
        count: Which repetition (1-108 in a mala, or absolute count)
    """
    quarters: Tuple[Quarter, Quarter, Quarter, Quarter] = field(
        default=(QUARTER_1, QUARTER_2, QUARTER_3, QUARTER_4)
    )
    count: int = 1  # Which repetition

    @property
    def padas(self) -> Tuple[Pada, ...]:
        """All 16 words."""
        result = []
        for quarter in self.quarters:
            result.extend(quarter.padas)
        return tuple(result)

    @property
    def aksaras(self) -> Tuple[Aksara, ...]:
        """All 32 syllables."""
        result = []
        for quarter in self.quarters:
            result.extend(quarter.aksaras)
        return tuple(result)

    @property
    def devanagari(self) -> str:
        """Full mantra in Devanagari."""
        return " ".join(p.devanagari for p in self.padas)

    @property
    def iast(self) -> str:
        """Full mantra in IAST."""
        return " ".join(p.iast for p in self.padas)

    @property
    def roman(self) -> str:
        """Full mantra in Roman."""
        return " ".join(p.roman for p in self.padas)

    @property
    def word_count(self) -> int:
        """Number of words (always 16)."""
        return 16

    @property
    def syllable_count(self) -> int:
        """Number of syllables (always 32)."""
        return 32

    def get_quarter(self, index: int) -> Quarter:
        """Get quarter by index (0-3)."""
        if 0 <= index < 4:
            return self.quarters[index]
        raise IndexError(f"Invalid quarter index: {index}")

    def get_pada(self, index: int) -> Pada:
        """Get word by index (0-15)."""
        if 0 <= index < 16:
            return self.padas[index]
        raise IndexError(f"Invalid pada index: {index}")

    def __str__(self) -> str:
        return self.iast

    def __repr__(self) -> str:
        return f"Vakya(count={self.count})"

    def __iter__(self) -> Iterator[Pada]:
        return iter(self.padas)

    def __len__(self) -> int:
        return 16


# =============================================================================
# THE STANDARD MAHAMANTRA
# =============================================================================

MAHAMANTRA: Final[Vakya] = Vakya()


def create_vakya(count: int = 1) -> Vakya:
    """Create a Vakya with specific count."""
    return Vakya(count=count)


def iter_vakya_quarters(vakya: Optional[Vakya] = None) -> Iterator[Quarter]:
    """Iterate through quarters of a vakya."""
    v = vakya or MAHAMANTRA
    yield from v.quarters


def iter_vakya_padas(vakya: Optional[Vakya] = None) -> Iterator[Pada]:
    """Iterate through padas of a vakya."""
    v = vakya or MAHAMANTRA
    yield from v.padas


__all__ = [
    "QuarterType",
    "Quarter",
    "Vakya",
    # The four quarters
    "QUARTER_1",
    "QUARTER_2",
    "QUARTER_3",
    "QUARTER_4",
    "QUARTERS",
    # The standard mantra
    "MAHAMANTRA",
    # Functions
    "create_vakya",
    "iter_vakya_quarters",
    "iter_vakya_padas",
]
