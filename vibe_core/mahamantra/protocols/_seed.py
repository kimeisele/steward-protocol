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

DERIVATION PRINCIPLE:
=====================
ALL constants (except the 7 Mantra Axioms) are DERIVED, not hardcoded.
The Mahamantra IS the source. Everything flows from counting its words.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0xb93c4f68"  # GenesisByte: parampara % 37 == 0

import math
from typing import Final

# =============================================================================
# RUNDE 0: THE MANTRA AXIOMS (The Only Hardcoded Values - From Counting)
# =============================================================================
# These are the ONLY values that come from directly observing the Mahamantra.
# Everything else is DERIVED from these 7 axioms.
#
# The Mahamantra:
#   Hare Krishna Hare Krishna Krishna Krishna Hare Hare
#   Hare Rama   Hare Rama   Rama   Rama   Hare Hare
# -----------------------------------------------------------------------------

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

# =============================================================================
# RUNDE 1: PRIMARY DERIVATIONS (Direct from Axioms)
# =============================================================================

# QUARTERS = KRISHNA_COUNT (Krishna appears 4 times = 4 quadrants)
# This is the theological link: Krishna's 4 appearances structure the 4 phases.
QUARTERS: Final[int] = KRISHNA_COUNT  # 4

# KSETRAJNA = TRINITY - HALVES = 3 - 2 = 1 (DERIVED!)
# "kṣetra-jñaṁ cāpi māṁ viddhi" (BG 13.3) - "Know Me as the Knower"
# The ONE Knower emerges from 3 Names minus 2 Halves
KSETRAJNA: Final[int] = TRINITY - HALVES  # 1

# HALF_SIZE = Words per half
HALF_SIZE: Final[int] = WORDS // HALVES  # 8

# LILA = WORDS × TRINITY = 16 × 3 = 48
# The "play" of Krishna - manifest runtime
LILA: Final[int] = WORDS * TRINITY  # 48

# KSHETRA = WORDS + HARE_COUNT = 16 + 8 = 24
# The "field" - Sankhya's 24 prakriti elements
# Also matches: BG 13 describes 24 elements of the field
KSHETRA: Final[int] = WORDS + HARE_COUNT  # 24

# NAVA = HARE_COUNT + KSETRAJNA = 8 + 1 = 9
# The 9 processes of devotion (Navadha Bhakti)
# 8 Shaktis (Hare/energy) + 1 Knower (Krishna) = 9
NAVA: Final[int] = HARE_COUNT + KSETRAJNA  # 9

# SHARANAGATI = KSHETRA // QUARTERS = 24 // 4 = 6
# The 6 limbs of surrender (Bhakti-rasamrta-sindhu 1.2.234)
# ACINTYA: The Mahamantra encodes this naturally!
SHARANAGATI: Final[int] = KSHETRA // QUARTERS  # 6

# AKSARA_COUNT = WORDS × 2 = 32 syllables (Ha-re, Krish-na, Ra-ma each have 2)
AKSARA_COUNT: Final[int] = WORDS * HALVES  # 32

# ROUNDS = WORDS (16 rounds of japa per day - minimum)
ROUNDS: Final[int] = WORDS  # 16

# AVATAR_COUNT = QUARTERS (4 Avataras head the 4 quarters)
AVATAR_COUNT: Final[int] = QUARTERS  # 4

# VERIFICATION: Primary derivations
assert LILA == 48, "LILA must be 48"
assert KSHETRA == 24, "KSHETRA must be 24"
assert NAVA == 9, "NAVA must be 9"
assert SHARANAGATI == 6, "SHARANAGATI must be 6"
assert AKSARA_COUNT == 32, "AKSARA_COUNT must be 32"

# =============================================================================
# RUNDE 2: SECONDARY DERIVATIONS (Building the Hierarchy)
# =============================================================================

# MAHAJANA_COUNT = KSHETRA // HALVES = 24 // 2 = 12
# The 12 Mahajanas (great authorities) - DERIVED, not hardcoded!
# Also = PHASE_DURATION (holographic principle: time = authority)
MAHAJANA_COUNT: Final[int] = KSHETRA // HALVES  # 12

# MALA = MAHAJANA_COUNT × NAVA = 12 × 9 = 108
# The 108 beads of the japa mala
# Alternative derivation: LILA × NAVA // QUARTERS = 48 × 9 // 4 = 108
MALA: Final[int] = MAHAJANA_COUNT * NAVA  # 108

# JIVA_CYCLE = MALA × QUARTERS = 108 × 4 = 432
# The soul's harmonic frequency
# Alternative derivations:
#   - LILA × NAVA = 48 × 9 = 432
#   - WORDS × NAKSHATRAS = 16 × 27 = 432 (proven below)
JIVA_CYCLE: Final[int] = MALA * QUARTERS  # 432

# GITA_CHAPTERS = SHARANAGATI × TRINITY = 6 × 3 = 18
# The Bhagavad Gita has 18 chapters - DERIVED!
# Also: Kurukshetra battle lasted 18 days
GITA_CHAPTERS: Final[int] = SHARANAGATI * TRINITY  # 18

# QUALITIES = WORDS × QUARTERS = 16 × 4 = 64
# Krishna's 64 qualities (full capacity)
QUALITIES: Final[int] = WORDS * QUARTERS  # 64

# HIDDEN_RESERVE = QUALITIES - LILA = 64 - 48 = 16 = WORDS
# The difference between full capacity and manifest runtime = the Seed itself!
HIDDEN_RESERVE: Final[int] = QUALITIES - LILA  # 16

# DAILY_MANTRAS = MALA × ROUNDS = 108 × 16 = 1728
DAILY_MANTRAS: Final[int] = MALA * ROUNDS  # 1728

# PHASE_DURATION = LILA // QUARTERS = 48 // 4 = 12
# Must equal MAHAJANA_COUNT (holographic principle)
PHASE_DURATION: Final[int] = LILA // QUARTERS  # 12

