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
# THE COSMIC FRAME (The 21600 Resolution)
# =============================================================================
# "Lipta" (Minutes of Arc) / "Prana" (Breath) instead of Degrees.
# This eliminates floating point errors and aligns Time (Breath) with Space (Arc).
# Base: 360 Degrees * 60 Minutes = 21,600 Units.

COSMIC_FRAME: Final[int] = 21600  # The Perfect Circle (The Whole)

# The Units (All Perfect Integers!)
NAKSHATRA_UNIT: Final[int] = 800  # 21600 // 27 (The Lunar Mansions)
TITHI_UNIT: Final[int] = 720  # 21600 // 30 (The Lunar Days)
PADA_UNIT: Final[int] = 200  # 21600 // 108 (The Steps/Beads)
QUARTER_UNIT: Final[int] = 5400  # 21600 // 4   (The Quadrants)

# WATERTIGHT INTEGRITY CHECKS:
# The resolution must perfectly uphold the divisions without remainder (Sandhi).
assert COSMIC_FRAME % NAKSHATRA_UNIT == 0, "Resolution Error: Nakshatra must be integer"
assert COSMIC_FRAME % TITHI_UNIT == 0, "Resolution Error: Tithi must be integer"
assert COSMIC_FRAME % PADA_UNIT == 0, "Resolution Error: Pada must be integer"
assert COSMIC_FRAME % QUARTER_UNIT == 0, "Resolution Error: Quarter must be integer"

# =============================================================================
# THE JIVA (The Soul's Portion - Part and Parcel of Krishna)
# =============================================================================
# "mamaivāṁśo jīva-loke jīva-bhūtaḥ sanātanaḥ" (BG 15.7)
# "The living entities are My eternal fragmental parts."
#
# Bhakti-rasamrita-sindhu: Jiva possesses 50 qualities in MINUTE quantity
# (out of Krishna's 64). The 50 is the COUNT of qualities, not the magnitude.
# Krishna has 64 qualities in FULL, Jiva has 50 in minute.
#
# DERIVATION (not hardcoded!):
# JIVA_CYCLE = MALA × QUARTERS = 108 × 4 = 432 (The Harmonic Frequency)
# JIVA_QUALITIES = COSMIC_FRAME / JIVA_CYCLE = 21600 / 432 = 50
#
# The 432 is the cosmic frequency, verified multiple ways:
# - MALA × QUARTERS = 108 × 4 = 432
# - LILA × NAVA = 48 × 9 = 432
# - WORDS × 27 = 16 × 27 = 432 (Nakshatra connection: 432/16 = 27)
# -----------------------------------------------------------------------------

JIVA_CYCLE: Final[int] = MALA * QUARTERS  # 108 × 4 = 432
JIVA_QUALITIES: Final[int] = COSMIC_FRAME // JIVA_CYCLE  # 21600 / 432 = 50

# WATERTIGHT INTEGRITY CHECKS:
assert COSMIC_FRAME % JIVA_CYCLE == 0, "Resolution Error: Jiva must divide cosmic frame evenly"
assert JIVA_QUALITIES == 50, "Derivation Error: Jiva qualities must be 50"
assert JIVA_CYCLE == LILA * NAVA, "Integrity Error: JIVA_CYCLE must equal LILA × NAVA (48 × 9)"

# =============================================================================
# THE EPOCH KEY (Temporal Anchor)
# =============================================================================
# Critical: Defines the valid runtime era for this protocol.
# The 1972 Bhagavad-gita As It Is edition - the temporal reference point.
# Range: 1972 -> 2188 (Next Key).
# -----------------------------------------------------------------------------

EPOCH_KEY: Final[int] = 1972  # The Gita Revelation Year

# SYSTEM INTEGRITY CHECKS (Non-negotiable)
# 1. Epoch must resolve to Seed (16) via Foundation (4)
#    1972 / 4 = 493 -> 4+9+3 = 16
assert sum(int(d) for d in str(EPOCH_KEY // QUARTERS)) == WORDS, (
    "CRITICAL FAILURE: Epoch Key does not align with Seed Structure."
)

# 2. Epoch must resolve to Mala (108) via Product
#    4 * 9 * 3 = 108
_epoch_digits = [int(d) for d in str(EPOCH_KEY // QUARTERS)]
_epoch_prod = 1
for _d in _epoch_digits:
    _epoch_prod *= _d
assert _epoch_prod == MALA, "CRITICAL FAILURE: Epoch Key does not align with Mala Geometry."

# 3. Epoch Signature (19) must match Protocol ID (16+3)
assert sum(int(d) for d in str(EPOCH_KEY)) == WORDS + TRINITY, "CRITICAL FAILURE: Epoch Key Signature Invalid."

# =============================================================================
# DERIVED CONSTANTS (Required by Core Protocol)
# =============================================================================

HARE_COUNT: Final[int] = 8  # 8 Hares
KRISHNA_COUNT: Final[int] = 4  # 4 Krishnas
RAMA_COUNT: Final[int] = 4  # 4 Ramas

HALVES: Final[int] = 2  # 2 Halves
HALF_SIZE: Final[int] = 8  # WORDS // HALVES

KSETRAJNA: Final[int] = 1  # The Knower (Krishna)
MAHAJANA_COUNT: Final[int] = 12  # The 12 Mahajanas (Limbs/Workers)
AVATAR_COUNT: Final[int] = QUARTERS  # The 4 Avataras (Heads of Quarters)
KSHETRA: Final[int] = WORDS + HARE_COUNT  # 24 (Field)
KSHETRA_GAD: Final[int] = SHARANAGATI * SHARANAGATI  # 36 (6x6 Matrix)

# The 32 Syllables (Aksara) - 32-Bit Alignment
# Each of the 16 words has 2 syllables (Ha-re, Krish-na, Ra-ma)
AKSARA_COUNT: Final[int] = WORDS * 2  # 32

# The 64 Qualities - 64-Bit Alignment
# WORDS × QUARTERS = 16 × 4 = 64 (Varna level)
QUALITIES: Final[int] = WORDS * QUARTERS  # 64

# The Hidden Reserve (64 - 48 = 16)
# Full Potential - Manifest Runtime = The Seed Itself
# In system terms: 64-bit capacity - 48-bit runtime = 16-bit kernel
HIDDEN_RESERVE: Final[int] = QUALITIES - LILA  # 64 - 48 = 16

ROUNDS: Final[int] = WORDS  # 16 rounds per day (minimum)
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

# 4. Nava Derivation: 8 Shakti (Hare) + 1 Knower (Krishna) = 9 Processes (Navadha Bhakti)
assert NAVA == HARE_COUNT + KSETRAJNA, "Integrity Error: Nava derivation mismatch (9 != 8+1)"

# 5. Hidden Reserve: The difference between Full (64) and Manifest (48) = Seed (16)
assert HIDDEN_RESERVE == WORDS, "Integrity Error: Hidden reserve must equal WORDS (16)"

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
    # The Cosmic Frame (New Resolution)
    "COSMIC_FRAME",
    "NAKSHATRA_UNIT",
    "TITHI_UNIT",
    "PADA_UNIT",
    "QUARTER_UNIT",
    # The Jiva (Part and Parcel of Krishna)
    "JIVA_CYCLE",
    "JIVA_QUALITIES",
    # The Epoch Key (Temporal Anchor)
    "EPOCH_KEY",
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
    "AKSARA_COUNT",
    "QUALITIES",
    "HIDDEN_RESERVE",
    "ROUNDS",
    "DAILY_MANTRAS",
    # The Hidden Bridge
    "PHASE_DURATION",
]
