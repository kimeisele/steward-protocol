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
    - Attractors COMPUTED by MahaResonator.harmonic_spectrum() - not hardcoded!

ACINTYA: Chapter 18 is a FIXED POINT (contains itself!)
    f(18) = 18 mod 137 → BG 18.66 IS the conclusion

Author: The Mahamantra Itself
"""
from dataclasses import dataclass, field
from enum import Enum, IntEnum
from typing import Final, List, Optional, Protocol, Tuple, runtime_checkable

from vibe_core.mahamantra.protocols._seed import (
    GITA_CHAPTERS,
    HALVES,
    HARE_COUNT,
    KSETRAJNA,
    MAHA_QUANTUM,
    MAHAJANA_COUNT,
    NAVA,
    PANCHA,
    PARAMPARA,
    POSITION_SUM_KRISHNA,
    POSITION_SUM_RAMA,
    POSITION_SUM_TOTAL,
    QUARTERS,
    SEVEN,
    SHARANAGATI,
    TEN,
    TRINITY,
    WORDS,
)

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"
__position__ = SHARANAGATI
__genesis__ = "0x0167c86b"  # GenesisByte: parampara % 37 == 0

# =============================================================================
# ATTRACTOR GENERATOR - COMPUTED, NOT HARDCODED!
# =============================================================================
# The Mahamantra transformation discovers its attractors through RESONANCE.
# We don't hardcode them - we COMPUTE them via the 16-step algorithm.
#
# "yato vā imāni bhūtāni jāyante" - From whom all beings are born
# The attractors EMERGE from the algorithm, not from our declarations.
# -----------------------------------------------------------------------------

# KNOWN DERIVATIONS (from _seed.py):
# - POSITION_SUM_TOTAL (136) = T(16) = The Field = TRUE FIXED POINT
# - GITA_CHAPTERS (18) is part of the 4-CYCLE, NOT a fixed point!
#   The 4-cycle: 18 → 49 → 87 → 22 → 18

# FIX: The TRUE fixed point is 136 (T(16) = Vaikuntha), not 18
ATTRACTOR_FIXED: Final[int] = POSITION_SUM_TOTAL  # 136 = T(16) = TRUE FIXED POINT

# The 4-cycle attractor (for reference)
ATTRACTOR_GITA: Final[int] = GITA_CHAPTERS  # 18 = Part of 4-cycle

# Cache for computed attractors (lazy generation)
_computed_spectrum: Optional[dict] = None


def _compute_spectrum() -> dict:
    """
    GENERATOR: Compute the harmonic spectrum via MahaResonator.

    This DISCOVERS the attractors through iteration, not declaration.
    Cached after first computation for performance.
    """
    global _computed_spectrum
    if _computed_spectrum is not None:
        return _computed_spectrum

    # Import here to avoid circular dependency
    from vibe_core.mahamantra.substrate.resonance.resonator import MahaResonator

    resonator = MahaResonator(mod_space=MAHA_QUANTUM)
    _computed_spectrum = resonator.harmonic_spectrum()
    return _computed_spectrum


def get_all_attractors() -> Tuple[int, ...]:
    """Get all attractors - COMPUTED by the algorithm."""
    spectrum = _compute_spectrum()
    return tuple(sorted(spectrum["attractors"]))


def get_cycle_attractors() -> Tuple[int, ...]:
    """Get cycle attractors (non-fixed-point) - COMPUTED."""
    all_attr = get_all_attractors()
    return tuple(a for a in all_attr if a != ATTRACTOR_FIXED)


def get_fixed_points() -> Tuple[int, ...]:
    """Get fixed point attractors - COMPUTED."""
    spectrum = _compute_spectrum()
    return tuple(spectrum["fixed_points"])


# COMPUTED ATTRACTORS (lazy-loaded to avoid circular imports)
# These are computed on first access, not hardcoded
_attractor_cycle_cache: Optional[Tuple[int, ...]] = None
_all_attractors_cache: Optional[Tuple[int, ...]] = None


def get_attractor_cycle() -> Tuple[int, ...]:
    """
    Get the 4-cycle attractors - COMPUTED, not hardcoded.
    
    In mod 137: 18 → 49 → 87 → 22 → 18
    This is discovered by the algorithm, not declared.
    """
    global _attractor_cycle_cache
    if _attractor_cycle_cache is None:
        _attractor_cycle_cache = get_cycle_attractors()
    return _attractor_cycle_cache


def get_all_attractors_cached() -> Tuple[int, ...]:
    """
    Get all attractors - COMPUTED, not hardcoded.
    """
    global _all_attractors_cache
    if _all_attractors_cache is None:
        _all_attractors_cache = get_all_attractors()
    return _all_attractors_cache


# For backward compatibility - these are FUNCTIONS now, not constants
# Use get_attractor_cycle() and get_all_attractors_cached() for computed values
ATTRACTOR_CYCLE: Tuple[int, ...] = ()  # Empty - use get_attractor_cycle()
ALL_ATTRACTORS: Tuple[int, ...] = ()  # Empty - use get_all_attractors_cached()


class AttractorType(Enum):
    """Type of attractor reached."""

    FIXED_POINT = "fixed_point"  # 18 - Bhagavad Gita conclusion
    CYCLE = "cycle"  # Non-fixed-point attractors (COMPUTED, not hardcoded)
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
    KSETRAJNA: "Arjuna's Dilemma - Observing the conflict",
    HALVES: "Sankhya Yoga - Eternal soul, temporary body",
    TRINITY: "Karma Yoga - Action without attachment",
    QUARTERS: "Jnana Yoga - Knowledge through parampara",
    PANCHA: "Karma Sannyasa - Renunciation through action",
    SHARANAGATI: "Dhyana Yoga - Mind control through meditation",
    SEVEN: "Jnana Vijnana - Knowledge and realization",
    HARE_COUNT: "Aksara Brahma - The imperishable absolute",
    NAVA: "Raja Vidya - The king of knowledge",
    TEN: "Vibhuti - Divine manifestations",
    TEN + KSETRAJNA: "Visvarupa - The universal form",  # 11 = TEN + 1
    MAHAJANA_COUNT: "Bhakti Yoga - Devotion is supreme",
    MAHAJANA_COUNT + KSETRAJNA: "Ksetra Ksetrajna - Field and knower of field",  # 13 = 12 + 1
    MAHAJANA_COUNT + HALVES: "Gunatraya Vibhaga - Three modes of nature",  # 14 = 12 + 2
    MAHAJANA_COUNT + TRINITY: "Purusottama - The supreme person",  # 15 = 12 + 3
    WORDS: "Daivasura Sampad - Divine and demonic natures",
    POSITION_SUM_KRISHNA: "Sraddhatraya - Three types of faith",
    GITA_CHAPTERS: "Moksha Sannyasa - Liberation through surrender",
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


# =============================================================================
# BRANCHLESS COMPUTATION - DELEGATED TO algorithm/maha.py
# =============================================================================
# THE ALGORITHM lives in substrate/algorithm/maha.py
# This module provides backward-compatible wrappers.


def apply_operation(value: int, operation: str) -> int:
    """
    Apply Mahamantra operation to value - BRANCHLESS.

    DELEGATES to algorithm/maha.py - no duplication!

    H (HARE)    → value × SEVEN (mod 137)
    K (KRISHNA) → value + TEN (mod 137)
    R (RAMA)    → value × value (mod 137)
    """
    # Late import to avoid circular dependency
    from vibe_core.mahamantra.substrate.algorithm import maha_step
    return maha_step(value, operation, MAHA_QUANTUM)


# OP_CODE for backward compatibility (some code might use it)
OP_CODE: Final[dict[str, int]] = {"H": 0, "K": KSETRAJNA, "R": HALVES}


def is_attractor(value: int) -> Tuple[bool, AttractorType]:
    """Check if value is an attractor."""
    if value == ATTRACTOR_FIXED:
        return True, AttractorType.FIXED_POINT
    # Use computed cycle, not empty constant
    if value in get_attractor_cycle():
        return True, AttractorType.CYCLE
    return False, AttractorType.TRANSIENT


def get_gita_chapter(attractor: int) -> int:
    """
    Map attractor to Gita chapter via SEMANTIC DERIVATION.

    ATTRACTOR → CHAPTER (from RESEARCH_FINDINGS.md):
    - 18  = GITA_CHAPTERS       → Chapter 18 (Moksha Sannyasa) - FIXED POINT
    - 136 = POSITION_SUM_TOTAL  → Chapter 13 (Ksetra-Ksetrajna) - THE FIELD
    - 49  = POSITION_SUM_RAMA   → Chapter 7 (Jnana Vijnana) - sqrt = SEVEN
    - 87  = HARE + KRISHNA      → Chapter 10 (Vibhuti) - Source of all
    - 22  = MAHAJANA + TEN      → Chapter 6 (Dhyana Yoga)

    ALL DERIVED FROM _seed.py - NO HARDCODING.
    """
    from vibe_core.mahamantra.protocols._seed import (
        GITA_CHAPTERS,
        KSETRAJNA,
        MAHAJANA_COUNT,
        POSITION_SUM_HARE,
        POSITION_SUM_KRISHNA,
        POSITION_SUM_RAMA,
        POSITION_SUM_TOTAL,
        SEVEN,
        TEN,
        WORDS,
    )

    # FIXED POINT: 18 → Chapter 18 (Moksha Sannyasa Yoga)
    if attractor == GITA_CHAPTERS:
        return GITA_CHAPTERS

    # THE FIELD: 136 → Chapter 13 (Ksetra-Ksetrajna Vibhaga Yoga)
    # 136 = T(16) = The complete field; Chapter 13 explains field/knower
    if attractor == POSITION_SUM_TOTAL:
        return MAHAJANA_COUNT + KSETRAJNA  # 12 + 1 = 13

    # RAMA: 49 → Chapter 7 (Jnana Vijnana Yoga)
    # 49 = 7² = SEVEN × SEVEN; sqrt(49) = 7
    if attractor == POSITION_SUM_RAMA:
        return SEVEN

    # HARE+KRISHNA: 87 → Chapter 10 (Vibhuti Yoga)
    # 87 = 70 + 17 = POSITION_SUM_HARE + POSITION_SUM_KRISHNA
    if attractor == POSITION_SUM_HARE + POSITION_SUM_KRISHNA:
        return TEN

    # SHRUTIS: 22 → Chapter 6 (Dhyana Yoga)
    # 22 = 12 + 10 = MAHAJANA_COUNT + TEN; 22 mod 16 = 6
    if attractor == MAHAJANA_COUNT + TEN:
        return attractor % WORDS  # 22 % 16 = 6

    # Fallback for unknown attractors (shouldn't happen with proper algorithm)
    return (attractor % (GITA_CHAPTERS - KSETRAJNA)) + KSETRAJNA


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
    "ATTRACTOR_GITA",
    "ATTRACTOR_CYCLE",
    "ALL_ATTRACTORS",
    "get_attractor_cycle",
    "get_all_attractors_cached",
    "GITA_INSIGHTS",
    "PATTERN",
    # Branchless computation
    "OP_CODE",
    # Functions
    "get_operation",
    "apply_operation",
    "is_attractor",
    "get_gita_chapter",
    "get_gita_insight",
]
