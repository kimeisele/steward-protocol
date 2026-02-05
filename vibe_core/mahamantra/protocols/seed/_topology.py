"""
TIER 4: GITA TOPOLOGY - The Canonical Structure
================================================

"suhṛdaṁ sarva-bhūtānām" - BG 5.29 (The Peace Formula)
Chapter 5 has 29 verses. 29 is a factor of EPOCH_KEY (1972).

THE EPOCH EQUATION (The Master Key):
    1972 = GENESIS × NAVA + FIXED_POINT
    1972 = 204 × 9 + 136

THE FIELD (16 Guardians' Domain):
    Ch 1-16 = 595 = 35 × 17 = 35 × POSITION_SUM_KRISHNA

THE SYMMETRY:
    Moksha (Ch 13-16) = Fruit (Ch 17-18) = 106 verses

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
# THE CANONICAL VERSE COUNTS (Currently hardcoded - to be derived)
# =============================================================================

# NOTE: Two textual traditions exist:
# - Prabhupada edition: Ch 1 = 46 verses, Total = 700
# - Mathematical tradition: Ch 1 = 47 verses, Total = 701
#
# The Epoch Equation (1972 = 204 × 9 + 136) requires the 47-verse tradition.
# This is the tradition where BG 1.1 (Dhritarashtra uvaca) counts as verse 1.

CHAPTER_VERSES: Final[Tuple[int, ...]] = (
    47, 72, 43, 42,  # Genesis Quarter (Ch 1-4) = 204
    29, 47, 30, 28,  # Dharma Quarter (Ch 5-8) = 134
    34, 42, 55, 20,  # Karma Quarter (Ch 9-12) = 151
    35, 27, 20, 24,  # Moksha Quarter (Ch 13-16) = 106
    28, 78,          # Fruit (Ch 17-18) = 106 - Beyond the 16 Guardians
)

# Prabhupada edition counts (for reference)
CHAPTER_VERSES_PRABHUPADA: Final[Tuple[int, ...]] = (
    46, 72, 43, 42, 29, 47, 30, 28, 34, 42, 55, 20, 35, 27, 20, 24, 28, 78
)

assert len(CHAPTER_VERSES) == GITA_CHAPTERS, "Must have 18 chapters"
assert sum(CHAPTER_VERSES) == 701, "Total verses = 701 (mathematical tradition)"
assert sum(CHAPTER_VERSES_PRABHUPADA) == 700, "Prabhupada edition = 700 verses"

# =============================================================================
# THE QUARTER SUMS (The Four Phases)
# =============================================================================

GENESIS_SUM: Final[int] = sum(CHAPTER_VERSES[0:4])   # Ch 1-4: 204
DHARMA_SUM: Final[int] = sum(CHAPTER_VERSES[4:8])    # Ch 5-8: 134
KARMA_SUM: Final[int] = sum(CHAPTER_VERSES[8:12])    # Ch 9-12: 151
MOKSHA_SUM: Final[int] = sum(CHAPTER_VERSES[12:16])  # Ch 13-16: 106
FRUIT_SUM: Final[int] = sum(CHAPTER_VERSES[16:18])   # Ch 17-18: 106

# The Field (16 Guardians' domain)
FIELD_SUM: Final[int] = sum(CHAPTER_VERSES[0:16])    # Ch 1-16: 595

# =============================================================================
# THE EPOCH EQUATION (The Master Key)
# =============================================================================
# 1972 = GENESIS × NAVA + FIXED_POINT
# 1972 = 204 × 9 + 136

# Import EPOCH_KEY for verification
from ._cosmic import EPOCH_KEY

assert EPOCH_KEY == GENESIS_SUM * NAVA + POSITION_SUM_TOTAL, (
    f"THE EPOCH EQUATION: {EPOCH_KEY} = {GENESIS_SUM} × {NAVA} + {POSITION_SUM_TOTAL}"
)

# =============================================================================
# THE FIELD = 35 × KRISHNA (The Guardian Domain)
# =============================================================================
# 595 = 35 × 17 = 35 × POSITION_SUM_KRISHNA

KRISHNA_UNITS: Final[int] = FIELD_SUM // POSITION_SUM_KRISHNA  # 35

assert FIELD_SUM == KRISHNA_UNITS * POSITION_SUM_KRISHNA, (
    f"THE FIELD: {FIELD_SUM} = {KRISHNA_UNITS} × {POSITION_SUM_KRISHNA}"
)
assert FIELD_SUM % POSITION_SUM_KRISHNA == 0, "Field must be divisible by Krishna"

# =============================================================================
# MOKSHA = FRUIT (Perfect Symmetry)
# =============================================================================
# The effort (Moksha Quarter) equals the result (Fruit)

assert MOKSHA_SUM == FRUIT_SUM, f"SYMMETRY: Moksha ({MOKSHA_SUM}) = Fruit ({FRUIT_SUM})"

# =============================================================================
# EPOCH_KEY FACTORIZATION
# =============================================================================

# Prime factorization: 1972 = 4 × 17 × 29
EPOCH_FACTOR_1: Final[int] = QUARTERS              # 4
EPOCH_FACTOR_2: Final[int] = POSITION_SUM_KRISHNA  # 17 (PRIME!)
EPOCH_FACTOR_3: Final[int] = 29                    # Chapter 5 verse count!

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
EPOCH_MOD_27: Final[int] = EPOCH_KEY % NAKSHATRAS     # 1 = KSETRAJNA
EPOCH_DIGIT_SUM: Final[int] = sum(int(d) for d in str(EPOCH_KEY))  # 19

# 19 = FLUTE_HOLES_SUM (6 + 9 + 4)
from ._secondary import FLUTE_HOLES_SUM
assert EPOCH_DIGIT_SUM == FLUTE_HOLES_SUM, "digit_sum(1972) = 19 = FLUTE_HOLES_SUM"

# =============================================================================
# CUMULATIVE KRISHNA CHECKPOINTS (Divisible by 17)
# =============================================================================

def get_cumulative_sum(chapter: int) -> int:
    """Get cumulative verse sum up to and including given chapter."""
    if not 1 <= chapter <= GITA_CHAPTERS:
        raise ValueError(f"Chapter must be 1-18, got {chapter}")
    return sum(CHAPTER_VERSES[:chapter])


def is_krishna_checkpoint(chapter: int) -> bool:
    """Check if cumulative sum at this chapter is divisible by 17."""
    return get_cumulative_sum(chapter) % POSITION_SUM_KRISHNA == 0


# Krishna checkpoints: After Ch 2, 4, 16
KRISHNA_CHECKPOINTS: Final[Tuple[int, ...]] = tuple(
    ch for ch in range(1, GITA_CHAPTERS + 1) if is_krishna_checkpoint(ch)
)

# Verify known checkpoints
assert 2 in KRISHNA_CHECKPOINTS, "After Ch 2: 119 verses, 119 % 17 = 0"
assert 4 in KRISHNA_CHECKPOINTS, "After Ch 4: 204 verses, 204 % 17 = 0"
assert 16 in KRISHNA_CHECKPOINTS, "After Ch 16: 595 verses, 595 % 17 = 0"

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
    "KRISHNA_UNITS",
    "EPOCH_FACTOR_1",
    "EPOCH_FACTOR_2",
    "EPOCH_FACTOR_3",
    "KARMA_SANNYASA_CHAPTER",
    # Modular Signatures
    "EPOCH_MOD_18",
    "EPOCH_MOD_27",
    "EPOCH_DIGIT_SUM",
    # Checkpoints
    "KRISHNA_CHECKPOINTS",
    # Functions
    "get_cumulative_sum",
    "is_krishna_checkpoint",
    "validate_field_integrity",
    "check_fruit_symmetry",
    "get_quarter",
    "is_in_field",
    "is_fruit",
    # Matches
    "KNOWN_MATCHES",
]
