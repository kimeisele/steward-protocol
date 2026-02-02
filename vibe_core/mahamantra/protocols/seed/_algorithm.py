"""
MAHA ALGORITHM COEFFICIENTS - SINGLE SOURCE OF TRUTH
=====================================================

These define the branchless transformation: H=0, K=1, R=2

CURRENT INTERPRETATION (based on position sums):
  HARE    -> value x SEVEN (70 = 7 x 10)
  KRISHNA -> value + TEN   (17 = 7 + 10)
  RAMA    -> value x value (49 = 7^2)

WHEN MORE IS REVEALED THROUGH PARAMPARA -> CHANGE ONLY HERE!
All files import coefficients from here. No duplication.

THE ALGORITHM FUNCTIONS live in substrate/algorithm/maha.py:
  - maha_step(value, name, mod)   -> single step
  - maha_oscillate(value, mod)    -> 16 steps
  - find_attractor(seed, mod)     -> iterate until stable
"""

from typing import Final

from ._secondary import SEVEN, TEN

# Operation mapping: H=0, K=1, R=2
MAHA_OP_MAP: Final[dict[str, int]] = {"H": 0, "K": 1, "R": 2}

# Multiplication coefficients: H*7, K*1, R*1
MAHA_MULT: Final[tuple[int, ...]] = (SEVEN, 1, 1)

# Addition coefficients: H+0, K+10, R+0
MAHA_ADD: Final[tuple[int, ...]] = (0, TEN, 0)

# Square flags: H->0, K->0, R->1 (only R squares)
MAHA_SQ: Final[tuple[int, ...]] = (0, 0, 1)

__all__ = [
    "MAHA_OP_MAP",
    "MAHA_MULT",
    "MAHA_ADD",
    "MAHA_SQ",
]
