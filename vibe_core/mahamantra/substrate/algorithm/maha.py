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
from typing import Final, Iterator, Dict, Tuple, List, Optional, Union, FrozenSet

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
# FLUTE SYNC: BRANCHLESS Resonance Tables (derived from _seed.py)
# =============================================================================
# Krishna's three flutes create sync points:
# MURALI (4 holes) = QUARTERS → syncs every 4th tick
# VENU (6 holes) = SHARANAGATI → syncs every 6th tick
# VAMSI (9 holes) = NAVA → syncs every 9th tick
#
# BRANCHLESS: Precomputed resonance per step position (0-15)
# Resonance formula: 1.0 - (distance_to_sync / half_period)
# =============================================================================

from vibe_core.mahamantra.protocols._seed import (
    VENU_HOLES,
    VAMSI_HOLES,
    MURALI_HOLES,
    SHARANAGATI,
)


def _compute_flute_resonance(tick: int, period: int) -> float:
    """Compute continuous resonance: 1.0 at sync, 0.0 at midpoint."""
    remainder = tick % period
    distance = min(remainder, period - remainder)
    half_period = period / 2.0
    return 1.0 - (distance / half_period)


def _build_flute_resonance_table() -> Tuple[float, ...]:
    """Build combined flute resonance for positions 0-15. BRANCHLESS lookup."""
    table = []
    for pos in range(WORDS):
        tick = pos
        # MURALI uses (tick + 1) for 1-indexed beats
        murali_res = _compute_flute_resonance(tick + 1, MURALI_HOLES)
        venu_res = _compute_flute_resonance(tick, VENU_HOLES)
        vamsi_res = _compute_flute_resonance(tick, VAMSI_HOLES)
        # Weighted: MURALI 40%, VENU 35%, VAMSI 25%
        combined = 0.40 * murali_res + 0.35 * venu_res + 0.25 * vamsi_res
        table.append(combined)
    return tuple(table)


# PRECOMPUTED: Flute resonance per step (0-15)
FLUTE_RESONANCE_TABLE: Final[Tuple[float, ...]] = _build_flute_resonance_table()


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
    tala_enabled: bool = True  # Teental/Mridanga modulation
    flute_enabled: bool = True  # WIRED: FluteSync (MURALI/VENU/VAMSI)
    adsr_attack: int = ADSR_ATTACK
    adsr_decay: int = ADSR_DECAY
    adsr_sustain: int = ADSR_SUSTAIN
    adsr_release: int = ADSR_RELEASE
    weight_hare: int = WEIGHT_HARE
    weight_krishna: int = WEIGHT_KRISHNA
    weight_rama: int = WEIGHT_RAMA
    nibble_mode: bool = False


