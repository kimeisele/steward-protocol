"""
MAHA KIRTAN - The Compute Orchestrator
=======================================

"kīrtanīyaḥ sadā hariḥ"

Bridges the 7-beat Lila Step Sequencer with MahaAlgorithm transforms
for rhythmic computations.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x672435f8"

from dataclasses import dataclass
from typing import Final, List, Union, Optional

from vibe_core.mahamantra.protocols._seed import (
    MAHA_QUANTUM,
    SEVEN,
    VINA_STRINGS,
)
from vibe_core.mahamantra.protocols._header import MahaCell

from vibe_core.mahamantra.substrate.algorithm.maha import MahaModularSynth
from vibe_core.mahamantra.substrate.resonance.resonator import MahaResonator
from vibe_core.mahamantra.substrate.resonance.oracle import MahaOracle

from vibe_core.mahamantra.substrate.lila_chronology import (
    get_kirtan_runtime,
    get_step_sequencer,
)

@dataclass(frozen=True)
class KirtanComputeResult:
    """Result of a MahaKirtan compute cycle."""
    seed: int
    transformed_value: int
    beat_number: int  # 1-7
    beat_year: int
    beat_delta: int
    call_response: str
    flute_resonance: int
    vina_resonance: int
    vina_string: int
    oracle_validated: bool
    parampara_channel: int
    round_number: int
    resonance_level: int
    cell: Optional[MahaCell] = None


@dataclass
class MahaKirtanState:
    """State of the MahaKirtan compute orchestrator."""
    current_tick: int = 0
    current_round: int = 0
    total_computations: int = 0
    resonance_level: int = 0
    last_oracle_result: bool = True
    accumulated_value: int = 0


class MahaKirtan:
    """The Maha Kirtan Compute Orchestrator."""

    BEATS_PER_ROUND: Final[int] = SEVEN
    ROUNDS_PER_MALA: Final[int] = 108
    DEFAULT_MOD_SPACE: Final[int] = MAHA_QUANTUM

    def __init__(self, mod_space: int = MAHA_QUANTUM, kirtan_mode: str = "alternating", use_oracle: bool = True) -> None:
        self.mod_space = mod_space
        self.kirtan_mode = kirtan_mode
        self.use_oracle = use_oracle

        self._synth = MahaModularSynth(default_preset="quantum")
        self._resonator = MahaResonator(mod_space=mod_space)
        self._oracle = MahaOracle() if use_oracle else None
        self._sequencer = get_step_sequencer(kirtan_mode)
        self._runtime = get_kirtan_runtime()
        self._state = MahaKirtanState()

    def _get_flute_resonance(self, tick: int) -> int:
        return tick % self.mod_space

    def _get_vina_resonance(self, seed: int, tick: int) -> Tuple[int, int]:
        vina_resonance = seed % self.mod_space
        vina_string = (seed % VINA_STRINGS) + 1
        return vina_resonance, vina_string

    def _oracle_prefilter(self, seed: int) -> Tuple[bool, int]:
        if not self.use_oracle or self._oracle is None:
             return True, -1
        reading = self._oracle.consult_seed(seed)
        return reading.parampara_validated, reading.parampara_channel

    def compute(self, input_data: Union[int, MahaCell]) -> KirtanComputeResult:
        if isinstance(input_data, int):
            seed = input_data
            cell = None
        else:
            cell = input_data
            seed = cell.header.sravanam

        state = self._runtime.tick()
        beat = state.current_beat
        tick = state.tick

        oracle_valid, parampara_channel = self._oracle_prefilter(seed)
        self._state.last_oracle_result = oracle_valid
        
        flute_resonance = self._get_flute_resonance(tick)
        vina_resonance, vina_string = self._get_vina_resonance(seed, tick)
        
        beat_modulated_seed = (seed + beat.delta) % self.mod_space
        transformed = self._synth.transform(beat_modulated_seed)

        if flute_resonance > 0:
            resonance_boost = (transformed * flute_resonance) // self.mod_space
            transformed = (transformed + resonance_boost) % self.mod_space

        threshold = self.mod_space // 3
        if vina_resonance > threshold:
            vina_boost = (transformed * vina_resonance) // (self.mod_space * 2)
            transformed = (transformed + vina_boost) % self.mod_space

        self._state.current_tick = tick
        self._state.current_round = state.round_number
        self._state.total_computations += 1
        self._state.resonance_level = (self._state.resonance_level + flute_resonance + vina_resonance) % self.mod_space
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
            resonance_level=self._state.resonance_level,
            cell=cell,
        )

    def compute_round(self, seed: int) -> List[KirtanComputeResult]:
        results = []
        for _ in range(self.BEATS_PER_ROUND):
            result = self.compute(seed)
            results.append(result)
            seed = result.transformed_value
        return results

    def compute_rounds(self, seed: int, num_rounds: int = 7) -> List[KirtanComputeResult]:
        results = []
        current_seed = seed
        for _ in range(num_rounds):
            round_results = self.compute_round(current_seed)
            results.extend(round_results)
            current_seed = round_results[-1].transformed_value
        return results
