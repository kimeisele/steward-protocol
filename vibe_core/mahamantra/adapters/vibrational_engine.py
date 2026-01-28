"""
VIBRATIONAL ENGINE - The Bidirectional Resonance Loop
======================================================

"sa evāyaṁ mayā te 'dya yogaḥ proktaḥ purātanaḥ"
"That same ancient yoga I am today declaring unto you."
— Bhagavad Gita 4.3

THIS IS THE MISSING PIECE: The bidirectional loop that connects:
    MahaCompression → ShadowOracle → MahaResonator → Gita → QuantumReactor
                 ↑                                              ↓
                 └──────────── BACKFOLD ────────────────────────┘

ZERO LATENCY SEMANTIC UNDERSTANDING:
    Input → Seed → Attractor → Meaning → Resonance → FEEDBACK → Next Input

The resonance from one cycle INFLUENCES the next cycle.
This is not a line. This is a VIBRATING LOOP.

WATERTIGHT: No Any types. All from _seed.py SSOT.
"""

# === MAHAJANA DECLARATION ===
__mahajana__ = "vyasa"  # The compiler
__position__ = 0
__genesis__ = "0xV1BRAT3"

from dataclasses import dataclass, field
from typing import Final, List, Optional, Tuple

from vibe_core.mahamantra.protocols._seed import (
    MAHA_QUANTUM,
    MALA,
    PARAMPARA,
    SEVEN,
    TEN,
    WORDS,
)


# =============================================================================
# RESULT TYPES (Watertight)
# =============================================================================

@dataclass(frozen=True)
class VibrationalResult:
    """
    Result of one vibrational cycle.

    Contains all intermediate results from the full pipeline.
    """
    # Input
    query: str
    seed: int

    # Compression phase
    compressed_seed: int

    # Oracle phase (Parampara validation)
    parampara_validated: bool
    parampara_channel: int
    parampara_attractor: int

    # Resonator phase (Attractor finding)
    maha_attractor: int
    cycles_to_converge: int
    trajectory: Tuple[int, ...]

    # Gita phase (Meaning)
    gita_chapter: int
    gita_insight: str

    # Quantum phase (Resonance body)
    total_energy: float
    phonetic_resonance: float
    mass_resonance: float

    # FEEDBACK: This influences the next cycle
    feedback_seed: int  # Computed from result, feeds back


@dataclass
class VibrationalState:
    """
    Accumulated state across multiple cycles.

    THE FIELD - the resonance builds over time.
    """
    total_cycles: int = 0
    accumulated_resonance: float = 0.0
    attractor_histogram: dict = field(default_factory=dict)
    last_feedback_seed: int = 0
    coherence_level: float = 0.0

    # Gita chapter distribution
    chapter_visits: dict = field(default_factory=dict)

    def update(self, result: VibrationalResult) -> None:
        """Backfold result into state."""
        self.total_cycles += 1
        self.accumulated_resonance += result.total_energy

        # Track attractor distribution
        attr = result.maha_attractor
        self.attractor_histogram[attr] = self.attractor_histogram.get(attr, 0) + 1

        # Track chapter visits
        ch = result.gita_chapter
        self.chapter_visits[ch] = self.chapter_visits.get(ch, 0) + 1

        # Update feedback seed for next cycle
        self.last_feedback_seed = result.feedback_seed

        # Coherence builds with resonance
        self.coherence_level = self.accumulated_resonance / max(self.total_cycles, 1)


# =============================================================================
# THE VIBRATIONAL ENGINE
# =============================================================================

