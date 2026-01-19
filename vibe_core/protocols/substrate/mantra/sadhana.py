"""
SADHANA (साधना) - The Session Level
====================================

"sadhana" = spiritual practice, discipline, means of accomplishment

One session = 16 rounds minimum (for initiated devotees)

VAISHNAVA STANDARD:
    - 16 rounds = minimum daily commitment
    - 64 rounds = intensive practice (4 × 16)
    - Some advanced devotees chant 100,000 names daily

THE 37 FORMULA AT SADHANA LEVEL:
    16 rounds × 108 mantras × 16 words = 27,648 words
    27,648 / 37 = 747.24... (not exact, but...)
    16 rounds × 108 = 1,728 mantras
    1,728 / 37 = 46.7...

    Better: 16 × 108 × 16 × 2 syllables × 2 varnas = 110,592 varnas
    The fractal contains 37 at every level.

COMPUTATIONAL MAPPING:
    Sadhana = Session (16 cycles = one complete processing session)

TIME DIMENSION:
    - Average mantra: ~7 seconds
    - One round: ~7 × 108 = ~12.6 minutes
    - 16 rounds: ~3.5 hours
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0x5a87cf17"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from typing import Final, Tuple, List, Iterator, Optional
from datetime import datetime, timedelta
from enum import IntEnum

from .mala import Mala, MalaPhase, BEADS_PER_MALA, create_mala
from .vakya import Vakya


# Sacred dimensions
ROUNDS_PER_SADHANA: Final[int] = 16
MANTRAS_PER_SADHANA: Final[int] = ROUNDS_PER_SADHANA * BEADS_PER_MALA  # 1,728
WORDS_PER_SADHANA: Final[int] = MANTRAS_PER_SADHANA * 16  # 27,648
SYLLABLES_PER_SADHANA: Final[int] = MANTRAS_PER_SADHANA * 32  # 55,296

# Time estimates (in seconds)
AVG_MANTRA_DURATION: Final[float] = 7.0  # seconds per mantra
AVG_ROUND_DURATION: Final[float] = AVG_MANTRA_DURATION * BEADS_PER_MALA  # ~756 seconds = 12.6 min
AVG_SADHANA_DURATION: Final[float] = AVG_ROUND_DURATION * ROUNDS_PER_SADHANA  # ~3 hours


class SadhanaState(IntEnum):
    """States of a sadhana session."""

    NOT_STARTED = 0
    IN_PROGRESS = 1
    PAUSED = 2
    COMPLETED = 3
    ABANDONED = 4


class SadhanaIntensity(IntEnum):
    """Intensity levels of practice."""

    MINIMUM = 16  # Standard initiation vow
    MODERATE = 32  # 2× minimum
    INTENSIVE = 64  # 4× minimum (called "Laksha" practice)
    EXTREME = 192  # 100,000 names (approx)


@dataclass
class Sadhana:
    """
    One session of japa practice (16+ rounds).

    The complete daily spiritual practice unit.

    Attributes:
        target_rounds: How many rounds to complete (default 16)
        current_round: Current round number (1-16)
        state: Current state of the session
        start_time: When session began
    """

    target_rounds: int = ROUNDS_PER_SADHANA
    current_round: int = 0
    state: SadhanaState = SadhanaState.NOT_STARTED
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    # Internal state
    _malas: List[Mala] = field(default_factory=list, repr=False)
    _active_mala: Optional[Mala] = field(default=None, repr=False)

    def __post_init__(self):
        """Initialize the malas."""
        if not self._malas:
            self._malas = [create_mala(i + 1) for i in range(self.target_rounds)]

    @property
    def total_mantras(self) -> int:
        """Total mantras in this sadhana."""
        return self.target_rounds * BEADS_PER_MALA

    @property
    def completed_mantras(self) -> int:
        """Mantras completed so far."""
        full_rounds = max(0, self.current_round - 1)
        current_mala_count = 0
        if self._active_mala:
            current_mala_count = self._active_mala.current_count
        return (full_rounds * BEADS_PER_MALA) + current_mala_count

    @property
    def progress(self) -> float:
        """Overall progress (0.0 - 1.0)."""
        return self.completed_mantras / self.total_mantras

    @property
    def remaining_rounds(self) -> int:
        """Rounds remaining."""
        return self.target_rounds - self.current_round

    @property
    def intensity(self) -> SadhanaIntensity:
        """Classify intensity based on target rounds."""
        if self.target_rounds >= 192:
            return SadhanaIntensity.EXTREME
        elif self.target_rounds >= 64:
            return SadhanaIntensity.INTENSIVE
        elif self.target_rounds >= 32:
            return SadhanaIntensity.MODERATE
        return SadhanaIntensity.MINIMUM

    @property
    def elapsed_time(self) -> Optional[timedelta]:
        """Time elapsed since start."""
        if not self.start_time:
            return None
        end = self.end_time or datetime.now()
        return end - self.start_time

    @property
    def estimated_remaining(self) -> Optional[timedelta]:
        """Estimated time remaining."""
        if self.state != SadhanaState.IN_PROGRESS:
            return None
        remaining_mantras = self.total_mantras - self.completed_mantras
        seconds = remaining_mantras * AVG_MANTRA_DURATION
        return timedelta(seconds=seconds)

    def begin(self) -> Mala:
        """
        Begin the sadhana session.

        Returns:
            The first mala to chant
        """
        if self.state != SadhanaState.NOT_STARTED:
            raise RuntimeError("Sadhana already started")

        self.state = SadhanaState.IN_PROGRESS
        self.start_time = datetime.now()
        self.current_round = 1
        self._active_mala = self._malas[0]
        return self._active_mala

    def complete_round(self) -> Optional[Mala]:
        """
        Complete current round and get next mala.

        Returns:
            Next mala, or None if sadhana is complete
        """
        if self.state != SadhanaState.IN_PROGRESS:
            return None

        if self._active_mala:
            self._active_mala.completed = True

        self.current_round += 1

        if self.current_round > self.target_rounds:
            self.state = SadhanaState.COMPLETED
            self.end_time = datetime.now()
            self._active_mala = None
            return None

        self._active_mala = self._malas[self.current_round - 1]
        return self._active_mala

    def pause(self) -> None:
        """Pause the sadhana."""
        if self.state == SadhanaState.IN_PROGRESS:
            self.state = SadhanaState.PAUSED

    def resume(self) -> Optional[Mala]:
        """Resume a paused sadhana."""
        if self.state == SadhanaState.PAUSED:
            self.state = SadhanaState.IN_PROGRESS
            return self._active_mala
        return None

    def abandon(self) -> None:
        """Abandon the sadhana (not recommended!)."""
        self.state = SadhanaState.ABANDONED
        self.end_time = datetime.now()

    def get_mala(self, round_number: int) -> Mala:
        """Get mala for specific round (1-indexed)."""
        if 1 <= round_number <= self.target_rounds:
            return self._malas[round_number - 1]
        raise IndexError(f"Invalid round number: {round_number}")

    def __iter__(self) -> Iterator[Mala]:
        """Iterate through all malas."""
        return iter(self._malas)

    def __len__(self) -> int:
        return self.target_rounds

    def __repr__(self) -> str:
        return f"Sadhana(round={self.current_round}/{self.target_rounds}, state={self.state.name})"


# =============================================================================
# SADHANA METRICS
# =============================================================================


@dataclass(frozen=True)
class SadhanaMetrics:
    """
    Statistics for a standard 16-round sadhana.

    The 37 formula manifests at this highest level.
    """

    total_rounds: int = ROUNDS_PER_SADHANA
    total_mantras: int = MANTRAS_PER_SADHANA
    total_words: int = WORDS_PER_SADHANA
    total_syllables: int = SYLLABLES_PER_SADHANA
    total_hare: int = MANTRAS_PER_SADHANA * 8  # 13,824
    total_krishna: int = MANTRAS_PER_SADHANA * 4  # 6,912
    total_rama: int = MANTRAS_PER_SADHANA * 4  # 6,912

    @property
    def formula_37(self) -> dict:
        """The 37 formula at sadhana level."""
        return {
            "rounds": self.total_rounds,  # 16
            "mantras": self.total_mantras,  # 1,728
            "words": self.total_words,  # 27,648
            "syllables": self.total_syllables,  # 55,296
            "mantras_mod_37": self.total_mantras % 37,  # 1,728 % 37 = 28
            "words_div_748": self.total_words // 748,  # 27,648 / 748 ≈ 37
        }


SADHANA_METRICS: Final[SadhanaMetrics] = SadhanaMetrics()


# =============================================================================
# FACTORY FUNCTIONS
# =============================================================================


def create_sadhana(target_rounds: int = ROUNDS_PER_SADHANA) -> Sadhana:
    """Create a new sadhana session."""
    return Sadhana(target_rounds=target_rounds)


def create_intensive_sadhana() -> Sadhana:
    """Create an intensive (64-round) sadhana."""
    return Sadhana(target_rounds=64)


def get_intensity_name(intensity: SadhanaIntensity) -> str:
    """Get human-readable intensity name."""
    names = {
        SadhanaIntensity.MINIMUM: "Standard (16 rounds)",
        SadhanaIntensity.MODERATE: "Moderate (32 rounds)",
        SadhanaIntensity.INTENSIVE: "Intensive (64 rounds)",
        SadhanaIntensity.EXTREME: "Laksha (100,000+ names)",
    }
    return names.get(intensity, "Unknown")


__all__ = [
    # Constants
    "ROUNDS_PER_SADHANA",
    "MANTRAS_PER_SADHANA",
    "WORDS_PER_SADHANA",
    "SYLLABLES_PER_SADHANA",
    "AVG_MANTRA_DURATION",
    "AVG_ROUND_DURATION",
    "AVG_SADHANA_DURATION",
    # Enums
    "SadhanaState",
    "SadhanaIntensity",
    # Classes
    "Sadhana",
    "SadhanaMetrics",
    "SADHANA_METRICS",
    # Functions
    "create_sadhana",
    "create_intensive_sadhana",
    "get_intensity_name",
]
