from dataclasses import dataclass
from typing import Dict, List, Protocol, Tuple, runtime_checkable

from vibe_core.mahamantra.protocols._seed import MAHAJANA_COUNT, PANCHA, QUARTERS


@runtime_checkable
class MahaSynthProtocol(Protocol):
    """
    Protocol for MahaSynth: 16-Step Modular Sequencer.

    Computer step sequencer based on Mahamantra structure.
    """

    def step(self, value: int, position: int) -> "StepResult":
        """Execute a single step."""
        ...

    def cycle(self, seed: int) -> "CycleResult":
        """Execute one complete 16-step cycle."""
        ...

    def resonate(self, seed: int, max_cycles: int = 100) -> "ResonanceResult":
        """Find attractor for a seed."""
        ...

    def spectrum(self, sample_size: int = 256) -> "SpectrumResult":
        """Analyze harmonic spectrum."""
        ...

    def cycle_batch(self, seeds: List[int]) -> List["CycleResult"]:
        """Execute cycles for multiple seeds."""
        ...

    def resonate_batch(self, seeds: List[int]) -> List["ResonanceResult"]:
        """Find attractors for multiple seeds."""
        ...

    def stats(self) -> Dict[str, object]:
        """Get synth statistics."""
        ...

    @property
    def params(self) -> "SynthParams": ...

    @property
    def mod_space(self) -> int: ...

    @property
    def preset(self) -> str: ...


@dataclass(frozen=True)
class SynthParams:
    """Modular Synthesizer Parameters."""

    mod_space: int
    feedback: int = 0
    phase_offset: int = 0
    lfo_enabled: bool = True
    lfo_rate: int = QUARTERS  # QUARTERS
    adsr_attack: int = PANCHA  # PANCHA
    adsr_decay: int = MAHAJANA_COUNT  # MAHAJANA_COUNT
    adsr_sustain: int = PANCHA  # PANCHA
    adsr_release: int = MAHAJANA_COUNT  # MAHAJANA_COUNT
    nibble_mode: bool = False


@dataclass(frozen=True)
class StepResult:
    """Result of executing one step."""

    position: int
    name: str
    quarter: int
    input_value: int
    output_value: int
    operation: str
    observer_beat: int


@dataclass(frozen=True)
class CycleResult:
    """Result of a complete 16-step cycle."""

    seed: int
    final_value: int
    steps: Tuple[StepResult, ...]
    mod_space: int
    preset: str


@dataclass(frozen=True)
class ResonanceResult:
    """Result of resonance analysis."""

    seed: int
    attractor: int
    cycles_to_converge: int
    cycle_length: int
    trajectory: Tuple[int, ...]


@dataclass(frozen=True)
class SpectrumResult:
    """Harmonic spectrum analysis."""

    mod_space: int
    attractors: Tuple[int, ...]
    attractor_names: Dict[int, str]
    convergence_map: Dict[int, int]
