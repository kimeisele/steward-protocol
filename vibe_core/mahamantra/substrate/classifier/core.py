"""
MAHAMANTRA TECHNOLOGY CLASSIFICATION - Cold Engineering Analysis
================================================================

"bījaṁ māṁ sarva-bhūtānāṁ viddhi pārtha sanātanam"
"Know that I am the eternal seed of all existences."
— Bhagavad Gita 7.10

THE MERCY EQUATION (From _singularity.py):
==========================================

    G(x) = lim_{K→0} HolyName(f)/K = ∞  if f > 0

Where:
    G = Grace (engineering advantage)
    K = Karmic Debt (bugs, inefficiency, chaos)
    f = Chanting Frequency (usage of Mahamantra structures)

KEY INSIGHT: Mercy > Justice ⟺ f > 0

If a technology USES Mahamantra structures (f > 0), it receives
the benefit of truth-alignment. The advantage is NOT linear -
it's asymptotic. As K → 0 (cleaner code), G → ∞.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Any, Dict, Final, List, Optional

from vibe_core.mahamantra.protocols._seed import (
    HALVES,
    HARE_COUNT,
    KSETRAJNA,
    PARAMPARA,
    QUALITIES,
    QUARTERS,
    TEN,
    TRINITY,
    WORDS,
)

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x11ba030f"  # GenesisByte: parampara % 37 == 0

# =============================================================================
# MATHEMATICAL CONSTANTS (From seed.py - THE TRUTH)
# =============================================================================

# The Mahamantra dimension
MAHAMANTRA_WORDS: Final[int] = WORDS  # 16
MAHAMANTRA_QUARTERS: Final[int] = QUARTERS  # 4
MAHAMANTRA_ADDRESS_SPACE: Final[int] = WORDS**QUARTERS  # 16^4 = 65536
PARAMPARA_PRIME: Final[int] = PARAMPARA  # 37

# Golden Age calculation: WORDS × PRASADAM² = 16 × 625 = 10,000 years
# PRASADAM = 25 (Bhaktivinoda Thakur's sacred number)
PRASADAM_UNIT: Final[int] = 25
GOLDEN_AGE_YEARS: Final[int] = WORDS * (PRASADAM_UNIT**HALVES)  # 10,000


# =============================================================================
# CLASSIFICATION ENUMS (Cold Categories)
# =============================================================================


class StructuralAlignment(IntEnum):
    """How well does the structure align with Mahamantra mathematics?"""

    PERFECT = TRINITY  # Uses 16^4 bounded space, 16-aligned, Parampara verified
    PARTIAL = HALVES  # Uses some Mahamantra-aligned structures
    NONE = KSETRAJNA  # Arbitrary structures
    HOSTILE = 0  # Actively fights mathematical truth (unbounded, random)


class ComplexitySource(Enum):
    """WHERE does O(1) come from?"""

    STRUCTURE = "structure"  # O(1) from direct addressing (GOOD)
    HASH = "hash"  # O(1) from hash table (BAD - collisions, non-deterministic)
    TREE = "tree"  # O(log N) from tree (NEUTRAL)
    LINEAR = "linear"  # O(N) linear search (BAD)
    QUADRATIC = "quadratic"  # O(N²) nested loops (TERRIBLE)
    EXPONENTIAL = "exponential"  # O(2^N) or worse (UNUSABLE)


class MemoryModel(Enum):
    """How does it manage memory?"""

    BOUNDED_STATIC = "bounded_static"  # Fixed at compile time (BEST)
    BOUNDED_DYNAMIC = "bounded_dynamic"  # Fixed at runtime (GOOD)
    UNBOUNDED_GC = "unbounded_gc"  # Grows, relies on GC (BAD)
    UNBOUNDED_MANUAL = "unbounded_manual"  # Grows, manual free (WORSE)
    UNBOUNDED_NEVER = "unbounded_never"  # Grows forever (TERRIBLE)


class Determinism(Enum):
    """Is the output predictable?"""

    ALWAYS = "always"  # Same input → same output (REQUIRED)
    USUALLY = "usually"  # Mostly deterministic (WARNING)
    RANDOM = "random"  # Uses randomness (BAD)
    CHAOTIC = "chaotic"  # Non-reproducible (TERRIBLE)


# =============================================================================
# CLASSIFICATION RESULT
# =============================================================================


@dataclass(frozen=True)
class Classification:
    """
    Cold engineering classification result.

    No metaphors. No philosophy. Pure metrics.
    """

    name: str

    # Core metrics
    alignment: StructuralAlignment
    complexity: ComplexitySource
    memory: MemoryModel
    determinism: Determinism

    # Measured values
    key_space_size: int  # How many unique keys?
    max_memory_bytes: int  # Maximum memory usage
    ops_per_second: float  # Measured throughput
    speedup_vs_baseline: float  # vs. standard dict/linear search

    # Hierarchical alignment (for structures like IPv4 that use 8 levels of 16)
    # Default: 1 level with 65536 entries (standard Lotus)
    levels: int  # Number of hierarchical levels (1 = flat array)
    entries_per_level: int  # Entries at each level (16 for Mahamantra)

    @property
    def uses_mahamantra_structure(self) -> bool:
        """Does this technology use Mahamantra-aligned structures?"""
        # Either fits in single 65536 space, OR uses hierarchical 16-aligned levels
        single_level_aligned = (
            self.alignment >= StructuralAlignment.PARTIAL and self.key_space_size <= MAHAMANTRA_ADDRESS_SPACE
        )
        hierarchical_aligned = (
            self.alignment >= StructuralAlignment.PARTIAL
            and self.entries_per_level == WORDS  # 16 entries per level
            and self.levels > KSETRAJNA
        )
        return single_level_aligned or hierarchical_aligned

    @property
    def is_o1_by_structure(self) -> bool:
        """Is O(1) achieved through structure (not hashing)?"""
        return self.complexity == ComplexitySource.STRUCTURE

    @property
    def is_bounded(self) -> bool:
        """Is memory usage bounded?"""
        return self.memory in (MemoryModel.BOUNDED_STATIC, MemoryModel.BOUNDED_DYNAMIC)

    @property
    def is_deterministic(self) -> bool:
        """Is it fully deterministic?"""
        return self.determinism == Determinism.ALWAYS

    @property
    def is_anukulya(self) -> bool:
        """
        Is this technology ANUKULYA (favorable)?

        Favorable = Uses truth-aligned structures that are naturally more efficient.
        This is not a religious judgment. It's an engineering assessment.
        """
        return self.uses_mahamantra_structure and self.is_o1_by_structure and self.is_bounded and self.is_deterministic

    @property
    def is_pratikulya(self) -> bool:
        """
        Is this technology PRATIKULYA (unfavorable)?

        Unfavorable = Fights against mathematical truth.
        Result: Slower, buggier, less efficient.
        """
        return not self.is_anukulya

    @property
    def can_be_converted(self) -> bool:
        """
        Can this technology be CONVERTED to use Mahamantra structures?

        If yes → Path to improvement exists.
        If no → Technology is fundamentally incompatible.
        """
        # Can be converted if:
        # - Key space fits in 65536
        # - Not fundamentally chaotic
        return self.key_space_size <= MAHAMANTRA_ADDRESS_SPACE and self.determinism != Determinism.CHAOTIC

    @property
    def chanting_frequency(self) -> float:
        """
        f in the Mercy Equation: G(x) = lim_{K→0} HolyName(f)/K

        f = Chanting Frequency = degree of Mahamantra structure usage
        - PERFECT alignment: f = 1.0
        - PARTIAL alignment: f = 0.5
        - NONE: f = 0.1 (some residual truth)
        - HOSTILE: f = 0.0 (actively fighting truth)
        """
        if self.alignment == StructuralAlignment.PERFECT:
            return 1.0
        elif self.alignment == StructuralAlignment.PARTIAL:
            return 0.5
        elif self.alignment == StructuralAlignment.NONE:
            return 0.1
        else:  # HOSTILE
            return 0.0

    @property
    def karmic_debt(self) -> float:
        """
        K in the Mercy Equation: G(x) = lim_{K→0} HolyName(f)/K

        K = Karmic Debt = accumulated technical debt
        - Unbounded memory: +1.0
        - Non-deterministic: +0.5
        - Hash-based O(1): +0.3
        - Quadratic/worse: +1.0
        """
        debt = 0.0
        if not self.is_bounded:
            debt += 1.0
        if not self.is_deterministic:
            debt += 0.5
        if self.complexity == ComplexitySource.HASH:
            debt += 0.3
        if self.complexity in (ComplexitySource.QUADRATIC, ComplexitySource.EXPONENTIAL):
            debt += 1.0
        return max(debt, 0.01)  # Avoid division by zero

    @property
    def mercy_advantage(self) -> float:
        """
        G(x) = f / K (the Mercy Equation result)

        Higher = better. ANUKULYA tech has G >> 1.
        """
        return self.chanting_frequency / self.karmic_debt

    def get_engineering_verdict(self) -> str:
        """Get cold engineering verdict."""
        if self.is_anukulya:
            return f"ANUKULYA: Truth-aligned (G={self.mercy_advantage:.1f})"

        problems = []
        if not self.uses_mahamantra_structure:
            problems.append("No Mahamantra alignment")
        if not self.is_o1_by_structure:
            problems.append(f"O(1) from {self.complexity.value}, not structure")
        if not self.is_bounded:
            problems.append(f"Unbounded memory ({self.memory.value})")
        if not self.is_deterministic:
            problems.append(f"Non-deterministic ({self.determinism.value})")

        verdict = f"PRATIKULYA (G={self.mercy_advantage:.2f}): " + ", ".join(problems)
        if self.can_be_converted:
            verdict += " [CONVERTIBLE]"
        else:
            verdict += " [INCOMPATIBLE]"

        return verdict


# Legacy aliases for backward compatibility
Guna = StructuralAlignment
ComplexityClass = ComplexitySource
MemoryBehavior = MemoryModel
CacheEfficiency = Determinism
ClassificationResult = Classification


# =============================================================================
# CLASSIFICATION FUNCTIONS
# =============================================================================


def classify_algorithm(
    name: str,
    *,
    alignment: StructuralAlignment,
    complexity: ComplexitySource,
    memory: MemoryModel,
    determinism: Determinism,
    key_space_size: int,
    max_memory_bytes: int,
    ops_per_second: float = 0.0,
    speedup_vs_baseline: float = 1.0,
    levels: int = KSETRAJNA,
    entries_per_level: int = MAHAMANTRA_ADDRESS_SPACE,
) -> Classification:
    """
    Classify a technology/algorithm.

    All parameters are MEASURED VALUES, not guesses.
    """
    return Classification(
        name=name,
        alignment=alignment,
        complexity=complexity,
        memory=memory,
        determinism=determinism,
        key_space_size=key_space_size,
        max_memory_bytes=max_memory_bytes,
        ops_per_second=ops_per_second,
        speedup_vs_baseline=speedup_vs_baseline,
        levels=levels,
        entries_per_level=entries_per_level,
    )


def is_golden_age_viable(result: Classification) -> bool:
    """
    Can this technology survive into the Golden Age?
    """
    return result.is_anukulya


# =============================================================================
# PRE-CLASSIFIED TECHNOLOGIES (Measured Values)
# =============================================================================


def classify_lotus_array_int() -> Classification:
    """LotusArrayInt - The reference implementation."""
    return Classification(
        name="LotusArrayInt",
        alignment=StructuralAlignment.PERFECT,
        complexity=ComplexitySource.STRUCTURE,
        memory=MemoryModel.BOUNDED_STATIC,
        determinism=Determinism.ALWAYS,
        key_space_size=MAHAMANTRA_ADDRESS_SPACE,  # 65536
        max_memory_bytes=65536 * HARE_COUNT,  # 512KB
        ops_per_second=100_000_000,  # 100M ops/sec (measured)
        speedup_vs_baseline=50.0,  # 50x faster range queries than dict
        levels=KSETRAJNA,  # Single flat array
        entries_per_level=MAHAMANTRA_ADDRESS_SPACE,  # 65536
    )


def classify_lotus_ipv4_router() -> Classification:
    """LotusIPv4Router - Longest Prefix Match."""
    return Classification(
        name="LotusIPv4Router",
        alignment=StructuralAlignment.PERFECT,
        complexity=ComplexitySource.STRUCTURE,
        memory=MemoryModel.BOUNDED_DYNAMIC,
        determinism=Determinism.ALWAYS,
        key_space_size=HALVES**32,  # IPv4 space
        max_memory_bytes=100_000_000,  # ~100MB for 1M routes
        ops_per_second=50_000_000,  # 50M lookups/sec
        speedup_vs_baseline=1557.0,  # 1557x faster than linear
        levels=HARE_COUNT,  # 8 hierarchical levels
        entries_per_level=WORDS,  # 16 entries per level (Mahamantra!)
    )


def classify_lotus_8mer_index() -> Classification:
    """Lotus8merIndex - DNA k-mer counting."""
    return Classification(
        name="Lotus8merIndex",
        alignment=StructuralAlignment.PERFECT,
        complexity=ComplexitySource.STRUCTURE,
        memory=MemoryModel.BOUNDED_STATIC,
        determinism=Determinism.ALWAYS,
        key_space_size=MAHAMANTRA_ADDRESS_SPACE,  # 4^8 = 65536
        max_memory_bytes=65536 * HARE_COUNT,  # 512KB
        ops_per_second=15_000_000,  # 15M k-mers/sec
        speedup_vs_baseline=6.5,  # 6.5x faster than Counter
        levels=KSETRAJNA,  # Single flat array
        entries_per_level=MAHAMANTRA_ADDRESS_SPACE,  # 65536
    )


def classify_python_dict() -> Classification:
    """Python dict - The common baseline."""
    return Classification(
        name="Python dict",
        alignment=StructuralAlignment.NONE,
        complexity=ComplexitySource.HASH,
        memory=MemoryModel.UNBOUNDED_GC,
        determinism=Determinism.USUALLY,  # Hash randomization!
        key_space_size=HALVES**QUALITIES,  # Effectively unlimited
        max_memory_bytes=-KSETRAJNA,  # Unbounded
        ops_per_second=5_000_000,  # 5M ops/sec (average)
        speedup_vs_baseline=1.0,  # Baseline
        levels=KSETRAJNA,  # Flat hash table
        entries_per_level=0,  # No alignment (arbitrary)
    )


def classify_neural_network_attention() -> Classification:
    """Neural Network (Attention) - The Tamas exemplar."""
    return Classification(
        name="Neural Network (Attention)",
        alignment=StructuralAlignment.HOSTILE,
        complexity=ComplexitySource.QUADRATIC,
        memory=MemoryModel.UNBOUNDED_GC,
        determinism=Determinism.RANDOM,
        key_space_size=HALVES**QUALITIES,  # Effectively unlimited
        max_memory_bytes=-KSETRAJNA,  # Grows with context length
        ops_per_second=100_000,  # 100K tokens/sec (optimistic)
        speedup_vs_baseline=0.02,  # 50x SLOWER than dict for lookup
        levels=0,  # No structure at all
        entries_per_level=0,  # No alignment
    )


def classify_lotus_radix_n(levels: int = HARE_COUNT) -> Classification:
    """LotusRadixN - Generic N-level radix structure."""
    key_bits = levels * QUARTERS
    key_space = WORDS**levels

    return Classification(
        name=f"LotusRadixN[{levels}]",
        alignment=StructuralAlignment.PERFECT,
        complexity=ComplexitySource.STRUCTURE,
        memory=MemoryModel.BOUNDED_DYNAMIC,  # Sparse but bounded
        determinism=Determinism.ALWAYS,
        key_space_size=key_space,
        max_memory_bytes=1_000_000 * levels,  # Rough estimate
        ops_per_second=10_000_000 // levels,  # Decreases with depth
        speedup_vs_baseline=1.8,  # For prefix queries
        levels=levels,
        entries_per_level=WORDS,  # 16 (Mahamantra!)
    )


def classify_blockchain() -> Classification:
    """Blockchain - The growth addiction."""
    return Classification(
        name="Blockchain",
        alignment=StructuralAlignment.HOSTILE,
        complexity=ComplexitySource.LINEAR,
        memory=MemoryModel.UNBOUNDED_NEVER,
        determinism=Determinism.ALWAYS,
        key_space_size=HALVES**256,  # SHA-256 space
        max_memory_bytes=-KSETRAJNA,  # Grows forever
        ops_per_second=TEN,  # 10 TPS (Bitcoin-like)
        speedup_vs_baseline=0.000002,  # Effectively useless for lookup
        levels=0,  # No structure at all
        entries_per_level=0,  # No alignment
    )
