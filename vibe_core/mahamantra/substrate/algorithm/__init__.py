"""
MAHA ALGORITHM - The 16-Step Execution Model
=============================================

THE SINGLE SOURCE OF TRUTH for Mahamantra computation.

PRIMITIVE FUNCTIONS (use these!):
    maha_step(value, name, mod)     - Single step transformation
    maha_oscillate(value, mod)      - Full 16-step cycle
    find_attractor(seed, mod)       - Find stable state

CLASSES:
    MahaAlgorithm16    - Pure 16-step executor
    MahaModularSynth   - Runtime-adjustable transformer
"""
from .maha import (
    # PRIMITIVE FUNCTIONS - THE API
    maha_step,
    maha_oscillate,
    find_attractor,
    # CLASSES
    MahaAlgorithm16,
    MahaModularSynth,
    MahaSynthParams,
    AlgorithmStep,
    Operation,
    Phase,
    SYNTH_PRESETS,
)

__all__ = [
    # PRIMITIVE FUNCTIONS - THE API
    "maha_step",
    "maha_oscillate",
    "find_attractor",
    # CLASSES
    "MahaAlgorithm16",
    "MahaModularSynth",
    "MahaSynthParams",
    "AlgorithmStep",
    "Operation",
    "Phase",
    "SYNTH_PRESETS",
]
