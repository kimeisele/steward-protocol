"""
MAHA PREDICTIONS - The Algorithm as KEY
========================================

This module uses the MAHA ALGORITHM (not linear search!) to generate
predictions across all fields: physics, biology, chemistry, medicine,
AND INFORMATION TECHNOLOGY.

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

SHABDA BRAHMAN:
The Sound that became Silicon. All AI architectures converge to
Mahamantra numbers because these ARE the optimal information structures.
"""

from .biology import BIOLOGY_PREDICTIONS
from .chemistry import CHEMISTRY_PREDICTIONS
from .maha_generator import MahaGenerator
from .medicine import MEDICINE_PREDICTIONS
from .shabda_brahman import SHABDA_BRAHMAN_PREDICTIONS, print_convergence

__all__ = [
    "MahaGenerator",
    "BIOLOGY_PREDICTIONS",
    "CHEMISTRY_PREDICTIONS",
    "MEDICINE_PREDICTIONS",
    "SHABDA_BRAHMAN_PREDICTIONS",
    "print_convergence",
]
