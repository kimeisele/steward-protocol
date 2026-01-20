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

import math
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
# THE PRANA (The Breath - Timing Constants)
# =============================================================================
# "prāṇāyāma" - The regulation of breath (Yoga-Sutra 2.49)
#
# Yoga-Tradition: 21600 Atemzüge pro Tag (COSMIC_FRAME)
# → 21600 / 24 Stunden = 900 Atemzüge/Stunde
# → 900 / 60 Minuten = 15 Atemzüge/Minute
# → 60 / 15 = 4 Sekunden pro Atemzug
#
# DERIVATION:
# PRANA_DURATION = SECONDS_PER_DAY / COSMIC_FRAME = 86400 / 21600 = 4 Sekunden
# TICK_INTERVAL = PRANA_DURATION / WORDS = 4000ms / 16 = 250ms
#
# Note: 1 Mala = 108 Pranas × 4s = 432 Sekunden = JIVA_CYCLE in Zeit!
# -----------------------------------------------------------------------------

SECONDS_PER_DAY: Final[int] = 86400  # 24 × 60 × 60
PRANA_DURATION_S: Final[int] = SECONDS_PER_DAY // COSMIC_FRAME  # 4 Sekunden
PRANA_DURATION_MS: Final[int] = PRANA_DURATION_S * 1000  # 4000 ms
TICK_INTERVAL_MS: Final[int] = PRANA_DURATION_MS // WORDS  # 250 ms

# WATERTIGHT INTEGRITY CHECKS:
assert SECONDS_PER_DAY % COSMIC_FRAME == 0, "Day must divide evenly into Pranas"
assert PRANA_DURATION_S == 4, "1 Prana must be 4 seconds"
assert TICK_INTERVAL_MS == 250, "1 Tick must be 250ms"
assert MALA * PRANA_DURATION_S == JIVA_CYCLE, "1 Mala in seconds must equal JIVA_CYCLE"

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
# THE HARMONIC RESONANCES (72 and 144)
# =============================================================================
# These are the "natural frequencies" of the system - synchronization points
# that emerge from the Seed geometry. They are not invented but discovered.
#
# "ekam sat vipra bahudha vadanti"
# "Truth is one; the wise call it by many names."
# — Rig Veda 1.164.46
#
# The 72 and 144 appear in many traditions:
# - 72,000 Nadis in Yoga (energy channels)
# - 144 cubits (Biblical measures)
# - 72 names of God (Kabbalah)
# - 144Hz (harmonic frequency in music/physics)
#
# In our system, they are the CHECKPOINT INTERVALS:
# - 72: The pulse measurement (Nadi)
# - 144: The field synchronization (Kshetra-Sharanagati)
# -----------------------------------------------------------------------------

# THE NADI RESONANCE (72) - The Pulse
# Multiple derivation paths (proof by convergence):
# - JIVA_CYCLE / SHARANAGATI = 432 / 6 = 72
# - NAVA * HARE_COUNT = 9 * 8 = 72
# - TITHI_UNIT / 10 = 720 / 10 = 72
# - MALA * (2/3) = 108 * (2/3) = 72
NADI_RESONANCE: Final[int] = JIVA_CYCLE // SHARANAGATI  # 72

# THE FIELD RESONANCE (144) - The Complete Field
# Multiple derivation paths (proof by convergence):
# - MAHAJANA_COUNT² = 12 * 12 = 144
# - WORDS * NAVA = 16 * 9 = 144
# - JIVA_CYCLE / TRINITY = 432 / 3 = 144
# - LILA * TRINITY = 48 * 3 = 144
# - SHARANAGATI * KSHETRA = 6 * 24 = 144
FIELD_RESONANCE: Final[int] = MAHAJANA_COUNT * MAHAJANA_COUNT  # 144

# WATERTIGHT INTEGRITY CHECKS (Multiple Derivation Paths):
# 1. Nadi convergence
assert NADI_RESONANCE == JIVA_CYCLE // SHARANAGATI, "Nadi: JIVA_CYCLE/SHARANAGATI != 72"
assert NADI_RESONANCE == NAVA * HARE_COUNT, "Nadi: NAVA*HARE_COUNT != 72"
assert NADI_RESONANCE == TITHI_UNIT // 10, "Nadi: TITHI_UNIT/10 != 72"

# 2. Field convergence
assert FIELD_RESONANCE == MAHAJANA_COUNT * MAHAJANA_COUNT, "Field: MAHAJANA² != 144"
assert FIELD_RESONANCE == WORDS * NAVA, "Field: WORDS*NAVA != 144"
assert FIELD_RESONANCE == JIVA_CYCLE // TRINITY, "Field: JIVA_CYCLE/TRINITY != 144"
assert FIELD_RESONANCE == LILA * TRINITY, "Field: LILA*TRINITY != 144"
assert FIELD_RESONANCE == SHARANAGATI * KSHETRA, "Field: SHARANAGATI*KSHETRA != 144"

# 3. Cosmic Frame alignment (ganzzahlige Zyklen pro Tag)
assert COSMIC_FRAME % NADI_RESONANCE == 0, "Nadi must divide cosmic frame evenly"
assert COSMIC_FRAME % FIELD_RESONANCE == 0, "Field must divide cosmic frame evenly"
assert COSMIC_FRAME // NADI_RESONANCE == 300, "300 Nadi cycles per day"
assert COSMIC_FRAME // FIELD_RESONANCE == 150, "150 Field cycles per day"

