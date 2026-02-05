"""
MAHA SYNTH - 16-Step Modular Sequencer
======================================

"venum kvanantam aravinda-dalayataksham"
"Krishna plays His flute, with lotus-petal eyes"
— Brahma-samhita 5.30

THIS IS NOT AN AUDIO SYNTHESIZER.
THIS IS A COMPUTATIONAL STEP SEQUENCER WITH MODULAR ARCHITECTURE.

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
    - SEVEN = 8 - 1 = 7

MODULAR KNOBS:
    mod_space     - Resonant frequency (17=classical, 137=quantum, 512=wide)
    feedback      - State preservation between steps
    ADSR          - Envelope shaping (Attack/Decay/Sustain/Release)
    LFO           - Low frequency oscillation modulation
    phase_offset  - Starting position in cycle

PRESETS:
    classical - Converges to fixed point (mod 17)
    quantum   - Moderate diversity (mod 137, default)
    trinity   - 3-state output (unstable)
    pancha    - 5-way classification
    nava      - 9-state output (navadha bhakti)
    wide      - Maximum diversity (mod 512)

POLYRHYTHM:
    - 16 and 7 are COPRIME (GCD = 1)
    - LCM(16, 7) = 112 = full cycle before realignment
    - 16 mod 7 = 2 = HALVES

USAGE:
======
    from vibe_core.mahamantra import mahamantra

    # Get synth with preset
    synth = mahamantra.synth(preset="quantum")

    # Execute one step
    result = synth.step(value=42, position=1)

    # Execute full 16-step cycle
    cycle = synth.cycle(seed=42)

    # Find attractor (stable resonance)
    attractor = synth.resonate(seed=42)

    # Analyze harmonic spectrum
    spectrum = synth.spectrum()
"""

from typing import Final, Tuple, Dict, Optional, List, Any

# === MAHAJANA DECLARATION ===
__mahajana__ = "narada"
__position__ = 3
__genesis__ = "0x7382dc4f"  # GenesisByte: parampara % 37 == 0

from vibe_core.mahamantra.protocols.synth import (
    MahaSynthProtocol,
    SynthParams,
    StepResult,
    CycleResult,
    ResonanceResult,
    SpectrumResult,
)
from vibe_core.mahamantra.protocols._seed import (
    GITA_CHAPTERS,
    HALVES,
    KSETRAJNA,
    KSHETRA,
    MAHA_QUANTUM,
    MAHAJANA_COUNT,
    MAHAMANTRA_NAME_HARE,
    MAHAMANTRA_NAME_KRISHNA,
    MAHAMANTRA_WORD_PATTERN,
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
    # Core coefficients for synth-specific step() logic (with ADSR/LFO modulation)
    MAHA_OP_MAP as _OP_MAP,
    MAHA_MULT as _MULT,
    MAHA_ADD as _ADD,
    MAHA_SQ as _SQ,
)

# THE ALGORITHM - for resonance/attractor discovery
from vibe_core.mahamantra.substrate.algorithm import maha_oscillate


# =============================================================================
# CONSTANTS (DERIVED from _seed.py)
# =============================================================================

# The Mahamantra pattern (16 words)
# The Mahamantra pattern (16 words)
PATTERN: Final[Tuple[str, ...]] = MAHAMANTRA_WORD_PATTERN

# Binary pattern from Mahamantra (0=HARE, 1=NAME)
# Derived: 0 if Name is HARE, else 1
BINARY_PATTERN: Final[Tuple[int, ...]] = tuple(
    0 if name == MAHAMANTRA_NAME_HARE else 1 for name in PATTERN
)

# Position sums reveal operations (DERIVED!)
WEIGHT_HARE: Final[int] = SEVEN * TEN      # 7 × 10 = 70
WEIGHT_KRISHNA: Final[int] = SEVEN + TEN   # 7 + 10 = 17
WEIGHT_RAMA: Final[int] = SEVEN * SEVEN    # 7 × 7 = 49