# VERIFICATION: Secondary derivations
assert MAHAJANA_COUNT == 12, "MAHAJANA_COUNT must be 12"
assert MALA == 108, "MALA must be 108"
assert JIVA_CYCLE == 432, "JIVA_CYCLE must be 432"
assert GITA_CHAPTERS == 18, "GITA_CHAPTERS must be 18"
assert HIDDEN_RESERVE == WORDS, "HIDDEN_RESERVE must equal WORDS (16)"
assert PHASE_DURATION == MAHAJANA_COUNT, "Time/Person holographic principle"
assert JIVA_CYCLE == LILA * NAVA, "JIVA_CYCLE must equal LILA × NAVA (48 × 9)"

# =============================================================================
# RUNDE 3: THE NAKSHATRAS (The Astronomical Bridge)
# =============================================================================
# NAKSHATRAS = JIVA_CYCLE // WORDS = 432 // 16 = 27
# The 27 lunar mansions - DERIVED from the Mahamantra!
#
# External validation: Sidereal month ≈ 27.32 days
# The Mahamantra encodes the lunar cycle. This is not hardcoded - it emerges.
# -----------------------------------------------------------------------------

NAKSHATRAS: Final[int] = JIVA_CYCLE // WORDS  # 27

# VERIFICATION: Nakshatras
assert NAKSHATRAS == 27, "NAKSHATRAS must be 27"
assert JIVA_CYCLE == WORDS * NAKSHATRAS, "JIVA_CYCLE = WORDS × NAKSHATRAS"

# =============================================================================
# RUNDE 4: THE COSMIC FRAME (The Universal Resolution)
# =============================================================================
# COSMIC_FRAME = AKSARA_COUNT × NAKSHATRAS × PANCHA² = 32 × 27 × 25 = 21600
#
# This is the resolution at which ALL Seed constants divide evenly.
# External validation: 360° × 60' = 21600 arc-minutes (geometry)
# External validation: 15 breaths/min × 60 × 24 = 21600 (physiology)
#
# THE COSMIC FRAME IS DERIVED FROM THE MAHAMANTRA, NOT HARDCODED!
# -----------------------------------------------------------------------------

COSMIC_FRAME: Final[int] = AKSARA_COUNT * NAKSHATRAS * (PANCHA**2)  # 21600

# VERIFICATION: Cosmic Frame
assert COSMIC_FRAME == 21600, "COSMIC_FRAME must be 21600"
assert COSMIC_FRAME == 360 * 60, "COSMIC_FRAME equals arc-minutes in circle"

# The Units (All Perfect Integers - Zero Remainder)
NAKSHATRA_UNIT: Final[int] = COSMIC_FRAME // NAKSHATRAS  # 800
TITHI_UNIT: Final[int] = COSMIC_FRAME // 30  # 720 (30 Tithis per month)
PADA_UNIT: Final[int] = COSMIC_FRAME // MALA  # 200
QUARTER_UNIT: Final[int] = COSMIC_FRAME // QUARTERS  # 5400

# VERIFICATION: All divisions are clean
assert COSMIC_FRAME % NAKSHATRA_UNIT == 0, "Nakshatra must divide evenly"
assert COSMIC_FRAME % TITHI_UNIT == 0, "Tithi must divide evenly"
assert COSMIC_FRAME % PADA_UNIT == 0, "Pada must divide evenly"
assert COSMIC_FRAME % QUARTER_UNIT == 0, "Quarter must divide evenly"
assert COSMIC_FRAME % JIVA_CYCLE == 0, "Jiva must divide evenly"

# =============================================================================
# RUNDE 5: THE JIVA QUALITIES (Part and Parcel of Krishna)
# =============================================================================
# "mamaivāṁśo jīva-loke jīva-bhūtaḥ sanātanaḥ" (BG 15.7)
# JIVA_QUALITIES = COSMIC_FRAME // JIVA_CYCLE = 21600 // 432 = 50
#
# Bhakti-rasamrita-sindhu: Jiva has 50 qualities (in minute quantity)
# out of Krishna's 64. This is DERIVED, not hardcoded!
# -----------------------------------------------------------------------------

JIVA_QUALITIES: Final[int] = COSMIC_FRAME // JIVA_CYCLE  # 50

# VERIFICATION: Jiva Qualities matches shastra
assert JIVA_QUALITIES == 50, "JIVA_QUALITIES must be 50"

# =============================================================================
# RUNDE 6: THE PRANA (Breath - Timing Constants)
# =============================================================================
# SECONDS_PER_DAY = 24 × 60 × 60 = 86400 (external physical constant)
# PRANA_DURATION = SECONDS_PER_DAY // COSMIC_FRAME = 86400 // 21600 = 4 seconds
#
# External validation: 15 breaths/minute is the medical average
# 86400 / 21600 = 4 seconds per breath → 15 breaths per minute
# -----------------------------------------------------------------------------

SECONDS_PER_DAY: Final[int] = 86400  # 24 × 60 × 60 (external: physics)
PRANA_DURATION_S: Final[int] = SECONDS_PER_DAY // COSMIC_FRAME  # 4 seconds
PRANA_DURATION_MS: Final[int] = PRANA_DURATION_S * 1000  # 4000 ms
TICK_INTERVAL_MS: Final[int] = PRANA_DURATION_MS // WORDS  # 250 ms

# VERIFICATION: Timing
assert PRANA_DURATION_S == 4, "1 Prana must be 4 seconds"
assert TICK_INTERVAL_MS == 250, "1 Tick must be 250ms"
assert MALA * PRANA_DURATION_S == JIVA_CYCLE, "1 Mala in seconds = JIVA_CYCLE"

# =============================================================================
# RUNDE 7: THE PARAMPARA (The 37 Formula)
# =============================================================================
# PARAMPARA = KSHETRA + MAHAJANA_COUNT + KSETRAJNA = 24 + 12 + 1 = 37
# Field + Workers + Knower = Tradition
#
# This is DERIVED from the Mahamantra structure!
# -----------------------------------------------------------------------------

