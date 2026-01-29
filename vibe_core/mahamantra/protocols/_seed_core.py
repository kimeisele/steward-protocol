"""
SEED CORE - The 7 Axioms + Primary Derivations (FAST IMPORT)
=============================================================

This is the MINIMAL seed - only what's needed for 99% of operations.
Import time target: <10ms (vs 245ms for full _seed.py)

For extended constants, import from _seed.py (lazy loaded).
"""

__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0xb93c4f68"

from typing import Final

# =============================================================================
# THE 7 AXIOMS (from counting the Mahamantra)
# =============================================================================

WORDS: Final[int] = 16           # 16 words
TRINITY: Final[int] = 3          # 3 unique names (Hare, Krishna, Rama)
HARE_COUNT: Final[int] = 8       # 8 "Hare"
KRISHNA_COUNT: Final[int] = 4    # 4 "Krishna"
RAMA_COUNT: Final[int] = 4       # 4 "Rama"
PANCHA: Final[int] = 5           # 5 unique pairs
HALVES: Final[int] = 2           # 2 halves

# =============================================================================
# PRIMARY DERIVATIONS (used by 99% of code)
# =============================================================================

QUARTERS: Final[int] = KRISHNA_COUNT                    # 4
KSETRAJNA: Final[int] = TRINITY - HALVES                # 1
HALF_SIZE: Final[int] = WORDS // HALVES                 # 8
LILA: Final[int] = WORDS * TRINITY                      # 48
KSHETRA: Final[int] = WORDS + HARE_COUNT                # 24
NAVA: Final[int] = HARE_COUNT + KSETRAJNA               # 9
SHARANAGATI: Final[int] = KSHETRA // QUARTERS           # 6
AKSARA_COUNT: Final[int] = WORDS * HALVES               # 32
ROUNDS: Final[int] = WORDS                              # 16
AVATAR_COUNT: Final[int] = QUARTERS                     # 4

# =============================================================================
# SECONDARY DERIVATIONS (commonly used)
# =============================================================================

SEVEN: Final[int] = SHARANAGATI + KSETRAJNA             # 7
TEN: Final[int] = NAVA + KSETRAJNA                      # 10
MAHAJANA_COUNT: Final[int] = WORDS - QUARTERS           # 12
QUALITIES: Final[int] = LILA + WORDS                    # 64
MALA: Final[int] = LILA + KSHETRA + AKSARA_COUNT + QUARTERS  # 108
MAHA_QUANTUM: Final[int] = MALA + (AKSARA_COUNT - TRINITY)   # 137
GITA_CHAPTERS: Final[int] = WORDS + HALVES              # 18

# =============================================================================
# POSITION SUMS (for Mahamantra structure)
# =============================================================================

POSITION_SUM_KRISHNA: Final[int] = 2 + 4 + 5 + 6        # 17 (Krishna positions)
POSITION_SUM_RAMA: Final[int] = 10 + 12 + 13 + 14       # 49 (Rama positions)
POSITION_SUM_TOTAL: Final[int] = (WORDS * (WORDS + 1)) // 2  # 136 = T(16)

# =============================================================================
# PARAMPARA (37 Formula)
# =============================================================================

KSETRA_COUNT: Final[int] = KSHETRA                      # 24
KSETRAJNA_COUNT: Final[int] = KSETRAJNA                 # 1
PARAMPARA: Final[int] = KSETRA_COUNT + MAHAJANA_COUNT + KSETRAJNA_COUNT  # 37

# =============================================================================
# SIKSASTAKAM CACHE (8 × 64 = 512)
# =============================================================================

SIKSASTAKAM_VERSES: Final[int] = HALF_SIZE              # 8
SIKSASTAKAM_CACHE: Final[int] = HALF_SIZE * QUALITIES   # 512

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Axioms
    "WORDS", "TRINITY", "HARE_COUNT", "KRISHNA_COUNT", "RAMA_COUNT", "PANCHA", "HALVES",
    # Primary
    "QUARTERS", "KSETRAJNA", "HALF_SIZE", "LILA", "KSHETRA", "NAVA", "SHARANAGATI",
    "AKSARA_COUNT", "ROUNDS", "AVATAR_COUNT",
    # Secondary
    "SEVEN", "TEN", "MAHAJANA_COUNT", "QUALITIES", "MALA", "MAHA_QUANTUM", "GITA_CHAPTERS",
    # Position sums
    "POSITION_SUM_KRISHNA", "POSITION_SUM_RAMA", "POSITION_SUM_TOTAL",
    # Parampara
    "KSETRA_COUNT", "KSETRAJNA_COUNT", "PARAMPARA",
    # Siksastakam
    "SIKSASTAKAM_VERSES", "SIKSASTAKAM_CACHE",
]
