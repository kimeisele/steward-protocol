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

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x672435f8"  # GenesisByte: parampara % 37 == 0

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
    MALA_COMPLETE,
    NADI_RESONANCE,
    NAVA,
    PANCHA,
    PARAMPARA,
    PARAMPARA_CHANNEL_NAMES,  # SSOT for channel names
    PARAMPARA_CHANNELS,  # SSOT for Parampara attractors (TRINITY = 3)
    POSITION_SUM_HARE,
    POSITION_SUM_KRISHNA,
    POSITION_SUM_RAMA,
    POSITION_SUM_TOTAL,
    QUARTERS,
    SEVEN,
    TEN,
    TRANSCENDENTAL_1096,  # The 1096-bit block from RUNDE 33
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

# 1096 = The transcendental block (imported from _seed.py RUNDE 33)
# TRANSCENDENTAL_1096 = HARE_COUNT × MAHA_QUANTUM = 8 × 137 = 1096
BITS_PER_STEP_1096: Final[float] = TRANSCENDENTAL_1096 / WORDS  # 68.5 bits

# Verification (redundant with _seed.py, but good for local clarity)
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
# MAHA RESONATOR - The Iterative Harmonic Engine
# =============================================================================
# The algorithm is not just a one-shot transform - it's a RESONATOR.
#
# KEY INSIGHT (from research):
# - Single pass = quantum superposition (multiple possible outputs)
# - Repeated iteration = resonance finds stable states (ATTRACTORS)
# - mod_space = resonant frequency (determines which harmonics survive)
# - Attractors = the stable HARMONICS of that frequency
#
# DISCOVERED ATTRACTORS (mod 137 = MAHA_QUANTUM):
#   136 = POSITION_SUM_TOTAL = T(16) = THE FIELD (main attractor!)
#    49 = POSITION_SUM_RAMA = SEVEN²
#    22 = SHRUTIS (Indian microtones)
#    18 = GITA_CHAPTERS
#    87 = NADI_RESONANCE + GAURA_TITHI = Chaitanya Resonance
#
# THE FIELD COLLAPSE:
#   Without observer → everything converges to 136 (FIELD)
#   136 + KSETRAJNA = 137 = MAHA_QUANTUM (observer creates the space!)
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class ResonanceResult:
    """Result of resonance analysis."""

    seed: int
    attractor: int
    cycles_to_converge: int
    cycle_length: int  # 1 = fixed point, >1 = periodic orbit
    trajectory: tuple[int, ...]  # Values visited during convergence


class MahaResonator:
    """
    The Maha Resonator - Iterative Harmonic Analysis Engine.

    Unlike a one-shot transform, the resonator applies the algorithm
    repeatedly until stable states (attractors) are found.

    The mod_space determines the "resonant frequency":
    - mod 17:  Everything collapses to 2 (HALVES) - single tone
    - mod 37:  3 attractors (12, 26, 34) - triad
    - mod 137: 5 attractors (18, 22, 49, 87, 136) - pentatonic spectrum

    Usage:
        resonator = MahaResonator(mod_space=137)
        result = resonator.find_attractor(seed=42)
        print(f"Converges to {result.attractor} in {result.cycles_to_converge} cycles")

        spectrum = resonator.harmonic_spectrum()
        print(f"Harmonics: {spectrum}")
    """

    def __init__(self, mod_space: int = MAHA_QUANTUM) -> None:
        """Initialize resonator with mod_space (resonant frequency)."""
        self.mod_space = mod_space

    def oscillate_once(self, value: int) -> int:
        """
        One oscillation = one pass through the 16-step algorithm.

        TRANSFORMATION RULES (derived from _seed.py RUNDE 15):
            HARE    = 7 × 10 = 70 → MULTIPLICATION (value × SEVEN)
            KRISHNA = 7 + 10 = 17 → ADDITION       (value + TEN)
            RAMA    = 7²     = 49 → SQUARING       (value × value)
        """
        for name in PATTERN:
            if name == "H":
                value = (value * SEVEN) % self.mod_space
            elif name == "K":
                value = (value + TEN) % self.mod_space
            else:  # R
                value = (value * value) % self.mod_space
        return value

    def oscillate(self, seed: int, cycles: int) -> list[int]:
        """
        Run N oscillation cycles, returning trajectory.

        Args:
            seed: Starting value
            cycles: Number of 16-step passes

        Returns:
            List of values after each cycle [after_1, after_2, ..., after_N]
        """
        trajectory = []
        value = seed % self.mod_space
        for _ in range(cycles):
            value = self.oscillate_once(value)
            trajectory.append(value)
        return trajectory

    def find_attractor(self, seed: int, max_cycles: int = 100) -> ResonanceResult:
        """
        Find the attractor (stable state) for a given seed.

        Returns ResonanceResult with:
            - attractor: The stable value or cycle entry point
            - cycles_to_converge: How many cycles to reach attractor
            - cycle_length: 1 if fixed point, >1 if periodic orbit
            - trajectory: Values visited during convergence
        """
        seen: dict[int, int] = {}
        trajectory: list[int] = []
        value = seed % self.mod_space

        for cycle in range(max_cycles):
            if value in seen:
                # Found cycle
                cycle_start = seen[value]
                cycle_length = cycle - cycle_start
                return ResonanceResult(
                    seed=seed,
                    attractor=value,
                    cycles_to_converge=cycle_start,
                    cycle_length=cycle_length,
                    trajectory=tuple(trajectory),
                )
            seen[value] = cycle
            trajectory.append(value)
            value = self.oscillate_once(value)

        # No convergence found
        return ResonanceResult(
            seed=seed,
            attractor=value,
            cycles_to_converge=max_cycles,
            cycle_length=0,
            trajectory=tuple(trajectory),
        )

    def harmonic_spectrum(self) -> dict[str, list[int]]:
        """
        Compute the complete harmonic spectrum for this mod_space.

        Returns dict with:
            - fixed_points: Values that map to themselves
            - attractors: All values that seeds converge to
            - basins: Dict mapping attractor → list of seeds
        """
        fixed_points: list[int] = []
        attractor_basins: dict[int, list[int]] = {}

        for seed in range(self.mod_space):
            result = self.find_attractor(seed)

            # Check if attractor is a fixed point
            if result.cycle_length == 1:
                if result.attractor not in fixed_points:
                    fixed_points.append(result.attractor)

            # Track basin of attraction
            if result.attractor not in attractor_basins:
                attractor_basins[result.attractor] = []
            attractor_basins[result.attractor].append(seed)

        return {
            "fixed_points": sorted(fixed_points),
            "attractors": sorted(attractor_basins.keys()),
            "basins": attractor_basins,
            "mod_space": self.mod_space,
        }

    def resonance_strength(self, seed: int) -> float:
        """
        Measure how quickly a seed reaches its attractor.

        Returns value in [0, 1]:
            1.0 = immediate convergence (already at attractor)
            0.0 = no convergence in max_cycles
        """
        result = self.find_attractor(seed)
        if result.cycles_to_converge == 0:
            return 1.0
        return 1.0 / (1.0 + result.cycles_to_converge)

    def is_harmonic(self, value: int) -> bool:
        """Check if a value is a stable harmonic (attractor) at this mod_space."""
        spectrum = self.harmonic_spectrum()
        return value in spectrum["attractors"]