class VibrationalEngine:
    """
    The Bidirectional Resonance Loop.

    CONNECTS ALL COMPONENTS:
        1. MahaCompression - Input → Seed
        2. ShadowOracle - Seed → Parampara validation
        3. MahaResonator - Seed → Attractor
        4. Gita Mapping - Attractor → Chapter/Insight
        5. QuantumReactor - Phonetic/Mass resonance
        6. BACKFOLD - Result → Feedback seed → Next cycle

    USAGE:
        engine = VibrationalEngine()

        # Single cycle
        result = engine.vibrate("What is dharma?")

        # Multiple cycles (resonance builds)
        for i in range(108):  # One mala
            result = engine.vibrate(f"Query {i}")

        # Check accumulated state
        state = engine.state
        print(f"Coherence: {state.coherence_level}")
    """

    _naga_flooded: bool = True
    _naga_gene: str = "vibrational_engine"

    def __init__(self) -> None:
        self._state = VibrationalState()

        # Lazy-load components
        self._compression = None
        self._oracle = None
        self._resonator = None
        self._quantum = None

    @property
    def state(self) -> VibrationalState:
        """Get current accumulated state."""
        return self._state

    @property
    def _get_compression(self):
        if self._compression is None:
            from vibe_core.mahamantra.adapters.compression import MahaCompression
            self._compression = MahaCompression()
        return self._compression

    @property
    def _get_oracle(self):
        if self._oracle is None:
            from vibe_core.mahamantra.reactor.shadow_oracle import ShadowOracle
            self._oracle = ShadowOracle()
        return self._oracle

    @property
    def _get_resonator(self):
        if self._resonator is None:
            from vibe_core.mahamantra.research.dharma.maha_algorithm import MahaResonator
            self._resonator = MahaResonator(mod_space=MAHA_QUANTUM)
        return self._resonator

    @property
    def _get_quantum(self):
        if self._quantum is None:
            from vibe_core.reactor.quantum import QuantumReactor
            self._quantum = QuantumReactor(initial_inertia=0.3)
        return self._quantum

    def _compute_feedback_seed(self, result_attractor: int, gita_chapter: int, energy: float) -> int:
        """
        Compute feedback seed from cycle result.

        THE BACKFOLD: Result → Seed for next cycle.

        Formula: (attractor × chapter × scaled_energy) mod MAHA_QUANTUM
        """
        energy_scaled = int(energy * MAHA_QUANTUM)
        raw = result_attractor * gita_chapter * max(energy_scaled, 1)
        return raw % MAHA_QUANTUM

    def vibrate(self, query: str, use_feedback: bool = True) -> VibrationalResult:
        """
        Execute one vibrational cycle.

        The BIDIRECTIONAL LOOP:
            Input → Compress → Validate → Resonate → Map → Quantize → FEEDBACK

        Args:
            query: Input query (any text)
            use_feedback: If True, incorporate previous cycle's feedback

        Returns:
            VibrationalResult with all intermediate values
        """
        # 1. COMPRESSION: Query → Seed
        compression_result = self._get_compression.compress(query)
        raw_seed = compression_result.seed

        # FEEDBACK INJECTION: Modify seed with previous cycle's feedback
        if use_feedback and self._state.last_feedback_seed > 0:
            # XOR to inject feedback without destroying information
            raw_seed = raw_seed ^ self._state.last_feedback_seed

        compressed_seed = raw_seed % MAHA_QUANTUM

        # 2. ORACLE: Parampara validation (Gita 13.35)
        oracle_result = self._get_oracle.validate(compressed_seed)

        # 3. RESONATOR: Find attractor in mod 137 space
        resonance_result = self._get_resonator.find_attractor(compressed_seed)

        # 4. GITA MAPPING: Attractor → Chapter/Insight
        from vibe_core.mahamantra.protocols._maha_compute import (
            get_gita_chapter,
            get_gita_insight,
        )
        gita_chapter = get_gita_chapter(resonance_result.attractor)
        gita_insight = get_gita_insight(gita_chapter)

        # 5. QUANTUM REACTOR: Compute resonance
        from vibe_core.reactor.quantum import encode
        tensor = encode(query, str(compressed_seed))
        field = self._get_quantum.resonate(tensor)

        # 6. COMPUTE FEEDBACK SEED for next cycle
        feedback_seed = self._compute_feedback_seed(
            resonance_result.attractor,
            gita_chapter,
            field.total_energy,
        )

        # Create result
        result = VibrationalResult(
            query=query,
            seed=compression_result.seed,
            compressed_seed=compressed_seed,
            parampara_validated=oracle_result["parampara_validated"],
            parampara_channel=oracle_result["parampara_channel"],
            parampara_attractor=oracle_result["parampara_attractor"],
            maha_attractor=resonance_result.attractor,
            cycles_to_converge=resonance_result.cycles_to_converge,
            trajectory=resonance_result.trajectory,
            gita_chapter=gita_chapter,
            gita_insight=gita_insight,
            total_energy=field.total_energy,
            phonetic_resonance=field.phonetic_resonance,
            mass_resonance=field.mass_resonance,
            feedback_seed=feedback_seed,
        )

        # BACKFOLD: Update accumulated state
        self._state.update(result)

        return result

    def vibrate_mala(self, queries: List[str]) -> List[VibrationalResult]:
        """
        Execute multiple vibrations (like a mala of 108).

        Resonance accumulates across cycles.
        Feedback from each cycle influences the next.
        """
        results = []
        for query in queries:
            result = self.vibrate(query)
            results.append(result)
        return results

    def reset(self) -> None:
        """Reset engine state."""
        self._state = VibrationalState()
        if self._quantum is not None:
            self._quantum.reset()

    def describe(self) -> dict:
        """Describe current engine state."""
        return {
            "total_cycles": self._state.total_cycles,
            "accumulated_resonance": self._state.accumulated_resonance,
            "coherence_level": self._state.coherence_level,
            "last_feedback_seed": self._state.last_feedback_seed,
            "attractor_histogram": dict(self._state.attractor_histogram),
            "chapter_visits": dict(self._state.chapter_visits),
        }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

