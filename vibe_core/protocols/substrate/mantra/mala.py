"""
MALA (माला) - The Round Level
=============================

"mala" = garland, rosary, necklace

One round = 108 mantras (vakyas)

SACRED NUMBERS:
    108 = 1 × 2² × 3³ = 1 × 4 × 27
    108 = 12 × 9 (12 zodiac signs × 9 planets)
    108 = 27 × 4 (27 nakshatras × 4 quarters)

JAPA MALA STRUCTURE:
    - 108 beads for counting mantras
    - 1 sumeru bead (the mount, not counted)
    - Turn at sumeru, never cross it

COMPUTATIONAL MAPPING:
    Mala = Round (108 instructions = one execution cycle)

THE 37 FORMULA AT MALA LEVEL:
    108 = 3 × 36 = 3 × (24 + 12) = 3 × 37 - 3
    Or: 108 / 3 = 36, 36 + 1 = 37
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0x0e429509"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from typing import Final, Tuple, List, Iterator, Optional
from enum import IntEnum

from .vakya import Vakya, MAHAMANTRA, create_vakya
from .pada import Pada
from .aksara import Aksara


# Sacred dimensions
BEADS_PER_MALA: Final[int] = 108
SUMERU_COUNT: Final[int] = 1  # The mount bead


class MalaPhase(IntEnum):
    """Phases within a mala (for tracking progress)."""

    BEGINNING = 0  # 1-27: Establishing connection
    ASCENDING = 1  # 28-54: Building momentum
    PEAK = 2  # 55-81: Deep absorption
    COMPLETING = 3  # 82-108: Integration


@dataclass
class Mala:
    """
    One round of japa (108 mantras).

    The fundamental unit of sadhana practice.

    Attributes:
        round_number: Which round (1-16 in standard sadhana)
        current_count: Current position in the mala (1-108)
        completed: Whether this mala is finished
    """

    round_number: int = 1
    current_count: int = 0
    completed: bool = False

    # Internal state
    _vakyas: List[Vakya] = field(default_factory=list, repr=False)

    def __post_init__(self):
        """Initialize the 108 vakyas."""
        if not self._vakyas:
            self._vakyas = [create_vakya(i + 1) for i in range(BEADS_PER_MALA)]

    @property
    def total_mantras(self) -> int:
        """Total mantras in a mala (always 108)."""
        return BEADS_PER_MALA

    @property
    def total_words(self) -> int:
        """Total words in a mala (108 × 16 = 1728)."""
        return BEADS_PER_MALA * 16

    @property
    def total_syllables(self) -> int:
        """Total syllables in a mala (108 × 32 = 3456)."""
        return BEADS_PER_MALA * 32

    @property
    def phase(self) -> MalaPhase:
        """Current phase based on count."""
        if self.current_count <= 27:
            return MalaPhase.BEGINNING
        elif self.current_count <= 54:
            return MalaPhase.ASCENDING
        elif self.current_count <= 81:
            return MalaPhase.PEAK
        else:
            return MalaPhase.COMPLETING

    @property
    def progress(self) -> float:
        """Progress as percentage (0.0 - 1.0)."""
        return self.current_count / BEADS_PER_MALA

    @property
    def remaining(self) -> int:
        """Mantras remaining."""
        return BEADS_PER_MALA - self.current_count

    def chant_one(self) -> Optional[Vakya]:
        """
        Chant one mantra, advancing the count.

        Returns:
            The vakya chanted, or None if mala is complete
        """
        if self.completed:
            return None

        vakya = self._vakyas[self.current_count]
        self.current_count += 1

        if self.current_count >= BEADS_PER_MALA:
            self.completed = True

        return vakya

    def get_vakya(self, index: int) -> Vakya:
        """Get vakya at specific position (0-107)."""
        if 0 <= index < BEADS_PER_MALA:
            return self._vakyas[index]
        raise IndexError(f"Invalid vakya index: {index}")

    def reset(self) -> None:
        """Reset the mala for another round."""
        self.current_count = 0
        self.completed = False

    def __iter__(self) -> Iterator[Vakya]:
        """Iterate through all 108 vakyas."""
        return iter(self._vakyas)

    def __len__(self) -> int:
        return BEADS_PER_MALA

    def __repr__(self) -> str:
        return f"Mala(round={self.round_number}, count={self.current_count}/{BEADS_PER_MALA})"


# =============================================================================
# MALA METRICS
# =============================================================================


@dataclass(frozen=True)
class MalaMetrics:
    """
    Statistics for a mala.

    The 37 formula manifests here:
    - 108 mantras contain patterns of 37
    """

    total_mantras: int = BEADS_PER_MALA
    total_words: int = BEADS_PER_MALA * 16  # 1728
    total_syllables: int = BEADS_PER_MALA * 32  # 3456
    total_hare: int = BEADS_PER_MALA * 8  # 864
    total_krishna: int = BEADS_PER_MALA * 4  # 432
    total_rama: int = BEADS_PER_MALA * 4  # 432

    @property
    def formula_37(self) -> dict:
        """The 37 formula at mala level."""
        return {
            "mantras_div_3": self.total_mantras // 3,  # 36
            "plus_one": (self.total_mantras // 3) + 1,  # 37
            "words_mod_37": self.total_words % 37,  # 1728 % 37 = 28
            "syllables_mod_37": self.total_syllables % 37,  # 3456 % 37 = 13
        }


MALA_METRICS: Final[MalaMetrics] = MalaMetrics()


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================


def create_mala(round_number: int = 1) -> Mala:
    """Create a new mala for a specific round."""
    return Mala(round_number=round_number)


def iter_mala_vakyas(mala: Optional[Mala] = None) -> Iterator[Vakya]:
    """Iterate through vakyas in a mala."""
    m = mala or create_mala()
    yield from m


def get_phase_name(phase: MalaPhase) -> str:
    """Get human-readable phase name."""
    names = {
        MalaPhase.BEGINNING: "Establishing Connection",
        MalaPhase.ASCENDING: "Building Momentum",
        MalaPhase.PEAK: "Deep Absorption",
        MalaPhase.COMPLETING: "Integration",
    }
    return names.get(phase, "Unknown")


__all__ = [
    "BEADS_PER_MALA",
    "SUMERU_COUNT",
    "MalaPhase",
    "Mala",
    "MalaMetrics",
    "MALA_METRICS",
    # Functions
    "create_mala",
    "iter_mala_vakyas",
    "get_phase_name",
]