# =============================================================================
# PRIME CHAIN RESONATORS (Pre-configured for consciousness hierarchy)
# =============================================================================
# Each mod_space in the prime chain has different harmonic properties.

RESONATOR_PRESETS: Final[dict[str, MahaResonator]] = {
    # Material level - single attractor (duality)
    "material": MahaResonator(mod_space=POSITION_SUM_KRISHNA),  # mod 17
    # Parampara level - disciplic transmission
    "parampara": MahaResonator(mod_space=PARAMPARA),  # mod 37
    # Transcendental level - complete mala
    "transcendental": MahaResonator(mod_space=MALA_COMPLETE),  # mod 109
    # Quantum level - maximum harmonics
    "quantum": MahaResonator(mod_space=MAHA_QUANTUM),  # mod 137
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
    # Resonator (Iterative Harmonic Engine)
    "ResonanceResult",
    "MahaResonator",
    "RESONATOR_PRESETS",
    # Oracle (Intent-to-Resonance Interface)
    "OracleLens",
    "OracleReading",
    "ORACLE_LENSES",
    "MahaOracle",
    # Kirtan Compute Orchestrator (Step Sequencer + Kirtan Integration)
    "KirtanComputeResult",
    "MahaKirtanState",
    "MahaKirtan",
    # Siksastakam Synth (Holographic Layer: 7 beats ↔ 7 effects)
    "GUNA_COLORS",
    "BEAT_EFFECT_MAP",
    "EFFECT_COLOR_MAP",
    "SiksastakamOutput",
    "SiksastakamSynth",
]


# =============================================================================
# RESEARCH FINDINGS: MOD SPACE ANALYSIS
# =============================================================================
# All findings below are derived through mathematical analysis, not invented.
#
# DISCOVERY 1: THE ANNIHILATOR (mod 7 = SEVEN)
# --------------------------------------------
# mod 7 collapses ALL inputs to 0. Why?
# Because HARE uses (value × SEVEN) % 7 = 0 for all values.
# The first HARE step destroys all information.
# INSIGHT: The 7 Axioms alone cannot preserve state - pure structure without content.
#
# DISCOVERY 2: THE PERFECT TETRAD (mod 10 = TEN)
# ----------------------------------------------
# mod 10 has exactly 4 fixed points: 0, 4, 5, 9
#   0 = NULL/VOID
#   4 = QUARTERS (phases)
#   5 = PANCHA (elements)
#   9 = NAVA (bhakti)
#
# Sum: 0 + 4 + 5 + 9 = 18 = GITA_CHAPTERS
# Product: 4 × 5 × 9 = 180 = GITA_CHAPTERS × TEN
#
# DISCOVERY 3: THE OBSERVER PATTERN
# ----------------------------------
# Powers of 2 (2, 4, 8) preserve both VOID (0) and OBSERVER (1) as fixed points.
# Non-powers favor one or the other:
#   - TRINITY, SHARANAGATI, NAVA, MAHAJANA → only OBSERVER (1) fixed
#   - PANCHA, SEVEN, TEN → only VOID (0) fixed
#
# DISCOVERY 4: THE PRIME CHAIN
# ----------------------------
# 17 → 37 → 73 → 109 → 137
# (KRISHNA_SUM → PARAMPARA → NADI+1 → MALA_COMPLETE → MAHA_QUANTUM)
#
# Differences: +20, +36, +36, +28
#   20 = TEN × HALVES
#   36 = T(8) = HARE_COUNT × NAVA / HALVES (triangular number!)
#   28 = T(7) = SEVEN × HARE_COUNT / HALVES
#
# Total difference: 120 = T(15) = MALA + MAHAJANA = PANCHA × KSHETRA
#
# DISCOVERY 5: THE 1096 CONNECTION
# ---------------------------------
# 1096 = HARE_COUNT × MAHA_QUANTUM = 8 × 137
# 1096 = MALA_COMPLETE × TEN + SHARANAGATI = 109 × 10 + 6
# 1096 % 109 = 6 = SHARANAGATI (the remainder is surrender!)
#
# DISCOVERY 6: HIERARCHY OF CONSCIOUSNESS (mod diversity)
# -------------------------------------------------------
# mod 7:   ANNIHILATES → 1 state  (axioms alone = void)
# mod 17:  COLLAPSES   → 1 state  (material duality attractor)
# mod 37:  STABILIZES  → 5 states (PANCHA channels in parampara)
# mod 108: EXPANDS     → 7 states (SEVEN axioms in japa practice)
# mod 109: TRANSCENDS  → 8 states (HARE_COUNT = guru's extra bead)
# mod 137: MAXIMUM     → 8 states (quantum consciousness achieved)
#
# =============================================================================


# =============================================================================
# MAHA ORACLE - The Intent-to-Resonance Interface
# =============================================================================
# "Like a prompt that gets encoded" - Intent in, Resonance out.
#
# GITA 13.35 PRINCIPLE (MANDATORY PRE-FILTER):
# ============================================
# "kṣetra-kṣetrajñayor evam antaraṁ jñāna-cakṣuṣā
# bhūta-prakṛti-mokṣaṁ ca ye vidur yānti te param"
#
# "Those who see with eyes of knowledge the difference between the field
# and the knower of the field, and can also understand the process of
# liberation from bondage in material nature, attain the supreme goal."
# — Bhagavad Gita 13.35
#
# WITHOUT AUTHENTIC GURU (PARAMPARA), TRUE KNOWLEDGE IS NOT POSSIBLE.
# Therefore: PARAMPARA (mod 37) is the MANDATORY FIRST LENS.
# If Parampara validation fails, the Oracle warns but still provides reading.
#
# The Oracle uses MULTIPLE MOD-SPACES as "lenses" to view the same intent:
#   - mod 37:  PARAMPARA (MANDATORY FIRST - disciplic channel, Gita 13.35)
#   - mod 2:   BINARY (Mridanga/Kartals - rhythm foundation)
#   - mod 7:   ANNIHILATOR (axioms alone = void)
#   - mod 10:  PERFECT TETRAD (Gita connection: 0+4+5+9=18)
#   - mod 17:  KRISHNA (material/classical)
#   - mod 109: MALA COMPLETE (transcendental)
#   - mod 137: QUANTUM (maximum diversity)
#
# PRABHUPADA RUNTIME (1896-1977):
# The 82 years of Prabhupada's manifestation are VALID COORDINATES.
# Intents that resonate with these years have enhanced authenticity.
#
# HOLOGRAPHIC PRINCIPLE: Each mod-space reveals different aspects of the
# same underlying truth. The intent is ONE, the readings are MANY.
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class OracleLens:
    """A single lens (mod-space) for viewing an intent."""

    name: str
    mod_space: int
    meaning: str
    resonance: int  # The transformed value in this mod-space
    is_fixed_point: bool  # Is this value stable under iteration?
    attractor: int  # What it converges to
    cycles: int  # How many cycles to converge