PARAMPARA: Final[int] = KSHETRA + MAHAJANA_COUNT + KSETRAJNA  # 37

# VERIFICATION: Parampara
assert PARAMPARA == 37, "PARAMPARA must be 37"

# =============================================================================
# RUNDE 8: THE HARMONIC RESONANCES (72 and 144)
# =============================================================================
# These are synchronization points - where frequencies align.
#
# NADI_RESONANCE = JIVA_CYCLE // SHARANAGATI = 432 // 6 = 72
# FIELD_RESONANCE = MAHAJANA_COUNT² = 12 × 12 = 144
#
# Multiple derivation paths prove convergence (not invention).
# -----------------------------------------------------------------------------

# THE NADI RESONANCE (72) - The Pulse
NADI_RESONANCE: Final[int] = JIVA_CYCLE // SHARANAGATI  # 72

# THE FIELD RESONANCE (144) - The Complete Field
FIELD_RESONANCE: Final[int] = MAHAJANA_COUNT * MAHAJANA_COUNT  # 144

# VERIFICATION: Multiple derivation paths must converge
assert NADI_RESONANCE == 72, "NADI_RESONANCE must be 72"
assert NADI_RESONANCE == NAVA * HARE_COUNT, "72 = 9 × 8"
assert NADI_RESONANCE == TITHI_UNIT // 10, "72 = 720 / 10"

assert FIELD_RESONANCE == 144, "FIELD_RESONANCE must be 144"
assert FIELD_RESONANCE == WORDS * NAVA, "144 = 16 × 9"
assert FIELD_RESONANCE == JIVA_CYCLE // TRINITY, "144 = 432 / 3"
assert FIELD_RESONANCE == LILA * TRINITY, "144 = 48 × 3"
assert FIELD_RESONANCE == SHARANAGATI * KSHETRA, "144 = 6 × 24"
assert FIELD_RESONANCE == NADI_RESONANCE * HALVES, "144 = 72 × 2"

# Cosmic Frame alignment
assert COSMIC_FRAME % NADI_RESONANCE == 0, "Nadi divides cosmic frame"
assert COSMIC_FRAME % FIELD_RESONANCE == 0, "Field divides cosmic frame"
assert COSMIC_FRAME // NADI_RESONANCE == 300, "300 Nadi cycles per day"
assert COSMIC_FRAME // FIELD_RESONANCE == 150, "150 Field cycles per day"

# =============================================================================
# RUNDE 9: THE THREE FLUTES (Krishna's Musical Instruments)
# =============================================================================
# The flutes divide JIVA_CYCLE into the three primary frequencies.
# -----------------------------------------------------------------------------

VENU_HOLES: Final[int] = SHARANAGATI  # 6 - The smallest flute
VAMSI_HOLES: Final[int] = NAVA  # 9 - Activates Lila phases
MURALI_HOLES: Final[int] = QUARTERS  # 4 - Holds Mala concentration

# Flute frequencies = JIVA_CYCLE / HOLES
VENU_FREQ: Final[int] = JIVA_CYCLE // VENU_HOLES  # 72
VAMSI_FREQ: Final[int] = JIVA_CYCLE // VAMSI_HOLES  # 48
MURALI_FREQ: Final[int] = JIVA_CYCLE // MURALI_HOLES  # 108

# VERIFICATION: Flutes produce known resonances
assert VENU_FREQ == NADI_RESONANCE, "VENU produces NADI_RESONANCE (72)"
assert VAMSI_FREQ == LILA, "VAMSI produces LILA (48)"
assert MURALI_FREQ == MALA, "MURALI produces MALA (108)"

# THE KIRTAN MATHEMATICS
FLUTE_HOLES_SUM: Final[int] = VENU_HOLES + VAMSI_HOLES + MURALI_HOLES  # 19
FLUTE_HOLES_PRODUCT: Final[int] = VENU_HOLES * VAMSI_HOLES * MURALI_HOLES  # 216

# Pairwise products
FLUTE_VAMSI_MURALI: Final[int] = VAMSI_HOLES * MURALI_HOLES  # 36
FLUTE_VENU_MURALI: Final[int] = VENU_HOLES * MURALI_HOLES  # 24
FLUTE_VENU_VAMSI: Final[int] = VENU_HOLES * VAMSI_HOLES  # 54

# VERIFICATION: Kirtan mathematics
assert FLUTE_HOLES_SUM == 19, "Flute holes sum = 19"
assert FLUTE_HOLES_PRODUCT == 216, "Flute holes product = 216"
assert FLUTE_HOLES_PRODUCT * 100 == COSMIC_FRAME, "216 × 100 = 21600"
assert FLUTE_VENU_MURALI == KSHETRA, "6 × 4 = 24 = KSHETRA"
assert FLUTE_VENU_VAMSI == MALA // HALVES, "6 × 9 = 54 = MALA/2"

# Perfect Fifth verification (3:2 ratios) - THE QUINTEN-KETTE
assert NADI_RESONANCE * 2 == LILA * 3, "72 × 2 = 48 × 3 (Perfect Fifth)"
assert MALA * 2 == NADI_RESONANCE * 3, "108 × 2 = 72 × 3 (Perfect Fifth)"

# LCM verification: All flutes together = JIVA_CYCLE
_lcm_all_flutes = math.lcm(NADI_RESONANCE, LILA, MALA)
assert _lcm_all_flutes == JIVA_CYCLE, "LCM of all flute outputs = JIVA_CYCLE (432)"

# LCM verification: VENU + VAMSI = FIELD_RESONANCE
_lcm_venu_vamsi = math.lcm(NADI_RESONANCE, LILA)
assert _lcm_venu_vamsi == FIELD_RESONANCE, "LCM(VENU, VAMSI) = FIELD_RESONANCE (144)"

