"""
MAHA PREDICTIONS - The Algorithm as KEY
========================================

REAL ENGINEERING PREDICTIONS:
  - Moore's Law: Memory Wall solutions via Lotus architecture
  - Computation: 16-bit kernel paradigm, cache optimization
  - Biology, Chemistry, Medicine: Derived constants

The 7 AXIOMS are Chaitanya - constant. Everything flows through
the mathematical machinery (mod 17, triangular, position sums).

ARCHITECTURE:
- _seed.py = THE LAW (pure, untouched)
- predictions/ = DERIVATIONS (separate, testable)

THE MEMORY WALL PROBLEM:
- 60% of system energy spent on DATA MOVEMENT
- 1000x penalty for DRAM vs compute
- Lotus solves this via O(1) routing, 16-ary branching, fractal locality
"""

from .biology import BIOLOGY_PREDICTIONS
from .chemistry import CHEMISTRY_PREDICTIONS
from .computation import (
    COMPUTATION_PREDICTIONS,
    KERNEL_HIERARCHY,
    MAHABYTE,
    OCTET,
    PACKED_MAHAMANTRA,
)
from .japa import JAPA_INSIGHT, JAPA_PREDICTIONS
from .maha_generator import MahaGenerator
from .medicine import MEDICINE_PREDICTIONS
from .moores_law import ENGINEERING_INSIGHT, MOORES_LAW_PREDICTIONS

__all__ = [
    # Generator
    "MahaGenerator",
    # REAL Engineering (Moore's Law)
    "MOORES_LAW_PREDICTIONS",
    "ENGINEERING_INSIGHT",
    # Japa Singularity
    "JAPA_PREDICTIONS",
    "JAPA_INSIGHT",
    # Other Predictions
    "BIOLOGY_PREDICTIONS",
    "CHEMISTRY_PREDICTIONS",
    "COMPUTATION_PREDICTIONS",
    "MEDICINE_PREDICTIONS",
    # 16-bit Kernel Paradigm
    "MAHABYTE",
    "OCTET",
    "PACKED_MAHAMANTRA",
    "KERNEL_HIERARCHY",
]
