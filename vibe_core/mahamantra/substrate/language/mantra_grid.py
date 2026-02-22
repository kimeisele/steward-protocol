"""
MANTRA GRID — 32-Step Sequencer derived from seed.MAHAMANTRA
=============================================================

16 words × 2 beats = 32 steps. Each step carries HolyName identity
and a compositional mode. NO HARDCODED SEQUENCE — derived from SSOT.

Mode mapping (Pancha Tattva derived):
    Hare    = Shakti (energy/devotion) → DHARMA
    Krishna = Source (identity/wisdom) → GENESIS
    Rama    = Ananda (stability/action) → KARMA
"""

from __future__ import annotations

from functools import lru_cache
from typing import Dict, Final, List, NamedTuple, Tuple

from vibe_core.mahamantra.protocols._seed import (
    HALVES,
    KSETRAJNA,
    QUARTERS,
    WORDS,
)
from vibe_core.mahamantra.substrate.language.types import SyllableVector
from vibe_core.mahamantra.substrate.seed import (
    MAHAMANTRA,
    HolyName,
)

_GRID_STEPS: Final[int] = WORDS * HALVES  # 32

_HOLYNAME_MODE: Final[Dict[HolyName, str]] = {
    HolyName.HARE: "DHARMA",
    HolyName.KRISHNA: "GENESIS",
    HolyName.RAMA: "KARMA",
}


class GridStep(NamedTuple):
    """One position in the 32-step mantra sequencer."""

    position: int  # 0-31
    holy_name: HolyName  # HARE/KRISHNA/RAMA (from seed.MAHAMANTRA)
    mode: str  # DHARMA/GENESIS/KARMA
    beat: int  # 0=downbeat (stressed), 1=upbeat (unstressed)


@lru_cache(maxsize=1)
def build_mantra_grid() -> Tuple[GridStep, ...]:
    """Build the 32-step mantra sequencer grid from seed.MAHAMANTRA."""
    assert len(MAHAMANTRA) == WORDS
    grid: List[GridStep] = []
    for i, name in enumerate(MAHAMANTRA):
        mode = _HOLYNAME_MODE[name]
        grid.append(GridStep(position=i * HALVES, holy_name=name, mode=mode, beat=0))
        grid.append(GridStep(position=i * HALVES + KSETRAJNA, holy_name=name, mode=mode, beat=1))
    return tuple(grid)


def alignment_score(sv: SyllableVector, gs: GridStep) -> int:
    """Score how well a syllable vector fits a grid step."""
    score = 0
    # Stressed syllables prefer downbeats
    if sv.stress >= KSETRAJNA and gs.beat == 0:
        score += 3
    elif sv.stress == 0 and gs.beat == KSETRAJNA:
        score += 2
    # Heavy syllables prefer Krishna/Rama (heavier names)
    if sv.weight >= 3 and gs.holy_name in (HolyName.KRISHNA, HolyName.RAMA):
        score += 2
    elif sv.weight <= HALVES and gs.holy_name == HolyName.HARE:
        score += KSETRAJNA
    # High vowels resonate with Hare (open, devotional)
    if sv.height >= QUARTERS and gs.holy_name == HolyName.HARE:
        score += KSETRAJNA
    # Low vowels resonate with Krishna (deep, foundational)
    if sv.height <= HALVES and gs.holy_name == HolyName.KRISHNA:
        score += KSETRAJNA
    return score


def align_syllables_to_grid(
    vectors: Tuple[SyllableVector, ...],
) -> Tuple[int, ...]:
    """Find best-fit alignment of syllable vectors onto the 32-step grid.

    Returns tuple of grid step indices (one per syllable).
    """
    if not vectors:
        return ()

    grid = build_mantra_grid()
    n_syl = len(vectors)
    n_grid = len(grid)

    if n_syl == KSETRAJNA:
        best_pos = 0
        best_score = -1
        for pos in range(n_grid):
            score = alignment_score(vectors[0], grid[pos])
            if score > best_score:
                best_score = score
                best_pos = pos
        return (best_pos,)

    # Multi-syllable: sliding window over grid
    best_start = 0
    best_total = -1

    for start in range(n_grid):
        total = 0
        for j in range(n_syl):
            step_idx = (start + j) % n_grid
            total += alignment_score(vectors[j], grid[step_idx])
        if total > best_total:
            best_total = total
            best_start = start

    return tuple((best_start + j) % n_grid for j in range(n_syl))


def get_holyname_mode() -> Dict[HolyName, str]:
    """Expose the HolyName→mode mapping for external use."""
    return dict(_HOLYNAME_MODE)