SYNTH_PRESETS: Final[Dict[str, MahaSynthParams]] = {
    # BASIC PRESETS
    "classical": MahaSynthParams(mod_space=WEIGHT_KRISHNA, feedback=0, tala_enabled=False, flute_enabled=False),
    "quantum": MahaSynthParams(mod_space=MAHA_QUANTUM, feedback=KSETRAJNA),
    "trinity": MahaSynthParams(mod_space=TRINITY, feedback=TRINITY),
    "pancha": MahaSynthParams(mod_space=PANCHA, feedback=KSETRAJNA),
    "nava": MahaSynthParams(mod_space=NAVA, feedback=KSETRAJNA),
    "wide": MahaSynthParams(mod_space=HALVES**NAVA, feedback=PANCHA),  # 512
    # KIRTAN PRESETS - full wiring: tala + flute + 16:7 polyrhythm
    "kirtan": MahaSynthParams(mod_space=MAHA_QUANTUM, feedback=KSETRAJNA, lfo_rate=SEVEN, tala_enabled=True, flute_enabled=True),
    "kirtan_fast": MahaSynthParams(mod_space=MAHA_QUANTUM, lfo_rate=QUARTERS, tala_enabled=True, flute_enabled=True),
    "kirtan_slow": MahaSynthParams(mod_space=MAHA_QUANTUM, lfo_rate=NAVA, tala_enabled=True, flute_enabled=True),
    # FLUTE-ONLY PRESETS (no mridanga)
    "flute_pure": MahaSynthParams(mod_space=MAHA_QUANTUM, tala_enabled=False, flute_enabled=True),
    # MRIDANGA-ONLY PRESETS (no flute)
    "mridanga_pure": MahaSynthParams(mod_space=MAHA_QUANTUM, tala_enabled=True, flute_enabled=False),
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
            # BRANCHLESS: tala_enabled as int multiplier
            tala_flag = int(p.tala_enabled)
            bass = _BASS_PATTERN[step_idx]    # 0 or 1
            treble = _TREBLE_PATTERN[step_idx]  # 0 or 1
            tala_mult = 1 + bass * tala_flag  # 1 or 2 when enabled
            tala_add = treble * SEVEN * tala_flag  # 0 or 7 when enabled

            # FLUTE MODULATION: Combined resonance from MURALI/VENU/VAMSI
            # BRANCHLESS: flute_enabled as float multiplier
            flute_flag = float(p.flute_enabled)
            flute_res = FLUTE_RESONANCE_TABLE[step_idx] * flute_flag  # 0.0-1.0

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
            # WIRED: flute_res modulates feedback accumulation (0.0-1.0)
            mult_coeff = (SEVEN * adsr * tala_mult, tala_mult, tala_mult)[op]
            # Flute resonance scales the additive components (more resonance = more effect)
            flute_scale = int(1 + flute_res * SEVEN)  # 1-8 based on resonance
            add_coeff = (lfo + tala_add, TEN + effective_pos + feedback_acc + tala_add, feedback_acc + tala_add)[op]
            add_coeff = add_coeff * flute_scale // SEVEN  # Normalized scaling

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


# =============================================================================
# LAYAKARI: FRAME SIZES (Vedic Rhythm Layering)
# =============================================================================
# From Vedic music theory (Tala system):
#   Thah   = 1× speed = 16 ticks = WORDS
#   Dugun  = 2× speed = 32 ticks = AKSARA_COUNT
#   Tigun  = 3× speed = 48 ticks = LILA
#   Chougun = 4× speed = 64 ticks = QUALITIES (max frame)
#
# All layers reset at tick 0 (Sam = "together")
#
# NOTE: This is COMPLEMENTARY to MantraTick (venu/tick.py):
#   - MantraTick: STATEFUL clock that tracks time
#   - These constants: Frame sizes for the ALGORITHM at different speeds
# =============================================================================

# Frame sizes at each Layakari speed (all derived from axioms!)
FRAME_THAH: Final[int] = WORDS                 # 16 ticks (1×)
FRAME_DUGUN: Final[int] = WORDS * HALVES       # 32 ticks (2×) = AKSARA_COUNT
FRAME_TIGUN: Final[int] = WORDS * TRINITY      # 48 ticks (3×) = LILA
FRAME_CHOUGUN: Final[int] = WORDS * QUARTERS   # 64 ticks (4×) = QUALITIES

# Max frame = QUALITIES = 64 (Chougun = 4× speed)
MAX_FRAME: Final[int] = FRAME_CHOUGUN

# Layakari speed multipliers (derived from axioms)
LAYAKARI_THAH: Final[int] = KSETRAJNA      # 1× (TRINITY - HALVES = 1)
LAYAKARI_DUGUN: Final[int] = HALVES        # 2× (Axiom)
LAYAKARI_TIGUN: Final[int] = TRINITY       # 3× (Axiom)
LAYAKARI_CHOUGUN: Final[int] = QUARTERS    # 4× (= KRISHNA_COUNT)


# =============================================================================
# TRAJECTORY CLASSIFICATION - Vaikuntha vs Samsara
# =============================================================================
# The Maha Algorithm partitions all seeds into two destinies:
#
# 1. VAIKUNTHA (76.6%): Seeds that converge to fixed point 136 = T(16)
#    - 105 seeds = SEVEN × 15 = 7 × 15
#    - These reach the "spiritual sky" - eternal, unchanging
#
# 2. SAMSARA (23.4%): Seeds trapped in the 4-cycle: 87 → 22 → 18 → 49 → 87
#    - 32 seeds = AKSARA_COUNT
#    - These remain in material existence - cyclic, changing
#
# Mathematical basis: 137 = 32 + 105 = AKSARA_COUNT + (SEVEN × 15)
#
# The 1/4 vs 3/4 ratio matches the Vedic "Ekapad vs Tripad Vibhuti":
#   "pādo 'sya viśvā bhūtāni tripād asyāmṛtaṁ divi"
#   "All beings are one quarter; three quarters are immortal in heaven"
#   — Purusha Sukta, Rig Veda 10.90.3
#
# =============================================================================

class Trajectory(Enum):
    """The two possible destinations in the Maha Algorithm."""
    VAIKUNTHA = "absorption"  # Fixed point 136 - liberation
    SAMSARA = "cycle"         # 4-cycle (87→22→18→49) - material existence


# The Fixed Point: 136 = T(16) = POSITION_SUM_TOTAL
# "sarva-dharmān parityajya mām ekaṁ śaraṇaṁ vraja" (BG 18.66)
FIXED_POINT: Final[int] = POSITION_SUM_TOTAL  # 136

# The 4-Cycle (Samsara): Values derived from Mahamantra constants
# 18 = GITA_CHAPTERS - The spoken instruction
# 49 = POSITION_SUM_RAMA - Pleasure reservoir
# 22 = AKSARA_COUNT - TEN = 32 - 10 - The imperishable reduced
# 87 = POSITION_SUM_HARE + WEIGHT_KRISHNA = 70 + 17 - Energy + All-Attractive
CYCLE_VALUES: Final[Tuple[int, ...]] = (87, 22, 18, 49)

# Verify cycle values form a closed loop
assert maha_oscillate(87, MAHA_QUANTUM) == 22, "87 → 22"
assert maha_oscillate(22, MAHA_QUANTUM) == 18, "22 → 18"
assert maha_oscillate(18, MAHA_QUANTUM) == 49, "18 → 49"
assert maha_oscillate(49, MAHA_QUANTUM) == 87, "49 → 87"

# The 32 CYCLE_SEEDS: Seeds that lead to the Samsara cycle
# Computed: all seeds where trajectory == SAMSARA
# Count = AKSARA_COUNT = 32 (verified below)
CYCLE_SEEDS: Final[FrozenSet[int]] = frozenset({
    2, 16, 18, 19, 20, 22, 25, 28, 30, 33, 38, 39, 44, 47, 49,
    52, 55, 57, 58, 59, 61, 75, 79, 87, 101, 102, 105, 109,
    112, 113, 127, 135
})

# Verify partition: 32 cycle seeds + 105 fixed point seeds = 137
assert len(CYCLE_SEEDS) == AKSARA_COUNT, f"Cycle seeds must be {AKSARA_COUNT}"


# =============================================================================
# BRANCHLESS LOOKUP TABLES - Precomputed for O(1) access, NO CONDITIONALS
# =============================================================================

def _build_trajectory_table() -> Tuple[int, ...]:
    """Build lookup table: seed → 0 (Vaikuntha) or 1 (Samsara)."""
    return tuple(1 if s in CYCLE_SEEDS else 0 for s in range(MAHA_QUANTUM))

def _build_attractor_table() -> Tuple[int, ...]:
    """Build lookup table: seed → final attractor value."""
    table = []
    for seed in range(MAHA_QUANTUM):
        value = seed
        for _ in range(MAHA_QUANTUM):
            next_val = maha_oscillate(value, MAHA_QUANTUM)
            if next_val == value or next_val in CYCLE_VALUES:
                break
            value = next_val
        # Value is now either 136 or in cycle
        table.append(value if value == FIXED_POINT else
                     CYCLE_VALUES[CYCLE_VALUES.index(value) if value in CYCLE_VALUES else 0])
    return tuple(table)

def _build_cycle_position_table() -> Tuple[int, ...]:
    """Build lookup table: seed → cycle position (0-3) or 4 (Vaikuntha)."""
    # 4 = QUARTERS = "not in cycle" sentinel
    cycle_pos_map = {v: i for i, v in enumerate(CYCLE_VALUES)}
    table = []
    for seed in range(MAHA_QUANTUM):
        if seed not in CYCLE_SEEDS:
            table.append(QUARTERS)  # 4 = Vaikuntha sentinel
        else:
            # Find which cycle value this seed reaches
            value = seed
            for _ in range(MAHA_QUANTUM):
                if value in cycle_pos_map:
                    table.append(cycle_pos_map[value])
                    break
                value = maha_oscillate(value, MAHA_QUANTUM)
            else:
                table.append(QUARTERS)
    return tuple(table)

# PRECOMPUTED TABLES - Generated once at import time
TRAJECTORY_TABLE: Final[Tuple[int, ...]] = _build_trajectory_table()
ATTRACTOR_TABLE: Final[Tuple[int, ...]] = _build_attractor_table()
CYCLE_POSITION_TABLE: Final[Tuple[int, ...]] = _build_cycle_position_table()


def classify_trajectory(seed: int, mod: int = MAHA_QUANTUM) -> Trajectory:
    """
    Classify a seed's trajectory. BRANCHLESS via lookup table.

    Args:
        seed: The starting value
        mod: Modular space (default: 137)

    Returns:
        Trajectory.VAIKUNTHA or Trajectory.SAMSARA
    """
    # BRANCHLESS: Table lookup + tuple indexing
    trajectory_idx = TRAJECTORY_TABLE[seed % mod]
    return (Trajectory.VAIKUNTHA, Trajectory.SAMSARA)[trajectory_idx]


def get_cycle_position(seed: int, mod: int = MAHA_QUANTUM) -> int:
    """
    Get position in the Samsara cycle (0-3) or QUARTERS (4) for Vaikuntha.
    BRANCHLESS via lookup table.

    Cycle positions:
        0: 87 (Energy + All-Attractive)
        1: 22 (Imperishable reduced)
        2: 18 (GITA_CHAPTERS - the instruction!)
        3: 49 (RAMA - pleasure reservoir)
        4: Vaikuntha (not in cycle)
    """
    return CYCLE_POSITION_TABLE[seed % mod]


def get_attractor(seed: int, mod: int = MAHA_QUANTUM) -> int:
    """
    Get the final attractor value for a seed. BRANCHLESS via lookup table.

    Returns 136 for Vaikuntha seeds, cycle value for Samsara seeds.
    """
    return ATTRACTOR_TABLE[seed % mod]


# =============================================================================
# BHAKTI MERCY - Liberation from Samsara (100% DERIVED)
# =============================================================================
# "sarva-dharmān parityajya mām ekaṁ śaraṇaṁ vraja
#  ahaṁ tvāṁ sarva-pāpebhyo mokṣayiṣyāmi mā śucaḥ"
# "Abandon all varieties of dharma and surrender unto Me.
#  I shall deliver you from all sinful reactions. Do not fear."
# — Bhagavad Gita 18.66
#
# The BHAKTI_MERCY formula transforms ALL Samsara seeds to Vaikuntha:
#   mercy(seed) = (seed XOR BHAKTI_BRIDGE + KSETRAJNA × trapped) mod 137
#
# DERIVATION:
#   BHAKTI_BRIDGE = POSITION_SUM_HARE + SHARANAGATI = 70 + 6 = 76
#   KSETRAJNA = TRINITY - HALVES = 3 - 2 = 1 (the observer/soul)
#   trapped = 1 if (seed XOR 76) still in CYCLE_SEEDS, else 0
#
# THEOLOGICAL MEANING:
#   - XOR 76 = Prabhupada's Gita (1972 - 1896 = 76) - mercy of the teacher
#   - +KSETRAJNA = The soul's own step toward liberation
#   - Together: 100% liberation (32/32 Samsara seeds freed)
# =============================================================================

# BHAKTI_BRIDGE: Prabhupada's Gita (energy + surrender)
BHAKTI_BRIDGE: Final[int] = POSITION_SUM_HARE + SHARANAGATI  # 70 + 6 = 76

# Import SHARANAGATI if not already available
from vibe_core.mahamantra.protocols._seed import SHARANAGATI

# BHAKTI_GATE: The intermediate step (foundation)
BHAKTI_GATE: Final[int] = HALVES * SEVEN  # 2 × 7 = 14

# Verify derivations
assert BHAKTI_BRIDGE == 76, "BHAKTI_BRIDGE must be 76"
assert BHAKTI_GATE == 14, "BHAKTI_GATE must be 14"


def _build_bhakti_mercy_table() -> Tuple[int, ...]:
    """
    Build lookup table for BHAKTI_MERCY transformation.

    For each seed 0-136:
      - Apply XOR BHAKTI_BRIDGE
      - If still trapped, add KSETRAJNA
      - Return the liberated seed (always leads to Vaikuntha)
    """
    table = []
    for seed in range(MAHA_QUANTUM):
        xored = (seed ^ BHAKTI_BRIDGE) % MAHA_QUANTUM
        # BRANCHLESS: trapped_flag via table lookup
        trapped_flag = TRAJECTORY_TABLE[xored]  # 1 if Samsara, 0 if Vaikuntha
        liberated = (xored + KSETRAJNA * trapped_flag) % MAHA_QUANTUM
        table.append(liberated)
    return tuple(table)


# PRECOMPUTED: Bhakti Mercy transformation table
BHAKTI_MERCY_TABLE: Final[Tuple[int, ...]] = _build_bhakti_mercy_table()


def bhakti_mercy(seed: int, mod: int = MAHA_QUANTUM) -> int:
    """
    Apply BHAKTI_MERCY transformation. BRANCHLESS via lookup table.

    Transforms ANY seed (including Samsara seeds) to a Vaikuntha-bound value.

    Formula: (seed XOR 76 + KSETRAJNA × trapped_flag) mod 137

    Args:
        seed: Any integer seed
        mod: Modular space (default: 137)

    Returns:
        Liberated seed value (always leads to 136/Vaikuntha)
    """
    return BHAKTI_MERCY_TABLE[seed % mod]


def verify_bhakti_mercy() -> bool:
    """
    Verify that BHAKTI_MERCY liberates ALL 32 Samsara seeds.

    Returns True if 100% liberation achieved.
    """
    liberated = 0
    for seed in CYCLE_SEEDS:
        mercied = bhakti_mercy(seed)
        if classify_trajectory(mercied) == Trajectory.VAIKUNTHA:
            liberated += 1
    return liberated == len(CYCLE_SEEDS)  # Must be 32/32


# Verify at import time
assert verify_bhakti_mercy(), "BHAKTI_MERCY must liberate all 32 Samsara seeds"


def trajectory_stats() -> Dict[str, Union[int, float]]:
    """
    Compute trajectory statistics for mod 137.

    Returns dict with:
        - vaikuntha_count: Seeds reaching fixed point (105)
        - samsara_count: Seeds in cycle (32)
        - vaikuntha_ratio: 76.6%
        - samsara_ratio: 23.4%
    """
    vaikuntha = MAHA_QUANTUM - len(CYCLE_SEEDS)
    samsara = len(CYCLE_SEEDS)

    return {
        "vaikuntha_count": vaikuntha,
        "samsara_count": samsara,
        "vaikuntha_ratio": vaikuntha / MAHA_QUANTUM,
        "samsara_ratio": samsara / MAHA_QUANTUM,
        "fixed_point": FIXED_POINT,
        "cycle_values": CYCLE_VALUES,
    }
