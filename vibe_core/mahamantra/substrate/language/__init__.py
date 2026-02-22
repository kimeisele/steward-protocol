"""
MAHA LANGUAGE — Deterministic Language Generation from Vibration
================================================================

"vāṇī tasya kā" — What is the speech of that One?

Production-grade language engine decomposed from the research monolith.
Each module has a single responsibility:

    types.py        — Result types (EngineResult, RhythmProfile, SyllableVector)
    phonetics.py    — 3D syllable vectors from CMU ARPAbet + fallback
    mantra_grid.py  — 32-step mantra sequencer grid (16 words × 2 beats)
    mode_affinity.py — WordNet graph-distance mode classification
    section_router.py — Attractor → Kapitel 18 section + verse template
    composer.py     — Scoring atoms (prosodic_affinity, chamber_boost, etc.)
    engine.py       — Thin orchestrator wiring Lotus → adapter → EngineResult

SUBSTRATE LEVEL: Pure math. Composition lives in adapters/composition.py.
Protocol lives in protocols/_composition.py.
"""

from vibe_core.mahamantra.substrate.language.types import (
    EngineResult,
    RhythmProfile,
    StateVector,
    SyllableVector,
)
from vibe_core.mahamantra.substrate.language.engine import (
    MahaLanguageEngine,
    generate,
    get_engine,
)

__all__ = [
    "EngineResult",
    "MahaLanguageEngine",
    "RhythmProfile",
    "StateVector",
    "SyllableVector",
    "generate",
    "get_engine",
]
