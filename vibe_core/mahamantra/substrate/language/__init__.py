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
    composer.py     — Rhythmic sequencing composition (words → English)
    engine.py       — Thin orchestrator wiring all stages

SUBSTRATE LEVEL: This is language as vibration routing, not NLP.
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
from vibe_core.mahamantra.substrate.language.composer import compose_from_wave

__all__ = [
    "EngineResult",
    "MahaLanguageEngine",
    "RhythmProfile",
    "StateVector",
    "SyllableVector",
    "compose_from_wave",
    "generate",
    "get_engine",
]
