"""
MAHA RESONATOR - Iterative Harmonic Analysis Engine
===================================================

"Cycles of time, cycles of thought."

Unlike a one-shot transform, the resonator applies the algorithm
repeatedly until stable states (attractors) are found.

The mod_space determines the "resonant frequency".

NOTE: Uses maha_oscillate() from algorithm/ - NO DUPLICATION.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x672435f8"

from dataclasses import dataclass
from typing import Final, Dict, List, Tuple

from vibe_core.mahamantra.protocols._seed import (
    MAHA_QUANTUM,
    PARAMPARA,
    POSITION_SUM_KRISHNA,
    MALA_COMPLETE,
)

# THE ALGORITHM - imported from SSOT, not reimplemented!
from vibe_core.mahamantra.substrate.algorithm import maha_oscillate


@dataclass(frozen=True)
class ResonanceResult:
    """Result of resonance analysis."""
    seed: int
    attractor: int
    cycles_to_converge: int
    cycle_length: int  # 1 = fixed point, >1 = periodic orbit
    trajectory: Tuple[int, ...]


class MahaResonator:
    """
    The Maha Resonator.
    Finds attractors by iterating the Maha Algorithm.
    """
    def __init__(self, mod_space: int = MAHA_QUANTUM) -> None:
        self.mod_space = mod_space

    def oscillate_once(self, value: int) -> int:
        """One oscillation = one pass through the 16-step algorithm."""
        # DELEGATE to algorithm/ - no duplication!
        # Note: Uses legacy maha_oscillate (12/16 coverage) for backward compatibility.
        # For 16/16 coverage, use MahaModularSynth.transform() directly.
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            return maha_oscillate(value, self.mod_space)

    def find_attractor(self, seed: int, max_cycles: int = 100) -> ResonanceResult:
        """Find the attractor (stable state) for a given seed."""
        seen: Dict[int, int] = {}
        trajectory: List[int] = []
        value = seed % self.mod_space

        for cycle in range(max_cycles):
            if value in seen:
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

        return ResonanceResult(
            seed=seed,
            attractor=value,
            cycles_to_converge=max_cycles,
            cycle_length=0,
            trajectory=tuple(trajectory),
        )

    def harmonic_spectrum(self) -> Dict[str, List[int]]:
        """Compute complete harmonic spectrum for this mod_space."""
        fixed_points = []
        attractor_basins: Dict[int, List[int]] = {}

        for seed in range(self.mod_space):
            result = self.find_attractor(seed)
            if result.cycle_length == 1:
                if result.attractor not in fixed_points:
                    fixed_points.append(result.attractor)

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
        result = self.find_attractor(seed)
        if result.cycles_to_converge == 0:
            return 1.0
        return 1.0 / (1.0 + result.cycles_to_converge)


# Preset Resonators
RESONATOR_PRESETS: Final[Dict[str, MahaResonator]] = {
    "material": MahaResonator(mod_space=POSITION_SUM_KRISHNA), # 17
    "parampara": MahaResonator(mod_space=PARAMPARA),           # 37
    "transcendental": MahaResonator(mod_space=MALA_COMPLETE),  # 109
    "quantum": MahaResonator(mod_space=MAHA_QUANTUM),          # 137
}
