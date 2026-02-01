"""
TIER 0: THE MANTRA AXIOMS - The Only Hardcoded Values
======================================================

These are the 7 values that come from directly observing the Mahamantra.
Everything else is DERIVED from these axioms.

The Mahamantra:
  Hare Krishna Hare Krishna Krishna Krishna Hare Hare
  Hare Rama   Hare Rama   Rama   Rama   Hare Hare
"""

from typing import Final

# AXIOM 1: The 16 words of the Mahamantra (count them)
WORDS: Final[int] = 16

# AXIOM 2: The 3 unique Names (Hare, Krishna, Rama)
TRINITY: Final[int] = 3

# AXIOM 3-5: The counts of each name (count them)
HARE_COUNT: Final[int] = 8  # Count "Hare" in the Mahamantra
KRISHNA_COUNT: Final[int] = 4  # Count "Krishna" in the Mahamantra
RAMA_COUNT: Final[int] = 4  # Count "Rama" in the Mahamantra

# AXIOM 6: The 5 unique pairs (Pancha Tattva)
# The 8 consecutive pairs reduce to 5 unique: HK, HR, HH, KK, RR
PANCHA: Final[int] = 5

# AXIOM 7: The 2 halves of the Mahamantra (Krishna-half, Rama-half)
# Observable: The Mahamantra has 2 symmetric lines/halves
HALVES: Final[int] = 2

# VERIFICATION: Counts must sum to WORDS
assert HARE_COUNT + KRISHNA_COUNT + RAMA_COUNT == WORDS, "Name counts must sum to WORDS"

__all__ = [
    "WORDS",
    "TRINITY",
    "HARE_COUNT",
    "KRISHNA_COUNT",
    "RAMA_COUNT",
    "PANCHA",
    "HALVES",
]