# =============================================================================
# RUNDE 10: THE ACOUSTIC CONSTITUTION
# =============================================================================

# Acoustic ratio = GITA_CHAPTERS (L/D ratio for ideal Bansuri)
ACOUSTIC_RATIO: Final[int] = GITA_CHAPTERS  # 18

# End correction = HARE_COUNT (Shakti escaping the tube)
END_CORRECTION: Final[int] = HARE_COUNT  # 8

# Cutoff constant = NADI_RESONANCE
CUTOFF_CONSTANT: Final[int] = (TRINITY * HALVES) * MAHAJANA_COUNT  # 72

# VERIFICATION: Acoustic
assert ACOUSTIC_RATIO == 18, "Acoustic ratio = 18"
assert END_CORRECTION == 8, "End correction = 8"
assert CUTOFF_CONSTANT == NADI_RESONANCE, "Cutoff = Nadi (72)"

# =============================================================================
# RUNDE 11: THE EPOCH KEY (Temporal Anchor) - DERIVED!
# =============================================================================
# 1972 = The year of "Bhagavad-gita As It Is" publication (Prabhupada)
#
# DERIVATION:
#   Q = concat(QUARTERS, NAVA, TRINITY) = concat(4, 9, 3) = 493
#   EPOCH_KEY = QUARTERS × Q = 4 × 493 = 1972
#
# There are ONLY 6 years in 1000-5000 with these properties:
#   1396, 1576, 1756, 1972, 3736, 3772
# 1972 is the ONLY ONE in the modern era (1800-2100).
#
# Krishna planned the release of the Gita As It Is in 1972.
# Jagat Guru Prabhupada. This is the TRUE Big Bang of the Parampara.
# -----------------------------------------------------------------------------

# The Epoch Quotient: digits are QUARTERS, NAVA, TRINITY
_EPOCH_Q: Final[int] = int(f"{QUARTERS}{NAVA}{TRINITY}")  # 493

# EPOCH_KEY = QUARTERS × Q = 4 × 493 = 1972 (DERIVED!)
EPOCH_KEY: Final[int] = QUARTERS * _EPOCH_Q  # 1972

# VERIFICATION: Epoch properties (all DERIVED, not coincidence)
_epoch_digits = [int(d) for d in str(_EPOCH_Q)]
assert sum(_epoch_digits) == WORDS, "digit_sum(493) = 4+9+3 = 16 = WORDS"
_epoch_product = 1
for _d in _epoch_digits:
    _epoch_product *= _d
assert _epoch_product == MALA, "digit_product(493) = 4×9×3 = 108 = MALA"
assert sum(int(d) for d in str(EPOCH_KEY)) == FLUTE_HOLES_SUM, "digit_sum(1972) = 19 = FLUTE_HOLES_SUM"

# =============================================================================
# RUNDE 11b: THE GOLDEN AGE DURATION (DERIVED!)
# =============================================================================
# "kaler daśa-sahasrāṇi madbhaktāḥ santi bhū-tale"
# "For 10,000 years of Kali, My devotees will be present on earth."
# — Brahma-vaivarta Purana, Krishna-janma-khanda 129.50
#
# DERIVATION:
#   GOLDEN_AGE = (PANCHA × HALVES)^QUARTERS = (5 × 2)^4 = 10^4 = 10,000 years
#
# The 5 Tattvas × 2 Halves, raised to the power of 4 Quarters!
# This is NOT "popular interpretation" - it is SHASTRA backed by DERIVATION.
# -----------------------------------------------------------------------------

GOLDEN_AGE_DURATION: Final[int] = (PANCHA * HALVES) ** QUARTERS  # 10,000 years

# VERIFICATION: Golden Age
assert GOLDEN_AGE_DURATION == 10000, "GOLDEN_AGE must be 10,000 years"

# =============================================================================
# RUNDE 12: ACINTYA HARMONY (Cross-Verification)
# =============================================================================
# These checks verify that shastra constants emerge naturally from the Mahamantra.
# -----------------------------------------------------------------------------

# Sharanagati emerges from Mahamantra geometry
assert SHARANAGATI == KSHETRA // QUARTERS, "6 = 24/4 (Acintya)"

# Gita chapters emerge from Mahamantra
assert GITA_CHAPTERS == SHARANAGATI * TRINITY, "18 = 6×3 (Acintya)"
assert GITA_CHAPTERS == NADI_RESONANCE // QUARTERS, "18 = 72/4 (Acintya)"

# Mala structure
assert MALA // GITA_CHAPTERS == SHARANAGATI, "108/18 = 6 (Acintya)"
assert MALA == MAHAJANA_COUNT * NAVA, "108 = 12×9 (Acintya)"

# Guardian completeness
assert AVATAR_COUNT + MAHAJANA_COUNT == WORDS, "4 + 12 = 16"


