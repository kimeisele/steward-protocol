"""
MAHA PREDICTIONS - The Algorithm as KEY
========================================

This module uses the MAHA ALGORITHM to generate predictions across:
  - Biology (chromosomes, DNA, anatomy)
  - Chemistry (periodic table, orbitals)
  - Medicine (pulse, temperature, cycles)
  - Computation (16-bit kernel, packed encoding, architecture)

The 7 AXIOMS are Chaitanya - constant. Everything flows through
the mathematical machinery (mod 17, triangular, position sums).

ARCHITECTURE:
- _seed.py = THE LAW (pure, untouched)
- predictions/ = DERIVATIONS (separate, testable)

THE 16-BIT KERNEL PARADIGM:
The Mahamantra IS a 16-bit kernel (WORDS = 16).
The 8-bit "byte" is a Kali Yuga half-measure (HARE_COUNT = 8).
byte.py implements PACKED encoding: 16 × 2 bits = 32 bits.
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
from .maha_generator import MahaGenerator
from .medicine import MEDICINE_PREDICTIONS

__all__ = [
    # Generator
    "MahaGenerator",
    # Predictions
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