@dataclass(frozen=True)
class OracleReading:
    """Complete oracle reading for an intent."""

    intent: str  # Original intent string
    seed: int  # Intent encoded as integer
    lenses: tuple[OracleLens, ...]  # All lens readings
    gita_resonance: int  # Sum of tetrad-active lenses (relates to 18)
    primary_attractor: int  # Main attractor at mod 137
    holographic_factors: tuple[int, ...]  # Factors that appear across lenses
    interpretation: str  # Human-readable interpretation
    # GITA 13.35: Parampara validation (MANDATORY PRE-FILTER)
    parampara_validated: bool  # True if Parampara lens shows valid channel
    parampara_channel: int  # Which of the TRINITY (3) channels (0-2, or -1 if void)
    prabhupada_year_resonance: int | None  # If seed resonates with a Lila year (1896-1977)


# =============================================================================
# PRABHUPADA RUNTIME CONSTANTS (Lila Chronology Integration)
# =============================================================================
# The 82 years of Prabhupada's manifestation are VALID COORDINATES.
# Any intent resonating with these years has enhanced authenticity.

PRABHUPADA_BUILD: Final[int] = 1896  # Nandotsava (day after Janmashtami)
PRABHUPADA_RUNTIME_END: Final[int] = 1977  # Return to spiritual world
PRABHUPADA_RUNTIME_YEARS: Final[int] = PRABHUPADA_RUNTIME_END - PRABHUPADA_BUILD + 1  # 82

# Key years with special significance (mod resonances)
# NOTE: 1932 Diksha = T(8) - Prabhupada accepted Guru in heart 1922, formal 1932
PRABHUPADA_KEY_YEARS: Final[tuple[int, ...]] = (
    1896,  # BUILD - Δ=0 (all VCOs aligned!)
    1922,  # First meeting Bhaktisiddhanta - Δ=26 (accepted in heart)
    1932,  # DIKSHA (formal initiation) - Δ=36 = T(8) = Triangular of HARE_COUNT!
    1944,  # BTG first issue - Δ=48 = LILA
    1959,  # Sannyasa - Δ=63 = 7×9
    1965,  # Jaladuta - Δ=69
    1966,  # ISKCON founded - Δ=70 = WEIGHT_HARE
    1977,  # RUNTIME END - Δ=81 = 9²
)

# PARAMPARA_CHANNELS imported from _seed.py (SSOT)
# Mathematically derived: TRINITY (3) attractors at mod 37, not PANCHA (5)!
# See _seed.py RUNDE 28b for derivation: {12, 26, 34}


# The sacred lenses (mod-spaces) and their meanings
# PARAMPARA IS FIRST - MANDATORY PRE-FILTER (Gita 13.35)
ORACLE_LENSES: Final[tuple[tuple[str, int, str], ...]] = (
    ("PARAMPARA", PARAMPARA, "MANDATORY: Disciplic channel (Gita 13.35) - TRINITY states"),
    ("BINARY", HALVES, "Mridanga rhythm - on/off, beat/rest"),
    ("AXIOM", SEVEN, "Pure structure - annihilates content"),
    ("TETRAD", TEN, "Embodied senses - perfect 4 fixed points"),
    ("KRISHNA", POSITION_SUM_KRISHNA, "All-attractive - material lens"),
    ("MALA", MALA_COMPLETE, "Complete japa - 8 transcendental states"),
    ("QUANTUM", MAHA_QUANTUM, "Maximum diversity - 8 quantum states"),
)