# ADSR envelope (from binary pattern 01011100)
ADSR_ATTACK: Final[int] = PANCHA           # 5 - rising
ADSR_DECAY: Final[int] = MAHAJANA_COUNT    # 12 - falling
ADSR_SUSTAIN: Final[int] = PANCHA          # 5 - steady
ADSR_RELEASE: Final[int] = MAHAJANA_COUNT  # 12 - final fall

# Full cycle length (polyrhythm)
import math
FULL_CYCLE: Final[int] = (WORDS * SEVEN) // math.gcd(WORDS, SEVEN)  # 112


# =============================================================================
# SYNTH-SPECIFIC COEFFICIENT TABLES (Core coefficients imported from _seed.py)
# =============================================================================
# For step() with ADSR: HARE uses ADSR multiplier, KRISHNA/RAMA don't
_ADSR_MULT: Final[Tuple[int, ...]] = (1, 0, 0)  # HARE uses ADSR, others don't
# For step() with position: KRISHNA adds position, others don't
_POS_ADD: Final[Tuple[int, ...]] = (0, 1, 0)    # KRISHNA adds pos, others don't
# For step() with LFO: HARE uses LFO, others don't
_LFO_ADD: Final[Tuple[int, ...]] = (1, 0, 0)    # HARE adds LFO, others don't


# =============================================================================
# PRESETS
# =============================================================================

SYNTH_PRESETS: Final[Dict[str, SynthParams]] = {
    # CLASSICAL: Original behavior - converges to fixed point
    "classical": SynthParams(mod_space=WEIGHT_KRISHNA, feedback=0),
    # QUANTUM: Default - moderate diversity with observer (feedback=1)
    "quantum": SynthParams(mod_space=MAHA_QUANTUM, feedback=KSETRAJNA),
    # TRINITY: 3-state output (unstable, like muon)
    "trinity": SynthParams(mod_space=TRINITY, feedback=TRINITY),
    # PANCHA: 5-way classification (ADSR-active)
    "pancha": SynthParams(mod_space=PANCHA, feedback=KSETRAJNA),
    # NAVA: 9-state output (navadha bhakti)
    "nava": SynthParams(mod_space=NAVA, feedback=KSETRAJNA),
    # WIDE: Maximum diversity (512-bit space)
    "wide": SynthParams(mod_space=512, feedback=PANCHA),
}

# Known attractors for MAHA_QUANTUM (137) - ALL DERIVED FROM SSOT
# Derived constants (no hardcoding)
_SHRUTIS_VAL: Final[int] = KSHETRA - HALVES  # 24 - 2 = 22
_HARE_KRISHNA_VAL: Final[int] = POSITION_SUM_HARE + POSITION_SUM_KRISHNA  # 70 + 17 = 87

QUANTUM_ATTRACTORS: Final[Dict[int, str]] = {
    POSITION_SUM_TOTAL: "FIELD (T(16) = Position Sum Total)",  # 136
    POSITION_SUM_RAMA: "RAMA (7² = Position Sum Rama)",  # 49
    _SHRUTIS_VAL: "SHRUTIS (Indian microtones)",  # 22
    GITA_CHAPTERS: "GITA_CHAPTERS",  # 18
    _HARE_KRISHNA_VAL: "CHAITANYA (Hare + Krishna combined)",  # 87
}


# =============================================================================
# TRIANGULAR FUNCTION
# =============================================================================

def triangular(n: int) -> int:
    """T(n) = n(n+1)/2 - Sum of integers 1 to n."""
    return n * (n + 1) // 2


# =============================================================================
# MAHA SYNTH
# =============================================================================

