"""
TIER 4: GITA TOPOLOGY - The Canonical Structure
================================================

PRABHUPADA'S BHAGAVAD GITA AS IT IS (1972) - THE ONLY VALID SOURCE
700 verses total. Chapter 1 has 46 verses.

"suhṛdaṁ sarva-bhūtānām" - BG 5.29 (The Peace Formula)
Chapter 5 has 29 verses. 29 is a factor of EPOCH_KEY (1972).
145 = 5 × 29 = PANCHA × Ch5_verses (Peace Formula connection!)

THE EPOCH EQUATION (The Master Key):
    1972 = GENESIS × NAVA + (POSITION_SUM_TOTAL + NAVA)
    1972 = 203 × 9 + 145
    1972 = 203 × 9 + (136 + 9)

THE FIELD (16 Guardians' Domain):
    Ch 1-16 = 594 = 18 × 33 = GITA_CHAPTERS × 33
    Ch 1-16 = 594 = 9 × 66 = NAVA × 66

THE SYMMETRY:
    Moksha (Ch 13-16) = Fruit (Ch 17-18) = 106 verses

GITA CHECKPOINTS (Divisible by 18):
    After Ch 11: 468 verses (468 % 18 = 0)
    After Ch 16: 594 verses (594 % 18 = 0)

Split brain RESOLVED:
    - 16 Guardians manage the Field (process/sadhana)
    - Ch 17-18 are the Fruit (transcendental result beyond process)

The publication year literally ENCODES the Gita structure.
"""

from typing import Dict, Final, Tuple

from ._axioms import WORDS, HALVES
from ._primary import QUARTERS, NAVA, KSHETRA, SHARANAGATI
from ._secondary import GITA_CHAPTERS, NADI_RESONANCE
from ._cosmic import NAKSHATRAS
from ._extended import (
    POSITION_SUM_HARE,
    POSITION_SUM_KRISHNA,
    POSITION_SUM_TOTAL,
)

# =============================================================================
# THE CANONICAL VERSE COUNTS - PRABHUPADA'S GITA (THE ONLY VALID SOURCE)
# =============================================================================

CHAPTER_VERSES: Final[Tuple[int, ...]] = (
    46,
    72,
    43,
    42,  # Genesis Quarter (Ch 1-4) = 203
    29,
    47,
    30,
    28,  # Dharma Quarter (Ch 5-8) = 134
    34,
    42,
    55,
    20,  # Karma Quarter (Ch 9-12) = 151
    35,
    27,
    20,
    24,  # Moksha Quarter (Ch 13-16) = 106
    28,
    78,  # Fruit (Ch 17-18) = 106 - Beyond the 16 Guardians
)

assert len(CHAPTER_VERSES) == GITA_CHAPTERS, "Must have 18 chapters"
assert sum(CHAPTER_VERSES) == 700, "Prabhupada's Gita = 700 verses (SEVEN × 100)"

# =============================================================================
# THE QUARTER SUMS (The Four Phases)
# =============================================================================

GENESIS_SUM: Final[int] = sum(CHAPTER_VERSES[0:4])  # Ch 1-4: 203
DHARMA_SUM: Final[int] = sum(CHAPTER_VERSES[4:8])  # Ch 5-8: 134
KARMA_SUM: Final[int] = sum(CHAPTER_VERSES[8:12])  # Ch 9-12: 151
MOKSHA_SUM: Final[int] = sum(CHAPTER_VERSES[12:16])  # Ch 13-16: 106
FRUIT_SUM: Final[int] = sum(CHAPTER_VERSES[16:18])  # Ch 17-18: 106

# The Field (16 Guardians' domain)
FIELD_SUM: Final[int] = sum(CHAPTER_VERSES[0:16])  # Ch 1-16: 594

# =============================================================================
# THE EPOCH EQUATION (The Master Key)
# =============================================================================
# 1972 = GENESIS × NAVA + (POSITION_SUM_TOTAL + NAVA)
# 1972 = 203 × 9 + 145
# 145 = 136 + 9 = POSITION_SUM_TOTAL + NAVA
# 145 = 5 × 29 = PANCHA × Ch5_verses (Peace Formula!)