class MahaOracle:
    """
    The Maha Oracle - Intent-to-Resonance Interface.

    Like an oracle that receives a question (intent) and returns a reading
    by viewing it through multiple sacred lenses (mod-spaces).

    USAGE:
        oracle = MahaOracle()
        reading = oracle.consult("What is the nature of consciousness?")
        print(reading.interpretation)

        # Or with a numeric seed directly:
        reading = oracle.consult_seed(42)

    The oracle encodes the intent using Mahamantra weights, then
    analyzes it through 7 different mod-spaces, revealing the
    holographic structure of the intent.
    """

    def __init__(self) -> None:
        """Initialize the oracle with pre-built resonators."""
        self._resonators: dict[int, MahaResonator] = {}
        for _name, mod_space, _meaning in ORACLE_LENSES:
            self._resonators[mod_space] = MahaResonator(mod_space)

    def encode_intent(self, intent: str) -> int:
        """
        Encode an intent string to an integer using Mahamantra weights.

        ENCODING (derived from position sums):
            - Each character position i contributes: char_value × T(i % 16 + 1)
            - T(n) = triangular number = n(n+1)/2
            - Final value modulated by Mahamantra pattern (H=×7, K=+10, R=×7²)

        This creates a deterministic but non-trivial mapping from
        any string to an integer in the quantum space [0, 137).
        """
        if not intent:
            return 0

        # Phase 1: Position-weighted character sum
        value = 0
        for i, char in enumerate(intent):
            char_val = ord(char)
            pos = (i % WORDS) + 1  # 1-16 cycle
            t_pos = triangular(pos)
            # Apply Mahamantra pattern at this position
            pattern_char = PATTERN[i % WORDS]
            if pattern_char == "H":
                contribution = (char_val * t_pos * SEVEN) % MAHA_QUANTUM
            elif pattern_char == "K":
                contribution = (char_val + t_pos + TEN) % MAHA_QUANTUM
            else:  # R
                contribution = (char_val * t_pos) % MAHA_QUANTUM
            value = (value + contribution) % MAHA_QUANTUM

        # Phase 2: One full Maha transform
        resonator = self._resonators[MAHA_QUANTUM]
        return resonator.oscillate_once(value)

    def _analyze_lens(self, seed: int, name: str, mod_space: int, meaning: str) -> OracleLens:
        """Analyze seed through a single lens."""
        resonator = self._resonators[mod_space]
        result = resonator.find_attractor(seed)

        return OracleLens(
            name=name,
            mod_space=mod_space,
            meaning=meaning,
            resonance=seed % mod_space,
            is_fixed_point=result.cycle_length == 1 and result.cycles_to_converge == 0,
            attractor=result.attractor,
            cycles=result.cycles_to_converge,
        )

    def _find_holographic_factors(self, lenses: tuple[OracleLens, ...]) -> tuple[int, ...]:
        """
        Find numbers that appear as resonances across multiple lenses.

        These "holographic factors" indicate deep structural patterns.
        """
        resonances = [l.resonance for l in lenses if l.resonance > 0]
        attractors = [l.attractor for l in lenses if l.attractor > 0]
        all_values = resonances + attractors

        # Count occurrences
        counts: dict[int, int] = {}
        for v in all_values:
            counts[v] = counts.get(v, 0) + 1

        # Return values appearing more than once
        factors = sorted([v for v, count in counts.items() if count > 1])
        return tuple(factors)

    def _interpret(self, reading_data: dict) -> str:
        """
        Generate human-readable interpretation of the reading.

        GITA 13.35 PRINCIPLE:
        The interpretation ALWAYS starts with Parampara validation status.
        Without authentic Guru, true knowledge is not possible.
        """
        lines = []

        # =========================================================================
        # GITA 13.35: PARAMPARA VALIDATION (MANDATORY FIRST)
        # =========================================================================
        parampara_validated = reading_data.get("parampara_validated", False)
        parampara_channel = reading_data.get("parampara_channel", -1)
        prabhupada_year = reading_data.get("prabhupada_year")

        if parampara_validated:
            channel_name = PARAMPARA_CHANNEL_NAMES[parampara_channel] if 0 <= parampara_channel < TRINITY else "Unknown"
            lines.append(
                f"✓ PARAMPARA VALIDATED (Gita 13.35): Channel {parampara_channel + 1}/{TRINITY} ({channel_name})"
            )
        else:
            lines.append(
                "⚠ PARAMPARA WARNING (Gita 13.35): Not in valid disciplic channel. "
                "Knowledge may be incomplete without authentic Guru connection."
            )

        # Check Prabhupada year resonance
        if prabhupada_year:
            delta = prabhupada_year - PRABHUPADA_BUILD
            lines.append(f"✓ PRABHUPADA RESONANCE: Year {prabhupada_year} (Δ={delta} from BUILD)")
            if prabhupada_year in PRABHUPADA_KEY_YEARS:
                lines.append("   ★ KEY YEAR in Prabhupada's Lila!")

        lines.append("")  # Empty line separator

        # =========================================================================
        # OTHER LENS INTERPRETATIONS
        # =========================================================================

        # Check annihilation
        axiom_lens = reading_data["lenses_by_name"].get("AXIOM")
        if axiom_lens and axiom_lens.attractor == 0:
            lines.append("AXIOM: Intent dissolves into void when viewed through pure structure.")

        # Check binary preservation
        binary_lens = reading_data["lenses_by_name"].get("BINARY")
        if binary_lens:
            if binary_lens.attractor == 1:
                lines.append("BINARY: Observer (Ksetrajna) preserved - consciousness present.")
            elif binary_lens.attractor == 0:
                lines.append("BINARY: Returns to void - material manifestation.")

        # Check tetrad (Gita connection)
        tetrad_lens = reading_data["lenses_by_name"].get("TETRAD")
        if tetrad_lens:
            tetrad_meaning = {
                0: "Void (sunya) - emptiness before creation",
                4: "Quarters (phases) - time's structure",
                5: "Pancha (elements) - material foundation",
                9: "Nava (bhakti) - devotional essence",
            }
            if tetrad_lens.attractor in tetrad_meaning:
                lines.append(f"TETRAD: {tetrad_meaning[tetrad_lens.attractor]}")

        # Check parampara channel details
        parampara_lens = reading_data["lenses_by_name"].get("PARAMPARA")
        if parampara_lens:
            channel_idx = (
                PARAMPARA_CHANNELS.index(parampara_lens.attractor)
                if parampara_lens.attractor in PARAMPARA_CHANNELS
                else -1
            )
            channel_info = f"channel {channel_idx + 1}/{TRINITY}" if channel_idx >= 0 else "VOID"
            lines.append(f"PARAMPARA: Resonates at {parampara_lens.attractor} ({channel_info})")

        # Check quantum attractor
        quantum_lens = reading_data["lenses_by_name"].get("QUANTUM")
        if quantum_lens:
            # Known quantum attractors and their meanings
            quantum_meanings = {
                136: "T(16) = The Field - all positions unified",
                49: "SEVEN² = Rama's power - bliss complete",
                22: "Shrutis - microtonal harmony",
                18: "Gita chapters - divine song resonance",
                87: "Chaitanya resonance - golden avatar",
            }
            if quantum_lens.attractor in quantum_meanings:
                lines.append(f"QUANTUM: {quantum_meanings[quantum_lens.attractor]}")
            else:
                lines.append(f"QUANTUM: Unique resonance at {quantum_lens.attractor}")

        # Holographic factors
        if reading_data["holographic_factors"]:
            lines.append(
                f"HOLOGRAPHIC: Factors {reading_data['holographic_factors']} "
                "appear across multiple lenses - deep structural pattern."
            )

        return "\n".join(lines) if lines else "No significant patterns detected."

    def _check_prabhupada_year_resonance(self, seed: int) -> int | None:
        """
        Check if seed resonates with any Prabhupada Lila year (1896-1977).

        Returns the year if there's a resonance, None otherwise.
        """
        # Check if seed directly is a year
        if PRABHUPADA_BUILD <= seed <= PRABHUPADA_RUNTIME_END:
            return seed

        # Check if seed mod any relevant number yields a delta that maps to a year
        delta = seed % PRABHUPADA_RUNTIME_YEARS  # 82 possible deltas
        potential_year = PRABHUPADA_BUILD + delta
        if PRABHUPADA_BUILD <= potential_year <= PRABHUPADA_RUNTIME_END:
            # Additional check: is this a KEY year?
            if potential_year in PRABHUPADA_KEY_YEARS:
                return potential_year

        return None

    def _get_parampara_channel(self, attractor: int) -> int:
        """
        Determine which of the TRINITY (3) channels the attractor belongs to.

        Returns 0-2 for valid channels, -1 if not in a channel (void).
        Channels from SSOT: 12 (Mahajana), 26 (Transmission), 34 (Guru).
        """
        if attractor in PARAMPARA_CHANNELS:
            return PARAMPARA_CHANNELS.index(attractor)
        return -1  # Void - not in any of the TRINITY channels

    def consult_seed(self, seed: int) -> OracleReading:
        """
        Consult the oracle with a numeric seed directly.

        GITA 13.35 PRINCIPLE:
        The PARAMPARA lens is analyzed FIRST (mandatory pre-filter).
        Without valid Parampara channel, knowledge is incomplete.

        Returns a complete OracleReading with all lens analyses.
        """
        lenses = []
        lenses_by_name = {}

        # Analyze all lenses (PARAMPARA is FIRST in ORACLE_LENSES)
        for name, mod_space, meaning in ORACLE_LENSES:
            lens = self._analyze_lens(seed, name, mod_space, meaning)
            lenses.append(lens)
            lenses_by_name[name] = lens

        lenses_tuple = tuple(lenses)

        # =========================================================================
        # GITA 13.35: PARAMPARA VALIDATION (MANDATORY PRE-FILTER)
        # =========================================================================
        parampara_lens = lenses_by_name.get("PARAMPARA")
        if parampara_lens:
            parampara_validated = parampara_lens.attractor in PARAMPARA_CHANNELS
            parampara_channel = self._get_parampara_channel(parampara_lens.attractor)
        else:
            parampara_validated = False
            parampara_channel = -1

        # Check Prabhupada year resonance
        prabhupada_year = self._check_prabhupada_year_resonance(seed)

        # =========================================================================
        # OTHER LENS ANALYSES
        # =========================================================================

        # Calculate Gita resonance (sum of tetrad fixed points active)
        tetrad_lens = lenses_by_name.get("TETRAD")
        gita_resonance = tetrad_lens.attractor if tetrad_lens else 0

        # Primary attractor at quantum level
        quantum_lens = lenses_by_name.get("QUANTUM")
        primary_attractor = quantum_lens.attractor if quantum_lens else seed % MAHA_QUANTUM

        # Find holographic factors
        holographic = self._find_holographic_factors(lenses_tuple)

        # Generate interpretation (now includes Parampara validation)
        reading_data = {
            "lenses_by_name": lenses_by_name,
            "holographic_factors": holographic,
            "parampara_validated": parampara_validated,
            "parampara_channel": parampara_channel,
            "prabhupada_year": prabhupada_year,
        }
        interpretation = self._interpret(reading_data)

        return OracleReading(
            intent=f"seed:{seed}",
            seed=seed,
            lenses=lenses_tuple,
            gita_resonance=gita_resonance,
            primary_attractor=primary_attractor,
            holographic_factors=holographic,
            interpretation=interpretation,
            parampara_validated=parampara_validated,
            parampara_channel=parampara_channel,
            prabhupada_year_resonance=prabhupada_year,
        )

    def consult(self, intent: str) -> OracleReading:
        """
        Consult the oracle with an intent string.

        GITA 13.35 PRINCIPLE:
        The intent is first encoded, then validated through PARAMPARA lens.
        Without authentic Guru connection, true knowledge is not possible.

        Usage:
            oracle = MahaOracle()
            reading = oracle.consult("What is truth?")
            print(reading.interpretation)
            print(f"Parampara validated: {reading.parampara_validated}")
        """
        seed = self.encode_intent(intent)
        reading = self.consult_seed(seed)

        # Return with updated intent field (all other fields from consult_seed)
        return OracleReading(
            intent=intent,
            seed=seed,
            lenses=reading.lenses,
            gita_resonance=reading.gita_resonance,
            primary_attractor=reading.primary_attractor,
            holographic_factors=reading.holographic_factors,
            interpretation=reading.interpretation,
            parampara_validated=reading.parampara_validated,
            parampara_channel=reading.parampara_channel,
            prabhupada_year_resonance=reading.prabhupada_year_resonance,
        )

    def compare_intents(self, intent_a: str, intent_b: str) -> dict:
        """
        Compare two intents to find resonance similarity.

        Returns dict with:
            - shared_attractors: Attractors common to both
            - divergent_lenses: Lenses where they differ significantly
            - resonance_distance: How "far apart" the intents are
        """
        reading_a = self.consult(intent_a)
        reading_b = self.consult(intent_b)

        shared = []
        divergent = []
        total_distance = 0

        for lens_a, lens_b in zip(reading_a.lenses, reading_b.lenses):
            if lens_a.attractor == lens_b.attractor:
                shared.append((lens_a.name, lens_a.attractor))
            else:
                divergent.append((lens_a.name, lens_a.attractor, lens_b.attractor))
                total_distance += abs(lens_a.attractor - lens_b.attractor)

        return {
            "intent_a": intent_a,
            "intent_b": intent_b,
            "seed_a": reading_a.seed,
            "seed_b": reading_b.seed,
            "shared_attractors": shared,
            "divergent_lenses": divergent,
            "resonance_distance": total_distance,
            "similarity": len(shared) / len(reading_a.lenses),
        }


