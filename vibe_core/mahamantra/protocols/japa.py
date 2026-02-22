from typing import Protocol, runtime_checkable, List, Optional
from vibe_core.mahamantra.protocols._seed import KSETRAJNA
from dataclasses import dataclass
from enum import Enum


@runtime_checkable
class MahaJapaProtocol(Protocol):
    """
    Protocol for MahaJapa: The Mathematics of Hearing and Chanting.

    Simulates the 108-round mala cycle and collapse detection.
    """

    def round(self, seed: int, round_number: int = KSETRAJNA) -> "RoundResult":
        """Execute a single japa round."""
        ...

    def mala(self, seed: int = 0) -> "MalaResult":
        """Execute a complete mala (108 rounds)."""
        ...

    def golden_age_status(self, current_year: Optional[int] = None) -> "GoldenAgeStatus":
        """Get the status of the Golden Age."""
        ...

    def is_collapsed(self, value: int) -> "CollapseResult":
        """Check if a value represents the collapsed state."""
        ...

    def nava_vidha(self) -> List[str]:
        """Get the 9 processes of devotional service."""
        ...

    def humility_qualities(self) -> List[str]:
        """Get the 4 qualities of humility."""
        ...

    def constants(self) -> dict:
        """Get all japa constants."""
        ...


class JapaState(Enum):
    """State of the japa process."""

    HEARING = "hearing"
    CHANTING = "chanting"
    PRASADAM = "prasadam"
    COLLAPSED = "collapsed"


@dataclass(frozen=True)
class RoundResult:
    """Result of a single japa round."""

    round_number: int
    seed: int
    hearing: int
    chanting: int
    prasadam: int
    state: JapaState
    value: int

    @property
    def is_collapsed(self) -> bool: ...


@dataclass(frozen=True)
class MalaResult:
    """Result of a complete mala."""

    rounds: int
    seed: int
    final_value: int
    final_state: JapaState
    collapse_count: int
    total_prasadam: int
    attractor: Optional[int]

    @property
    def is_complete(self) -> bool: ...
    @property
    def collapse_ratio(self) -> float: ...


@dataclass(frozen=True)
class GoldenAgeStatus:
    """Status of the Golden Age."""

    start_year: int
    end_year: int
    current_year: int

    @property
    def years_elapsed(self) -> int:
        return self.current_year - self.start_year

    @property
    def years_remaining(self) -> int:
        return max(0, self.end_year - self.current_year)

    @property
    def progress_percent(self) -> float:
        total = self.end_year - self.start_year
        if total == 0:
            return 0.0
        return (self.years_elapsed / total) * 100.0

    @property
    def is_active(self) -> bool:
        return self.start_year <= self.current_year <= self.end_year

    @property
    def formula(self) -> str:
        return f"{self.years_elapsed} / {self.end_year - self.start_year} years"


@dataclass(frozen=True)
class CollapseResult:
    """Result of collapse detection."""

    is_collapsed: bool
    input_value: int
    collapse_value: int
    prasadam: int
    kshetra: int
    ksetrajna: int
    interpretation: str

    @property
    def formula(self) -> str:
        return f"{self.prasadam} - {self.kshetra} = {self.ksetrajna}"
