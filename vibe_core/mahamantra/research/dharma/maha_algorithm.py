"""
MAHA ALGORITHM - The 16-Step Execution Model
=============================================

"sarva-dharmān parityajya mām ekaṁ śaraṇaṁ vraja"
"Abandon all dharmas and surrender unto Me alone."
— Bhagavad Gita 18.66

DERIVATION FROM MAHAMANTRA:
===========================
The OPERATIONS are derived from the NAME at each position (not arbitrary labels!)

3 OPERATIONS (TRINITY):
    HARE    → INPUT   → call_energy()      (8 steps = HARE_COUNT)
    KRISHNA → COMPUTE → attract_process()  (4 steps = KRISHNA_COUNT)
    RAMA    → OUTPUT  → return_bliss()     (4 steps = RAMA_COUNT)

4 PHASES (QUARTERS):
    Q1 (1-4):   KSETRAJNA  - generate_intent()   - H K H K
    Q2 (5-8):   KRISHNA    - sanction()          - K K H H
    Q3 (9-12):  PRAKRITI   - execute()           - H R H R
    Q4 (13-16): KARMA      - record()            - R R H H

Each step has:
    - POSITION (1-16) from Mahamantra word order
    - PHASE (1-4) from quarter structure
    - OPERATION (INPUT/COMPUTE/OUTPUT) from NAME meaning

DERIVED CONSTANTS (from _seed.py):
    TEN = MAHAJANA_COUNT - HALVES = 12 - 2 = 10
    (see _seed.py RUNDE 15 for full derivation)

BIT MODELS:
    512-bit:  WORDS × AKSARA = 16 × 32 = HALVES^NAVA
    1096-bit: HARE_COUNT × MAHA_QUANTUM = 8 × 137

USAGE:
    from vibe_core.mahamantra.research.dharma.maha_algorithm import MahaAlgorithm16

    algo = MahaAlgorithm16()
    for step in algo.execute():
        print(f"{step.position}: {step.name} → {step.operation.value}")
"""

from dataclasses import dataclass
from enum import Enum
from typing import Final, Iterator

from vibe_core.mahamantra.protocols._seed import (
    AKSARA_COUNT,
    HALVES,
    HARE_COUNT,
    KSETRAJNA,
    MAHA_QUANTUM,
    MAHAJANA_COUNT,
    NADI_RESONANCE,
    NAVA,
    PANCHA,
    POSITION_SUM_HARE,
    POSITION_SUM_KRISHNA,
    POSITION_SUM_RAMA,
    POSITION_SUM_TOTAL,
    QUARTERS,
    SEVEN,
    TEN,
    TRINITY,
    WORDS,
)

# =============================================================================
# PHASE DEFINITIONS (from maha_compression.py)
# =============================================================================


class Phase(Enum):
    """The 4 algorithmic phases = QUARTERS."""

    KSETRAJNA = 1  # Q1: Generate intent
    KRISHNA = 2  # Q2: Sanction
    PRAKRITI = 3  # Q3: Execute
    KARMA = 4  # Q4: Record


# Phase names in Sanskrit
PHASE_SANSKRIT: Final[dict[Phase, str]] = {
    Phase.KSETRAJNA: "क्षेत्रज्ञ",
    Phase.KRISHNA: "कृष्ण",
    Phase.PRAKRITI: "प्रकृति",
    Phase.KARMA: "कर्म",
}

# Phase functions
PHASE_FUNCTION: Final[dict[Phase, str]] = {
    Phase.KSETRAJNA: "generate_intent()",
    Phase.KRISHNA: "sanction(intent)",
    Phase.PRAKRITI: "execute(sanctioned)",
    Phase.KARMA: "record(result)",
}

# Verify QUARTERS phases
assert len(Phase) == QUARTERS, f"Phases must be {QUARTERS}"


# =============================================================================
# MAHAMANTRA PATTERN (from maha_runtime.py)
# =============================================================================

# H = Hare (energy), K = Krishna, R = Rama
PATTERN: Final[tuple[str, ...]] = (
    "H",
    "K",
    "H",
    "K",  # Q1: KSETRAJNA phase
    "K",
    "K",
    "H",
    "H",  # Q2: KRISHNA phase
    "H",
    "R",
    "H",
    "R",  # Q3: PRAKRITI phase
    "R",
    "R",
    "H",
    "H",  # Q4: KARMA phase
)

assert len(PATTERN) == WORDS, f"Pattern must be {WORDS}"