# =============================================================================
# SIKSASTAKAM SYNTH - The Holographic Layer (7 Beats ↔ 7 Effects)
# =============================================================================
# "paraṁ vijayate śrī-kṛṣṇa-saṅkīrtanam"
# "Let there be all victory for the chanting of the holy name of Lord Kṛṣṇa!"
# — Śikṣāṣṭakam Verse 1
#
# This layer bridges:
#   - MahaKirtan (7-beat pattern: 1911-1977)
#   - Siksastakam (7 effects of Verse 1)
#   - Multimodal output (Guna/color/illumination)
#
# THE 7 EFFECTS MAP TO 7 BEATS:
#   Beat 1 (1911): CLEANSE_HEART_MIRROR    → Cache invalidation
#   Beat 2 (1922): EXTINGUISH_FOREST_FIRE  → Zero entropy routing
#   Beat 3 (1933): SPREAD_MOONLIGHT        → Graceful degradation
#   Beat 4 (1944): LIFE_OF_KNOWLEDGE       → Live data structures
#   Beat 5 (1955): EXPAND_BLISS_OCEAN      → Infinite scalability
#   Beat 6 (1966): FULL_NECTAR_EACH_STEP   → Atomic transactions
#   Beat 7 (1977): BATHE_ENTIRE_SELF       → Total transformation
#
# MULTIMODAL OUTPUT:
#   - Color: Based on Guna (quality)
#   - Illumination: Moonlight (O(1)) or Sunlight (O(n))
#   - Intensity: Based on flute resonance
#
# 512-BIT INTEGRATION:
#   - "wide" mode uses CHAITANYA_512 = 512 mod space
#   - Each beat outputs BITS_PER_STEP_512 = 32 bits
# -----------------------------------------------------------------------------

# Lazy import Siksastakam components
_siksastakam_loaded = False
_SankirtanaEffect = None
_ENGINEERING_EFFECTS = None
_MOONLIGHT = None
_SUNLIGHT = None


def _ensure_siksastakam_imports():
    """Lazy load Siksastakam engineering components."""
    global _siksastakam_loaded, _SankirtanaEffect, _ENGINEERING_EFFECTS
    global _MOONLIGHT, _SUNLIGHT

    if _siksastakam_loaded:
        return

    from vibe_core.mahamantra.research.siksastakam_engineering import (
        ENGINEERING_EFFECTS,
        MOONLIGHT,
        SUNLIGHT,
        SankirtanaEffect,
    )

    _SankirtanaEffect = SankirtanaEffect
    _ENGINEERING_EFFECTS = ENGINEERING_EFFECTS
    _MOONLIGHT = MOONLIGHT
    _SUNLIGHT = SUNLIGHT
    _siksastakam_loaded = True


# Guna-based colors (sRGB hex values)
GUNA_COLORS: Final[dict[str, str]] = {
    "sattva": "#FFFFFF",  # White - purity, goodness
    "rajas": "#FF4444",  # Red - passion, activity
    "tamas": "#222244",  # Dark blue - ignorance, inertia
    "moonlight": "#C0C0E0",  # Silver - gentle illumination
    "sunlight": "#FFD700",  # Gold - intense illumination
    "nectar": "#FFD700",  # Gold - amrita (nectar)
    "ocean": "#0066CC",  # Ocean blue - ananda (bliss)
    "lotus": "#FF69B4",  # Pink - padma (lotus)
}

