"""
MAHA ALGORITHM - The 16-Step Execution Model
=============================================

"sarva-dharmān parityajya mām ekaṁ śaraṇaṁ vraja"
"Abandon all dharmas and surrender unto Me alone."
— Bhagavad Gita 18.66

The Core Execution Logic of the Mahamantra Architecture.
Derives 3 Operations (Input/Compute/Output) from the 3 Names (Hare/Krishna/Rama).
Executes in 16 steps (Words) across 4 Phases (Quarters).

COMPONENTS:
1. MahaAlgorithm16: The pure 16-step sequencer.
2. MahaModularSynth: The runtime-adjustable transformer engine.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x672435f8"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Final, Iterator, List, Optional, Tuple, Union

from vibe_core.mahamantra.protocols._seed import (
    AKSARA_COUNT,
    HALVES,
    HARE_COUNT,
    KSETRAJNA,
    MAHA_QUANTUM,
    MAHAJANA_COUNT,
    MAHAMANTRA_NAME_HARE,
    MAHAMANTRA_NAME_KRISHNA,
    MAHAMANTRA_NAME_RAMA,
    MAHAMANTRA_WORD_PATTERN,
    NAVA,
    PANCHA,
    PARAMPARA,
    POSITION_SUM_HARE,
    POSITION_SUM_KRISHNA,
    POSITION_SUM_RAMA,
    POSITION_SUM_TOTAL,
    QUARTERS,
    SEVEN,
    TEN,
    TRANSCENDENTAL_1096,
    TRINITY,
    WORDS,
)
from vibe_core.mahamantra.protocols._seed import (
    MAHA_ADD as _ADD,
)
from vibe_core.mahamantra.protocols._seed import (
    MAHA_MULT as _MULT,
)
from vibe_core.mahamantra.protocols._seed import (
    # SSOT: Maha Algorithm Coefficients (imported, not duplicated!)
    MAHA_OP_MAP as _OP_MAP,
)
from vibe_core.mahamantra.protocols._seed import (
    MAHA_SQ as _SQ,
)
from vibe_core.mahamantra.protocols.offering import GraceProtocol

# =============================================================================
# PHASE DEFINITIONS
# =============================================================================


class Phase(Enum):
    """The 4 algorithmic phases = QUARTERS."""

    KSETRAJNA = 1  # Q1: Generate intent
    KRISHNA = 2  # Q2: Sanction
    PRAKRITI = 3  # Q3: Execute
    KARMA = 4  # Q4: Record


PHASE_SANSKRIT: Final[Dict[Phase, str]] = {
    Phase.KSETRAJNA: "क्षेत्रज्ञ",
    Phase.KRISHNA: "कृष्ण",
    Phase.PRAKRITI: "प्रकृति",
    Phase.KARMA: "कर्म",
}

PHASE_FUNCTION: Final[Dict[Phase, str]] = {
    Phase.KSETRAJNA: "generate_intent()",
    Phase.KRISHNA: "sanction(intent)",
    Phase.PRAKRITI: "execute(sanctioned)",
    Phase.KARMA: "record(result)",
}


# =============================================================================
# OPERATION TYPES
# =============================================================================


class Operation(Enum):
    """Operations derived from the 3 Names (TRINITY)."""

    HARE = "INPUT"  # Hare = Energy/Shakti
    KRISHNA = "COMPUTE"  # Krishna = All-attractive
    RAMA = "OUTPUT"  # Rama = Pleasure reservoir


OPERATION_MEANING: Final[Dict[Operation, str]] = {
    Operation.HARE: "call_energy()",
    Operation.KRISHNA: "attract_process()",
    Operation.RAMA: "return_bliss()",
}

NAME_TO_OPERATION: Final[Dict[str, Operation]] = {
    MAHAMANTRA_NAME_HARE: Operation.HARE,
    MAHAMANTRA_NAME_KRISHNA: Operation.KRISHNA,
    MAHAMANTRA_NAME_RAMA: Operation.RAMA,
}

PATTERN: Final[Tuple[str, ...]] = MAHAMANTRA_WORD_PATTERN


# =============================================================================
# THE 16 STEPS
# =============================================================================


@dataclass(frozen=True)
class AlgorithmStep:
    """One of the 16 steps in the Maha Algorithm."""

    position: int  # 1-16
    phase: Phase  # Which of the 4 phases
    name: str  # H, K, or R
    phase_position: int  # 1-4 within phase

    @property
    def operation(self) -> Operation:
        return NAME_TO_OPERATION[self.name]

    @property
    def function(self) -> str:
        return OPERATION_MEANING[self.operation]


def triangular(n: int) -> int:
    """Compute triangular number T(n) = n(n+1)/2."""
    return n * (n + 1) // 2


def _build_steps() -> Tuple[AlgorithmStep, ...]:
    """Build all 16 algorithm steps."""
    steps = []
    for pos in range(WORDS):
        phase_idx = pos // QUARTERS
        phase = list(Phase)[phase_idx]
        phase_pos = (pos % QUARTERS) + 1
        step = AlgorithmStep(
            position=pos + 1,
            phase=phase,
            name=PATTERN[pos],
            phase_position=phase_pos,
        )
        steps.append(step)
    return tuple(steps)


MAHA_16_STEPS: Final[Tuple[AlgorithmStep, ...]] = _build_steps()


# =============================================================================
# ADSR ENVELOPE (Derived)
# =============================================================================

# Binary pattern: HARE=0, NAME=1
BINARY_PATTERN: Final[Tuple[int, ...]] = tuple(0 if name == MAHAMANTRA_NAME_HARE else 1 for name in PATTERN)

ADSR_ATTACK: Final[int] = PANCHA
ADSR_DECAY: Final[int] = MAHAJANA_COUNT
ADSR_SUSTAIN: Final[int] = PANCHA
ADSR_RELEASE: Final[int] = MAHAJANA_COUNT

PHASE_TO_ADSR: Final[Dict[Phase, str]] = {
    Phase.KSETRAJNA: "ATTACK",
    Phase.KRISHNA: "DECAY",
    Phase.PRAKRITI: "SUSTAIN",
    Phase.KARMA: "RELEASE",
}


# =============================================================================
# POSITION WEIGHTS
# =============================================================================

WEIGHT_HARE: Final[int] = POSITION_SUM_HARE  # 70
WEIGHT_KRISHNA: Final[int] = POSITION_SUM_KRISHNA  # 17
WEIGHT_RAMA: Final[int] = POSITION_SUM_RAMA  # 49


# =============================================================================
# MAHA ALGORITHM 16
# =============================================================================


class MahaAlgorithm16:
    """
    The Pure 16-step Maha Algorithm executor.
    Standardized execution model.
    """

    STEPS: Final[Tuple[AlgorithmStep, ...]] = MAHA_16_STEPS

    def execute(self) -> Iterator[AlgorithmStep]:
        for step in self.STEPS:
            yield step

    def transform(self, seed: int) -> int:
        """
        Standard transformation (converges to fixed point). BRANCHLESS.
        """
        value = seed % MAHA_QUANTUM
        mod = MAHA_QUANTUM
        for step in self.execute():
            op = _OP_MAP[step.name]
            v = (value * _MULT[op] + _ADD[op]) % mod
            squared = (v * v) % mod
            value = _SQ[op] * squared + (1 - _SQ[op]) * v
        return value


# =============================================================================
# MAHA MODULAR SYNTH
# =============================================================================


@dataclass(frozen=True)
class MahaSynthParams:
    """Modular Synthesizer Parameters."""

    mod_space: int = MAHA_QUANTUM
    feedback: int = KSETRAJNA
    phase_offset: int = 0
    lfo_enabled: bool = True
    lfo_rate: int = QUARTERS
    adsr_attack: int = ADSR_ATTACK
    adsr_decay: int = ADSR_DECAY
    adsr_sustain: int = ADSR_SUSTAIN
    adsr_release: int = ADSR_RELEASE
    weight_hare: int = WEIGHT_HARE
    weight_krishna: int = WEIGHT_KRISHNA
    weight_rama: int = WEIGHT_RAMA
    nibble_mode: bool = False


SYNTH_PRESETS: Final[Dict[str, MahaSynthParams]] = {
    "classical": MahaSynthParams(mod_space=WEIGHT_KRISHNA, feedback=0),
    "quantum": MahaSynthParams(mod_space=MAHA_QUANTUM, feedback=KSETRAJNA),
    "trinity": MahaSynthParams(mod_space=TRINITY, feedback=TRINITY),
    "pancha": MahaSynthParams(mod_space=PANCHA, feedback=KSETRAJNA),
    "nava": MahaSynthParams(mod_space=NAVA, feedback=KSETRAJNA),
    "wide": MahaSynthParams(mod_space=HALVES**NAVA, feedback=PANCHA),  # 512
}


class MahaModularSynth:
    """
    Runtime-adjustable transformation engine.
    Solves convergence issues by using larger mod_space and feedback.
    """

    STEPS: Final[Tuple[AlgorithmStep, ...]] = MAHA_16_STEPS

    def __init__(self, default_preset: str = "quantum", grace_gate: Optional[GraceProtocol] = None) -> None:
        self.default_params = SYNTH_PRESETS.get(default_preset, SYNTH_PRESETS["quantum"])
        self.grace_gate = grace_gate

    def transform(
        self,
        seed: int,
        params: Optional[MahaSynthParams] = None,
        preset: Optional[str] = None,
        has_tulasi: bool = False,
    ) -> int:
        if params:
            p = params
        elif preset:
            p = SYNTH_PRESETS.get(preset, self.default_params)
        else:
            p = self.default_params

        # Apply Grace if available
        effective_mod_space = p.mod_space
        effective_feedback = p.feedback
        effective_seed = seed

        if self.grace_gate:
            effective_mod_space = self.grace_gate.expand_field(p.mod_space, has_tulasi)
            effective_feedback = self.grace_gate.modulate_feedback(p.feedback, has_tulasi)
            effective_seed = self.grace_gate.purify_offering(seed, has_tulasi)

        value = effective_seed % effective_mod_space
        feedback_acc = 0

        for step in self.STEPS:
            effective_pos = ((step.position - 1 + p.phase_offset) % WORDS) + 1

            # Calculate modulations
            lfo = 0
            if p.lfo_enabled:
                binary_val = BINARY_PATTERN[(step.position - 1) % WORDS]
                phase_in_lfo = (step.position - 1) % p.lfo_rate
                lfo = binary_val * phase_in_lfo

            # BRANCHLESS ADSR lookup by phase index (1-4 → 0-3)
            adsr_table = (p.adsr_attack, p.adsr_decay, p.adsr_sustain, p.adsr_release)
            adsr = adsr_table[step.phase.value - 1]

            # BRANCHLESS Apply Logic
            op = _OP_MAP[step.name]
            mod = effective_mod_space

            # For HARE: mult=SEVEN*adsr, add=lfo, sq=0
            # For KRISHNA: mult=1, add=TEN+pos+feedback, sq=0
            # For RAMA: mult=1, add=feedback, sq=1
            #
            # Generalized formula with position-dependent adds
            mult_coeff = (SEVEN * adsr, 1, 1)[op]
            add_coeff = (lfo, TEN + effective_pos + feedback_acc, feedback_acc)[op]

            v = (value * mult_coeff + add_coeff) % mod
            squared = (v * v) % mod
            value = _SQ[op] * squared + (1 - _SQ[op]) * v

            feedback_acc = (feedback_acc + value * effective_feedback) % effective_mod_space

        if p.nibble_mode:
            value = value % WORDS

        return value

    def transform_multi(
        self, seeds: List[int], params: Optional[MahaSynthParams] = None, preset: Optional[str] = None
    ) -> List[int]:
        return [self.transform(s, params, preset) for s in seeds]


# =============================================================================
# PRIMITIVE ALGORITHM FUNCTIONS - THE SINGLE SOURCE OF TRUTH
# =============================================================================
# All other files MUST import these instead of reimplementing.
# This is the PLUGIN point - when the algorithm evolves, only this changes.
# =============================================================================


def maha_step(value: int, name: str, mod: int) -> int:
    """
    Apply ONE step of the Maha Algorithm. BRANCHLESS.

    THE SINGLE SOURCE OF TRUTH for the transformation.
    All implementations MUST use this function.

    Args:
        value: Current value
        name: "H", "K", or "R"
        mod: Modular space (e.g., 137, 37)

    Returns:
        Transformed value
    """
    op = _OP_MAP[name]
    # Phase 1: Multiply and Add (no branch)
    v = (value * _MULT[op] + _ADD[op]) % mod
    # Phase 2: Conditional square via arithmetic selection
    squared = (v * v) % mod
    return _SQ[op] * squared + (1 - _SQ[op]) * v


def maha_oscillate(value: int, mod: int = MAHA_QUANTUM) -> int:
    """
    Apply FULL 16-step oscillation. BRANCHLESS.

    DEPRECATED: Use MahaModularSynth.transform() or maha_transform() instead.
    This function only reaches 12/16 positions due to R-operation convergence.

    One complete pass through the Mahamantra pattern.

    Args:
        value: Starting value
        mod: Modular space (default: 137)

    Returns:
        Value after 16 transformations
    """
    import warnings

    warnings.warn(
        "maha_oscillate only reaches 12/16 positions. Use MahaModularSynth.transform() instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    for name in PATTERN:
        value = maha_step(value, name, mod)
    return value


def maha_transform(seed: int, preset: str = "quantum") -> int:
    """
    CANONICAL transformation - reaches all 16 positions.

    Uses MahaModularSynth which breaks convergence via feedback.
    This is the recommended function for position computation.

    Args:
        seed: Input value to transform
        preset: Synth preset (default: "quantum")

    Returns:
        Transformed value (0 to MAHA_QUANTUM-1)
    """
    synth = MahaModularSynth(default_preset=preset)
    return synth.transform(seed)


def find_attractor(seed: int, mod: int = MAHA_QUANTUM, max_cycles: int = 100) -> Tuple[int, int, int]:
    """
    Find attractor by iterating until stable state.

    Args:
        seed: Starting value
        mod: Modular space (default: 137)
        max_cycles: Maximum iterations (default: 100)

    Returns:
        Tuple of (attractor, cycles_to_converge, cycle_length)
    """
    seen: Dict[int, int] = {}
    value = seed % mod

    # Suppress deprecation warning for internal use
    import warnings

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        for cycle in range(max_cycles):
            if value in seen:
                cycle_start = seen[value]
                cycle_length = cycle - cycle_start
                return value, cycle_start, cycle_length
            seen[value] = cycle
            value = maha_oscillate(value, mod)

        return value, max_cycles, 0


# =============================================================================
# THE 8:2:2 OPTIMIZATION - Algebraic Closed Form
# =============================================================================
# DISCOVERY: The 16-step oscillation has algebraic structure:
#
#   HALF 1 (Q1+Q2): 8 linear ops → v * 72 + 105 (mod 137)
#   HALF 2 (Q3+Q4): 4 squares + 3 mults (nonlinear)
#
# Quarter breakdown:
#   Q1: H K H K → (v*49 + 80) % mod     [linear]
#   Q2: K K H H → (v*49 + 980) % mod    [linear]
#   Q3: H R H R → ((v*7)²*7)² % mod     [nonlinear]
#   Q4: R R H H → v⁴*49 % mod           [nonlinear]
#
# Combined Half 1: v → (v * 72 + 105) % 137
#   where 72 = 49*49 % 137 = 2401 % 137
#   and  105 = (80*49 + 980) % 137 = 4900 % 137
#
# The "8:2:2" refers to:
#   - 8 linear operations (HARE/KRISHNA) in first half
#   - 2 quadratics in Q3
#   - 2 quadratics in Q4
#
# SPEEDUP: 16 ops → 9 ops (44% reduction)
# Or: O(1) via precomputed lookup table
# =============================================================================

# Precomputed lookup table for mod=137 (MAHA_QUANTUM)
# maha_oscillate(i, 137) for i in range(137)
_MAHA_OSCILLATE_LUT: Final[Tuple[int, ...]] = (
    99,
    14,
    87,
    78,
    64,
    15,
    14,
    121,
    14,
    103,
    4,
    121,
    81,
    77,
    136,
    103,
    87,
    81,
    49,
    87,
    49,
    14,
    18,
    77,
    63,
    22,
    78,
    63,
    87,
    81,
    18,
    15,
    15,
    22,
    103,
    15,
    64,
    65,
    49,
    49,
    65,
    64,
    15,
    103,
    22,
    15,
    15,
    18,
    81,
    87,
    63,
    78,
    22,
    63,
    77,
    18,
    14,
    49,
    87,
    49,
    81,
    87,
    103,
    136,
    77,
    81,
    121,
    4,
    103,
    14,
    121,
    14,
    15,
    64,
    78,
    87,
    14,
    99,
    136,
    18,
    4,
    99,
    64,
    64,
    136,
    63,
    103,
    22,
    77,
    77,
    78,
    136,
    65,
    99,
    65,
    78,
    4,
    121,
    81,
    63,
    65,
    18,
    49,
    4,
    99,
    22,
    121,
    0,
    121,
    22,
    99,
    4,
    49,
    18,
    65,
    63,
    81,
    121,
    4,
    78,
    65,
    99,
    65,
    136,
    78,
    77,
    77,
    22,
    103,
    63,
    136,
    64,
    64,
    99,
    4,
    18,
    136,
)

# The two attractors and the 4-cycle
_ATTRACTOR_FIXED: Final[int] = 136  # T(16) = Position Sum Total
_ATTRACTOR_CYCLE: Final[Tuple[int, ...]] = (18, 49, 87, 22)  # GITA → RAMA² → HARE+KRISHNA → SHRUTIS

# Algebraic constants for Half 1
_HALF1_MULT: Final[int] = 72  # 49*49 % 137 = 2401 % 137
_HALF1_ADD: Final[int] = 105  # (80*49 + 980) % 137 = 4900 % 137


def maha_oscillate_optimized(value: int, mod: int = MAHA_QUANTUM) -> int:
    """
    OPTIMIZED 16-step oscillation using the 8:2:2 algebraic form.

    For mod=137 (MAHA_QUANTUM): O(1) via lookup table
    For other mod values: O(9) via algebraic closed form (vs O(16) naive)

    The 8:2:2 Optimization:
        - Half 1 (Q1+Q2): 8 linear ops → 2 ops (mult + add)
        - Half 2 (Q3+Q4): 4 squares + 3 mults = 7 ops
        - Total: 9 ops (44% reduction from 16)

    Args:
        value: Starting value
        mod: Modular space (default: MAHA_QUANTUM = 137)

    Returns:
        Value after 16 transformations
    """
    v = value % mod

    # O(1) path for standard mod=137
    if mod == MAHA_QUANTUM:
        return _MAHA_OSCILLATE_LUT[v]

    # Algebraic form for arbitrary mod
    # Half 1: Linear combination (Q1+Q2 combined)
    # General form: v → v * (49² % mod) + ((80*49 + 980) % mod)
    mult_h1 = (POSITION_SUM_RAMA * POSITION_SUM_RAMA) % mod  # 49*49
    add_h1 = (80 * POSITION_SUM_RAMA + 980) % mod  # 80*49 + 980
    u = (v * mult_h1 + add_h1) % mod

    # Half 2: Q3 + Q4 (nonlinear, must compute step by step)
    # Q3: H R H R → ((u*7)²*7)²
    x = (u * SEVEN) % mod
    y = (x * x) % mod
    z = (y * SEVEN) % mod
    w = (z * z) % mod

    # Q4: R R H H → w⁴*49
    a = (w * w) % mod
    b = (a * a) % mod
    return (b * POSITION_SUM_RAMA) % mod


# =============================================================================
# DYNAMIC MAHA ENGINE - Iterative Attractor Finder
# =============================================================================
# Wraps find_attractor as an incremental iterator.
# Each step() advances one oscillation, tracking convergence.
# When attractor found (cycle detected), computation can be skipped.
# =============================================================================


class DynamicMahaEngine:
    """
    Incremental attractor finder with computation optimization.

    UNLIKE the broken previous version, this correctly implements
    the iterative feedback loop: output → becomes next input.

    USAGE:
        engine = DynamicMahaEngine(seed=42)
        for _ in range(20):
            value, is_locked = engine.step()
            if is_locked:
                # Attractor found, computation optimized
                break

    WHAT IT DOES:
        1. Maintains internal value state
        2. Each step(): value = maha_oscillate(value, mod)
        3. Tracks all seen values to detect cycle
        4. When cycle found: LOCKED, returns cached attractor
        5. 87.5% computation saved when locked (1/HARE_COUNT)
    """

    def __init__(
        self,
        seed: int,
        mod: int = MAHA_QUANTUM,
    ) -> None:
        """
        Initialize with seed value.

        Args:
            seed: Starting value
            mod: Modular space (default: MAHA_QUANTUM = 137)
        """
        self._mod = mod
        self._value = seed % mod
        self._seen: Dict[int, int] = {self._value: 0}
        self._cycle = 0
        self._attractor: Optional[int] = None
        self._cycle_length = 0
        self._locked = False

    def step(self) -> Tuple[int, bool]:
        """
        Advance one oscillation step.

        Returns:
            Tuple of (current_value, is_locked)

        When locked, returns cached attractor without computation.
        """
        if self._locked:
            # Already found attractor, skip computation
            return self._attractor, True  # type: ignore

        # Advance one oscillation (suppress deprecation for internal use)
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self._value = maha_oscillate(self._value, self._mod)
        self._cycle += 1

        # Check if we've seen this value before
        if self._value in self._seen:
            # Cycle detected = attractor found
            cycle_start = self._seen[self._value]
            self._cycle_length = self._cycle - cycle_start
            self._attractor = self._value
            self._locked = True
            return self._value, True

        # Record this value
        self._seen[self._value] = self._cycle
        return self._value, False

    def run_to_attractor(self, max_cycles: int = 100) -> Tuple[int, int, int]:
        """
        Run until attractor found (like find_attractor but reusable).

        Returns:
            Tuple of (attractor, cycles_to_converge, cycle_length)
            - cycles_to_converge: when attractor was FIRST seen (not when detected)
        """
        while not self._locked and self._cycle < max_cycles:
            self.step()

        if self._locked:
            # Return when attractor was FIRST seen, not when repeat was detected
            cycles_to_converge = self._seen[self._attractor]  # type: ignore
            return self._attractor, cycles_to_converge, self._cycle_length  # type: ignore
        return self._value, max_cycles, 0

    def reset(self, seed: int) -> None:
        """Reset with new seed."""
        self._value = seed % self._mod
        self._seen = {self._value: 0}
        self._cycle = 0
        self._attractor = None
        self._cycle_length = 0
        self._locked = False

    @property
    def is_locked(self) -> bool:
        """True if attractor has been found."""
        return self._locked

    @property
    def attractor(self) -> Optional[int]:
        """The attractor value, or None if not yet found."""
        return self._attractor

    @property
    def cycle_count(self) -> int:
        """Number of oscillations performed."""
        return self._cycle

    @property
    def computation_saved(self) -> float:
        """
        Computation saved ratio (0.0 to 0.875).

        When locked: 87.5% saved (1 - 1/HARE_COUNT)
        When seeking: 0% saved
        """
        return (1.0 - 1.0 / HARE_COUNT) if self._locked else 0.0