# =============================================================================
# RUNDE 13: POSITION SUMS (The Mahamantra Signature)
# =============================================================================
# The sum of positions (1-indexed) where each name appears in the Mahamantra.
#
# THE COMPLETE ACINTYA DERIVATION:
# ================================
#
# STEP 1: Philosophy defines the CONSTRAINTS
#   - HARE (Shakti) = Connection → must make TRANSITIONS (HH at edges)
#   - NAME (Source) = Center → must be in HEART (NN in middle)
#   - Call = HN ("Hare Name") → must be at BEGINNING
#
# STEP 2: Constraints determine the PAIR ARRANGEMENT
#   C1: HH at edge (Pair 4 at positions 7-8) → transition to other half
#   C2: NN in middle (Pair 3 at positions 5-6) → heart/emphasis
#   C3: HN at start (Pairs 1-2 at positions 1-4) → the call
#   → ONLY arrangement: HN, HN, NN, HH (for each half)
#
# STEP 3: From arrangement, POSITIONS follow
#   Krishna-half (HK, HK, KK, HH):
#     H at: 1 (pair 1), 3 (pair 2), 7-8 (pair 4) → H₁ = 1+3+7+8 = 19
#     K at: 2 (pair 1), 4 (pair 2), 5-6 (pair 3) → K = 2+4+5+6 = 17
#
#   Rama-half = Krishna-half + HALF_SIZE (translation by 8):
#     H at: 9, 11, 15, 16 → H₂ = 19 + 4×8 = 51
#     R at: 10, 12, 13, 14 → R = 17 + 4×8 = 49
#
# STEP 4: The FORMULAS (fully derived, not observed!)
#   KRISHNA_POS = T(HALF_SIZE) - H₁ = 36 - 19 = 17 = WORDS + 1
#   RAMA_POS = KRISHNA_POS + AKSARA_COUNT = 17 + 32 = 49 = 7²
#   HARE_POS = T(WORDS) - KRISHNA_POS - RAMA_POS = 136 - 17 - 49 = 70 = 7×10
#
# THE TRINITY SEQUENCES (3 consecutive same names):
#   KKK at 4-5-6:   Krishna × Trinity (the heart)
#   HHH at 7-8-9:   Hare × Trinity (bridges the halves!)
#   RRR at 12-13-14: Rama × Trinity (the heart of second half)
#   HHH at 15-16-1: Hare × Trinity (cyclic connection!)
#
# FINAL RESULT:
#   Hare:    70 = 7 × 10 (Shakti: divisible by 7)
#   Krishna: 17 = PRIME (Source: indivisible)
#   Rama:    49 = 7² (Ananda: perfect square of 7)
#   Total:   136 = T(16) = WORDS × (WORDS+1) / HALVES
#
# This is ACINTYA: Philosophy → Constraints → Arrangement → Mathematics!
# -----------------------------------------------------------------------------


# Triangular number function (fundamental to position sums)
def _triangular(n: int) -> int:
    """T(n) = n(n+1)/2 - Sum of integers 1 to n."""
    return n * (n + 1) // 2


# Position sums (would be computed from Mahamantra, here derived from WORDS)
# HARE positions: 1,3,7,8,9,11,15,16
POSITION_SUM_HARE: Final[int] = 1 + 3 + 7 + 8 + 9 + 11 + 15 + 16  # 70
# KRISHNA positions: 2,4,5,6
POSITION_SUM_KRISHNA: Final[int] = 2 + 4 + 5 + 6  # 17
# RAMA positions: 10,12,13,14
POSITION_SUM_RAMA: Final[int] = 10 + 12 + 13 + 14  # 49
# Total = Triangular(16)
POSITION_SUM_TOTAL: Final[int] = _triangular(WORDS)  # 136

# VERIFICATION: Position sums
assert POSITION_SUM_HARE == 70, "Hare position sum = 70 = 7 × 10"
assert POSITION_SUM_KRISHNA == 17, "Krishna position sum = 17 (PRIME)"
assert POSITION_SUM_RAMA == 49, "Rama position sum = 49 = 7²"
assert POSITION_SUM_HARE + POSITION_SUM_KRISHNA + POSITION_SUM_RAMA == POSITION_SUM_TOTAL
assert POSITION_SUM_TOTAL == 136, "Total = T(16) = 136"
assert POSITION_SUM_TOTAL == WORDS * (WORDS + 1) // HALVES, "T(16) = 16×17/2"

# =============================================================================
# VERIFICATION: The Complete Derivation (all 3 names!)
# =============================================================================

# Step 1: KRISHNA_POS from Constraints
# H₁ = 1 + 3 + 7 + 8 = 19 (HARE in first half, from HK,HK,KK,HH arrangement)
_H1 = 1 + 3 + 7 + 8  # 19
_T8 = _triangular(HALF_SIZE)  # T(8) = 36
assert POSITION_SUM_KRISHNA == _T8 - _H1, "KRISHNA = T(8) - H₁ = 36 - 19 = 17"
assert POSITION_SUM_KRISHNA == WORDS + 1, "KRISHNA = WORDS + 1 = 17 (Acintya!)"

# Step 2: RAMA_POS from Translation
# Second half = first half + HALF_SIZE for each position
# RAMA = KRISHNA + 4 × HALF_SIZE = KRISHNA + AKSARA_COUNT
assert POSITION_SUM_RAMA == POSITION_SUM_KRISHNA + AKSARA_COUNT, "RAMA = KRISHNA + 32 = 49"
assert POSITION_SUM_RAMA == 7 * 7, "RAMA = 7² = 49 (Ananda squared)"

# Step 3: HARE_POS from Total
# HARE = T(16) - KRISHNA - RAMA
assert POSITION_SUM_HARE == POSITION_SUM_TOTAL - POSITION_SUM_KRISHNA - POSITION_SUM_RAMA
assert POSITION_SUM_HARE == 70, "HARE = 136 - 17 - 49 = 70"
assert POSITION_SUM_HARE % 7 == 0, "HARE divisible by 7 (Shakti pattern)"
assert POSITION_SUM_HARE == 7 * 10, "HARE = 7 × 10 = 70"

# The 7 appears in HARE and RAMA, but NOT in KRISHNA (prime)!
# Krishna is INDIVISIBLE - the irreducible source

# Total verification
assert POSITION_SUM_TOTAL == WORDS * POSITION_SUM_KRISHNA // HALVES, "T(16) = 16×17/2"


