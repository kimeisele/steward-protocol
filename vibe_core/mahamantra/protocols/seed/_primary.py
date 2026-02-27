"""
TIER 1: PRIMARY DERIVATIONS - Direct from Axioms
=================================================

These constants are derived directly from the 7 axioms.
No secondary derivations used here.
"""

from typing import Final

from ._axioms import (
    HALVES,
    HARE_COUNT,
    KRISHNA_COUNT,
    PANCHA,
    TRINITY,
    WORDS,
)

# QUARTERS = KRISHNA_COUNT (Krishna appears 4 times = 4 quadrants)
QUARTERS: Final[int] = KRISHNA_COUNT  # 4

# KSETRAJNA = TRINITY - HALVES = 3 - 2 = 1 (DERIVED!)
# "ksetra-jnam capi mam viddhi" (BG 13.3) - "Know Me as the Knower"
KSETRAJNA: Final[int] = TRINITY - HALVES  # 1

# HALF_SIZE = Words per half
HALF_SIZE: Final[int] = WORDS // HALVES  # 8

# LILA = WORDS x TRINITY = 16 x 3 = 48
# The "play" of Krishna - manifest runtime
LILA: Final[int] = WORDS * TRINITY  # 48

# KSHETRA = WORDS + HARE_COUNT = 16 + 8 = 24
# The "field" - Sankhya's 24 prakriti elements
KSHETRA: Final[int] = WORDS + HARE_COUNT  # 24

# NAVA = HARE_COUNT + KSETRAJNA = 8 + 1 = 9
# The 9 processes of devotion (Navadha Bhakti)
NAVA: Final[int] = HARE_COUNT + KSETRAJNA  # 9

# SHARANAGATI = KSHETRA // QUARTERS = 24 // 4 = 6
# The 6 limbs of surrender
SHARANAGATI: Final[int] = KSHETRA // QUARTERS  # 6

# AKSARA_COUNT = WORDS x 2 = 32 syllables
AKSARA_COUNT: Final[int] = WORDS * HALVES  # 32

# ROUNDS = WORDS (16 rounds of japa per day - minimum)
ROUNDS: Final[int] = WORDS  # 16

# AVATAR_COUNT = QUARTERS (4 Avataras head the 4 quarters)
AVATAR_COUNT: Final[int] = QUARTERS  # 4

# HEAD_POSITIONS - The positions of the 4 Avataras
HEAD_POSITIONS: Final[tuple[int, ...]] = tuple(q * (WORDS // QUARTERS) for q in range(QUARTERS))  # (0, 4, 8, 12)

# CONSECUTIVE_PAIRS = Words divided into pairs = HALF_SIZE
CONSECUTIVE_PAIRS: Final[int] = WORDS // HALVES  # 8

# PAIR_REDUNDANCY = How many pairs are duplicates = TRINITY
PAIR_REDUNDANCY: Final[int] = CONSECUTIVE_PAIRS - PANCHA  # 3


def is_head(position: int) -> bool:
    """Check if a position is a HEAD (Avatara) position."""
    return (position % WORDS) in HEAD_POSITIONS


def get_quarter_head(position: int) -> int:
    """Get the HEAD position for the Quarter containing this position."""
    quarter = (position % WORDS) // (WORDS // QUARTERS)
    return HEAD_POSITIONS[quarter]


# VERIFICATION
assert LILA == 48, "LILA must be 48"
assert KSHETRA == 24, "KSHETRA must be 24"
assert NAVA == 9, "NAVA must be 9"
assert SHARANAGATI == 6, "SHARANAGATI must be 6"
assert AKSARA_COUNT == 32, "AKSARA_COUNT must be 32"
assert HEAD_POSITIONS == (0, 4, 8, 12), "HEAD_POSITIONS must be (0, 4, 8, 12)"
assert CONSECUTIVE_PAIRS == HARE_COUNT, "8 pairs = 8 Hares"
assert PAIR_REDUNDANCY == TRINITY, "3 duplicates = 3 Names"

__all__ = [
    "QUARTERS",
    "KSETRAJNA",
    "HALF_SIZE",
    "LILA",
    "KSHETRA",
    "NAVA",
    "SHARANAGATI",
    "AKSARA_COUNT",
    "ROUNDS",
    "AVATAR_COUNT",
    "HEAD_POSITIONS",
    "CONSECUTIVE_PAIRS",
    "PAIR_REDUNDANCY",
    "is_head",
    "get_quarter_head",
]
