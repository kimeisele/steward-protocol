"""
THE SEED PROTOCOL - The Mathematical Constitution
=================================================

"bījaṁ māṁ sarva-bhūtānāṁ viddhi pārtha sanātanam"
"O Arjuna, know that I am the eternal seed of all existences."
— Bhagavad Gita 7.10

This protocol defines the INVARIANTS of the Mahamantra.
Any implementation of the Seed MUST adhere to these constants.

LOCATION: vibe_core.mahamantra.protocols._seed (THE LAW)
IMPLEMENTATION: vibe_core.mahamantra.substrate.seed (THE REALITY)

This file is the SINGLE SOURCE OF TRUTH for the sacred numbers.
The implementation imports from here to manifest the reality.
"""

from typing import Final

# =============================================================================
# THE SACRED CONSTANTS (The Invariants)
# =============================================================================

# The 16 words of the Mahamantra
# THE ATOMIC STEP (0.0625)
# 1 / 16 = 0.0625
# Bhagavad Gita 6.25: "sanaih sanaih" (step by step)
# This is the harmonic frequency of focus (Dharana).
WORDS: Final[int] = 16

# The 37 Formula (24 Kshetra + 12 Mahajanas + 1 Knower)
PARAMPARA: Final[int] = 37

# The 3 Names (Hare, Krishna, Rama)
TRINITY: Final[int] = 3

# The 4 Quarters (Genesis, Dharma, Karma, Moksha)
QUARTERS: Final[int] = 4

# The 5 Pairs (Pancha Tattva)
PANCHA: Final[int] = 5

# The 6 Limbs (Sharanagati)
SHARANAGATI: Final[int] = 6

# The 9 Islands (Navadvipa) & 9 Processes (Navadha Bhakti)
NAVA: Final[int] = 9

# The 48 Lila (16 * 3)
LILA: Final[int] = 48

# The 108 Mala (12 * 9)
MALA: Final[int] = 108

# =============================================================================
# DERIVED CONSTANTS (Required by Core Protocol)
# =============================================================================

HARE_COUNT: Final[int] = 8       # 8 Hares
KRISHNA_COUNT: Final[int] = 4    # 4 Krishnas
RAMA_COUNT: Final[int] = 4       # 4 Ramas

HALVES: Final[int] = 2           # 2 Halves
HALF_SIZE: Final[int] = 8        # WORDS // HALVES

KSETRAJNA: Final[int] = 1        # The Knower (Krishna)
MAHAJANA_COUNT: Final[int] = 12  # The 12 Mahajanas (Limbs/Workers)
AVATAR_COUNT: Final[int] = QUARTERS  # The 4 Avataras (Heads of Quarters)
KSHETRA: Final[int] = WORDS + HARE_COUNT  # 24 (Field)
KSHETRA_GAD: Final[int] = SHARANAGATI * SHARANAGATI  # 36 (6x6 Matrix)

ROUNDS: Final[int] = WORDS       # 16 rounds per day (minimum)
DAILY_MANTRAS: Final[int] = MALA * ROUNDS  # 1728 mantras minimum

# Verification of the 37 Formula
assert KSHETRA + MAHAJANA_COUNT + KSETRAJNA == PARAMPARA, "37 Formula Check Failed"

# =============================================================================
# THE HIDDEN BRIDGE (Dvadasa - The 12)
# =============================================================================
# Time (Lila phases) = Space (Mahajana authorities)
# The 12 is the common denominator between Time, Space, and Work.

# Phase duration derived from Lila structure (NOT hardcoded)
PHASE_DURATION: Final[int] = LILA // QUARTERS  # 48 / 4 = 12

# WATERTIGHT INTEGRITY CHECKS:
# 1. Holographic Principle: Time matches Authority
assert PHASE_DURATION == MAHAJANA_COUNT, "Integrity Error: Time/Person mismatch (12 != 12)"

# 2. Geometry of the Mala: 12 Guardians * 9 Islands = 108 Beads
assert MALA == MAHAJANA_COUNT * NAVA, "Integrity Error: Mala geometry mismatch (108 != 12*9)"

# 3. Guardian Completeness: 4 Avatars + 12 Mahajanas = 16 Words
assert AVATAR_COUNT + MAHAJANA_COUNT == WORDS, "Guardian count mismatch (4+12 != 16)"

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Sacred Constants
    "WORDS",
    "PARAMPARA",
    "TRINITY",
    "QUARTERS",
    "PANCHA",
    "SHARANAGATI",
    "NAVA",
    "LILA",
    "MALA",
    # Derived Constants
    "HARE_COUNT",
    "KRISHNA_COUNT",
    "RAMA_COUNT",
    "HALVES",
    "HALF_SIZE",
    "KSETRAJNA",
    "MAHAJANA_COUNT",
    "AVATAR_COUNT",
    "KSHETRA",
    "KSHETRA_GAD",
    "ROUNDS",
    "DAILY_MANTRAS",
    # The Hidden Bridge
    "PHASE_DURATION",
]