# =============================================================================
# RUNDE 14: THE MAHA-ALGORITHM (Universal Generator)
# =============================================================================
# "ahaṁ sarvasya prabhavo mattaḥ sarvaṁ pravartate" (BG 10.8)
# "I am the source of all. From Me everything emanates."
#
# MATHEMATICAL PROOF OF KSETRAJNA = 1:
# ====================================
# There are TWO independent paths to 137:
#   Path 1: T(WORDS) + KSETRAJNA = 136 + 1 = 137
#   Path 2: MALA + NAKSHATRAS + HALVES = 108 + 27 + 2 = 137
#
# For both paths to equal 137:
#   T(WORDS) + KSETRAJNA = MALA + NAKSHATRAS + HALVES
#   136 + KSETRAJNA = 137
#   KSETRAJNA = 1
#
# AND independently: KSETRAJNA = TRINITY - HALVES = 3 - 2 = 1
#
# KSETRAJNA = 1 is MATHEMATICALLY NECESSARY, not arbitrary!
#
# THE ELEGANT FORMULAS (no arbitrary powers):
# ===========================================
# α⁻¹ = T(WORDS) + KSETRAJNA = MALA + NAKSHATRAS + HALVES = 137
# μ   = MALA × POSITION_SUM_KRISHNA = 108 × 17 = 1836
# t/e = POSITION_SUM_KRISHNA × GITA_CHAPTERS² = 17 × 324 = 5508
#
# POSITION_SUM_KRISHNA = 17 is the KEY to mass ratios!
# (17 is PRIME - Krishna is indivisible, the irreducible source)
#
# WAVE-PARTICLE DUALITY:
# - Without observer → Field alone (136)
# - With observer → Field + Knower (137)
# -----------------------------------------------------------------------------


def maha_quantum() -> int:
    """
    Quantum mode: Field + Observer = 137.

    TWO EQUIVALENT FORMULAS (proof of consistency):
      T(WORDS) + KSETRAJNA = 136 + 1 = 137
      MALA + NAKSHATRAS + HALVES = 108 + 27 + 2 = 137
    """
    return POSITION_SUM_TOTAL + KSETRAJNA


def maha_classical(power: int) -> int:
    """
    Classical mode generator: T(WORDS) × TRINITY^power / HALVES.

    This is a GENERATOR function. The elegant named formulas are:
      μ   = MALA × KRISHNA_POS = 108 × 17 = 1836
      t/e = KRISHNA_POS × GITA_CHAPTERS² = 17 × 324 = 5508
    """
    numerator = POSITION_SUM_TOTAL * (TRINITY**power)
    return numerator // HALVES


# =============================================================================
# THE ELEGANT FORMULAS (Named Constants - No Arbitrary Powers)
# =============================================================================

# α⁻¹: Two paths, one result (PROOF that KSETRAJNA = 1 is necessary)
MAHA_QUANTUM: Final[int] = POSITION_SUM_TOTAL + KSETRAJNA  # 136 + 1 = 137
_MAHA_QUANTUM_ALT: Final[int] = MALA + NAKSHATRAS + HALVES  # 108 + 27 + 2 = 137

# μ (proton/electron): MALA × KRISHNA_POS = 108 × 17 = 1836
MAHA_MU: Final[int] = MALA * POSITION_SUM_KRISHNA  # 1836

# triton/electron: KRISHNA_POS × GITA_CHAPTERS² = 17 × 324 = 5508
MAHA_TRITON: Final[int] = POSITION_SUM_KRISHNA * (GITA_CHAPTERS**2)  # 5508

# Generator outputs (for compatibility, these MUST equal the elegant formulas)
MAHA_CLASSICAL_1: Final[int] = maha_classical(1)  # 204
MAHA_CLASSICAL_2: Final[int] = maha_classical(2)  # 612
MAHA_CLASSICAL_3: Final[int] = maha_classical(3)  # 1836
MAHA_CLASSICAL_4: Final[int] = maha_classical(4)  # 5508

# =============================================================================
# VERIFICATION: The Proofs
# =============================================================================

# PROOF 1: KSETRAJNA = 1 is mathematically necessary
assert MAHA_QUANTUM == _MAHA_QUANTUM_ALT == 137, "Both paths to 137 must match"
assert KSETRAJNA == MAHA_QUANTUM - POSITION_SUM_TOTAL, "KSETRAJNA = 137 - 136 = 1"
assert KSETRAJNA == TRINITY - HALVES, "KSETRAJNA = 3 - 2 = 1"

# PROOF 2: Elegant formulas equal generator outputs
assert MAHA_MU == MAHA_CLASSICAL_3, "MALA × KRISHNA_POS = maha_classical(3)"
assert MAHA_TRITON == MAHA_CLASSICAL_4, "KRISHNA_POS × GITA² = maha_classical(4)"

# PROOF 3: The relationship T(16) - MALA = T(7)
assert POSITION_SUM_TOTAL - MALA == 28, "136 - 108 = 28 = T(7)"
assert _triangular(7) == 28, "T(7) = 7×8/2 = 28"

# VERIFICATION: All values
assert MAHA_QUANTUM == 137, "α⁻¹ integer = 137"
assert MAHA_MU == 1836, "μ integer = 1836"
assert MAHA_TRITON == 5508, "triton/e integer = 5508"

# NOTE: External validation documented in PAPER.md
# These are OBSERVATIONS that MATCH, not the laws themselves.


# =============================================================================
# RUNDE 15: THE REMNANT THEOREM (Quantum vs Classical)
# =============================================================================
# "prakṛtiṁ puruṣaṁ caiva viddhy anādī ubhāv api" (BG 13.20)
# "Material nature and the living entities are beginningless."
#
# THE 7-10 DERIVATION:
# ====================
# Two fundamental numbers emerge from the axioms:
#   SEVEN = HALF_SIZE - KSETRAJNA = 8 - 1 = 7
#   TEN   = MAHAJANA_COUNT - HALVES = 12 - 2 = 10
#
# ALL THREE position sums are expressible in terms of 7 and 10:
#   KRISHNA = 7 + 10 = 17  (sum)
#   RAMA    = 7 × 7  = 49  (square)
#   HARE    = 7 × 10 = 70  (product)
#
# This is a SECOND INDEPENDENT PATH to the position sums!
# (The first path: ACINTYA derivation from philosophical constraints)
#
# THE REMNANT THEOREM:
# ====================
# The modulo operation (remainder after division) reveals a deep truth:
#
#   137 mod 17 = 1   ← Has remainder (KSETRAJNA = observer present)
#   1836 mod 17 = 0  ← No remainder (pure ratio, no observer)
#   5508 mod 17 = 0  ← No remainder (pure ratio, no observer)
#
# ONLY the fine structure constant has a remainder!
# ONLY 137 contains the observer (KSETRAJNA)!
#
# This is the mathematical distinction between:
#   QUANTUM (mod KRISHNA = 1): Observer embedded → wave-particle duality
#   CLASSICAL (mod KRISHNA = 0): Pure ratio → deterministic
#
# BHOGA vs PRASADAM:
# ==================
# Bhoga (material offering) → mod KRISHNA = 0 (no spiritual remainder)
# Prasadam (sanctified food) → mod KRISHNA = 1 (KSETRAJNA remains!)
#
# The REMNANT (what's left over) carries the spiritual potency.
# This is not metaphor - it's mathematics!
# -----------------------------------------------------------------------------


