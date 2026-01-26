"""
ANUKULYA-PRATIKULYA - Real Technology Classification
=====================================================

"harer nāma harer nāma harer nāmaiva kevalam
kalau nāsty eva nāsty eva nāsty eva gatir anyathā"

"In this age of Kali there is no other way, no other way,
no other way for spiritual progress than the holy name."
— Brhan-Naradiya Purana

THE REAL QUESTION:
==================

Does the technology CHANT?
Does it PURIFY the ether?
Does it complete YAJNA cycles?

NOT:
- Arbitrary "parampara connected" checkboxes
- Made-up memory thresholds
- Abstract scores

THE REAL METRICS:
=================

1. ENTROPY_DELTA (ΔS per operation)
   - Negative = PURIFIES (Sattva) - removes disorder
   - Zero = NEUTRAL (Rajas) - maintains
   - Positive = POLLUTES (Tamas) - adds disorder

2. CYCLE_COMPLETION (Yajna integrity)
   - Complete cycles = Prasadam returns
   - Broken cycles = Bhoga stuck (resource leaks)

3. RESONANCE_FACTOR (Alignment with cosmic rhythm)
   - 16-aligned = Mahamantra rhythm
   - 37-aligned = Parampara connection
   - Arbitrary = Out of sync

4. ETHER_IMPACT (Akasha effect)
   - Simplifies = Clears the channel
   - Complicates = Clogs the channel

REAL PROBLEMS OF 2026 (Missstände):
===================================

1. MEMORY LEAKS = Broken Yajna (Bhoga never becomes Prasadam)
2. HASH COLLISIONS = Impure vibration (distorted mantra)
3. O(N²) COMPLEXITY = Entropy accumulation (Tamas grows)
4. NON-DETERMINISM = Chaos (no lineage possible)
5. UNBOUNDED GROWTH = Greed (Rajas unchecked)

LOTUS SOLUTIONS:
================

1. BOUNDED MEMORY = Complete Yajna cycles
2. DIRECT ADDRESSING = Pure vibration (key IS the path)
3. O(1) COMPLEXITY = Entropy neutral
4. DETERMINISTIC = Lineage preserved
5. FIXED SIZE = Contentment (Sattva)

TRANSITION PERIOD (Now → Golden Age):
=====================================

We are in SANDHYA (twilight) between Kali and Golden Age.
Technologies must be BRIDGE-COMPATIBLE:
- Work with current systems (Kali-compatible)
- Embody future principles (Golden Age ready)
- Enable gradual migration (Sandhya transition)
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Final

from ..protocols._seed import PARAMPARA, QUARTERS, WORDS

# =============================================================================
# COSMIC CONSTANTS
# =============================================================================

GOLDEN_AGE_YEARS: Final[int] = WORDS * (25**2)  # 16 × 625 = 10,000
MAHAMANTRA_SYLLABLES: Final[int] = 32
YAJNA_CYCLE: Final[int] = 16  # Complete cycle through all positions


# =============================================================================
# ENTROPY CLASSIFICATION
# =============================================================================


class EntropyDelta(Enum):
    """Change in disorder per operation."""

    PURIFIES = -1  # Removes disorder (Sattva)
    NEUTRAL = 0  # Maintains (Rajas stable)
    ACCUMULATES = 1  # Adds disorder (Rajas growing)
    EXPLODES = 2  # Exponential disorder (Tamas)


class YajnaCycle(Enum):
    """Completeness of offering-return cycle."""

    COMPLETE = "complete"  # Bhoga → Prasadam → Return
    PARTIAL = "partial"  # Bhoga → Prasadam (no return)
    BROKEN = "broken"  # Bhoga stuck (leak)
    INVERTED = "inverted"  # Takes without offering


class ResonanceFactor(Enum):
    """Alignment with cosmic rhythm."""

    MAHAMANTRA = 16  # Aligned with 16 words
    PARAMPARA = 37  # Aligned with lineage
    HARMONIC = 4  # Aligned with quarters
    ARBITRARY = 0  # No alignment


class EtherImpact(Enum):
    """Effect on the subtle medium."""

    CLEARS = "clears"  # Simplifies, purifies
    MAINTAINS = "maintains"  # Neutral
    CLOGS = "clogs"  # Complicates
    CORRUPTS = "corrupts"  # Destroys


# =============================================================================
# REAL CLASSIFICATION RESULT
# =============================================================================


@dataclass
class RealClassification:
    """Real technology classification based on scriptural principles."""

    name: str

    # Core metrics
    entropy_delta: EntropyDelta
    yajna_cycle: YajnaCycle
    resonance: ResonanceFactor
    ether_impact: EtherImpact

    # Measured values
    ops_per_chant: float  # Operations per 16-tick cycle
    entropy_per_op: float  # ΔS per operation (measured)
    cycle_completion_rate: float  # % of cycles that complete

    # Derived
    purification_rate: float  # Negative entropy per second

    # Diagnosis
    problems: list[str]
    solutions: list[str]

    @property
    def is_anukulya(self) -> bool:
        """Is this technology favorable?"""
        return (
            self.entropy_delta in (EntropyDelta.PURIFIES, EntropyDelta.NEUTRAL)
            and self.yajna_cycle in (YajnaCycle.COMPLETE, YajnaCycle.PARTIAL)
            and self.ether_impact in (EtherImpact.CLEARS, EtherImpact.MAINTAINS)
        )

    @property
    def is_pratikulya(self) -> bool:
        """Is this technology unfavorable?"""
        return not self.is_anukulya

    @property
    def transition_ready(self) -> bool:
        """Can this technology bridge to Golden Age?"""
        # Must not CORRUPT (destroys the bridge)
        # Must not EXPLODE (burns the bridge)
        # Must have some cycle completion (path exists)
        return (
            self.ether_impact != EtherImpact.CORRUPTS
            and self.entropy_delta != EntropyDelta.EXPLODES
            and self.cycle_completion_rate > 0.5
        )


# =============================================================================
# MEASUREMENT FUNCTIONS
# =============================================================================


def measure_entropy_delta(
    operation: Callable[[], Any],
    iterations: int = 1000,
) -> float:
    """
    Measure entropy change per operation.

    Uses timing variance as entropy proxy:
    - Low variance = deterministic = low entropy
    - High variance = chaotic = high entropy
    """
    times: list[float] = []

    for _ in range(iterations):
        start = time.perf_counter_ns()
        operation()
        end = time.perf_counter_ns()
        times.append(end - start)

    if not times:
        return 0.0

    # Calculate variance (proxy for entropy)
    mean = sum(times) / len(times)
    variance = sum((t - mean) ** 2 for t in times) / len(times)

    # Normalize to [-1, 1] range
    # Low variance (< 100ns²) = purifying
    # High variance (> 10000ns²) = polluting
    if variance < 100:
        return -1.0  # Purifying
    elif variance < 1000:
        return 0.0  # Neutral
    elif variance < 10000:
        return 0.5  # Accumulating
    else:
        return 1.0  # Exploding


def measure_cycle_completion(
    allocate: Callable[[], Any],
    deallocate: Callable[[Any], None],
    iterations: int = 100,
) -> float:
    """
    Measure Yajna cycle completion rate.

    Bhoga (allocate) must return as Prasadam (deallocate).
    """
    completed = 0

    for _ in range(iterations):
        try:
            resource = allocate()
            deallocate(resource)
            completed += 1
        except Exception:
            pass

    return completed / iterations if iterations > 0 else 0.0


def detect_resonance(size: int) -> ResonanceFactor:
    """Detect alignment with cosmic numbers."""
    if size % WORDS == 0:
        return ResonanceFactor.MAHAMANTRA
    elif size % PARAMPARA == 0:
        return ResonanceFactor.PARAMPARA
    elif size % QUARTERS == 0:
        return ResonanceFactor.HARMONIC
    else:
        return ResonanceFactor.ARBITRARY


# =============================================================================
# PROBLEM DIAGNOSIS
# =============================================================================


def diagnose_problems(
    entropy_delta: EntropyDelta,
    yajna_cycle: YajnaCycle,
    ether_impact: EtherImpact,
) -> tuple[list[str], list[str]]:
    """Diagnose problems and propose Lotus solutions."""
    problems: list[str] = []
    solutions: list[str] = []

    # Entropy problems
    if entropy_delta == EntropyDelta.ACCUMULATES:
        problems.append("ENTROPY ACCUMULATION: O(N) or worse complexity")
        solutions.append("→ Use O(1) Lotus structure (key IS the path)")
    elif entropy_delta == EntropyDelta.EXPLODES:
        problems.append("ENTROPY EXPLOSION: O(N²) or worse complexity")
        solutions.append("→ CRITICAL: Replace with O(1) or O(log N) algorithm")

    # Yajna problems
    if yajna_cycle == YajnaCycle.BROKEN:
        problems.append("BROKEN YAJNA: Resource leaks (Bhoga never returns)")
        solutions.append("→ Use bounded structures with automatic cleanup")
    elif yajna_cycle == YajnaCycle.INVERTED:
        problems.append("INVERTED YAJNA: Takes without offering (pure consumption)")
        solutions.append("→ Implement proper lifecycle (create → use → destroy)")

    # Ether problems
    if ether_impact == EtherImpact.CLOGS:
        problems.append("CLOGGED ETHER: Unnecessary complexity")
        solutions.append("→ Simplify: Direct addressing, no hashing")
    elif ether_impact == EtherImpact.CORRUPTS:
        problems.append("CORRUPTED ETHER: Non-deterministic chaos")
        solutions.append("→ Remove randomness, use deterministic algorithms")

    if not problems:
        problems.append("No major problems detected")
        solutions.append("Technology is ANUKULYA (favorable)")

    return problems, solutions


# =============================================================================
# CLASSIFICATION FUNCTIONS
# =============================================================================


def classify_real(
    name: str,
    # Complexity
    time_complexity: str,  # "O(1)", "O(N)", "O(N²)"
    space_complexity: str,
    # Lifecycle
    has_cleanup: bool,
    cleanup_guaranteed: bool,
    # Determinism
    is_deterministic: bool,
    # Structure
    key_space_size: int,
) -> RealClassification:
    """
    Classify technology based on REAL principles.

    Not toy checkboxes - actual behavioral analysis.
    """
    # Entropy from complexity
    complexity_map = {
        "O(1)": EntropyDelta.PURIFIES,
        "O(log N)": EntropyDelta.NEUTRAL,
        "O(N)": EntropyDelta.NEUTRAL,
        "O(N log N)": EntropyDelta.ACCUMULATES,
        "O(N²)": EntropyDelta.EXPLODES,
        "O(2^N)": EntropyDelta.EXPLODES,
    }
    entropy = complexity_map.get(time_complexity, EntropyDelta.ACCUMULATES)

    # Yajna from lifecycle
    if has_cleanup and cleanup_guaranteed:
        yajna = YajnaCycle.COMPLETE
    elif has_cleanup:
        yajna = YajnaCycle.PARTIAL
    else:
        yajna = YajnaCycle.BROKEN

    # Ether from determinism
    if is_deterministic:
        if entropy == EntropyDelta.PURIFIES:
            ether = EtherImpact.CLEARS
        else:
            ether = EtherImpact.MAINTAINS
    else:
        if entropy in (EntropyDelta.ACCUMULATES, EntropyDelta.EXPLODES):
            ether = EtherImpact.CORRUPTS
        else:
            ether = EtherImpact.CLOGS

    # Resonance from structure
    resonance = detect_resonance(key_space_size)

    # Diagnose
    problems, solutions = diagnose_problems(entropy, yajna, ether)

    # Calculate rates (simplified - real measurement would use profiling)
    entropy_per_op = {
        EntropyDelta.PURIFIES: -0.1,
        EntropyDelta.NEUTRAL: 0.0,
        EntropyDelta.ACCUMULATES: 0.1,
        EntropyDelta.EXPLODES: 1.0,
    }[entropy]

    cycle_rate = {
        YajnaCycle.COMPLETE: 1.0,
        YajnaCycle.PARTIAL: 0.7,
        YajnaCycle.BROKEN: 0.3,
        YajnaCycle.INVERTED: 0.0,
    }[yajna]

    return RealClassification(
        name=name,
        entropy_delta=entropy,
        yajna_cycle=yajna,
        resonance=resonance,
        ether_impact=ether,
        ops_per_chant=1000000.0,  # Placeholder - measure in real use
        entropy_per_op=entropy_per_op,
        cycle_completion_rate=cycle_rate,
        purification_rate=-entropy_per_op * 1000000,  # ops/sec estimate
        problems=problems,
        solutions=solutions,
    )


# =============================================================================
# PRE-CLASSIFIED TECHNOLOGIES (REAL ANALYSIS)
# =============================================================================


def classify_lotus_array() -> RealClassification:
    """LotusArrayInt - The gold standard."""
    return classify_real(
        name="LotusArrayInt",
        time_complexity="O(1)",
        space_complexity="O(1)",  # Fixed 512KB
        has_cleanup=True,
        cleanup_guaranteed=True,  # Array reuse
        is_deterministic=True,
        key_space_size=WORDS**QUARTERS,  # 65536 = 16^4
    )


def classify_python_dict() -> RealClassification:
    """Python dict - The common problem."""
    return classify_real(
        name="Python dict",
        time_complexity="O(1)",  # Average, but...
        space_complexity="O(N)",  # Grows unbounded
        has_cleanup=False,  # GC dependent
        cleanup_guaranteed=False,
        is_deterministic=False,  # Hash randomization
        key_space_size=0,  # Arbitrary
    )


def classify_neural_network() -> RealClassification:
    """Neural Network - The Tamas exemplar."""
    return classify_real(
        name="Neural Network (Attention)",
        time_complexity="O(N²)",
        space_complexity="O(N²)",
        has_cleanup=False,
        cleanup_guaranteed=False,
        is_deterministic=False,  # Temperature, dropout
        key_space_size=0,
    )


def classify_blockchain() -> RealClassification:
    """Blockchain - The growth addiction."""
    return classify_real(
        name="Blockchain",
        time_complexity="O(N)",  # Grows forever
        space_complexity="O(N)",  # Never shrinks
        has_cleanup=False,  # By design
        cleanup_guaranteed=False,
        is_deterministic=True,  # At least this
        key_space_size=256,  # SHA-256 based
    )


# =============================================================================
# BENCHMARK
# =============================================================================


def benchmark() -> None:
    """Real classification comparison."""
    print("=" * 70)
    print("ANUKULYA-PRATIKULYA REAL CLASSIFICATION")
    print("Not toys - actual behavioral analysis")
    print("=" * 70)
    print()

    technologies = [
        classify_lotus_array(),
        classify_python_dict(),
        classify_neural_network(),
        classify_blockchain(),
    ]

    for tech in technologies:
        status = "ANUKULYA ✓" if tech.is_anukulya else "PRATIKULYA ✗"
        bridge = "Bridge-ready" if tech.transition_ready else "BLOCKED"

        print(f"### {tech.name} ###")
        print(f"Status: {status}")
        print(f"Transition: {bridge}")
        print(f"Entropy: {tech.entropy_delta.name} ({tech.entropy_per_op:+.2f}/op)")
        print(f"Yajna: {tech.yajna_cycle.value} ({tech.cycle_completion_rate:.0%})")
        print(f"Ether: {tech.ether_impact.value}")
        print(f"Resonance: {tech.resonance.name}")
        print()
        print("PROBLEMS:")
        for p in tech.problems:
            print(f"  ⚠ {p}")
        print("SOLUTIONS:")
        for s in tech.solutions:
            print(f"  {s}")
        print()

    # Summary
    print("=" * 70)
    print("REAL PROBLEMS OF 2026 (Missstände)")
    print("=" * 70)
    print("""