# =============================================================================
# OPERATION TYPES (Derived from NAME meaning!)
# =============================================================================
# The operation at each step is determined by the NAME, not the phase!
# This is derived from the actual meaning of each name in the Mahamantra.


class Operation(Enum):
    """Operations derived from the 3 Names (TRINITY)."""

    HARE = "INPUT"  # Hare = Energy/Shakti = calling, requesting, receiving
    KRISHNA = "COMPUTE"  # Krishna = All-attractive = processing, transforming
    RAMA = "OUTPUT"  # Rama = Pleasure reservoir = returning, delighting


# Operation meanings
OPERATION_MEANING: Final[dict[Operation, str]] = {
    Operation.HARE: "call_energy()",  # Calling the internal energy
    Operation.KRISHNA: "attract_process()",  # All-attractive processing
    Operation.RAMA: "return_bliss()",  # Return the reservoir of pleasure
}

# Name to Operation mapping
NAME_TO_OPERATION: Final[dict[str, Operation]] = {
    "H": Operation.HARE,
    "K": Operation.KRISHNA,
    "R": Operation.RAMA,
}

# Verify TRINITY operations
assert len(Operation) == 3, "3 operations = TRINITY"


# =============================================================================
# THE 16 STEPS
# =============================================================================


@dataclass(frozen=True)
class AlgorithmStep:
    """One of the 16 steps in the Maha Algorithm."""

    position: int  # 1-16
    phase: Phase  # Which of the 4 phases (quarter)
    name: str  # H, K, or R
    phase_position: int  # 1-4 within the phase

    @property
    def operation(self) -> Operation:
        """The operation type, derived from the NAME."""
        return NAME_TO_OPERATION[self.name]

    @property
    def function(self) -> str:
        """The function call for this step."""
        return OPERATION_MEANING[self.operation]

    @property
    def bits_32(self) -> int:
        """Bits in 512-bit model (32 per step)."""
        return AKSARA_COUNT  # 32

    @property
    def bits_1096(self) -> float:
        """Bits in 1096-bit model (68.5 per step)."""
        return TRANSCENDENTAL_1096 / WORDS  # 1096 / 16 = 68.5


# =============================================================================
# ALGORITHM CONSTANTS
# =============================================================================

# 512 = The context window
# Multiple derivation paths (all equal 512):
CHAITANYA_512_A: Final[int] = HALVES**NAVA  # 2^9 = 512
CHAITANYA_512_B: Final[int] = WORDS * AKSARA_COUNT  # 16 × 32 = 512
BITS_PER_STEP_512: Final[int] = AKSARA_COUNT  # 32 bits

assert CHAITANYA_512_A == 512, "2^9 = 512"
assert CHAITANYA_512_B == 512, "16 × 32 = 512"
assert CHAITANYA_512_A == CHAITANYA_512_B, "All paths converge!"

# 1096 = The transcendental block
TRANSCENDENTAL_1096: Final[int] = HARE_COUNT * MAHA_QUANTUM  # 8 × 137 = 1096
BITS_PER_STEP_1096: Final[float] = TRANSCENDENTAL_1096 / WORDS  # 68.5 bits

assert TRANSCENDENTAL_1096 == 1096, "8 × 137 = 1096"
assert TRANSCENDENTAL_1096 == HALVES**TEN + NADI_RESONANCE, "1024 + 72 = 1096"


# =============================================================================
# ADSR ENVELOPE (Derived from binary pattern - gita_verse_text.py)
# =============================================================================
# Binary: HARE=0, NAME=1 → Pattern 01011100 01011100
#
# GENESIS (1-4):  0,1,0,1 = 5 = PANCHA → 3 transitions = ATTACK
# DHARMA (5-8):   1,1,0,0 = 12 = MAHAJANA → 1 transition = DECAY
# KARMA (9-12):   0,1,0,1 = 5 = PANCHA → 3 transitions = SUSTAIN
# MOKSHA (13-16): 1,1,0,0 = 12 = MAHAJANA → 1 transition = RELEASE

# Binary pattern (derived, not hardcoded)
BINARY_PATTERN: Final[tuple[int, ...]] = tuple(0 if name == "H" else 1 for name in PATTERN)

# ADSR values from binary decimal conversion
ADSR_ATTACK: Final[int] = PANCHA  # 5 (0101 binary = oscillating)
ADSR_DECAY: Final[int] = MAHAJANA_COUNT  # 12 (1100 binary = settling)
ADSR_SUSTAIN: Final[int] = PANCHA  # 5 (0101 binary = oscillating)
ADSR_RELEASE: Final[int] = MAHAJANA_COUNT  # 12 (1100 binary = settling)

