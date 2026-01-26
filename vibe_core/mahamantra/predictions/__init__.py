"""
MAHA PREDICTIONS - The Algorithm as KEY
========================================

This module uses the MAHA ALGORITHM (not linear search!) to generate
predictions across all fields: physics, biology, chemistry, medicine.

The 7 AXIOMS are Chaitanya - constant. Everything else flows through
the mathematical machinery:

  - mod 17 classification (quantum vs classical vs trinity)
  - Triangular numbers T(n)
  - Position sums (KRISHNA=17, RAMA=49, HARE=70)
  - SEVEN=7 and TEN=10 as building blocks
  - Products, ratios, GCD/LCM

ARCHITECTURE:
- _seed.py = THE LAW (pure, untouched)
- predictions/ = DERIVATIONS (separate, testable)

This is TDD for science: find "red tests" (predictions),
then verify against measurement.
"""

from .biology import BIOLOGY_PREDICTIONS
from .chemistry import CHEMISTRY_PREDICTIONS
from .maha_generator import MahaGenerator
from .medicine import MEDICINE_PREDICTIONS

__all__ = [
    "MahaGenerator",
    "BIOLOGY_PREDICTIONS",
    "CHEMISTRY_PREDICTIONS",
    "MEDICINE_PREDICTIONS",
]