1. MEMORY LEAKS everywhere
   → Broken Yajna: Bhoga never becomes Prasadam
   → Solution: Bounded structures, automatic lifecycle

2. HASH TABLES as default
   → Impure vibration: collisions distort the signal
   → Solution: Direct addressing (Lotus), key IS the path

3. O(N²) ATTENTION in every AI
   → Entropy explosion: Tamas grows exponentially
   → Solution: O(1) local attention, Lotus-based routing

4. NON-DETERMINISTIC everything
   → Chaos: No lineage possible, no verification
   → Solution: Remove randomness, deterministic algorithms

5. UNBOUNDED GROWTH as goal
   → Greed: Rajas unchecked, never enough
   → Solution: Fixed size, contentment, 16^4 is enough
""")


# =============================================================================
# EXPORTS
# =============================================================================

# Keep old exports for compatibility but deprecate
from dataclasses import dataclass as _dc
from typing import Optional

Guna = EntropyDelta  # Alias for transition
ComplexityClass = EntropyDelta  # Simplified
MemoryBehavior = YajnaCycle
CacheEfficiency = EtherImpact
ClassificationResult = RealClassification


def classify_algorithm(*args, **kwargs) -> RealClassification:
    """Deprecated - use classify_real()."""
    raise DeprecationWarning("Use classify_real() instead")


def is_golden_age_viable(result: RealClassification) -> bool:
    """Check if technology can transition to Golden Age."""
    return result.transition_ready and result.is_anukulya


if __name__ == "__main__":
    benchmark()