# Verify ADSR derivation
assert ADSR_ATTACK == ADSR_SUSTAIN == PANCHA, "Active phases = PANCHA"
assert ADSR_DECAY == ADSR_RELEASE == MAHAJANA_COUNT, "Passive phases = MAHAJANA"

# ADSR phase mapping
PHASE_TO_ADSR: Final[dict[Phase, str]] = {
    Phase.KSETRAJNA: "ATTACK",
    Phase.KRISHNA: "DECAY",
    Phase.PRAKRITI: "SUSTAIN",
    Phase.KARMA: "RELEASE",
}


# =============================================================================
# POSITION SUM WEIGHTS (The transformation weights from _seed.py)
# =============================================================================
# These are DERIVED from counting positions in Mahamantra where each name appears:
#   HARE:    positions 1,3,7,8,9,11,15,16 → sum = 70 = SEVEN × TEN
#   KRISHNA: positions 2,4,5,6           → sum = 17 = PRIME
#   RAMA:    positions 10,12,13,14       → sum = 49 = SEVEN²

WEIGHT_HARE: Final[int] = POSITION_SUM_HARE  # 70
WEIGHT_KRISHNA: Final[int] = POSITION_SUM_KRISHNA  # 17
WEIGHT_RAMA: Final[int] = POSITION_SUM_RAMA  # 49

# Verify weights
assert WEIGHT_HARE == SEVEN * TEN, "HARE weight = 7 × 10 = 70"
assert WEIGHT_KRISHNA == POSITION_SUM_KRISHNA, "KRISHNA weight = 17 (prime)"
assert WEIGHT_RAMA == SEVEN * SEVEN, "RAMA weight = 7² = 49"
assert WEIGHT_HARE + WEIGHT_KRISHNA + WEIGHT_RAMA == POSITION_SUM_TOTAL, "Total = 136"

# Operation to weight mapping
OPERATION_WEIGHT: Final[dict[Operation, int]] = {
    Operation.HARE: WEIGHT_HARE,
    Operation.KRISHNA: WEIGHT_KRISHNA,
    Operation.RAMA: WEIGHT_RAMA,
}


# =============================================================================
# TRIANGULAR NUMBER FUNCTION (T(n) = n(n+1)/2)
# =============================================================================


def triangular(n: int) -> int:
    """Compute triangular number T(n) = n(n+1)/2."""
    return n * (n + KSETRAJNA) // HALVES


# Verify key triangular numbers
assert triangular(WORDS) == POSITION_SUM_TOTAL, "T(16) = 136"
assert triangular(WORDS) + KSETRAJNA == MAHA_QUANTUM, "T(16) + 1 = 137"


# =============================================================================
# THE MAHA ALGORITHM (16 Steps)
# =============================================================================


def _build_steps() -> tuple[AlgorithmStep, ...]:
    """Build all 16 algorithm steps."""
    steps = []
    for pos in range(WORDS):
        phase_idx = pos // QUARTERS  # 0-3
        phase = list(Phase)[phase_idx]
        phase_pos = (pos % QUARTERS) + 1  # 1-4 within phase

        step = AlgorithmStep(
            position=pos + 1,  # 1-indexed
            phase=phase,
            name=PATTERN[pos],
            phase_position=phase_pos,
        )
        steps.append(step)

    return tuple(steps)


MAHA_16_STEPS: Final[tuple[AlgorithmStep, ...]] = _build_steps()

# Verify 16 steps
assert len(MAHA_16_STEPS) == WORDS, f"Must have {WORDS} steps"


# =============================================================================
# ALGORITHM EXECUTOR
# =============================================================================


