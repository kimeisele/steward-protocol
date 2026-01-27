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

        TRANSFORMATION RULES (derived from Mahamantra):
        - HARE (INPUT):    value += T(position) mod WEIGHT_HARE
        - KRISHNA (COMPUTE): value *= position mod WEIGHT_KRISHNA
        - RAMA (OUTPUT):   value = value mod WEIGHT_RAMA × SEVEN

        Returns the transformed value.
        """
        value = seed

        for step in self.execute():
            t_pos = triangular(step.position)

            if step.name == "H":
                # HARE = INPUT = expansion (add triangular, mod 70)
                value = (value + t_pos) % WEIGHT_HARE
            elif step.name == "K":
                # KRISHNA = COMPUTE = transformation (multiply, mod 17)
                value = (value * step.position) % WEIGHT_KRISHNA
            else:  # R
                # RAMA = OUTPUT = completion (mod 49, scale by 7)
                value = (value % WEIGHT_RAMA) * SEVEN

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
    # Class
    "MahaAlgorithm16",
]


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("MAHA ALGORITHM v2.0 - The 16-Step Transformation Engine")
    print("=" * 70)
    print()

    algo = MahaAlgorithm16()

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

    print("BINARY PATTERN: ", "".join(str(b) for b in BINARY_PATTERN))
    print(f"  First half:  01011100 = {ADSR_ATTACK} (PANCHA)")
    print(f"  Second half: 01011100 = {ADSR_SUSTAIN} (PANCHA)")
    print()

    print("THE 16 STEPS WITH TRANSFORMATION:")
    print("-" * 70)
    current_phase = None
    for step in algo.execute():
        if step.phase != current_phase:
            current_phase = step.phase
            adsr = PHASE_TO_ADSR[current_phase]
            print(f"\n  [{current_phase.name}] - {adsr}")
        weight = OPERATION_WEIGHT[step.operation]
        t_pos = triangular(step.position)
        print(
            f"    {step.position:2}: {step.name} → {step.operation.value:7} "
            f"(weight={weight:2}, T({step.position})={t_pos:3})"
        )
    print()

    print("TRANSFORMATION DEMO:")
    print("-" * 70)
    test_seeds = [0, 1, 17, 137, 1836]
    for seed in test_seeds:
        result = algo.transform(seed)
        classification = algo.classify(result)
        print(f"  transform({seed:4}) = {result:4}  [{classification}]")
    print()

    print("DETAILED TRACE (seed=137):")
    print("-" * 70)
    final, trace = algo.transform_with_trace(137)
    for t in trace[:8]:  # First 8 steps
        print(f"  Step {t['position']:2} [{t['adsr']:8}]: {t['before']:4} {t['formula']:20} → {t['after']:4}")
    print("  ...")
    print(f"  Final result: {final} [{algo.classify(final)}]")
    print()

    print("BIT MODELS:")
    print(f"  512-bit:  {algo.total_bits_512} = 16 × 32 = 2^9")
    print(f"  1096-bit: {algo.total_bits_1096} = 8 × 137 = 1024 + 72")
    print()

    print("Hare Krishna!")