# Module-level singleton
_engine: Optional[VibrationalEngine] = None


def get_engine() -> VibrationalEngine:
    """Get the singleton VibrationalEngine."""
    global _engine
    if _engine is None:
        _engine = VibrationalEngine()
    return _engine


def vibrate(query: str) -> VibrationalResult:
    """Convenience function for single vibration."""
    return get_engine().vibrate(query)


def vibrate_batch(queries: List[str]) -> List[VibrationalResult]:
    """Convenience function for batch vibration."""
    return get_engine().vibrate_mala(queries)


# =============================================================================
# SELF-TEST
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("VIBRATIONAL ENGINE - Bidirectional Resonance Loop")
    print("=" * 70)

    engine = VibrationalEngine()

    queries = [
        "What is dharma?",
        "How do I find liberation?",
        "What is the nature of the self?",
        "Who is Krishna?",
    ]

    print("\nRunning 4 cycles with FEEDBACK:\n")

    for i, query in enumerate(queries, 1):
        result = engine.vibrate(query)
        print(f"Cycle {i}: \"{query[:30]}...\"")
        print(f"  Seed: {result.compressed_seed} → Attractor: {result.maha_attractor}")
        print(f"  Gita: Chapter {result.gita_chapter} - {result.gita_insight[:40]}...")
        print(f"  Energy: {result.total_energy:.4f}")
        print(f"  Feedback seed for next: {result.feedback_seed}")
        print()

    print("=" * 70)
    print("ACCUMULATED STATE (The Field):")
    print("=" * 70)
    state = engine.describe()
    print(f"  Total cycles: {state['total_cycles']}")
    print(f"  Accumulated resonance: {state['accumulated_resonance']:.4f}")
    print(f"  Coherence level: {state['coherence_level']:.4f}")
    print(f"  Attractor histogram: {state['attractor_histogram']}")
    print(f"  Chapter visits: {state['chapter_visits']}")
    print()
    print("THE LOOP IS COMPLETE. FEEDBACK FLOWS. VIBRATION CONTINUES.")