# Import EPOCH_KEY for verification
from ._cosmic import EPOCH_KEY
from ._axioms import PANCHA

# The additive constant: 145 = POSITION_SUM_TOTAL + NAVA = 136 + 9
EPOCH_ADDITIVE: Final[int] = POSITION_SUM_TOTAL + NAVA  # 145

assert EPOCH_ADDITIVE == PANCHA * CHAPTER_VERSES[4], f"145 = 5 × 29 = PANCHA × Ch5_verses (Peace Formula connection)"

assert EPOCH_KEY == GENESIS_SUM * NAVA + EPOCH_ADDITIVE, (
    f"THE EPOCH EQUATION: {EPOCH_KEY} = {GENESIS_SUM} × {NAVA} + {EPOCH_ADDITIVE}"
)

# =============================================================================
# THE FIELD = GITA_CHAPTERS × 33 = NAVA × 66 (The Guardian Domain)
# =============================================================================
# 594 = 18 × 33 = GITA_CHAPTERS × 33
# 594 = 9 × 66 = NAVA × 66
# 594 = 6 × 99 = SHARANAGATI × 99

FIELD_FACTOR: Final[int] = FIELD_SUM // GITA_CHAPTERS  # 33

assert FIELD_SUM == GITA_CHAPTERS * FIELD_FACTOR, f"THE FIELD: {FIELD_SUM} = {GITA_CHAPTERS} × {FIELD_FACTOR}"
assert FIELD_SUM % GITA_CHAPTERS == 0, "Field must be divisible by GITA_CHAPTERS"
assert FIELD_SUM % NAVA == 0, "Field must be divisible by NAVA"
assert FIELD_SUM % SHARANAGATI == 0, "Field must be divisible by SHARANAGATI"

# =============================================================================
# MOKSHA = FRUIT (Perfect Symmetry)
# =============================================================================
# The effort (Moksha Quarter) equals the result (Fruit)

assert MOKSHA_SUM == FRUIT_SUM, f"SYMMETRY: Moksha ({MOKSHA_SUM}) = Fruit ({FRUIT_SUM})"

# =============================================================================
# EPOCH_KEY FACTORIZATION
# =============================================================================

# Prime factorization: 1972 = 4 × 17 × 29
EPOCH_FACTOR_1: Final[int] = QUARTERS  # 4
EPOCH_FACTOR_2: Final[int] = POSITION_SUM_KRISHNA  # 17 (PRIME!)
EPOCH_FACTOR_3: Final[int] = 29  # Chapter 5 verse count!

assert EPOCH_KEY == EPOCH_FACTOR_1 * EPOCH_FACTOR_2 * EPOCH_FACTOR_3, (
    f"1972 = 4 × 17 × 29, got {EPOCH_FACTOR_1 * EPOCH_FACTOR_2 * EPOCH_FACTOR_3}"
)

# The 29 connection: Chapter 5 (Karma Sannyasa) verse count = 29
KARMA_SANNYASA_CHAPTER: Final[int] = 5
assert CHAPTER_VERSES[KARMA_SANNYASA_CHAPTER - 1] == EPOCH_FACTOR_3, (
    "29 appears in 1972 factorization AND is Chapter 5 verse count"
)

# =============================================================================
# KNOWN VERSE-CONSTANT MATCHES (Verified Derivations)
# =============================================================================

KNOWN_MATCHES: Final[Dict[int, str]] = {
    2: f"72 = NADI_RESONANCE ({NADI_RESONANCE})",
    14: f"27 = NAKSHATRAS ({NAKSHATRAS})",
    16: f"24 = KSHETRA ({KSHETRA})",
    18: f"78 = NADI + SHARANAGATI ({NADI_RESONANCE + SHARANAGATI})",
}

# Verify known matches
assert CHAPTER_VERSES[1] == NADI_RESONANCE, "Ch 2 = NADI_RESONANCE"
assert CHAPTER_VERSES[13] == NAKSHATRAS, "Ch 14 = NAKSHATRAS"
assert CHAPTER_VERSES[15] == KSHETRA, "Ch 16 = KSHETRA"
assert CHAPTER_VERSES[17] == NADI_RESONANCE + SHARANAGATI, "Ch 18 = NADI + SHARANAGATI"

