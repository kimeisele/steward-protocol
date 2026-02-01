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
from typing import Final, Iterator, Dict, Tuple, List, Optional, Union

from vibe_core.mahamantra.protocols.offering import GraceProtocol
from vibe_core.mahamantra.protocols._seed import (
    AKSARA_COUNT,
    HALVES,
    HARE_COUNT,
    KSETRAJNA,
    MAHA_QUANTUM,
    MAHAJANA_COUNT,
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
    MAHAMANTRA_WORD_PATTERN,
    MAHAMANTRA_NAME_HARE,
    MAHAMANTRA_NAME_KRISHNA,
    MAHAMANTRA_NAME_RAMA,
    # SSOT: Maha Algorithm Coefficients (imported, not duplicated!)
    MAHA_OP_MAP as _OP_MAP,
    MAHA_MULT as _MULT,
    MAHA_ADD as _ADD,
    MAHA_SQ as _SQ,
)

# TEENTAL WIRING: Patterns derived from _seed.py (inline to avoid circular import)
# Teental: Dha Dhin Dhin Dha | Dha Dhin Dhin Dha | Dha Tin Tin Ta | Ta Dhin Dhin Dha
# Binary:  11  11   11   11    11  11   11   11    11  01  01  10   10  11   11   11
# Bass (bit 1):  1   1    1    1     1   1    1    1     1   0   0   1    1   1    1    1
# Treble (bit 0): 1   1    1    1     1   1    1    1     1   1   1   0    0   1    1    1
_TEENTAL_BINARY: Final[Tuple[int, ...]] = (3, 3, 3, 3, 3, 3, 3, 3, 3, 1, 1, 2, 2, 3, 3, 3)
_BASS_PATTERN: Final[Tuple[int, ...]] = tuple((b >> 1) & 1 for b in _TEENTAL_BINARY)
_TREBLE_PATTERN: Final[Tuple[int, ...]] = tuple(b & 1 for b in _TEENTAL_BINARY)
# Verify lengths
assert len(_TEENTAL_BINARY) == WORDS, f"Teental must have {WORDS} beats"
assert len(_BASS_PATTERN) == WORDS
assert len(_TREBLE_PATTERN) == WORDS


# =============================================================================
# PHASE DEFINITIONS
# =============================================================================

class Phase(Enum):
    """The 4 algorithmic phases = QUARTERS."""
    KSETRAJNA = 1  # Q1: Generate intent
    KRISHNA = 2    # Q2: Sanction
    PRAKRITI = 3   # Q3: Execute
    KARMA = 4      # Q4: Record


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
    HARE = "INPUT"      # Hare = Energy/Shakti
    KRISHNA = "COMPUTE" # Krishna = All-attractive
    RAMA = "OUTPUT"     # Rama = Pleasure reservoir


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
    phase: Phase   # Which of the 4 phases
    name: str      # H, K, or R
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

WEIGHT_HARE: Final[int] = POSITION_SUM_HARE        # 70
WEIGHT_KRISHNA: Final[int] = POSITION_SUM_KRISHNA  # 17
WEIGHT_RAMA: Final[int] = POSITION_SUM_RAMA        # 49


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
    lfo_rate: int = SEVEN  # WIRED: Creates 16:7 polyrhythm (was QUARTERS)
    tala_enabled: bool = True  # NEW: Enable Teental/Mridanga modulation
    adsr_attack: int = ADSR_ATTACK
    adsr_decay: int = ADSR_DECAY
    adsr_sustain: int = ADSR_SUSTAIN
    adsr_release: int = ADSR_RELEASE
    weight_hare: int = WEIGHT_HARE
    weight_krishna: int = WEIGHT_KRISHNA
    weight_rama: int = WEIGHT_RAMA
    nibble_mode: bool = False


SYNTH_PRESETS: Final[Dict[str, MahaSynthParams]] = {
    "classical": MahaSynthParams(mod_space=WEIGHT_KRISHNA, feedback=0, tala_enabled=False),
    "quantum": MahaSynthParams(mod_space=MAHA_QUANTUM, feedback=KSETRAJNA),
    "trinity": MahaSynthParams(mod_space=TRINITY, feedback=TRINITY),
    "pancha": MahaSynthParams(mod_space=PANCHA, feedback=KSETRAJNA),
    "nava": MahaSynthParams(mod_space=NAVA, feedback=KSETRAJNA),
    "wide": MahaSynthParams(mod_space=HALVES**NAVA, feedback=PANCHA),  # 512
    # KIRTAN PRESETS - with full tala modulation
    "kirtan": MahaSynthParams(mod_space=MAHA_QUANTUM, feedback=KSETRAJNA, lfo_rate=SEVEN, tala_enabled=True),
    "kirtan_fast": MahaSynthParams(mod_space=MAHA_QUANTUM, lfo_rate=QUARTERS, tala_enabled=True),
    "kirtan_slow": MahaSynthParams(mod_space=MAHA_QUANTUM, lfo_rate=NAVA, tala_enabled=True),
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

    def transform(self, seed: int, params: Optional[MahaSynthParams] = None, preset: Optional[str] = None, has_tulasi: bool = False) -> int:
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
            step_idx = step.position - 1  # 0-indexed

            # Calculate modulations
            lfo = 0
            if p.lfo_enabled:
                binary_val = BINARY_PATTERN[step_idx % WORDS]
                phase_in_lfo = step_idx % p.lfo_rate  # WIRED: Uses SEVEN by default
                lfo = binary_val * phase_in_lfo

            # TALA MODULATION: Mridanga stroke affects intensity
            # Bass (baya) = energy multiplier, Treble (daya) = identity additive
            tala_mult = 1
            tala_add = 0
            if p.tala_enabled:
                bass = _BASS_PATTERN[step_idx]    # 0 or 1
                treble = _TREBLE_PATTERN[step_idx]  # 0 or 1
                # Both heads (Dha/Dhin) = full power, single head = half
                tala_mult = 1 + bass  # 1 or 2
                tala_add = treble * SEVEN  # 0 or 7

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
            # WIRED: tala_mult scales the coefficient, tala_add offsets
            mult_coeff = (SEVEN * adsr * tala_mult, tala_mult, tala_mult)[op]
            add_coeff = (lfo + tala_add, TEN + effective_pos + feedback_acc + tala_add, feedback_acc + tala_add)[op]

            v = (value * mult_coeff + add_coeff) % mod
            squared = (v * v) % mod
            value = _SQ[op] * squared + (1 - _SQ[op]) * v

            feedback_acc = (feedback_acc + value * effective_feedback) % effective_mod_space

        if p.nibble_mode:
            value = value % WORDS
            
        return value

    def transform_multi(self, seeds: List[int], params: Optional[MahaSynthParams] = None, preset: Optional[str] = None) -> List[int]:
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

    One complete pass through the Mahamantra pattern.

    Args:
        value: Starting value
        mod: Modular space (default: 137)

    Returns:
        Value after 16 transformations
    """
    for name in PATTERN:
        value = maha_step(value, name, mod)
    return value


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

    for cycle in range(max_cycles):
        if value in seen:
            cycle_start = seen[value]
            cycle_length = cycle - cycle_start
            return value, cycle_start, cycle_length
        seen[value] = cycle
        value = maha_oscillate(value, mod)

    return value, max_cycles, 0