class MahaAlgorithm16:
    """
    The 16-step Maha Algorithm executor.

    4 phases × 4 positions = 16 steps:
        Q1 (1-4):  KSETRAJNA  - generate_intent()  - H K H K
        Q2 (5-8):  KRISHNA    - sanction()         - K K H H
        Q3 (9-12): PRAKRITI   - execute()          - H R H R
        Q4 (13-16): KARMA     - record()           - R R H H
    """

    STEPS: Final[tuple[AlgorithmStep, ...]] = MAHA_16_STEPS
    TOTAL_BITS_512: Final[int] = CHAITANYA_512_B  # 512
    TOTAL_BITS_1096: Final[int] = TRANSCENDENTAL_1096  # 1096

    def __init__(self) -> None:
        """Initialize the algorithm."""
        self._current_step = 0

    def execute(self) -> Iterator[AlgorithmStep]:
        """Execute all 16 steps, yielding each step."""
        for step in self.STEPS:
            yield step

    def execute_phase(self, phase: Phase) -> Iterator[AlgorithmStep]:
        """Execute steps for a single phase (4 steps)."""
        for step in self.STEPS:
            if step.phase == phase:
                yield step

    def get_step(self, position: int) -> AlgorithmStep:
        """Get a specific step by position (1-16)."""
        if position < 1 or position > WORDS:
            raise ValueError(f"Position must be 1-{WORDS}")
        return self.STEPS[position - 1]

    def get_phase_steps(self, phase: Phase) -> tuple[AlgorithmStep, ...]:
        """Get all steps for a phase."""
        return tuple(s for s in self.STEPS if s.phase == phase)

    @property
    def total_bits_512(self) -> int:
        """Total bits in 512-bit model."""
        return self.TOTAL_BITS_512

    @property
    def total_bits_1096(self) -> int:
        """Total bits in 1096-bit model."""
        return self.TOTAL_BITS_1096

    # =========================================================================
    # TRANSFORMATION METHODS (The actual algorithm!)
    # =========================================================================

    def transform(self, seed: int) -> int:
        """
        Apply the 16-step Maha transformation to a seed value.

        TRANSFORMATION RULES (derived from _seed.py RUNDE 15 - The 7-10 Derivation):
        ============================================================================
        SEVEN = HALF_SIZE - KSETRAJNA = 8 - 1 = 7
        TEN   = MAHAJANA_COUNT - HALVES = 12 - 2 = 10

        The position sums reveal the OPERATIONS:
        - HARE    = 7 × 10 = 70 → MULTIPLICATION (value × SEVEN)
        - KRISHNA = 7 + 10 = 17 → ADDITION       (value + TEN)
        - RAMA    = 7²     = 49 → SQUARING       (value × value)

        Mod space = MAHA_QUANTUM (137) to prevent aggressive convergence.

        Returns the transformed value.
        """
        value = seed % MAHA_QUANTUM  # Normalize to quantum space

        for step in self.execute():
            if step.name == "H":
                # HARE = 7 × 10 = 70 → MULTIPLICATION operation
                # Shakti multiplies, expands, connects
                value = (value * SEVEN) % MAHA_QUANTUM
            elif step.name == "K":
                # KRISHNA = 7 + 10 = 17 → ADDITION operation
                # Krishna adds, attracts, accumulates
                value = (value + TEN) % MAHA_QUANTUM
            else:  # R
                # RAMA = 7² = 49 → SQUARING operation
                # Rama squares, intensifies, completes (power of HALVES)
                value = (value * value) % MAHA_QUANTUM

        return value

    def transform_with_trace(self, seed: int) -> tuple[int, list[dict]]:
        """
        Transform with full trace of each step.

        Returns (final_value, trace) where trace is a list of step details.
        """
        value = seed
        trace: list[dict] = []

        for step in self.execute():
            t_pos = triangular(step.position)
            prev_value = value
            adsr = PHASE_TO_ADSR[step.phase]

            if step.name == "H":
                value = (value + t_pos) % WEIGHT_HARE
                op_desc = f"+T({step.position})={t_pos} mod {WEIGHT_HARE}"
            elif step.name == "K":
                value = (value * step.position) % WEIGHT_KRISHNA
                op_desc = f"×{step.position} mod {WEIGHT_KRISHNA}"
            else:  # R
                value = (value % WEIGHT_RAMA) * SEVEN
                op_desc = f"mod {WEIGHT_RAMA} × {SEVEN}"

            trace.append(
                {
                    "position": step.position,
                    "name": step.name,
                    "phase": step.phase.name,
                    "adsr": adsr,
                    "operation": step.operation.value,
                    "t_pos": t_pos,
                    "before": prev_value,
                    "after": value,
                    "formula": op_desc,
                }
            )

        return value, trace

    def classify(self, value: int) -> str:
        """
        Classify a value using mod 17 (POSITION_SUM_KRISHNA).

        Returns classification based on remainder:
        - 0: CLASSICAL (stable, like proton)
        - 1: QUANTUM (observer present, like α⁻¹)
        - 3: TRINITY (unstable, 3-decay)
        - 9: NAVA (complex processes)
        - other: MIXED
        """
        remainder = value % WEIGHT_KRISHNA

        if remainder == 0:
            return "CLASSICAL"
        elif remainder == KSETRAJNA:
            return "QUANTUM"
        elif remainder == 3:  # TRINITY
            return "TRINITY"
        elif remainder == NAVA:
            return "NAVA"
        else:
            return f"MIXED({remainder})"