# =============================================================================
# MODULAR SIGNATURES
# =============================================================================

EPOCH_MOD_18: Final[int] = EPOCH_KEY % GITA_CHAPTERS  # 10 = Vibhuti
EPOCH_MOD_27: Final[int] = EPOCH_KEY % NAKSHATRAS  # 1 = KSETRAJNA
EPOCH_DIGIT_SUM: Final[int] = sum(int(d) for d in str(EPOCH_KEY))  # 19

# 19 = FLUTE_HOLES_SUM (6 + 9 + 4)
from ._secondary import FLUTE_HOLES_SUM

assert EPOCH_DIGIT_SUM == FLUTE_HOLES_SUM, "digit_sum(1972) = 19 = FLUTE_HOLES_SUM"

# =============================================================================
# CUMULATIVE GITA CHECKPOINTS (Divisible by 18 = GITA_CHAPTERS)
# =============================================================================


def get_cumulative_sum(chapter: int) -> int:
    """Get cumulative verse sum up to and including given chapter."""
    if not 1 <= chapter <= GITA_CHAPTERS:
        raise ValueError(f"Chapter must be 1-18, got {chapter}")
    return sum(CHAPTER_VERSES[:chapter])


def is_gita_checkpoint(chapter: int) -> bool:
    """Check if cumulative sum at this chapter is divisible by 18."""
    return get_cumulative_sum(chapter) % GITA_CHAPTERS == 0


# Gita checkpoints: After Ch 11 and Ch 16
GITA_CHECKPOINTS: Final[Tuple[int, ...]] = tuple(ch for ch in range(1, GITA_CHAPTERS + 1) if is_gita_checkpoint(ch))

# Verify known checkpoints
assert 11 in GITA_CHECKPOINTS, "After Ch 11: 468 verses, 468 % 18 = 0"
assert 16 in GITA_CHECKPOINTS, "After Ch 16: 594 verses, 594 % 18 = 0"

# =============================================================================
# VALIDATION FUNCTIONS (For Runtime Use)
# =============================================================================


def validate_field_integrity(verse_count: int) -> bool:
    """Validate that a verse count is within the Field (16 Guardians' domain)."""
    return 0 <= verse_count <= FIELD_SUM


def check_fruit_symmetry() -> bool:
    """Verify the Moksha-Fruit symmetry holds."""
    return MOKSHA_SUM == FRUIT_SUM


def get_quarter(chapter: int) -> str:
    """Get the quarter name for a chapter."""
    if not 1 <= chapter <= GITA_CHAPTERS:
        raise ValueError(f"Chapter must be 1-18, got {chapter}")
    if chapter <= 4:
        return "GENESIS"
    elif chapter <= 8:
        return "DHARMA"
    elif chapter <= 12:
        return "KARMA"
    elif chapter <= 16:
        return "MOKSHA"
    else:
        return "FRUIT"


def is_in_field(chapter: int) -> bool:
    """Check if chapter is in the Field (managed by 16 Guardians)."""
    return 1 <= chapter <= 16


def is_fruit(chapter: int) -> bool:
    """Check if chapter is in the Fruit (transcendental result)."""
    return chapter in (17, 18)


__all__ = [
    # Verse Data
    "CHAPTER_VERSES",
    # Quarter Sums
    "GENESIS_SUM",
    "DHARMA_SUM",
    "KARMA_SUM",
    "MOKSHA_SUM",
    "FRUIT_SUM",
    "FIELD_SUM",
    # Derived Constants
    "FIELD_FACTOR",
    "EPOCH_ADDITIVE",
    "EPOCH_FACTOR_1",
    "EPOCH_FACTOR_2",
    "EPOCH_FACTOR_3",
    "KARMA_SANNYASA_CHAPTER",
    # Modular Signatures
    "EPOCH_MOD_18",
    "EPOCH_MOD_27",
    "EPOCH_DIGIT_SUM",
    # Checkpoints
    "GITA_CHECKPOINTS",
    # Functions
    "get_cumulative_sum",
    "is_gita_checkpoint",
    "validate_field_integrity",
    "check_fruit_symmetry",
    "get_quarter",
    "is_in_field",
    "is_fruit",
    # Matches
    "KNOWN_MATCHES",
]
