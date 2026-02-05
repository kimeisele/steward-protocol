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
from vibe_core.mahamantra.protocols._seed import (KSETRAJNA)


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
from vibe_core.mahamantra.protocols._pancha import TattvaDict

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
        # FIX: Cache synth instance for performance (same algorithm as MahaKernel)
        from vibe_core.mahamantra.substrate.algorithm.maha import MahaModularSynth, MahaSynthParams
        self._synth = MahaModularSynth(default_preset="quantum")
        self._params = MahaSynthParams(mod_space=mod_space)

    # =========================================================================
    # PANCHA TATTVA PROTOCOL (5 Questions Every Entity Must Answer)
    # =========================================================================

    @property
    def __tattva__(self) -> TattvaDict:
        """The 5-fold truth of MahaResonator."""
        return {
            "chaitanya": "MahaResonator - Iterative Harmonic Analysis Engine",
            "nityananda": "maha_oscillate() from algorithm/ (SSOT)",
            "advaita": "find_attractor() - Seed → Attractor computation",
            "gadadhara": "Seed → Oscillate → Cycle Detection → Attractor",
            "srivasa": f"MAHA_QUANTUM ({MAHA_QUANTUM}), mod_space={self.mod_space}",
        }

    def oscillate_once(self, value: int) -> int:
        """One oscillation = one pass through the 16-step algorithm."""
        # FIX: Use cached MahaModularSynth for 16/16 coverage (same as MahaKernel)
        return self._synth.transform(value, params=self._params)

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
            if result.cycle_length == KSETRAJNA:
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

    def resonance_strength(self, seed: int) -> int:
        """Returns resonance strength scaled to COSMIC_FRAME (0-21600)."""
        result = self.find_attractor(seed)
        if result.cycles_to_converge == 0:
            return 21600  # 100%
        ratio = 1.0 / (1.0 + result.cycles_to_converge)
        return int(ratio * 21600)


# Preset Resonators
RESONATOR_PRESETS: Final[Dict[str, MahaResonator]] = {
    "material": MahaResonator(mod_space=POSITION_SUM_KRISHNA), # 17
    "parampara": MahaResonator(mod_space=PARAMPARA),           # 37
    "transcendental": MahaResonator(mod_space=MALA_COMPLETE),  # 109
    "quantum": MahaResonator(mod_space=MAHA_QUANTUM),          # 137
}