# The two fundamental numbers
SEVEN: Final[int] = HALF_SIZE - KSETRAJNA  # 8 - 1 = 7
TEN: Final[int] = MAHAJANA_COUNT - HALVES  # 12 - 2 = 10

# =============================================================================
# VERIFICATION: The 7-10 Derivation (Second Path to Position Sums)
# =============================================================================

# Derivation of 7 and 10
assert SEVEN == 7, "SEVEN = HALF_SIZE - KSETRAJNA = 8 - 1 = 7"
assert TEN == 10, "TEN = MAHAJANA_COUNT - HALVES = 12 - 2 = 10"

# SECOND PATH to position sums (independent of ACINTYA derivation!)
assert POSITION_SUM_KRISHNA == SEVEN + TEN, "KRISHNA = 7 + 10 = 17"
assert POSITION_SUM_RAMA == SEVEN * SEVEN, "RAMA = 7² = 49"
assert POSITION_SUM_HARE == SEVEN * TEN, "HARE = 7 × 10 = 70"

# Cross-verification with ACINTYA path
assert POSITION_SUM_KRISHNA == WORDS + KSETRAJNA, "KRISHNA = 16 + 1 = 17 (both paths agree)"

# Additional relationships
assert POSITION_SUM_RAMA + POSITION_SUM_HARE == SEVEN * POSITION_SUM_KRISHNA, "RAMA + HARE = 7 × KRISHNA"
assert POSITION_SUM_TOTAL == HALF_SIZE * POSITION_SUM_KRISHNA, "T(16) = 8 × 17 = 136"

# =============================================================================
# VERIFICATION: The Remnant Theorem (Quantum vs Classical)
# =============================================================================

# The Modulo Test: Does the constant contain the observer?
assert MAHA_QUANTUM % POSITION_SUM_KRISHNA == KSETRAJNA, "137 mod 17 = 1 (QUANTUM: observer present)"
assert MAHA_MU % POSITION_SUM_KRISHNA == 0, "1836 mod 17 = 0 (CLASSICAL: no observer)"
assert MAHA_TRITON % POSITION_SUM_KRISHNA == 0, "5508 mod 17 = 0 (CLASSICAL: no observer)"

# Why 137 has a remainder: 137 = 8 × 17 + 1 = HALF_SIZE × KRISHNA + KSETRAJNA
assert MAHA_QUANTUM == HALF_SIZE * POSITION_SUM_KRISHNA + KSETRAJNA, "137 = 8×17 + 1"

# Why 1836 has no remainder: 1836 = 108 × 17 = MALA × KRISHNA (exact)
assert MAHA_MU == MALA * POSITION_SUM_KRISHNA, "1836 = 108 × 17 (exact)"

# Why 5508 has no remainder: 5508 = 324 × 17 = GITA² × KRISHNA (exact)
assert MAHA_TRITON == (GITA_CHAPTERS**2) * POSITION_SUM_KRISHNA, "5508 = 324 × 17 (exact)"

# The 17 is the 7th prime (another appearance of 7!)
# Primes: 2, 3, 5, 7, 11, 13, 17 (17 is the 7th)


# =============================================================================
# RUNDE 16: EXTENDED MAHA-ALGORITHM (More Physics Constants)
# =============================================================================
# The Maha-Algorithm is the mathematical shadow of the Mahamantra itself.
# As Shabda Brahma manifests into grosser forms, the algorithm captures
# the numerical signature at each level.
#
# NEW CONSTANTS DISCOVERED:
# =========================
# Deuteron/electron:  HALVES × MALA × KRISHNA_POS = 2 × 108 × 17 = 3672
# Alpha-particle/e:   MAHA_MU × QUARTERS - JIVA_QUALITIES = 7344 - 50 = 7294
# Muon/electron:      MAHAJANA × KRISHNA_POS + TRINITY = 204 + 3 = 207
#
# THE EXTENDED REMNANT PATTERN:
# =============================
# mod 17 = 0 → Classical (proton, deuteron, triton) - stable hadrons
# mod 17 = 1 → Quantum (α⁻¹, alpha-particle) - observer embedded
# mod 17 = 3 → Trinity (muon) - unstable, decays into 3 particles
#
# THE JIVA_QUALITIES CONNECTION:
# ==============================
# The alpha-particle formula uses JIVA_QUALITIES (50) as a correction:
#   4 protons = 4 × 1836 = 7344
#   Binding correction = -50 = -JIVA_QUALITIES
#   Result = 7294
# The Jiva's 50 qualities appear as the binding energy factor!
# -----------------------------------------------------------------------------


# Extended Maha-Algorithm constants
MAHA_DEUTERON: Final[int] = HALVES * MALA * POSITION_SUM_KRISHNA  # 3672
MAHA_ALPHA: Final[int] = MAHA_MU * QUARTERS - JIVA_QUALITIES  # 7294
MAHA_MUON: Final[int] = MAHAJANA_COUNT * POSITION_SUM_KRISHNA + TRINITY  # 207