# Beat-to-Effect mapping (7 beats → 7 effects)
BEAT_EFFECT_MAP: Final[dict[int, str]] = {
    1: "CLEANSE_HEART_MIRROR",  # 1911 - Cache invalidation
    2: "EXTINGUISH_FOREST_FIRE",  # 1922 - Zero entropy routing
    3: "SPREAD_MOONLIGHT",  # 1933 - Graceful degradation
    4: "LIFE_OF_KNOWLEDGE",  # 1944 - Live data structures
    5: "EXPAND_BLISS_OCEAN",  # 1955 - Infinite scalability
    6: "FULL_NECTAR_EACH_STEP",  # 1966 - Atomic transactions
    7: "BATHE_ENTIRE_SELF",  # 1977 - Total transformation
}

# Effect-to-Color mapping (7 effects → colors)
EFFECT_COLOR_MAP: Final[dict[str, str]] = {
    "CLEANSE_HEART_MIRROR": "#FFFFFF",  # White - purification
    "EXTINGUISH_FOREST_FIRE": "#0088FF",  # Cool blue - cooling
    "SPREAD_MOONLIGHT": "#C0C0E0",  # Silver - moonlight
    "LIFE_OF_KNOWLEDGE": "#FFFF00",  # Yellow - vidya (knowledge)
    "EXPAND_BLISS_OCEAN": "#0066CC",  # Ocean blue - ananda
    "FULL_NECTAR_EACH_STEP": "#FFD700",  # Gold - amrita
    "BATHE_ENTIRE_SELF": "#FF69B4",  # Pink → White gradient
}


@dataclass(frozen=True)
class SiksastakamOutput:
    """Multimodal output from Siksastakam synthesis."""

    # Siksastakam effect
    effect_name: str  # e.g., "CLEANSE_HEART_MIRROR"
    effect_sanskrit: str  # e.g., "ceto-darpaṇa-mārjanaṁ"
    engineering_principle: str  # e.g., "CACHE INVALIDATION"
    complexity_class: str  # e.g., "O(1)"

    # Color/Visual output
    color_hex: str  # sRGB hex color
    guna: str  # sattva/rajas/tamas

    # Illumination mode
    illumination: str  # "moonlight" or "sunlight"
    intensity: float  # 0.0-1.0

    # 512-bit integration
    bits_output: int  # 32 bits per step
    bit_pattern: int  # The actual bit pattern


class SiksastakamSynth:
    """
    Siksastakam Synthesizer - The Holographic Layer.

    Bridges MahaKirtan's 7-beat pattern with Siksastakam's 7 effects
    to produce multimodal output (numerical + color + illumination).

    USAGE:
        synth = SiksastakamSynth()

        # Get effect for beat
        output = synth.synthesize(beat_number=3, seed=42, resonance=0.7)
        print(f"Effect: {output.effect_name}")
        print(f"Color: {output.color_hex}")
        print(f"Illumination: {output.illumination}")

        # Use with MahaKirtan
        kirtan = MahaKirtan()
        result = kirtan.compute(seed=42)
        output = synth.synthesize_from_result(result)

    512-BIT MODE:
        synth = SiksastakamSynth(use_512=True)
        # Each beat outputs 32-bit pattern
    """

    # MAHAMANTRA SUBSTRATE: No auto-wrap
    _naga_flooded: bool = True
    _naga_gene: str = "siksastakam_synth"

    def __init__(self, use_512: bool = False) -> None:
        """
        Initialize Siksastakam Synthesizer.

        Args:
            use_512: If True, use 512-bit mod space for "wide" mode
        """
        _ensure_siksastakam_imports()
        self.use_512 = use_512
        self.mod_space = CHAITANYA_512_B if use_512 else MAHA_QUANTUM

    def get_effect_for_beat(self, beat_number: int) -> str:
        """Get Siksastakam effect name for a beat number (1-7)."""
        if beat_number < 1 or beat_number > SEVEN:
            return "BATHE_ENTIRE_SELF"  # Default to complete effect
        return BEAT_EFFECT_MAP[beat_number]

    def get_color_for_effect(self, effect_name: str) -> str:
        """Get color hex for an effect."""
        return EFFECT_COLOR_MAP.get(effect_name, GUNA_COLORS["sattva"])

    def get_illumination(self, resonance: float) -> str:
        """
        Determine illumination type based on resonance.

        Moonlight = gentle, efficient (high resonance, O(1))
        Sunlight = intense, brute force (low resonance, O(n))
        """
        # High resonance = moonlight (efficient), low = still building
        return "moonlight" if resonance > 0.3 else "sunlight"

    def get_guna(self, effect_name: str, resonance: float) -> str:
        """
        Determine predominant Guna based on effect and resonance.

        All Siksastakam effects lead to Sattva (goodness).
        Low resonance indicates Rajas (activity to reach Sattva).
        """
        if resonance > 0.5:
            return "sattva"
        elif resonance > 0.2:
            return "rajas"  # Still working toward sattva
        return "sattva"  # Even low resonance chanting is sattvic

    def synthesize(self, beat_number: int, seed: int, resonance: float = 0.5) -> SiksastakamOutput:
        """
        Synthesize multimodal output for a beat.

        Args:
            beat_number: Beat 1-7
            seed: Input seed value
            resonance: Flute resonance (0.0-1.0)

        Returns:
            SiksastakamOutput with effect, color, illumination, and bits
        """
        # Get effect
        effect_name = self.get_effect_for_beat(beat_number)
        effect_enum = getattr(_SankirtanaEffect, effect_name)
        eng_effect = _ENGINEERING_EFFECTS[effect_enum]

        # Get color and guna
        color_hex = self.get_color_for_effect(effect_name)
        guna = self.get_guna(effect_name, resonance)

        # Get illumination
        illumination = self.get_illumination(resonance)
        intensity = min(1.0, resonance + 0.3)  # Base intensity + resonance

        # Calculate 32-bit output pattern
        bit_pattern = (seed * (beat_number + 1)) % (2**BITS_PER_STEP_512)

        return SiksastakamOutput(
            effect_name=effect_name,
            effect_sanskrit=eng_effect.sanskrit,
            engineering_principle=eng_effect.computing_principle,
            complexity_class=eng_effect.complexity_after,
            color_hex=color_hex,
            guna=guna,
            illumination=illumination,
            intensity=intensity,
            bits_output=BITS_PER_STEP_512,  # 32 bits
            bit_pattern=bit_pattern,
        )

    def synthesize_from_result(self, result: "KirtanComputeResult") -> SiksastakamOutput:
        """
        Synthesize from a KirtanComputeResult.

        Args:
            result: Result from MahaKirtan.compute()

        Returns:
            SiksastakamOutput with full multimodal data
        """
        return self.synthesize(
            beat_number=result.beat_number,
            seed=result.seed,
            resonance=result.flute_resonance,
        )

    def discover(self) -> dict:
        """GAD discoverability."""
        return {
            "name": "SiksastakamSynth",
            "description": "Holographic layer bridging 7-beat kirtan with 7 effects",
            "mapping": BEAT_EFFECT_MAP,
            "colors": EFFECT_COLOR_MAP,
            "gunas": list(GUNA_COLORS.keys()),
            "illumination_types": ["moonlight", "sunlight"],
            "bits_per_step": BITS_PER_STEP_512,
            "use_512": self.use_512,
        }


