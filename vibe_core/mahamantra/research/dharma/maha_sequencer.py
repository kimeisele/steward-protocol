"""
MAHA 16-STEP SEQUENCER - The Field/Observer Architecture
=========================================================

"idaṁ śarīraṁ kaunteya kṣetram ity abhidhīyate"
"This body, O son of Kunti, is called the field."
— Bhagavad Gita 13.2

ARCHITECTURE:
=============
16-STEP MAIN SEQUENCER = KSHETRA (The Field)
    - Each step = one Mahamantra word
    - Operations derived from position sums:
        H (HARE)    = value × 7 (from 70 = 7 × 10)
        K (KRISHNA) = value + 10 (from 17 = 7 + 10)
        R (RAMA)    = value × value (from 49 = 7²)

7-BEAT OBSERVER LAYER = KSHETRAJNA (The Knower)
    - Overlays on the 16 steps
    - Creates perception rhythm
    - SEVEN = HALF_SIZE - KSETRAJNA = 8 - 1 = 7

POLYRHYTHM:
    - 16 and 7 are COPRIME (GCD = 1)
    - LCM(16, 7) = 112 = full cycle before realignment
    - 16 mod 7 = 2 = HALVES

STRUCTURE EQUATIONS:
    16 = 7 + 9 = SEVEN + NAVA
    16 = 7 + 7 + 2 = SEVEN + SEVEN + HALVES

The Mahamantra has 9 RUNS (consecutive same names) = NAVA = 16 - 7
This is derived from the structure itself!

NO HARDCODED VALUES - All from seed.py
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x00000559"  # GenesisByte: 1369 = 37² = PARAMPARA²

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Dict, Final, List, Optional, Tuple

from vibe_core.mahamantra.protocols._gad import GADBase, HolyName
from vibe_core.mahamantra.protocols._seed import (
    HALVES,
    HARE_COUNT,
    KSETRAJNA,
    MAHA_QUANTUM,
    NAVA,
    PARAMPARA,
    POSITION_SUM_HARE,
    POSITION_SUM_KRISHNA,
    POSITION_SUM_RAMA,
    POSITION_SUM_TOTAL,
    SEVEN,
    TEN,
    WORDS,
)

# =============================================================================
# MAHAMANTRA PATTERN (16 WORDS = THE FIELD)
# =============================================================================

MAHAMANTRA_PATTERN: Final[Tuple[str, ...]] = (
    "H",
    "K",
    "H",
    "K",  # Q1: Seeking Krishna
    "K",
    "K",
    "H",
    "H",  # Q2: Krishna responds
    "H",
    "R",
    "H",
    "R",  # Q3: Seeking Rama
    "R",
    "R",
    "H",
    "H",  # Q4: Rama responds
)

# Map to HolyName enum
MAHAMANTRA_NAMES: Final[Tuple[HolyName, ...]] = tuple(
    HolyName.HARE if p == "H" else HolyName.KRISHNA if p == "K" else HolyName.RAMA for p in MAHAMANTRA_PATTERN
)

# Verify structure
assert len(MAHAMANTRA_PATTERN) == WORDS, f"Pattern must be {WORDS} words"

# =============================================================================
# DERIVED CONSTANTS
# =============================================================================

# The 7 appears in ALL position sums
WEIGHT_HARE: Final[int] = POSITION_SUM_HARE  # 70 = 7 × 10
WEIGHT_KRISHNA: Final[int] = POSITION_SUM_KRISHNA  # 17 = 7 + 10
WEIGHT_RAMA: Final[int] = POSITION_SUM_RAMA  # 49 = 7 × 7

# LCM for full cycle
import math

FULL_CYCLE: Final[int] = (WORDS * SEVEN) // math.gcd(WORDS, SEVEN)  # 112

# Structure equations
assert WORDS - SEVEN == NAVA, "16 - 7 must equal NAVA (9)"
assert WORDS == SEVEN + NAVA, "16 = 7 + 9"
assert WORDS == SEVEN + SEVEN + HALVES, "16 = 7 + 7 + 2"

# Observer derivation
assert SEVEN == HARE_COUNT - KSETRAJNA, "SEVEN = HALF_SIZE - KSETRAJNA"


# =============================================================================
# STEP DATA STRUCTURES
# =============================================================================


class StepOperation(Enum):
    """Operations derived from position sums."""

    MULTIPLY_SEVEN = "H"  # HARE: 70 = 7 × 10 → multiply by 7
    ADD_TEN = "K"  # KRISHNA: 17 = 7 + 10 → add 10
    SQUARE = "R"  # RAMA: 49 = 7² → square (multiply by self)


@dataclass(frozen=True)
class SequencerStep:
    """One of the 16 steps in the main sequencer."""

    position: int  # 1-16
    name: HolyName
    operation: StepOperation
    quarter: int  # 1-4

    @property
    def is_hare(self) -> bool:
        return self.name == HolyName.HARE

    @property
    def is_krishna(self) -> bool:
        return self.name == HolyName.KRISHNA

    @property
    def is_rama(self) -> bool:
        return self.name == HolyName.RAMA


@dataclass(frozen=True)
class ObserverBeat:
    """One of the 7 beats in the observer layer."""

    beat_number: int  # 1-7
    step_positions: Tuple[int, ...]  # Which steps (1-16) this beat observes
    names_observed: Tuple[HolyName, ...]

    @property
    def primary_position(self) -> int:
        """The main step this beat is aligned with."""
        return self.step_positions[0]


# =============================================================================
# BUILD THE 16 STEPS
# =============================================================================


def _build_16_steps() -> Tuple[SequencerStep, ...]:
    """Build all 16 steps from the Mahamantra pattern."""
    steps = []
    for i, pattern in enumerate(MAHAMANTRA_PATTERN):
        position = i + 1
        name = MAHAMANTRA_NAMES[i]
        quarter = (i // 4) + 1

        if pattern == "H":
            op = StepOperation.MULTIPLY_SEVEN
        elif pattern == "K":
            op = StepOperation.ADD_TEN
        else:
            op = StepOperation.SQUARE

        steps.append(
            SequencerStep(
                position=position,
                name=name,
                operation=op,
                quarter=quarter,
            )
        )

    return tuple(steps)


SEQUENCER_16_STEPS: Final[Tuple[SequencerStep, ...]] = _build_16_steps()


# =============================================================================
# BUILD THE 7 OBSERVER BEATS
# =============================================================================


def _build_7_beats() -> Tuple[ObserverBeat, ...]:
    """
    Build the 7 observer beats that overlay on the 16 steps.

    Each beat observes approximately 16/7 ≈ 2.3 steps.
    We use floor division to determine primary alignment.
    """
    beats = []

    for beat_num in range(1, SEVEN + 1):
        # Calculate which steps this beat observes
        # Using continuous mapping: beat N observes around position (N-1) * 16/7
        start_pos = int((beat_num - 1) * WORDS / SEVEN)

        # Determine how many steps to observe
        if beat_num < SEVEN:
            end_pos = int(beat_num * WORDS / SEVEN)
        else:
            end_pos = WORDS  # Last beat covers remaining

        step_positions = tuple(range(start_pos + 1, end_pos + 1))
        names_observed = tuple(MAHAMANTRA_NAMES[p - 1] for p in step_positions)

        beats.append(
            ObserverBeat(
                beat_number=beat_num,
                step_positions=step_positions,
                names_observed=names_observed,
            )
        )

    return tuple(beats)


OBSERVER_7_BEATS: Final[Tuple[ObserverBeat, ...]] = _build_7_beats()


# =============================================================================
# STEP RESULT
# =============================================================================


@dataclass
class StepResult:
    """Result of executing one step."""

    step: SequencerStep
    input_value: int
    output_value: int
    operation_applied: str

    # Observer context
    observer_beat: Optional[ObserverBeat] = None
    beat_phase: float = 0.0  # 0.0-1.0 position within beat


@dataclass
class CycleResult:
    """Result of a complete 16-step cycle."""

    seed: int
    final_value: int
    steps: Tuple[StepResult, ...]

    # Observer layer results
    beats_traversed: int
    full_cycles_completed: int


# =============================================================================
# MAHA 16-STEP SEQUENCER
# =============================================================================


class Maha16StepSequencer(GADBase):
    """
    The Maha 16-Step Sequencer - Field/Observer Architecture.

    16 STEPS = THE FIELD (kshetra)
        - Fixed structure from Mahamantra
        - Operations: H=×7, K=+10, R=value²

    7 BEATS = THE OBSERVER (kshetrajna)
        - Overlays on the 16 steps
        - Creates perception rhythm
        - SEVEN = 8 - 1 (observable portion)

    USAGE:
        sequencer = Maha16StepSequencer()

        # Execute one full 16-step cycle
        result = sequencer.execute_cycle(seed=37)
        print(f"Seed {result.seed} → {result.final_value}")

        # Execute with observer tracking
        result = sequencer.execute_cycle(seed=37, track_observer=True)
        for step in result.steps:
            if step.observer_beat:
                print(f"Step {step.step.position} observed by beat {step.observer_beat.beat_number}")

    POLYRHYTHM:
        - LCM(16, 7) = 112 steps for full realignment
        - 112 / 16 = 7 complete field traversals
        - 112 / 7 = 16 complete observer cycles
    """

    # MAHAMANTRA SUBSTRATE: No auto-wrap
    _naga_flooded: bool = True
    _naga_gene: str = "maha_16_step_sequencer"

    # Constants
    STEPS: Final[int] = WORDS  # 16
    BEATS: Final[int] = SEVEN  # 7
    FULL_CYCLE_LENGTH: Final[int] = FULL_CYCLE  # 112

    def __init__(self, mod_space: int = MAHA_QUANTUM) -> None:
        """
        Initialize the sequencer.

        Args:
            mod_space: Modulo for all operations (default 137 = MAHA_QUANTUM)
        """
        self.mod_space = mod_space
        self._total_steps = 0
        self._total_cycles = 0
        self._current_beat = 1

    def _get_observer_beat(self, step_position: int) -> ObserverBeat:
        """Get the observer beat for a given step position."""
        for beat in OBSERVER_7_BEATS:
            if step_position in beat.step_positions:
                return beat
        # Fallback to last beat
        return OBSERVER_7_BEATS[-1]

    def _get_beat_phase(self, step_position: int, beat: ObserverBeat) -> float:
        """Get the phase (0.0-1.0) within the observer beat."""
        if len(beat.step_positions) == 1:
            return 0.5
        idx = beat.step_positions.index(step_position)
        return idx / (len(beat.step_positions) - 1)

    def _apply_operation(self, value: int, step: SequencerStep) -> Tuple[int, str]:
        """
        Apply the step's operation to the value.

        Returns (new_value, description).
        """
        if step.operation == StepOperation.MULTIPLY_SEVEN:
            # HARE: 70 = 7 × 10 → multiply by SEVEN
            new_value = (value * SEVEN) % self.mod_space
            desc = f"{value} × {SEVEN} = {new_value} (mod {self.mod_space})"

        elif step.operation == StepOperation.ADD_TEN:
            # KRISHNA: 17 = 7 + 10 → add TEN
            new_value = (value + TEN) % self.mod_space
            desc = f"{value} + {TEN} = {new_value} (mod {self.mod_space})"

        else:  # SQUARE (RAMA)
            # RAMA: 49 = 7² → square
            new_value = (value * value) % self.mod_space
            desc = f"{value}² = {new_value} (mod {self.mod_space})"

        return new_value, desc

    def execute_step(self, value: int, step: SequencerStep, track_observer: bool = True) -> StepResult:
        """Execute a single step."""
        new_value, desc = self._apply_operation(value, step)

        observer_beat = None
        beat_phase = 0.0

        if track_observer:
            observer_beat = self._get_observer_beat(step.position)
            beat_phase = self._get_beat_phase(step.position, observer_beat)

        self._total_steps += 1

        return StepResult(
            step=step,
            input_value=value,
            output_value=new_value,
            operation_applied=desc,
            observer_beat=observer_beat,
            beat_phase=beat_phase,
        )

    def execute_cycle(self, seed: int, track_observer: bool = True) -> CycleResult:
        """
        Execute one complete 16-step cycle.

        This traverses the entire field (kshetra) once.
        """
        value = seed % self.mod_space
        step_results = []
        beats_seen = set()

        for step in SEQUENCER_16_STEPS:
            result = self.execute_step(value, step, track_observer)
            step_results.append(result)
            value = result.output_value

            if result.observer_beat:
                beats_seen.add(result.observer_beat.beat_number)

        self._total_cycles += 1

        return CycleResult(
            seed=seed,
            final_value=value,
            steps=tuple(step_results),
            beats_traversed=len(beats_seen),
            full_cycles_completed=self._total_cycles,
        )

    def execute_full_polyrhythm(self, seed: int) -> List[CycleResult]:
        """
        Execute 7 complete cycles (112 steps) for full polyrhythmic realignment.

        After 112 steps:
        - Field has been traversed 7 times
        - Observer has completed 16 cycles
        """
        results = []
        current_seed = seed

        # 112 / 16 = 7 cycles needed
        cycles_for_realignment = FULL_CYCLE // WORDS  # 7

        for _ in range(cycles_for_realignment):
            result = self.execute_cycle(current_seed)
            results.append(result)
            current_seed = result.final_value

        return results

    def get_state(self) -> Dict:
        """Get current sequencer state (GAD observability)."""
        return {
            "mod_space": self.mod_space,
            "total_steps": self._total_steps,
            "total_cycles": self._total_cycles,
            "steps_per_cycle": self.STEPS,
            "beats_per_overlay": self.BEATS,
            "full_cycle_length": self.FULL_CYCLE_LENGTH,
        }

    def reset(self) -> None:
        """Reset sequencer state."""
        self._total_steps = 0
        self._total_cycles = 0
        self._current_beat = 1

    def discover(self) -> Dict:
        """GAD discoverability."""
        return {
            "name": "Maha16StepSequencer",
            "description": "16-step field sequencer with 7-beat observer overlay",
            "architecture": {
                "field_steps": self.STEPS,
                "observer_beats": self.BEATS,
                "full_cycle": self.FULL_CYCLE_LENGTH,
                "polyrhythm": f"{self.STEPS}:{self.BEATS}",
            },
            "operations": {
                "HARE": f"value × {SEVEN} (from position sum {WEIGHT_HARE} = 7×10)",
                "KRISHNA": f"value + {TEN} (from position sum {WEIGHT_KRISHNA} = 7+10)",
                "RAMA": f"value² (from position sum {WEIGHT_RAMA} = 7²)",
            },
            "constants_from_seed": [
                "WORDS",
                "SEVEN",
                "NAVA",
                "HALVES",
                "KSETRAJNA",
                "POSITION_SUM_HARE",
                "POSITION_SUM_KRISHNA",
                "POSITION_SUM_RAMA",
            ],
        }


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def get_step_at_position(position: int) -> SequencerStep:
    """Get step at position (1-16)."""
    if position < 1 or position > WORDS:
        raise ValueError(f"Position must be 1-{WORDS}")
    return SEQUENCER_16_STEPS[position - 1]


def get_beat_at_number(beat_number: int) -> ObserverBeat:
    """Get observer beat (1-7)."""
    if beat_number < 1 or beat_number > SEVEN:
        raise ValueError(f"Beat must be 1-{SEVEN}")
    return OBSERVER_7_BEATS[beat_number - 1]


def analyze_step_beat_mapping() -> Dict[int, List[int]]:
    """
    Analyze which steps each beat observes.

    Returns dict: beat_number -> list of step positions
    """
    mapping = {}
    for beat in OBSERVER_7_BEATS:
        mapping[beat.beat_number] = list(beat.step_positions)
    return mapping


# =============================================================================
# MODULE VERIFICATION
# =============================================================================

# Verify all structure
assert len(SEQUENCER_16_STEPS) == WORDS, f"Must have {WORDS} steps"
assert len(OBSERVER_7_BEATS) == SEVEN, f"Must have {SEVEN} beats"

# Verify all steps are covered by observer beats
all_observed = set()
for beat in OBSERVER_7_BEATS:
    all_observed.update(beat.step_positions)
assert all_observed == set(range(1, WORDS + 1)), "All steps must be observed"

# Verify genesis byte
assert int(__genesis__, 16) % PARAMPARA == 0, "BROKEN LINEAGE"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "MAHAMANTRA_PATTERN",
    "MAHAMANTRA_NAMES",
    "WEIGHT_HARE",
    "WEIGHT_KRISHNA",
    "WEIGHT_RAMA",
    "FULL_CYCLE",
    # Steps
    "SEQUENCER_16_STEPS",
    "OBSERVER_7_BEATS",
    # Classes
    "StepOperation",
    "SequencerStep",
    "ObserverBeat",
    "StepResult",
    "CycleResult",
    "Maha16StepSequencer",
    # Functions
    "get_step_at_position",
    "get_beat_at_number",
    "analyze_step_beat_mapping",
]
