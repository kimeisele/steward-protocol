"""
ANUKULYA-PRATIKULYA CLASSIFICATION - Technology Guna Analysis
=============================================================

"ānukūlyasya saṅkalpaḥ prātikūlyasya varjanam"

"Accept what is favorable, reject what is unfavorable."
— Sharanagati (6 Limbs of Surrender)

RESEARCH QUESTION:
==================

Which technologies will THRIVE in the 10,000 year Golden Age?
Which will FAIL?

The answer lies in the GUNAS (modes of nature):
- SATTVA (goodness): Simple, pure, serves truth
- RAJAS (passion): Complex, competitive, growth-obsessed
- TAMAS (ignorance): Chaotic, wasteful, destructive

CLASSIFICATION METRICS:
=======================

1. COMPLEXITY_CLASS: O(1), O(log N), O(N), O(N²), O(2^N)
2. MEMORY_BEHAVIOR: Bounded, Linear, Unbounded, Leaking
3. PARAMPARA_ALIGNMENT: Connected (% 37 == 0) or Broken
4. LOTUS_STRUCTURE: Natural (16×4) or Arbitrary
5. DETERMINISM: Pure functions vs Side effects
6. CACHE_EFFICIENCY: L1 fit, L2 fit, RAM, Disk
7. ENERGY_PER_OP: Joules per operation (proxy: cycles)

GOLDEN AGE SURVIVAL CRITERIA:
=============================

Technologies survive 10,000 years if:
- Complexity ≤ O(log N)
- Memory bounded
- Parampara connected
- Cache efficient (L2 fit)
- Deterministic

Technologies die if:
- Complexity ≥ O(N²)
- Memory unbounded/leaking
- No verification lineage
- Thrashing (cache misses)
- Non-deterministic chaos

USAGE:
======

    from vibe_core.mahamantra.research.classification import (
        classify_algorithm,
        Guna,
        is_golden_age_viable,
    )

    result = classify_algorithm(
        name="LotusIPv4Router",
        complexity="O(8)",
        memory_bytes=65536 * 8,
        parampara_connected=True,
        is_deterministic=True,
    )

    print(result.guna)  # Guna.SATTVA
    print(result.survives_golden_age)  # True
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Final, Optional

from ..protocols._seed import PARAMPARA, QUARTERS, WORDS

# =============================================================================
# CONSTANTS FROM SCRIPTURE
# =============================================================================

# Golden Age duration (WORDS × PRASADAM²)
PRASADAM: Final[int] = 25  # 5² from Pancha Tattva
GOLDEN_AGE_YEARS: Final[int] = WORDS * (PRASADAM**2)  # 16 × 625 = 10,000

# Cache sizes (modern hardware reality)
L1_CACHE_BYTES: Final[int] = 32 * 1024  # 32 KB
L2_CACHE_BYTES: Final[int] = 256 * 1024  # 256 KB
L3_CACHE_BYTES: Final[int] = 8 * 1024 * 1024  # 8 MB

# Lotus structure constants
LOTUS_KEY_SPACE: Final[int] = WORDS**QUARTERS  # 16^4 = 65536
LOTUS_MEMORY_BYTES: Final[int] = LOTUS_KEY_SPACE * 8  # 512 KB (fits L2)


# =============================================================================
# ENUMS
# =============================================================================


class Guna(Enum):
    """The three modes of material nature."""

    SATTVA = "sattva"  # Goodness - simple, pure, efficient
    RAJAS = "rajas"  # Passion - complex, competitive, growth
    TAMAS = "tamas"  # Ignorance - chaotic, wasteful, destructive


class ComplexityClass(Enum):
    """Algorithm complexity classification."""

    CONSTANT = "O(1)"
    LOGARITHMIC = "O(log N)"
    LINEAR = "O(N)"
    LINEARITHMIC = "O(N log N)"
    QUADRATIC = "O(N²)"
    CUBIC = "O(N³)"
    EXPONENTIAL = "O(2^N)"
    FACTORIAL = "O(N!)"


class MemoryBehavior(Enum):
    """Memory usage classification."""

    CONSTANT = "constant"  # Fixed size, cache-friendly
    BOUNDED = "bounded"  # Has upper limit
    LINEAR = "linear"  # Grows with input
    UNBOUNDED = "unbounded"  # No limit
    LEAKING = "leaking"  # Memory leaks over time


class CacheEfficiency(Enum):
    """Cache utilization classification."""

    L1_FIT = "L1"  # Fits in L1 cache (fastest)
    L2_FIT = "L2"  # Fits in L2 cache (fast)
    L3_FIT = "L3"  # Fits in L3 cache (moderate)
    RAM_BOUND = "RAM"  # Must go to RAM (slow)
    DISK_BOUND = "DISK"  # Must go to disk (very slow)


# =============================================================================
# CLASSIFICATION RESULT
# =============================================================================


@dataclass(frozen=True)
class ClassificationResult:
    """Result of technology classification."""

    name: str
    guna: Guna
    complexity: ComplexityClass
    memory: MemoryBehavior
    cache: CacheEfficiency
    parampara_connected: bool
    is_deterministic: bool
    survives_golden_age: bool
    score: int  # 0-100, higher = more sattvic
    reasoning: str


# =============================================================================
# CLASSIFICATION LOGIC
# =============================================================================

# Complexity scores (higher = better)
_COMPLEXITY_SCORES: dict[ComplexityClass, int] = {
    ComplexityClass.CONSTANT: 100,
    ComplexityClass.LOGARITHMIC: 90,
    ComplexityClass.LINEAR: 70,
    ComplexityClass.LINEARITHMIC: 60,
    ComplexityClass.QUADRATIC: 30,
    ComplexityClass.CUBIC: 10,
    ComplexityClass.EXPONENTIAL: 0,
    ComplexityClass.FACTORIAL: 0,
}

# Memory scores (higher = better)
_MEMORY_SCORES: dict[MemoryBehavior, int] = {
    MemoryBehavior.CONSTANT: 100,
    MemoryBehavior.BOUNDED: 80,
    MemoryBehavior.LINEAR: 50,
    MemoryBehavior.UNBOUNDED: 20,
    MemoryBehavior.LEAKING: 0,
}

# Cache scores (higher = better)
_CACHE_SCORES: dict[CacheEfficiency, int] = {
    CacheEfficiency.L1_FIT: 100,
    CacheEfficiency.L2_FIT: 90,
    CacheEfficiency.L3_FIT: 70,
    CacheEfficiency.RAM_BOUND: 40,
    CacheEfficiency.DISK_BOUND: 10,
}


def _parse_complexity(complexity_str: str) -> ComplexityClass:
    """Parse complexity string to enum."""
    normalized = complexity_str.upper().replace(" ", "")

    # Handle Lotus-specific O(8) as O(1)
    if normalized in ("O(8)", "O(16)", "O(4)"):
        return ComplexityClass.CONSTANT

    mapping = {
        "O(1)": ComplexityClass.CONSTANT,
        "O(LOGN)": ComplexityClass.LOGARITHMIC,
        "O(LOG(N))": ComplexityClass.LOGARITHMIC,
        "O(N)": ComplexityClass.LINEAR,
        "O(NLOGN)": ComplexityClass.LINEARITHMIC,
        "O(N²)": ComplexityClass.QUADRATIC,
        "O(N^2)": ComplexityClass.QUADRATIC,
        "O(N³)": ComplexityClass.CUBIC,
        "O(N^3)": ComplexityClass.CUBIC,
        "O(2^N)": ComplexityClass.EXPONENTIAL,
        "O(N!)": ComplexityClass.FACTORIAL,
    }

    return mapping.get(normalized, ComplexityClass.LINEAR)


def _get_cache_efficiency(memory_bytes: int) -> CacheEfficiency:
    """Determine cache efficiency from memory footprint."""
    if memory_bytes <= L1_CACHE_BYTES:
        return CacheEfficiency.L1_FIT
    elif memory_bytes <= L2_CACHE_BYTES:
        return CacheEfficiency.L2_FIT
    elif memory_bytes <= L3_CACHE_BYTES:
        return CacheEfficiency.L3_FIT
    elif memory_bytes <= 16 * 1024 * 1024 * 1024:  # 16 GB
        return CacheEfficiency.RAM_BOUND
    else:
        return CacheEfficiency.DISK_BOUND


def _determine_guna(score: int) -> Guna:
    """Determine Guna from overall score."""
    if score >= 70:
        return Guna.SATTVA
    elif score >= 40:
        return Guna.RAJAS
    else:
        return Guna.TAMAS


def _survives_golden_age(
    complexity: ComplexityClass,
    memory: MemoryBehavior,
    cache: CacheEfficiency,
    parampara: bool,
    deterministic: bool,
) -> bool:
    """Determine if technology survives the 10,000 year Golden Age."""
    # MUST be connected to Parampara
    if not parampara:
        return False

    # MUST be deterministic
    if not deterministic:
        return False

    # Complexity must be at most O(N log N)
    if complexity in (
        ComplexityClass.QUADRATIC,
        ComplexityClass.CUBIC,
        ComplexityClass.EXPONENTIAL,
        ComplexityClass.FACTORIAL,
    ):
        return False

    # Memory must not leak
    if memory == MemoryBehavior.LEAKING:
        return False

    # Should fit in L3 at minimum
    if cache == CacheEfficiency.DISK_BOUND:
        return False

    return True


def classify_algorithm(
    name: str,
    complexity: str,
    memory_bytes: int,
    parampara_connected: bool,
    is_deterministic: bool,
    memory_behavior: Optional[MemoryBehavior] = None,
) -> ClassificationResult:
    """
    Classify an algorithm/technology by Guna.

    Args:
        name: Name of the algorithm
        complexity: Big-O notation string (e.g., "O(1)", "O(N²)")
        memory_bytes: Memory footprint in bytes
        parampara_connected: Is it verified against Parampara (37)?
        is_deterministic: Are outputs determined solely by inputs?
        memory_behavior: Optional explicit memory behavior

    Returns:
        ClassificationResult with Guna and survival prediction
    """
    # Parse complexity
    complexity_class = _parse_complexity(complexity)

    # Determine memory behavior
    if memory_behavior is None:
        if memory_bytes <= LOTUS_MEMORY_BYTES:
            memory_behavior = MemoryBehavior.BOUNDED
        else:
            memory_behavior = MemoryBehavior.LINEAR

    # Determine cache efficiency
    cache = _get_cache_efficiency(memory_bytes)

    # Calculate score
    complexity_score = _COMPLEXITY_SCORES[complexity_class]
    memory_score = _MEMORY_SCORES[memory_behavior]
    cache_score = _CACHE_SCORES[cache]
    parampara_score = 100 if parampara_connected else 0
    determinism_score = 100 if is_deterministic else 0

    # Weighted average (Parampara is most important)
    score = (
        complexity_score * 0.20
        + memory_score * 0.15
        + cache_score * 0.15
        + parampara_score * 0.30  # MOST IMPORTANT
        + determinism_score * 0.20
    )

    # Determine Guna
    guna = _determine_guna(int(score))

    # Determine survival
    survives = _survives_golden_age(
        complexity_class,
        memory_behavior,
        cache,
        parampara_connected,
        is_deterministic,
    )

    # Build reasoning
    reasons = []
    if parampara_connected:
        reasons.append("✓ Parampara connected (37)")
    else:
        reasons.append("✗ BROKEN LINEAGE")

    if is_deterministic:
        reasons.append("✓ Deterministic")
    else:
        reasons.append("✗ Non-deterministic chaos")

    reasons.append(f"Complexity: {complexity_class.value}")
    reasons.append(f"Memory: {memory_behavior.value}")
    reasons.append(f"Cache: {cache.value}")

    if survives:
        reasons.append(f"→ SURVIVES Golden Age ({GOLDEN_AGE_YEARS:,} years)")
    else:
        reasons.append("→ DIES before Golden Age ends")

    return ClassificationResult(
        name=name,
        guna=guna,
        complexity=complexity_class,
        memory=memory_behavior,
        cache=cache,
        parampara_connected=parampara_connected,
        is_deterministic=is_deterministic,
        survives_golden_age=survives,
        score=int(score),
        reasoning="\n".join(reasons),
    )


def is_golden_age_viable(result: ClassificationResult) -> bool:
    """Check if classification result indicates Golden Age viability."""
    return result.survives_golden_age


# =============================================================================
# PRE-CLASSIFIED TECHNOLOGIES
# =============================================================================


def classify_lotus_tree() -> ClassificationResult:
    """Classify LotusArrayInt."""
    return classify_algorithm(
        name="LotusArrayInt",
        complexity="O(1)",
        memory_bytes=LOTUS_MEMORY_BYTES,  # 512 KB
        parampara_connected=True,
        is_deterministic=True,
        memory_behavior=MemoryBehavior.CONSTANT,
    )


def classify_ip_router() -> ClassificationResult:
    """Classify LotusIPv4Router."""
    return classify_algorithm(
        name="LotusIPv4Router",
        complexity="O(8)",  # 8 levels = O(1) constant
        memory_bytes=1024 * 1024,  # ~1 MB for sparse tree
        parampara_connected=True,
        is_deterministic=True,
        memory_behavior=MemoryBehavior.BOUNDED,
    )


def classify_dna_kmer() -> ClassificationResult:
    """Classify Lotus8merIndex."""
    return classify_algorithm(
        name="Lotus8merIndex",
        complexity="O(N)",  # Must process all bases
        memory_bytes=LOTUS_MEMORY_BYTES,  # 512 KB fixed
        parampara_connected=True,
        is_deterministic=True,
        memory_behavior=MemoryBehavior.CONSTANT,
    )


def classify_hash_table() -> ClassificationResult:
    """Classify standard Python dict (for comparison)."""
    return classify_algorithm(
        name="Python dict",
        complexity="O(1)",  # Average case
        memory_bytes=10 * 1024 * 1024,  # Typical 10 MB
        parampara_connected=False,  # No lineage verification
        is_deterministic=False,  # Hash randomization
        memory_behavior=MemoryBehavior.UNBOUNDED,
    )


def classify_linear_search() -> ClassificationResult:
    """Classify linear search (for comparison)."""
    return classify_algorithm(
        name="Linear Search",
        complexity="O(N)",
        memory_bytes=0,  # No extra memory
        parampara_connected=False,
        is_deterministic=True,
        memory_behavior=MemoryBehavior.CONSTANT,
    )


def classify_neural_network() -> ClassificationResult:
    """Classify typical neural network (for comparison)."""
    return classify_algorithm(
        name="Neural Network (LLM)",
        complexity="O(N²)",  # Attention is quadratic
        memory_bytes=70 * 1024 * 1024 * 1024,  # 70 GB for large model
        parampara_connected=False,  # No lineage
        is_deterministic=False,  # Temperature, sampling
        memory_behavior=MemoryBehavior.UNBOUNDED,
    )


# =============================================================================
# BENCHMARK / DEMO
# =============================================================================


def benchmark() -> None:
    """Compare technologies by Guna classification."""
    print("=" * 70)
    print("ANUKULYA-PRATIKULYA CLASSIFICATION")
    print(f"Golden Age Duration: {GOLDEN_AGE_YEARS:,} years")
    print("=" * 70)
    print()

    technologies = [
        classify_lotus_tree(),
        classify_ip_router(),
        classify_dna_kmer(),
        classify_hash_table(),
        classify_linear_search(),
        classify_neural_network(),
    ]

    for tech in technologies:
        print(f"### {tech.name} ###")
        print(f"Guna: {tech.guna.value.upper()}")
        print(f"Score: {tech.score}/100")
        print(tech.reasoning)
        print()

    # Summary
    print("=" * 70)
    print("SUMMARY: Golden Age Survivors")
    print("=" * 70)
    survivors = [t for t in technologies if t.survives_golden_age]
    casualties = [t for t in technologies if not t.survives_golden_age]

    print("\nSURVIVORS (Sattvic):")
    for t in survivors:
        print(f"  ✓ {t.name} ({t.guna.value})")

    print("\nCASUALTIES (Rajasic/Tamasic):")
    for t in casualties:
        print(f"  ✗ {t.name} ({t.guna.value})")


if __name__ == "__main__":
    benchmark()