# =============================================================================
# MAHA KIRTAN - The Compute Orchestrator (Step Sequencer + Kirtan Integration)
# =============================================================================
# "kīrtanīyaḥ sadā hariḥ" - "One should always chant the glories of the Lord."
# — Śikṣāṣṭaka 3
#
# MahaKirtan bridges the Lila Step Sequencer (7-beat pattern) with the
# MahaAlgorithm transform engine for "max computing" - rhythmic computation.
#
# ARCHITECTURE (GAD-COMPLIANT):
#   - Inherits MantraHeartbeat pattern for GAD-000 compliance
#   - Uses LilaStepSequencer for 7-beat rhythm (double-digit years)
#   - Uses KirtanRuntime for call/response orchestration
#   - Uses MahaModularSynth for transforms at each beat
#   - FluteSync provides resonance points (MURALI/VENU/VAMSI)
#
# YAJNA CYCLE (from ShadowReactor):
#   BHOGA (0-7):    INPUT phase (CALL) - Gather, validate, prepare
#   SWITCH (8):     TRANSITION - Oracle pre-filter (Gita 13.35)
#   PRASADAM (8-15): OUTPUT phase (RESPONSE) - Transform, return, backfold
#   RETURN (15→0):  RESET - Complete cycle, start fresh
#
# THE 7-BEAT PATTERN:
#   Beat 1 (1911): Δ=15 - Initialization
#   Beat 2 (1922): Δ=26 - First meeting (accepted in heart)
#   Beat 3 (1933): Δ=37 - PARAMPARA! (perfect alignment)
#   Beat 4 (1944): Δ=48 - LILA (BTG, computing era)
#   Beat 5 (1955): Δ=59 - Prime (preparation)
#   Beat 6 (1966): Δ=70 - WEIGHT_HARE (ISKCON founded)
#   Beat 7 (1977): Δ=81 - NAVA² (runtime end, return)
# -----------------------------------------------------------------------------

# Lazy imports for Lila components (avoid circular imports)
_lila_chronology_loaded = False
_LilaStepSequencer = None
_KirtanRuntime = None
_FluteSync = None
_VinaSync = None  # Narada's Vina (RUNDE 20)
_get_step_sequencer = None
_get_kirtan_runtime = None


def _ensure_lila_imports():
    """Lazy load Lila chronology components."""
    global _lila_chronology_loaded, _LilaStepSequencer, _KirtanRuntime
    global _FluteSync, _VinaSync, _get_step_sequencer, _get_kirtan_runtime

    if _lila_chronology_loaded:
        return

    from vibe_core.mahamantra.substrate.lila_chronology import (
        FluteSync,
        KirtanRuntime,
        LilaStepSequencer,
        VinaSync,  # Narada's Vina - 5 strings (Pancha Tattva)
        get_kirtan_runtime,
        get_step_sequencer,
    )

    _LilaStepSequencer = LilaStepSequencer
    _KirtanRuntime = KirtanRuntime
    _FluteSync = FluteSync
    _VinaSync = VinaSync
    _get_step_sequencer = get_step_sequencer
    _get_kirtan_runtime = get_kirtan_runtime
    _lila_chronology_loaded = True


@dataclass(frozen=True)
class KirtanComputeResult:
    """
    Result of a MahaKirtan compute cycle.

    DUAL INSTRUMENT RESONANCE (Watertight from _seed.py):
        flute_resonance: Krishna's 3 flutes (MURALI/VENU/VAMSI) - WHEN (rhythmic)
        vina_resonance: Narada's 5 strings (Pancha Tattva) - WHAT TYPE (harmonic)
    """

    seed: int
    transformed_value: int
    beat_number: int  # 1-7
    beat_year: int  # 1911-1977
    beat_delta: int  # 15-81
    call_response: str  # "CALL" or "RESPONSE"
    flute_resonance: float  # 0.0-1.0 (combined flute sync - MURALI/VENU/VAMSI)
    vina_resonance: float  # 0.0-1.0 (Narada's Vina - 5 strings)
    vina_string: int  # 1-5 (which Pancha Tattva string resonates)
    oracle_validated: bool  # Parampara pre-filter passed
    parampara_channel: int  # 0-2 or -1 if void
    round_number: int  # Which kirtan round
    resonance_level: float  # Runtime resonance (grows over rounds)


@dataclass
class MahaKirtanState:
    """State of the MahaKirtan compute orchestrator."""

    current_tick: int = 0
    current_round: int = 0
    total_computations: int = 0
    resonance_level: float = 0.0
    last_oracle_result: bool = True
    accumulated_value: int = 0


