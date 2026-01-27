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

LOTUS FEET FOUNDATION:
    2 feet = HALVES
    5 toes each = PANCHA
    10 total = TEN = HALVES × PANCHA = FULL_SANKIRTAN_MULTIPLIER

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
    MAHA_QUANTUM,
    NADI_RESONANCE,
    NAVA,
    QUARTERS,
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
    print("=" * 60)
    print("MAHA ALGORITHM - The 16-Step Execution Model")
    print("=" * 60)
    print()

    algo = MahaAlgorithm16()

    print("THE 3 OPERATIONS (derived from NAME meaning):")
    for op in Operation:
        print(f"  {op.name:8} → {op.value:7} → {OPERATION_MEANING[op]}")
    print()

    print("THE 4 PHASES (quarter structure):")
    for phase in Phase:
        print(f"  {phase.value}. {phase.name:10} → {PHASE_FUNCTION[phase]}")
    print()

    print("THE 16 STEPS:")
    print("-" * 60)
    current_phase = None
    for step in algo.execute():
        if step.phase != current_phase:
            current_phase = step.phase
            print(f"\n  [{current_phase.name}]")
        print(f"    {step.position:2}: {step.name} → {step.operation.value:7} → {step.function}")
    print()

    # Count operations
    hare_ops = sum(1 for s in algo.execute() if s.name == "H")
    krishna_ops = sum(1 for s in algo.execute() if s.name == "K")
    rama_ops = sum(1 for s in algo.execute() if s.name == "R")
    print("OPERATION COUNTS (from Mahamantra):")
    print(f"  HARE (INPUT):    {hare_ops} steps = HARE_COUNT")
    print(f"  KRISHNA (COMPUTE): {krishna_ops} steps = KRISHNA_COUNT")
    print(f"  RAMA (OUTPUT):   {rama_ops} steps = RAMA_COUNT")
    print()

    print("BIT MODELS:")
    print(f"  512-bit model:  {algo.total_bits_512} bits = 16 × 32")
    print(f"  1096-bit model: {algo.total_bits_1096} bits = 8 × 137")
    print()

    print("Hare Krishna!")