class MahaSynth(MahaSynthProtocol):
    """
    16-Step Modular Sequencer.

    A computational step sequencer based on the Mahamantra structure:
    - 16 steps = The Field (kshetra)
    - 7 observer beats = The Knower (kshetrajna)
    - Modular knobs for runtime adjustment

    This is NOT audio synthesis.
    This is deterministic sequence generation.
    """

    _naga_flooded: bool = True
    _naga_gene: str = "maha_synth_sequencer"

    def __init__(
        self,
        preset: str = "quantum",
        params: Optional[SynthParams] = None,
    ) -> None:
        """
        Initialize the synth.

        Args:
            preset: Named preset from SYNTH_PRESETS
            params: Custom SynthParams (overrides preset)
        """
        self._preset_name = preset
        if params is not None:
            self._params = params
        else:
            self._params = SYNTH_PRESETS.get(preset, SYNTH_PRESETS["quantum"])

        self._total_steps = 0
        self._total_cycles = 0

    @property
    def params(self) -> SynthParams:
        """Current synth parameters."""
        return self._params

    @property
    def mod_space(self) -> int:
        """Current modulo space."""
        return self._params.mod_space

    @property
    def preset(self) -> str:
        """Current preset name."""
        return self._preset_name

    # =========================================================================
    # OBSERVER LAYER
    # =========================================================================

    def _get_observer_beat(self, position: int) -> int:
        """
        Get which of the 7 observer beats observes this position.

        Maps 16 steps to 7 beats using continuous mapping.
        """
        # beat = ceil(position * 7 / 16)
        return ((position - 1) * SEVEN // WORDS) + 1

    def _get_adsr_multiplier(self, quarter: int) -> int:
        """Get ADSR envelope multiplier for current quarter."""
        if quarter == 1:
            return self._params.adsr_attack   # 5 - rising
        elif quarter == 2:
            return self._params.adsr_decay    # 12 - falling
        elif quarter == 3:
            return self._params.adsr_sustain  # 5 - steady
        else:
            return self._params.adsr_release  # 12 - final fall

    def _get_lfo_value(self, position: int) -> int:
        """Calculate LFO modulation value for current step."""
        if not self._params.lfo_enabled:
            return 0
        binary_val = BINARY_PATTERN[(position - 1) % WORDS]
        phase_in_lfo = (position - 1) % self._params.lfo_rate
        return binary_val * phase_in_lfo

    # =========================================================================
    # CORE OPERATIONS
    # =========================================================================

    def step(self, value: int, position: int) -> StepResult:
        """
        Execute a single step at given position.

        Args:
            value: Input value
            position: Step position (1-16)

        Returns:
            StepResult with output and metadata
        """
        pos = ((position - 1) % WORDS) + 1  # Normalize to 1-16
        name = PATTERN[pos - 1]
        quarter = ((pos - 1) // QUARTERS) + 1
        adsr = self._get_adsr_multiplier(quarter)
        lfo = self._get_lfo_value(pos)
        mod = self._params.mod_space

        # BRANCHLESS computation via lookup tables
        op = _OP_MAP[name]

        # Compute all three possible outputs (only correct one will be selected)
        # HARE: value * SEVEN * adsr + lfo
        # KRISHNA: value + TEN + pos
        # RAMA: value * value

        # Base computation: mult × value + add
        adsr_factor = 1 + _ADSR_MULT[op] * (adsr - 1)  # 1 for K/R, adsr for H
        mult_coeff = _MULT[op] * adsr_factor
        add_coeff = _ADD[op] + _POS_ADD[op] * pos + _LFO_ADD[op] * lfo

        v = (value * mult_coeff + add_coeff) % mod

        # Conditional square via arithmetic selection
        squared = (v * v) % mod
        output = _SQ[op] * squared + (1 - _SQ[op]) * v

        # Operation string (for logging/debugging)
        op_templates = (
            f"{value} × {SEVEN} × {adsr} + {lfo} = {output} (mod {mod})",  # HARE
            f"{value} + {TEN} + {pos} = {output} (mod {mod})",             # KRISHNA
            f"{value}² = {output} (mod {mod})",                            # RAMA
        )
        operation = op_templates[op]

        self._total_steps += 1

        return StepResult(
            position=pos,
            name=name,
            quarter=quarter,
            input_value=value,
            output_value=output,
            operation=operation,
            observer_beat=self._get_observer_beat(pos),
        )

    def cycle(self, seed: int) -> CycleResult:
        """
        Execute one complete 16-step cycle.

        Args:
            seed: Starting value

        Returns:
            CycleResult with all step results
        """
        value = seed % self._params.mod_space
        steps = []
        feedback_acc = 0

        for pos in range(1, WORDS + 1):
            # Apply step
            result = self.step(value + feedback_acc, pos)
            steps.append(result)
            value = result.output_value

            # Accumulate feedback
            feedback_acc = (feedback_acc + value * self._params.feedback) % self._params.mod_space

        self._total_cycles += 1

        return CycleResult(
            seed=seed,
            final_value=value,
            steps=tuple(steps),
            mod_space=self._params.mod_space,
            preset=self._preset_name,
        )

    # =========================================================================
    # RESONANCE (ATTRACTOR DISCOVERY)
    # =========================================================================

    def _oscillate_once(self, value: int) -> int:
        """One oscillation = simplified 16-step pass (no ADSR/LFO for speed).

        DELEGATES to algorithm/ - no duplication!
        """
        return maha_oscillate(value, self._params.mod_space)

    def resonate(self, seed: int, max_cycles: int = 100) -> ResonanceResult:
        """
        Find the attractor (stable state) for a given seed.

        Repeated iteration finds stable harmonics (attractors).

        Args:
            seed: Starting value
            max_cycles: Maximum iterations before giving up

        Returns:
            ResonanceResult with attractor and convergence info
        """
        seen: Dict[int, int] = {}
        trajectory: List[int] = []
        value = seed % self._params.mod_space

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
            value = self._oscillate_once(value)

        # No convergence found
        return ResonanceResult(
            seed=seed,
            attractor=value,
            cycles_to_converge=max_cycles,
            cycle_length=0,
            trajectory=tuple(trajectory),
        )

    def spectrum(self, sample_size: int = 256) -> SpectrumResult:
        """
        Analyze the harmonic spectrum (all attractors).

        Args:
            sample_size: How many seeds to test

        Returns:
            SpectrumResult with all discovered attractors
        """
        convergence_map: Dict[int, int] = {}
        attractors_set: set = set()

        for seed in range(sample_size):
            result = self.resonate(seed)
            convergence_map[seed] = result.attractor
            attractors_set.add(result.attractor)

        attractors = tuple(sorted(attractors_set))

        # Name known attractors
        if self._params.mod_space == MAHA_QUANTUM:
            attractor_names = {a: QUANTUM_ATTRACTORS.get(a, f"Attractor-{a}") for a in attractors}
        else:
            attractor_names = {a: f"Attractor-{a}" for a in attractors}

        return SpectrumResult(
            mod_space=self._params.mod_space,
            attractors=attractors,
            attractor_names=attractor_names,
            convergence_map=convergence_map,
        )

    # =========================================================================
    # BATCH OPERATIONS
    # =========================================================================

    def cycle_batch(self, seeds: List[int]) -> List[CycleResult]:
        """Execute cycles for multiple seeds."""
        return [self.cycle(seed) for seed in seeds]

    def resonate_batch(self, seeds: List[int]) -> List[ResonanceResult]:
        """Find attractors for multiple seeds."""
        return [self.resonate(seed) for seed in seeds]

    # =========================================================================
    # STATS
    # =========================================================================

    def stats(self) -> Dict[str, Any]:
        """Get synth statistics."""
        return {
            "preset": self._preset_name,
            "mod_space": self._params.mod_space,
            "feedback": self._params.feedback,
            "total_steps": self._total_steps,
            "total_cycles": self._total_cycles,
            "steps_per_cycle": WORDS,
            "observer_beats": SEVEN,
            "full_polyrhythm_cycle": FULL_CYCLE,
        }


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_synth(preset: str = "quantum", params: Optional[SynthParams] = None) -> MahaSynth:
    """Create a new MahaSynth instance."""
    return MahaSynth(preset=preset, params=params)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MahaSynth",
    "SynthParams",
    "StepResult",
    "CycleResult",
    "ResonanceResult",
    "SpectrumResult",
    "SYNTH_PRESETS",
    "PATTERN",
    "create_synth",
]