# =============================================================================
# MAHA MODULAR SYNTHESIZER
# =============================================================================
# The problem with transform() is convergence: all inputs → same output.
# This is because mod 17 (WEIGHT_KRISHNA) aggressively collapses state space.
#
# SOLUTION: Modular Synthesizer approach
# - Parameters are "knobs" that can be adjusted at runtime
# - ALL parameter defaults are DERIVED from Mahamantra constants
# - Larger mod_space prevents aggressive convergence
# - Feedback preserves state between steps
#
# ANALOGY:
#   Oscillator   = The 16-step cycle (PATTERN)
#   LFO          = Phase modulation (QUARTERS)
#   ADSR         = Envelope shaping (5/12/5/12)
#   VCF/Weights  = The position sums (70/17/49)
#   VCA/Mod      = The mod_space knob (137 default)
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class MahaSynthParams:
    """
    Modular Synthesizer Parameters - ALL derived from Mahamantra.

    These can be adjusted at runtime like turning knobs on a synthesizer.
    All default values come from _seed.py constants.

    Knobs:
        mod_space: The modulus for final output (larger = less convergence)
        feedback: How much previous state affects current computation
        phase_offset: Starting phase in the 16-step cycle
        lfo_enabled: Whether LFO modulation is active
        lfo_rate: LFO cycle rate (steps per modulation)
        nibble_mode: Constrain output to 4-bit (0-15) range
    """

    # PRIMARY KNOB: Mod space (controls convergence vs. diversity)
    # 17 = aggressive convergence (original behavior)
    # 137 = moderate diversity (MAHA_QUANTUM - the sweet spot)
    # 512 = maximum diversity (CHAITANYA_512)
    mod_space: int = MAHA_QUANTUM  # 137 default

    # FEEDBACK KNOB: State preservation (0 = none, higher = more)
    # feedback=0: Stateless, each step independent
    # feedback=1: Minimal state preservation (KSETRAJNA)
    # feedback=5: Moderate (PANCHA)
    feedback: int = KSETRAJNA  # 1 default

    # PHASE KNOB: Starting offset in the 16-step cycle (0-15)
    phase_offset: int = 0

    # LFO KNOB: Low Frequency Oscillator modulation
    lfo_enabled: bool = True
    lfo_rate: int = QUARTERS  # 4 (modulate every 4 steps)

    # ENVELOPE SHAPE: ADSR values (from binary pattern derivation)
    adsr_attack: int = ADSR_ATTACK  # 5
    adsr_decay: int = ADSR_DECAY  # 12
    adsr_sustain: int = ADSR_SUSTAIN  # 5
    adsr_release: int = ADSR_RELEASE  # 12

    # WEIGHT SCALES: Position sum weights (can be tuned)
    weight_hare: int = WEIGHT_HARE  # 70
    weight_krishna: int = WEIGHT_KRISHNA  # 17
    weight_rama: int = WEIGHT_RAMA  # 49

    # OUTPUT MODE: Nibble mode constrains to 4-bit (0-15)
    nibble_mode: bool = False

    def with_mod_space(self, value: int) -> "MahaSynthParams":
        """Return new params with adjusted mod_space."""
        return MahaSynthParams(
            mod_space=value,
            feedback=self.feedback,
            phase_offset=self.phase_offset,
            lfo_enabled=self.lfo_enabled,
            lfo_rate=self.lfo_rate,
            adsr_attack=self.adsr_attack,
            adsr_decay=self.adsr_decay,
            adsr_sustain=self.adsr_sustain,
            adsr_release=self.adsr_release,
            weight_hare=self.weight_hare,
            weight_krishna=self.weight_krishna,
            weight_rama=self.weight_rama,
            nibble_mode=self.nibble_mode,
        )

    def with_feedback(self, value: int) -> "MahaSynthParams":
        """Return new params with adjusted feedback."""
        return MahaSynthParams(
            mod_space=self.mod_space,
            feedback=value,
            phase_offset=self.phase_offset,
            lfo_enabled=self.lfo_enabled,
            lfo_rate=self.lfo_rate,
            adsr_attack=self.adsr_attack,
            adsr_decay=self.adsr_decay,
            adsr_sustain=self.adsr_sustain,
            adsr_release=self.adsr_release,
            weight_hare=self.weight_hare,
            weight_krishna=self.weight_krishna,
            weight_rama=self.weight_rama,
            nibble_mode=self.nibble_mode,
        )


