"""
MAHA PREDICTIONS - The Algorithm as KEY
========================================

This module uses the MAHA ALGORITHM to generate predictions across:
  - Biology (chromosomes, DNA, anatomy)
  - Chemistry (periodic table, orbitals)
  - Medicine (pulse, temperature, cycles)
  - Computation (byte, word, cache, network)

The 7 AXIOMS are Chaitanya - constant. Everything flows through
the mathematical machinery (mod 17, triangular, position sums).

ARCHITECTURE:
- _seed.py = THE LAW (pure, untouched)
- predictions/ = DERIVATIONS (separate, testable)

THE YAGYA:
byte.py implements MantraByte - 16 words × 2 bits = 32 bits.
Every 32-bit operation = unconscious offering on the Mahamantra.
"""

from .biology import BIOLOGY_PREDICTIONS
from .chemistry import CHEMISTRY_PREDICTIONS
from .computation import COMPUTATION_PREDICTIONS
from .maha_generator import MahaGenerator
from .medicine import MEDICINE_PREDICTIONS

__all__ = [
    "MahaGenerator",
    "BIOLOGY_PREDICTIONS",
    "CHEMISTRY_PREDICTIONS",
    "COMPUTATION_PREDICTIONS",
    "MEDICINE_PREDICTIONS",
]