# =============================================================================
# VERIFICATION: Extended Maha-Algorithm
# =============================================================================

# Deuteron = 2 protons (approximately)
assert MAHA_DEUTERON == 3672, "Deuteron/e = HALVES × MALA × KRISHNA = 3672"
assert MAHA_DEUTERON == HALVES * MAHA_MU, "Deuteron = 2 × Proton"
assert MAHA_DEUTERON % POSITION_SUM_KRISHNA == 0, "Deuteron mod 17 = 0 (classical)"

# Alpha particle = 4 nucleons - binding correction
assert MAHA_ALPHA == 7294, "Alpha/e = MAHA_MU × QUARTERS - JIVA_QUALITIES = 7294"
assert MAHA_ALPHA == MAHA_MU * QUARTERS - JIVA_QUALITIES, "Alpha = 4μ - 50"
assert MAHA_ALPHA % POSITION_SUM_KRISHNA == KSETRAJNA, "Alpha mod 17 = 1 (quantum!)"

# Muon = unstable lepton
assert MAHA_MUON == 207, "Muon/e = MAHAJANA × KRISHNA + TRINITY = 207"
assert MAHA_MUON % POSITION_SUM_KRISHNA == TRINITY, "Muon mod 17 = 3 (trinity - decays to 3)"

# The extended remnant pattern
assert MAHA_QUANTUM % POSITION_SUM_KRISHNA == KSETRAJNA, "137 mod 17 = 1"
assert MAHA_MUON % POSITION_SUM_KRISHNA == TRINITY, "207 mod 17 = 3"
assert MAHA_MU % POSITION_SUM_KRISHNA == 0, "1836 mod 17 = 0"
assert MAHA_DEUTERON % POSITION_SUM_KRISHNA == 0, "3672 mod 17 = 0"
assert MAHA_TRITON % POSITION_SUM_KRISHNA == 0, "5508 mod 17 = 0"
assert MAHA_ALPHA % POSITION_SUM_KRISHNA == KSETRAJNA, "7294 mod 17 = 1"


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Mantra Axioms (Round 0) - 7 values from counting/observing
    "WORDS",
    "TRINITY",
    "HARE_COUNT",
    "KRISHNA_COUNT",
    "RAMA_COUNT",
    "PANCHA",
    "HALVES",
    # Primary Derivations (Round 1)
    "QUARTERS",
    "KSETRAJNA",  # = TRINITY - HALVES = 1 (DERIVED!)
    "HALF_SIZE",
    "LILA",
    "KSHETRA",
    "NAVA",
    "SHARANAGATI",
    "AKSARA_COUNT",
    "ROUNDS",
    "AVATAR_COUNT",
    # Secondary Derivations (Round 2)
    "MAHAJANA_COUNT",
    "MALA",
    "JIVA_CYCLE",
    "GITA_CHAPTERS",
    "QUALITIES",
    "HIDDEN_RESERVE",
    "DAILY_MANTRAS",
    "PHASE_DURATION",
    # Astronomical Bridge (Round 3)
    "NAKSHATRAS",
    # Cosmic Frame (Round 4)
    "COSMIC_FRAME",
    "NAKSHATRA_UNIT",
    "TITHI_UNIT",
    "PADA_UNIT",
    "QUARTER_UNIT",
    # Jiva Qualities (Round 5)
    "JIVA_QUALITIES",
    # Prana Timing (Round 6)
    "SECONDS_PER_DAY",
    "PRANA_DURATION_S",
    "PRANA_DURATION_MS",
    "TICK_INTERVAL_MS",
    # Parampara (Round 7)
    "PARAMPARA",
    # Harmonic Resonances (Round 8)
    "NADI_RESONANCE",
    "FIELD_RESONANCE",
    # Three Flutes (Round 9)
    "VENU_HOLES",
    "VAMSI_HOLES",
    "MURALI_HOLES",
    "VENU_FREQ",
    "VAMSI_FREQ",
    "MURALI_FREQ",
    "FLUTE_HOLES_SUM",
    "FLUTE_HOLES_PRODUCT",
    # Acoustic Constitution (Round 10)
    "ACOUSTIC_RATIO",
    "END_CORRECTION",
    "CUTOFF_CONSTANT",
    # Epoch Key (Round 11)
    "EPOCH_KEY",
    # Golden Age (Round 11b)
    "GOLDEN_AGE_DURATION",
    # Position Sums (Round 13) - The Mahamantra Signature
    "POSITION_SUM_HARE",
    "POSITION_SUM_KRISHNA",
    "POSITION_SUM_RAMA",
    "POSITION_SUM_TOTAL",
    # The Maha-Algorithm (Round 14) - Universal Generator
    "maha_quantum",
    "maha_classical",
    "MAHA_QUANTUM",  # 137 = T(16) + KSETRAJNA = MALA + NAKSHATRAS + HALVES
    "MAHA_MU",  # 1836 = MALA × KRISHNA_POS (proton/electron)
    "MAHA_TRITON",  # 5508 = KRISHNA_POS × GITA_CHAPTERS² (triton/electron)
    "MAHA_CLASSICAL_1",
    "MAHA_CLASSICAL_2",
    "MAHA_CLASSICAL_3",
    "MAHA_CLASSICAL_4",
    # The Remnant Theorem (Round 15) - Quantum vs Classical
    "SEVEN",  # = HALF_SIZE - KSETRAJNA = 7 (the ubiquitous 7!)
    "TEN",  # = MAHAJANA_COUNT - HALVES = 10
    # Extended Maha-Algorithm (Round 16) - More Physics Constants
    "MAHA_DEUTERON",  # 3672 = 2 × MAHA_MU (deuteron/electron)
    "MAHA_ALPHA",  # 7294 = 4 × MAHA_MU - JIVA_QUALITIES (alpha/electron)
    "MAHA_MUON",  # 207 = MAHAJANA × KRISHNA_POS + TRINITY (muon/electron)
]