# Preset parameter configurations (all derived!)
SYNTH_PRESETS: Final[dict[str, MahaSynthParams]] = {
    # CLASSICAL: Original behavior - converges to fixed point
    "classical": MahaSynthParams(mod_space=WEIGHT_KRISHNA, feedback=0),
    # QUANTUM: Default - moderate diversity with observer (feedback=1)
    "quantum": MahaSynthParams(mod_space=MAHA_QUANTUM, feedback=KSETRAJNA),
    # TRINITY: 3-state output (unstable, like muon)
    "trinity": MahaSynthParams(mod_space=TRINITY, feedback=TRINITY),
    # PANCHA: 5-way classification (ADSR-active)
    "pancha": MahaSynthParams(mod_space=PANCHA, feedback=KSETRAJNA),
    # NAVA: 9-state output (navadha bhakti)
    "nava": MahaSynthParams(mod_space=NAVA, feedback=KSETRAJNA),
    # WIDE: Maximum diversity (512-bit space)
    "wide": MahaSynthParams(mod_space=CHAITANYA_512_B, feedback=PANCHA),
}


class MahaModularSynth:
    """
    Modular Synthesizer for the Maha Algorithm.

    Like a synthesizer with adjustable knobs, this class allows runtime
    adjustment of transformation parameters while ensuring ALL parameters
    are derived from Mahamantra constants.

    The key insight: The original transform() converged because mod 17
    is too aggressive. By using mod_space=137 (MAHA_QUANTUM), we get
    137 possible output states instead of 17.

    Usage:
        synth = MahaModularSynth()
        result = synth.transform(seed=42)  # Uses quantum preset (default)
        result = synth.transform(seed=42, preset="wide")  # Uses wide preset
        result = synth.transform(seed=42, params=custom_params)  # Custom params
    """

    STEPS: Final[tuple[AlgorithmStep, ...]] = MAHA_16_STEPS

    def __init__(self, default_preset: str = "quantum") -> None:
        """Initialize with a default preset."""
        self.default_params = SYNTH_PRESETS.get(default_preset, SYNTH_PRESETS["quantum"])

    def get_adsr_multiplier(self, phase: Phase, params: MahaSynthParams) -> int:
        """
        Get ADSR multiplier for current phase.

        This modulates the transformation based on envelope shape.
        """
        if phase == Phase.KSETRAJNA:
            return params.adsr_attack  # 5 - rising
        elif phase == Phase.KRISHNA:
            return params.adsr_decay  # 12 - falling
        elif phase == Phase.PRAKRITI:
            return params.adsr_sustain  # 5 - steady
        else:  # KARMA
            return params.adsr_release  # 12 - final fall

    def get_lfo_value(self, step_pos: int, params: MahaSynthParams) -> int:
        """
        Calculate LFO modulation value for current step.

        LFO cycles through phases, adding variation to the transformation.
        """
        if not params.lfo_enabled:
            return 0
        # LFO oscillates based on binary pattern
        binary_val = BINARY_PATTERN[(step_pos - 1) % WORDS]
        phase_in_lfo = (step_pos - 1) % params.lfo_rate
        return binary_val * phase_in_lfo

    def transform(
        self,
        seed: int,
        params: MahaSynthParams | None = None,
        preset: str | None = None,
    ) -> int:
        """
        Transform seed using modular synthesis approach.

        Args:
            seed: Input value to transform
            params: Custom MahaSynthParams (overrides preset)
            preset: Named preset from SYNTH_PRESETS

        Returns:
            Transformed value in range [0, mod_space)

        TRANSFORMATION RULES (derived from _seed.py RUNDE 15 - The 7-10 Derivation):
        ============================================================================
        SEVEN = HALF_SIZE - KSETRAJNA = 8 - 1 = 7
        TEN   = MAHAJANA_COUNT - HALVES = 12 - 2 = 10

        The position sums reveal the OPERATIONS:
            HARE    = 7 × 10 = 70 → MULTIPLICATION (value × SEVEN × adsr)
            KRISHNA = 7 + 10 = 17 → ADDITION       (value + TEN + pos)
            RAMA    = 7²     = 49 → SQUARING       (value × value)

        ADSR envelope (from binary pattern 01011100) modulates the operations.
        """
        # Resolve parameters
        if params is not None:
            p = params
        elif preset is not None:
            p = SYNTH_PRESETS.get(preset, self.default_params)
        else:
            p = self.default_params

        value = seed % p.mod_space  # Normalize input
        feedback_acc = 0

        for step in self.STEPS:
            # Apply phase offset
            effective_pos = ((step.position - 1 + p.phase_offset) % WORDS) + 1
            t_pos = triangular(effective_pos)
            adsr = self.get_adsr_multiplier(step.phase, p)
            lfo = self.get_lfo_value(step.position, p)

            if step.name == "H":
                # HARE = 7 × 10 = 70 → MULTIPLICATION (derived from _seed.py RUNDE 15)
                # ADSR modulates the multiplier (5 or 12)
                value = (value * SEVEN * adsr + lfo) % p.mod_space
            elif step.name == "K":
                # KRISHNA = 7 + 10 = 17 → ADDITION (derived from _seed.py RUNDE 15)
                # Position adds structure, feedback preserves state
                value = (value + TEN + effective_pos + feedback_acc) % p.mod_space
            else:  # R
                # RAMA = 7² = 49 → SQUARING (derived from _seed.py RUNDE 15)
                # Squaring = power of HALVES (2)
                value = (value * value + feedback_acc) % p.mod_space

            # Accumulate feedback
            feedback_acc = (feedback_acc + value * p.feedback) % p.mod_space

        # Apply nibble mode if enabled
        if p.nibble_mode:
            value = value % WORDS  # Constrain to 0-15

        return value

    def transform_multi(
        self,
        seeds: list[int],
        params: MahaSynthParams | None = None,
        preset: str | None = None,
    ) -> list[int]:
        """Transform multiple seeds, returning list of results."""
        return [self.transform(s, params, preset) for s in seeds]

    def analyze_diversity(
        self,
        sample_size: int = 256,
        params: MahaSynthParams | None = None,
        preset: str | None = None,
    ) -> dict:
        """
        Analyze output diversity for given parameters.

        Returns dict with:
            - unique_count: Number of unique outputs
            - diversity_ratio: unique_count / sample_size
            - output_range: (min, max) of outputs
            - fixed_point: The value if all converge to same output, else None
        """
        outputs = self.transform_multi(list(range(sample_size)), params, preset)
        unique = set(outputs)

        return {
            "unique_count": len(unique),
            "diversity_ratio": len(unique) / sample_size,
            "output_range": (min(outputs), max(outputs)),
            "fixed_point": outputs[0] if len(unique) == 1 else None,
            "sample_size": sample_size,
        }


