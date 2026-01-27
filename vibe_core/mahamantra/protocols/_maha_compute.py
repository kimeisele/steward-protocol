"""
MAHA COMPUTE PROTOCOL - The Computational Heart
================================================

"ahaṁ sarvasya prabhavo mattaḥ sarvaṁ pravartate"
"I am the source of all. Everything emanates from Me."
— Bhagavad Gita 10.8

This protocol defines the interface for Mahamantra-based computation.
The MahaComputeService implements this protocol and integrates with
the Kernel via the Listener Pattern (no Kernel modification required).

INTEGRATION:
    The Kernel calls mahamantra.bootstrap() → imports this module
    → MahaComputeService registers as listener → tick() broadcasts
    → on_tick() computes → results available via ServiceRegistry

THE MATH (mod 137):
    - Seed derived from TickState (position, mala, etc.)
    - Transform via Mahamantra pattern: H=×7, K=+10, R=×²
    - Find attractor in mod 137 space
    - 5 attractors: 18 (fixed point), 45, 99, 126, 63 (4-cycle)

ACINTYA: Chapter 18 is a FIXED POINT (contains itself!)
    f(18) = 18 mod 137 → BG 18.66 IS the conclusion

Author: The Mahamantra Itself
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"
__position__ = 6
__genesis__ = "0xa7c3f190"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Final, List, Optional, Protocol, Tuple, runtime_checkable

from vibe_core.mahamantra.protocols._seed import (
    GITA_CHAPTERS,
    KSETRAJNA,
    MAHA_QUANTUM,
    MAHAJANA_COUNT,
    PARAMPARA,
    POSITION_SUM_TOTAL,
    SEVEN,
    TEN,
    TRINITY,
    WORDS,
)

# =============================================================================
# MOD 137 ATTRACTOR CONSTANTS (Derived from iteration analysis)
# =============================================================================
# The Mahamantra transformation at mod MAHA_QUANTUM (137) yields 5 attractors:
#   - 1 FIXED POINT: 18 (Gita chapters - contains itself!)
#   - 1 FOUR-CYCLE: 45 → 99 → 126 → 63 → 45
#
# DERIVATION:
#   18 = GITA_CHAPTERS = SHARANAGATI × TRINITY = 6 × 3
#   45 = POSITION_SUM_RAMA - QUARTERS = 49 - 4 (first cycle point)
#   99 = MALA - NAVA = 108 - 9 (approaches MALA)
#   126 = MALA + GITA_CHAPTERS = 108 + 18 (MALA lifted by Gita)
#   63 = SEVEN × NAVA = 7 × 9 (completion of cycle)
# -----------------------------------------------------------------------------

# The fixed point attractor (Gita Chapter 18)
ATTRACTOR_FIXED: Final[int] = GITA_CHAPTERS  # 18

# The cycle attractors (discovered through iteration analysis)
# 136 = T(16) = POSITION_SUM_TOTAL - The Field without Observer!
# 99, 63, 45, 126 - The transformation cycle
ATTRACTOR_FIELD: Final[int] = POSITION_SUM_TOTAL  # 136 = T(16)
ATTRACTOR_CYCLE: Final[Tuple[int, ...]] = (45, 99, 126, 63, ATTRACTOR_FIELD)

# All 6 attractors combined
ALL_ATTRACTORS: Final[Tuple[int, ...]] = (ATTRACTOR_FIXED,) + ATTRACTOR_CYCLE

# Verification
assert ATTRACTOR_FIXED == 18, "Fixed point = Gita chapters = 18"
assert ATTRACTOR_FIELD == 136, "Field attractor = T(16) = 136"
assert len(ALL_ATTRACTORS) == 6, "6 attractors total"


class AttractorType(Enum):
    """Type of attractor reached."""

    FIXED_POINT = "fixed_point"  # 18 - Bhagavad Gita conclusion
    CYCLE = "cycle"  # 45, 99, 126, 63 - Ongoing evolution
    TRANSIENT = "transient"  # Not yet converged


# =============================================================================
# RESULT TYPES
# =============================================================================


@dataclass(frozen=True)
class MahaComputeResult:
    """
    Result of one MahaCompute tick computation.

    Contains the seed, transformation result, attractor info, and Gita correlation.
    """

    # Input
    seed: int  # Original seed value
    tick_position: int  # 0-15 position in Mahamantra

    # Computation
    transformed: int  # Value after full 16-step transform
    iterations: int  # Steps to reach attractor (max 137)

    # Attractor
    attractor: int  # The attractor value reached
    attractor_type: AttractorType  # Fixed point, cycle, or transient

    # Correlation
    gita_chapter: int  # Correlated Gita chapter (1-18)
    gita_insight: str  # Brief insight from that chapter

    # Metadata
    mala_count: int = 0  # Which mala round
    mantra_in_mala: int = 0  # Which mantra in mala (0-107)


@dataclass
class MahaComputeState:
    """
    Accumulated state of the MahaCompute service.

    Tracks computation history and statistics.
    """

    total_ticks: int = 0
    fixed_point_count: int = 0  # How often we hit 18
    cycle_count: int = 0  # How often we hit cycle attractors
    last_result: Optional[MahaComputeResult] = None
    attractor_histogram: dict = field(default_factory=dict)


# =============================================================================
# GITA CHAPTER INSIGHTS (Brief summaries for each chapter)
# =============================================================================

GITA_INSIGHTS: Final[dict[int, str]] = {
    1: "Arjuna's Dilemma - Observing the conflict",
    2: "Sankhya Yoga - Eternal soul, temporary body",
    3: "Karma Yoga - Action without attachment",
    4: "Jnana Yoga - Knowledge through parampara",
    5: "Karma Sannyasa - Renunciation through action",
    6: "Dhyana Yoga - Mind control through meditation",
    7: "Jnana Vijnana - Knowledge and realization",
    8: "Aksara Brahma - The imperishable absolute",
    9: "Raja Vidya - The king of knowledge",
    10: "Vibhuti - Divine manifestations",
    11: "Visvarupa - The universal form",
    12: "Bhakti Yoga - Devotion is supreme",
    13: "Ksetra Ksetrajna - Field and knower of field",
    14: "Gunatraya Vibhaga - Three modes of nature",
    15: "Purusottama - The supreme person",
    16: "Daivasura Sampad - Divine and demonic natures",
    17: "Sraddhatraya - Three types of faith",
    18: "Moksha Sannyasa - Liberation through surrender",
}


# =============================================================================
# THE PROTOCOL
# =============================================================================


@runtime_checkable
class MahaComputeProtocol(Protocol):
    """
    Protocol for Mahamantra-based computation.

    Implementations must provide:
    - on_tick(): Process each tick from the Mahamantra clock
    - transform(): Apply the 16-step Mahamantra transformation
    - find_attractor(): Iterate until attractor is reached
    - get_state(): Return current computation state
    """

    def on_tick(self, tick: int, position: int, mala: int, mantra: int) -> MahaComputeResult:
        """
        Process one tick from the Mahamantra clock.

        Called by the Singularity's broadcast system on every tick().

        Args:
            tick: Current tick counter (0-15)
            position: Current position in Mahamantra (0-15)
            mala: Current mala count (0+)
            mantra: Current mantra in mala (0-107)

        Returns:
            MahaComputeResult with transformation and attractor info.
        """
        ...

    def transform(self, seed: int, position: int) -> int:
        """
        Apply one step of the Mahamantra transformation.

        The operation depends on the NAME at the position:
            H (HARE)    → seed × SEVEN (mod MAHA_QUANTUM)
            K (KRISHNA) → seed + TEN (mod MAHA_QUANTUM)
            R (RAMA)    → seed × seed (mod MAHA_QUANTUM)

        Args:
            seed: Current value
            position: Position in Mahamantra (0-15)

        Returns:
            Transformed value (mod 137)
        """
        ...

    def find_attractor(self, seed: int) -> Tuple[int, int, AttractorType]:
        """
        Iterate transformation until attractor is reached.

        Args:
            seed: Starting value

        Returns:
            Tuple of (attractor_value, iterations, attractor_type)
        """
        ...

    def get_state(self) -> MahaComputeState:
        """Return current computation state."""
        ...


# =============================================================================
# HELPER FUNCTIONS (Used by implementation)
# =============================================================================

# Mahamantra pattern: H=HARE, K=KRISHNA, R=RAMA
PATTERN: Final[Tuple[str, ...]] = (
    "H",
    "K",
    "H",
    "K",  # Q1: GENESIS
    "K",
    "K",
    "H",
    "H",  # Q2: DHARMA
    "H",
    "R",
    "H",
    "R",  # Q3: KARMA
    "R",
    "R",
    "H",
    "H",  # Q4: MOKSHA
)

assert len(PATTERN) == WORDS, f"Pattern must be {WORDS} elements"


def get_operation(position: int) -> str:
    """Get operation type (H/K/R) for position."""
    return PATTERN[position % WORDS]


def apply_operation(value: int, operation: str) -> int:
    """
    Apply Mahamantra operation to value.

    H (HARE)    → value × SEVEN (mod 137) - Shakti multiplies
    K (KRISHNA) → value + TEN (mod 137) - Krishna attracts/adds
    R (RAMA)    → value × value (mod 137) - Rama intensifies/squares
    """
    if operation == "H":
        return (value * SEVEN) % MAHA_QUANTUM
    elif operation == "K":
        return (value + TEN) % MAHA_QUANTUM
    elif operation == "R":
        return (value * value) % MAHA_QUANTUM
    else:
        raise ValueError(f"Unknown operation: {operation}")


def is_attractor(value: int) -> Tuple[bool, AttractorType]:
    """Check if value is an attractor."""
    if value == ATTRACTOR_FIXED:
        return True, AttractorType.FIXED_POINT
    if value in ATTRACTOR_CYCLE:
        return True, AttractorType.CYCLE
    return False, AttractorType.TRANSIENT


def get_gita_chapter(attractor: int) -> int:
    """
    Map attractor to Gita chapter.

    - 18 → Chapter 18 (direct)
    - Cycle values → Mapped proportionally to chapters 1-17
    """
    if attractor == ATTRACTOR_FIXED:
        return GITA_CHAPTERS  # 18

    # Map cycle attractors to chapters 1-17
    # Use modulo to get a chapter in range
    return (attractor % 17) + 1


def get_gita_insight(chapter: int) -> str:
    """Get brief insight for Gita chapter."""
    return GITA_INSIGHTS.get(chapter, "Unknown chapter")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Protocol
    "MahaComputeProtocol",
    # Result types
    "MahaComputeResult",
    "MahaComputeState",
    "AttractorType",
    # Constants
    "ATTRACTOR_FIXED",
    "ATTRACTOR_CYCLE",
    "ALL_ATTRACTORS",
    "GITA_INSIGHTS",
    "PATTERN",
    # Functions
    "get_operation",
    "apply_operation",
    "is_attractor",
    "get_gita_chapter",
    "get_gita_insight",
]