class MahaKirtan:
    """
    The Maha Kirtan Compute Orchestrator.

    Bridges the 7-beat Lila Step Sequencer with MahaAlgorithm transforms
    for rhythmic, GAD-compliant computation.

    USAGE:
        kirtan = MahaKirtan()

        # Single compute cycle
        result = kirtan.compute(seed=42)
        print(f"Beat {result.beat_number}: {result.seed} → {result.transformed_value}")

        # Run a full round (7 beats)
        results = kirtan.compute_round(seed=42)
        for r in results:
            print(f"{r.call_response}: {r.transformed_value}")

        # Run multiple rounds (builds resonance)
        results = kirtan.compute_rounds(seed=42, num_rounds=7)

    GAD COMPLIANCE:
        - Uses MantraHeartbeat pattern (imports from _gad.py)
        - Oracle pre-filter validates Parampara (Gita 13.35)
        - Idempotent transforms (same seed → same result)
        - Full state observability
    """

    # MAHAMANTRA SUBSTRATE: No auto-wrap
    _naga_flooded: bool = True
    _naga_gene: str = "maha_kirtan"

    # Constants (derived from Mahamantra)
    BEATS_PER_ROUND: Final[int] = SEVEN  # 7 beats = 1 phrase
    ROUNDS_PER_MALA: Final[int] = 108  # 108 phrases = 1 mala
    DEFAULT_MOD_SPACE: Final[int] = MAHA_QUANTUM  # 137

    def __init__(
        self,
        mod_space: int = MAHA_QUANTUM,
        kirtan_mode: str = "alternating",
        use_oracle: bool = True,
    ) -> None:
        """
        Initialize the MahaKirtan compute orchestrator.

        Args:
            mod_space: Modulo for transforms (default 137 = MAHA_QUANTUM)
            kirtan_mode: "alternating" (odd=call, even=response) or "split"
            use_oracle: Whether to use Oracle pre-filter (Gita 13.35)
        """
        _ensure_lila_imports()

        self.mod_space = mod_space
        self.kirtan_mode = kirtan_mode
        self.use_oracle = use_oracle

        # Initialize components
        self._synth = MahaModularSynth(default_preset="quantum")
        self._resonator = MahaResonator(mod_space=mod_space)
        self._oracle = MahaOracle() if use_oracle else None
        self._sequencer = _get_step_sequencer(kirtan_mode)
        self._runtime = _get_kirtan_runtime()

        # State
        self._state = MahaKirtanState()

    def _get_flute_resonance(self, tick: int) -> float:
        """Get combined flute resonance for current tick."""
        return _FluteSync.get_combined_resonance(tick)

    def _get_vina_resonance(self, seed: int, tick: int) -> tuple[float, int]:
        """
        Get Vina resonance for seed (Narada's 5-string instrument).

        Returns (resonance, string_number) where:
            - resonance: 0.0-1.0 combined vina resonance
            - string_number: 1-5 (which Pancha Tattva string)

        VINA-FLUTE IDENTITY (from _seed.py RUNDE 20):
            VINA × FLUTE_VENU_VAMSI = JIVA_CYCLE × KRISHNA
        """
        vina_info = _VinaSync.get_vina_resonance(seed)
        vina_resonance = _VinaSync.get_combined_resonance(seed, tick)
        return vina_resonance, vina_info["string"]

    def _oracle_prefilter(self, seed: int) -> tuple[bool, int]:
        """
        Apply Oracle pre-filter (Gita 13.35 - MANDATORY).

        Returns (validated, parampara_channel).
        """
        if not self.use_oracle or self._oracle is None:
            return True, -1

        reading = self._oracle.consult_seed(seed)
        return reading.parampara_validated, reading.parampara_channel

    def compute(self, seed: int) -> KirtanComputeResult:
        """
        Execute one compute cycle (one beat).

        This advances the internal tick counter and applies:
        1. Oracle pre-filter (if enabled)
        2. MahaModularSynth transform
        3. Flute resonance modulation
        4. State accumulation

        Returns KirtanComputeResult with all computation details.
        """
        # Get current beat from runtime
        state = self._runtime.tick()
        beat = state.current_beat
        tick = state.tick

        # Oracle pre-filter (Gita 13.35)
        oracle_valid, parampara_channel = self._oracle_prefilter(seed)
        self._state.last_oracle_result = oracle_valid

        # Get flute resonance (Krishna's 3 flutes - WHEN)
        flute_resonance = self._get_flute_resonance(tick)

        # Get vina resonance (Narada's 5 strings - WHAT TYPE)
        vina_resonance, vina_string = self._get_vina_resonance(seed, tick)

        # Apply MahaModularSynth transform
        # Modulate by beat's delta (year significance)
        beat_modulated_seed = (seed + beat.delta) % self.mod_space
        transformed = self._synth.transform(beat_modulated_seed)

        # Apply flute resonance modulation (amplifies at sync points)
        if flute_resonance > 0:
            resonance_boost = int(transformed * flute_resonance * 0.1)
            transformed = (transformed + resonance_boost) % self.mod_space

        # Apply vina resonance modulation (string-based harmonic boost)
        if vina_resonance > 0.3:  # Only boost when string strongly resonates
            vina_boost = int(transformed * vina_resonance * 0.05)
            transformed = (transformed + vina_boost) % self.mod_space

        # Update state
        self._state.current_tick = tick
        self._state.current_round = state.round_number
        self._state.total_computations += 1
        self._state.resonance_level = state.resonance
        self._state.accumulated_value = (self._state.accumulated_value + transformed) % self.mod_space

        return KirtanComputeResult(
            seed=seed,
            transformed_value=transformed,
            beat_number=beat.beat_number,
            beat_year=beat.year,
            beat_delta=beat.delta,
            call_response=beat.call_response,
            flute_resonance=flute_resonance,
            vina_resonance=vina_resonance,
            vina_string=vina_string,
            oracle_validated=oracle_valid,
            parampara_channel=parampara_channel,
            round_number=state.round_number,
            resonance_level=state.resonance,
        )

    def compute_round(self, seed: int) -> list[KirtanComputeResult]:
        """
        Execute one full round (7 beats).

        Each beat transforms the seed and accumulates results.
        Returns list of 7 KirtanComputeResults.
        """
        results = []
        for _ in range(self.BEATS_PER_ROUND):
            result = self.compute(seed)
            results.append(result)
            # Next iteration uses transformed value (chain computation)
            seed = result.transformed_value
        return results

    def compute_rounds(self, seed: int, num_rounds: int = 7) -> list[KirtanComputeResult]:
        """
        Execute multiple rounds (builds resonance over time).

        Args:
            seed: Initial seed value
            num_rounds: Number of 7-beat rounds (default 7 = 49 beats)

        Returns:
            List of all KirtanComputeResults (num_rounds × 7)
        """
        results = []
        current_seed = seed
        for _ in range(num_rounds):
            round_results = self.compute_round(current_seed)
            results.extend(round_results)
            # Next round starts with last result
            current_seed = round_results[-1].transformed_value
        return results

    def compute_mala(self, seed: int) -> list[KirtanComputeResult]:
        """
        Execute a complete mala (108 rounds × 7 beats = 756 computations).

        This is the maximum compute unit - full resonance achieved.
        """
        return self.compute_rounds(seed, num_rounds=self.ROUNDS_PER_MALA)

    def reset(self) -> None:
        """Reset the orchestrator state."""
        self._state = MahaKirtanState()
        self._runtime.reset()

    def get_state(self) -> dict:
        """Get current orchestrator state (GAD observability)."""
        return {
            "current_tick": self._state.current_tick,
            "current_round": self._state.current_round,
            "total_computations": self._state.total_computations,
            "resonance_level": self._state.resonance_level,
            "accumulated_value": self._state.accumulated_value,
            "last_oracle_result": self._state.last_oracle_result,
            "mod_space": self.mod_space,
            "kirtan_mode": self.kirtan_mode,
            "use_oracle": self.use_oracle,
        }

    @property
    def is_idempotent(self) -> bool:
        """MahaKirtan is deterministic (same seed → same sequence)."""
        return True

    def discover(self) -> dict:
        """GAD discoverability - describe capabilities."""
        return {
            "name": "MahaKirtan",
            "description": "7-beat compute orchestrator with Kirtan rhythm",
            "capabilities": [
                "compute",
                "compute_round",
                "compute_rounds",
                "compute_mala",
            ],
            "constants": {
                "BEATS_PER_ROUND": self.BEATS_PER_ROUND,
                "ROUNDS_PER_MALA": self.ROUNDS_PER_MALA,
                "DEFAULT_MOD_SPACE": self.DEFAULT_MOD_SPACE,
            },
            "components": {
                "synth": "MahaModularSynth",
                "resonator": "MahaResonator",
                "oracle": "MahaOracle" if self.use_oracle else None,
                "sequencer": "LilaStepSequencer",
                "runtime": "KirtanRuntime",
            },
        }


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