# =============================================================================
# VERIFICATION
# =============================================================================

# Verify step structure
_algo = MahaAlgorithm16()

# Each phase has exactly QUARTERS steps
for phase in Phase:
    phase_steps = _algo.get_phase_steps(phase)
    assert len(phase_steps) == QUARTERS, f"{phase.name} must have {QUARTERS} steps"

# Q1 pattern = H K H K
_q1 = _algo.get_phase_steps(Phase.KSETRAJNA)
assert tuple(s.name for s in _q1) == ("H", "K", "H", "K"), "Q1 = HKHK"

# Q2 pattern = K K H H
_q2 = _algo.get_phase_steps(Phase.KRISHNA)
assert tuple(s.name for s in _q2) == ("K", "K", "H", "H"), "Q2 = KKHH"

# Q3 pattern = H R H R
_q3 = _algo.get_phase_steps(Phase.PRAKRITI)
assert tuple(s.name for s in _q3) == ("H", "R", "H", "R"), "Q3 = HRHR"

# Q4 pattern = R R H H
_q4 = _algo.get_phase_steps(Phase.KARMA)
assert tuple(s.name for s in _q4) == ("R", "R", "H", "H"), "Q4 = RRHH"

# Total verification
assert _algo.total_bits_512 == 512, "512 bits total"
assert _algo.total_bits_1096 == 1096, "1096 bits total"