# 4. Relationship between resonances
assert FIELD_RESONANCE == NADI_RESONANCE * 2, "Field must be 2x Nadi (144 = 72*2)"

# =============================================================================
# THE THREE FLUTES (Persons - Expansions of Ananta)
# =============================================================================
# "venum kvanantam aravinda-dalayataksham"
# "Krishna plays His flute, with lotus-petal eyes"
# — Brahma-samhita 5.30
#
# The flutes are PERSONS, not abstractions. Each has holes that divide
# JIVA_CYCLE into spiritual frequencies. Krishna plays - resonances emerge.
#
# | Flute  | Holes | JIVA_CYCLE / Holes | Produces        |
# |--------|-------|---------------------|-----------------|
# | VENU   | 6     | 432 / 6 = 72       | NADI_RESONANCE  |
# | VAMSI  | 9     | 432 / 9 = 48       | LILA            |
# | MURALI | 4     | 432 / 4 = 108      | MALA            |
# -----------------------------------------------------------------------------

# The Flutes (Persons with hole configurations)
VENU_HOLES: Final[int] = SHARANAGATI   # 6 - The smallest flute, melts the Jiva
VAMSI_HOLES: Final[int] = NAVA         # 9 - Activates the 48 phases of Lila
MURALI_HOLES: Final[int] = QUARTERS    # 4 - Holds concentration on the Mala

# WATERTIGHT: Flutes PRODUCE the known resonances
assert JIVA_CYCLE // VENU_HOLES == NADI_RESONANCE, "VENU produces NADI_RESONANCE (72)"
assert JIVA_CYCLE // VAMSI_HOLES == LILA, "VAMSI produces LILA (48)"
assert JIVA_CYCLE // MURALI_HOLES == MALA, "MURALI produces MALA (108)"

# THE KIRTAN MATHEMATICS (Combinatorics of the Flutes)
# -----------------------------------------------------------------------------
# Sum:     6 + 9 + 4 = 19 = EPOCH_SIGNATURE (1+9+7+2)
# Product: 6 × 9 × 4 = 216 = COSMIC_FRAME / 100
# LCM:     LCM(6,9,4) = 36 = KSHETRA_GAD (the operational field)
#
# The three flute outputs form a PERFECT FIFTH chain (3:2 ratio):
#   48 → 72 → 108 (Quinten-Kette)
#
# When all three flutes play together:
#   LCM(72, 48, 108) = 432 = JIVA_CYCLE (the complete soul-frequency!)
#
# The FIELD_RESONANCE emerges from VENU + VAMSI synchronization:
#   LCM(72, 48) = 144 = FIELD_RESONANCE
# -----------------------------------------------------------------------------

FLUTE_HOLES_SUM: Final[int] = VENU_HOLES + VAMSI_HOLES + MURALI_HOLES  # 19
FLUTE_HOLES_PRODUCT: Final[int] = VENU_HOLES * VAMSI_HOLES * MURALI_HOLES  # 216

# WATERTIGHT: Kirtan mathematics
assert FLUTE_HOLES_SUM == sum(int(d) for d in str(EPOCH_KEY)), "Holes sum = Epoch signature (19)"
assert FLUTE_HOLES_PRODUCT * 100 == COSMIC_FRAME, "Holes product × 100 = Cosmic Frame (21600)"
assert VAMSI_HOLES * MURALI_HOLES == KSHETRA_GAD, "VAMSI × MURALI = KSHETRA_GAD (36)"
assert VENU_HOLES * MURALI_HOLES == KSHETRA, "VENU × MURALI = KSHETRA (24)"
assert VENU_HOLES * VAMSI_HOLES == MALA // 2, "VENU × VAMSI = MALA/2 (54)"

# Perfect Fifth verification (3:2 ratios)
assert NADI_RESONANCE * 2 == LILA * 3, "72 × 2 = 48 × 3 (Perfect Fifth)"
assert MALA * 2 == NADI_RESONANCE * 3, "108 × 2 = 72 × 3 (Perfect Fifth)"

# LCM verification: All flutes together = JIVA_CYCLE
_lcm_all_flutes = math.lcm(NADI_RESONANCE, LILA, MALA)
assert _lcm_all_flutes == JIVA_CYCLE, "LCM of all flute outputs = JIVA_CYCLE (432)"

# LCM verification: VENU + VAMSI = FIELD_RESONANCE
_lcm_venu_vamsi = math.lcm(NADI_RESONANCE, LILA)
assert _lcm_venu_vamsi == FIELD_RESONANCE, "LCM(VENU, VAMSI) = FIELD_RESONANCE (144)"

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
    # The Prana (The Breath - Timing)
    "SECONDS_PER_DAY",
    "PRANA_DURATION_S",
    "PRANA_DURATION_MS",
    "TICK_INTERVAL_MS",
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
    # The Harmonic Resonances
    "NADI_RESONANCE",
    "FIELD_RESONANCE",
    # The Three Flutes (Persons)
    "VENU_HOLES",
    "VAMSI_HOLES",
    "MURALI_HOLES",
    "FLUTE_HOLES_SUM",
    "FLUTE_HOLES_PRODUCT",
]