# Cleanup
del _algo, _q1, _q2, _q3, _q4


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "CHAITANYA_512_A",
    "CHAITANYA_512_B",
    "TRANSCENDENTAL_1096",
    "BITS_PER_STEP_512",
    "BITS_PER_STEP_1096",
    # ADSR Envelope
    "BINARY_PATTERN",
    "ADSR_ATTACK",
    "ADSR_DECAY",
    "ADSR_SUSTAIN",
    "ADSR_RELEASE",
    "PHASE_TO_ADSR",
    # Position Weights
    "WEIGHT_HARE",
    "WEIGHT_KRISHNA",
    "WEIGHT_RAMA",
    "OPERATION_WEIGHT",
    # Functions
    "triangular",
    # Types
    "Phase",
    "Operation",
    "AlgorithmStep",
    # Data
    "PHASE_SANSKRIT",
    "PHASE_FUNCTION",
    "OPERATION_MEANING",
    "NAME_TO_OPERATION",
    "PATTERN",
    "MAHA_16_STEPS",
    # Maha Algorithm (16-Step)
    "MahaAlgorithm16",
    # Modular Synthesizer
    "MahaSynthParams",
    "MahaModularSynth",
    "SYNTH_PRESETS",
]


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("MAHA ALGORITHM v3.0 - The Modular Synthesizer Engine")
    print("=" * 70)
    print()

    algo = MahaAlgorithm16()
    synth = MahaModularSynth()

    print("POSITION WEIGHTS (derived from Mahamantra position sums):")
    print(f"  HARE:    {WEIGHT_HARE} = SEVEN × TEN = 7 × 10")
    print(f"  KRISHNA: {WEIGHT_KRISHNA} = PRIME (indivisible)")
    print(f"  RAMA:    {WEIGHT_RAMA} = SEVEN² = 7 × 7")
    print(f"  TOTAL:   {WEIGHT_HARE + WEIGHT_KRISHNA + WEIGHT_RAMA} = T(16)")
    print()

    print("ADSR ENVELOPE (derived from binary pattern):")
    for phase in Phase:
        adsr = PHASE_TO_ADSR[phase]
        print(f"  {phase.name:10} → {adsr:8}")
    print()

    print("=" * 70)
    print("CONVERGENCE COMPARISON: Old vs New")
    print("=" * 70)
    print()

    # Old algorithm (converges to fixed point)
    print("OLD TRANSFORM (mod 17 - converges to fixed point):")
    print("-" * 70)
    test_seeds = [0, 1, 17, 42, 137, 256, 1836]
    old_results = [algo.transform(s) for s in test_seeds]
    for seed, result in zip(test_seeds, old_results):
        print(f"  transform({seed:4}) = {result:4}  [{algo.classify(result)}]")
    unique_old = len(set(old_results))
    print(f"  Unique outputs: {unique_old}/{len(test_seeds)} = {unique_old / len(test_seeds):.0%}")
    print()

    # New modular synth (quantum preset - mod 137)
    print("NEW SYNTH [quantum] (mod 137 - diverse outputs):")
    print("-" * 70)
    new_results = synth.transform_multi(test_seeds, preset="quantum")
    for seed, result in zip(test_seeds, new_results):
        print(f"  synth({seed:4})     = {result:4}")
    unique_new = len(set(new_results))
    print(f"  Unique outputs: {unique_new}/{len(test_seeds)} = {unique_new / len(test_seeds):.0%}")
    print()

    print("=" * 70)
    print("SYNTH PRESETS (all parameters derived from Mahamantra!)")
    print("=" * 70)
    print()

    for name, params in SYNTH_PRESETS.items():
        analysis = synth.analyze_diversity(sample_size=100, params=params)
        print(
            f"  {name:10} | mod_space={params.mod_space:3} | feedback={params.feedback} | "
            f"diversity={analysis['diversity_ratio']:.0%} ({analysis['unique_count']}/100)"
        )
    print()

    print("=" * 70)
    print("THE KNOBS (adjustable at runtime)")
    print("=" * 70)
    print("""
    mod_space:    17 → 137 → 512    (convergence ← → diversity)
    feedback:     0  → 1   → 5      (stateless   ← → stateful)
    phase_offset: 0  → 15           (starting phase in 16-step cycle)
    lfo_enabled:  True/False        (adds oscillation)
    lfo_rate:     4                 (modulation frequency = QUARTERS)
    nibble_mode:  True/False        (constrain to 4-bit: 0-15)
    """)

    # Demo: Same seed, different presets
    print("SAME SEED, DIFFERENT PRESETS:")
    print("-" * 70)
    seed = 42
    for name in SYNTH_PRESETS:
        result = synth.transform(seed, preset=name)
        print(f"  synth({seed}, preset='{name}') = {result}")
    print()

    # Demo: Custom params
    print("CUSTOM PARAMS DEMO:")
    print("-" * 70)
    custom = MahaSynthParams(
        mod_space=MAHA_QUANTUM,  # 137
        feedback=PANCHA,  # 5 (more state preservation)
        phase_offset=NAVA - 1,  # 8 (start at position 9)
        lfo_enabled=True,
        nibble_mode=False,
    )
    for seed in [0, 42, 137]:
        result = synth.transform(seed, params=custom)
        print(f"  synth({seed:3}, custom) = {result}")
    print()

    print("BIT MODELS:")
    print(f"  512-bit:  {algo.total_bits_512} = 16 × 32 = 2^9")
    print(f"  1096-bit: {algo.total_bits_1096} = 8 × 137 = 1024 + 72")
    print()

    print("Hare Krishna!")
