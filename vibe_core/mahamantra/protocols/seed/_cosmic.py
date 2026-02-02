"""
TIER 3-5: COSMIC FRAME & TIMING CONSTANTS
==========================================

Nakshatras, Cosmic Frame, Timing, and Jiva Qualities.
"""

from typing import Final

from ._axioms import WORDS, PANCHA, HALVES, HARE_COUNT, TRINITY
from ._primary import QUARTERS, KSETRAJNA, AKSARA_COUNT, LILA, SHARANAGATI, KSHETRA, NAVA
from ._secondary import JIVA_CYCLE, MALA, TEN

# NAKSHATRAS = JIVA_CYCLE // WORDS = 432 // 16 = 27
# The 27 lunar mansions
NAKSHATRAS: Final[int] = JIVA_CYCLE // WORDS  # 27

# COSMIC_FRAME = AKSARA_COUNT x NAKSHATRAS x PANCHA^2 = 32 x 27 x 25 = 21600
COSMIC_FRAME: Final[int] = AKSARA_COUNT * NAKSHATRAS * (PANCHA**2)  # 21600

# The Units
NAKSHATRA_UNIT: Final[int] = COSMIC_FRAME // NAKSHATRAS  # 800
# 30 Tithis per month = PANCHA * SHARANAGATI = 5 * 6 = 30 (DERIVED!)
TITHI_UNIT: Final[int] = COSMIC_FRAME // (PANCHA * SHARANAGATI)  # 720
PADA_UNIT: Final[int] = COSMIC_FRAME // MALA  # 200
QUARTER_UNIT: Final[int] = COSMIC_FRAME // QUARTERS  # 5400

# JIVA_QUALITIES = COSMIC_FRAME // JIVA_CYCLE = 21600 // 432 = 50
JIVA_QUALITIES: Final[int] = COSMIC_FRAME // JIVA_CYCLE  # 50

# =============================================================================
# PRANA TIMING - FULLY DERIVED FROM MAHAMANTRA
# =============================================================================
# The Vedic day is divided into 21600 pranas (COSMIC_FRAME).
# SECONDS_PER_DAY = COSMIC_FRAME × QUARTERS = 21600 × 4 = 86400
# This IS derivable - the relationship to seconds follows from the cosmic structure!

# SECONDS_PER_DAY = COSMIC_FRAME × QUARTERS = 21600 × 4 = 86400
SECONDS_PER_DAY: Final[int] = COSMIC_FRAME * QUARTERS  # 86400

# PRANA_DURATION_S = SECONDS_PER_DAY // COSMIC_FRAME = QUARTERS = 4
PRANA_DURATION_S: Final[int] = QUARTERS  # 4 seconds per prana

# PRANA_DURATION_MS = PRANA_DURATION_S × 1000 = QUARTERS × 1000 = 4000
# But we derive 1000 = TEN^TRINITY = 10^3
PRANA_DURATION_MS: Final[int] = QUARTERS * (TEN ** TRINITY)  # 4000

# TICK_INTERVAL_MS = PRANA_DURATION_MS // WORDS = 4000 // 16 = 250
TICK_INTERVAL_MS: Final[int] = PRANA_DURATION_MS // WORDS  # 250

# VERIFICATION
assert SECONDS_PER_DAY == 86400, "SECONDS_PER_DAY must be 86400"
assert PRANA_DURATION_S == 4, "PRANA_DURATION_S must be 4"
assert PRANA_DURATION_MS == 4000, "PRANA_DURATION_MS must be 4000"
assert TICK_INTERVAL_MS == 250, "TICK_INTERVAL_MS must be 250"

# Golden Age Duration
GOLDEN_AGE_DURATION: Final[int] = (PANCHA * HALVES) ** QUARTERS  # 10,000 years

# Epoch Key (1972) - FULLY DERIVED!
# _EPOCH_Q = concat(QUARTERS, NAVA, TRINITY) = "493" = 493
_EPOCH_Q: Final[int] = int(f"{QUARTERS}{NAVA}{TRINITY}")  # 493
EPOCH_KEY: Final[int] = QUARTERS * _EPOCH_Q  # 1972

# Chaitanya's birth year = 1-48-6 = KSETRAJNA-LILA-SHARANAGATI (FULLY DERIVED!)
# TEN^3 = 1000, TEN^1 = 10
CHAITANYA_BIRTH: Final[int] = KSETRAJNA * (TEN ** TRINITY) + LILA * TEN + SHARANAGATI  # 1486

# Kishora numerator (Krishna's eternal age 79/5 = 15.8)
KISHORA_NUMERATOR: Final[int] = PANCHA * WORDS - KSETRAJNA  # 79

# VERIFICATION
assert NAKSHATRAS == 27, "NAKSHATRAS must be 27"
assert COSMIC_FRAME == 21600, "COSMIC_FRAME must be 21600"
assert COSMIC_FRAME == 360 * 60, "COSMIC_FRAME equals arc-minutes in circle"
assert JIVA_QUALITIES == 50, "JIVA_QUALITIES must be 50"
assert GOLDEN_AGE_DURATION == 10000, "GOLDEN_AGE must be 10,000 years"
assert CHAITANYA_BIRTH == 1486, "CHAITANYA_BIRTH must be 1486"
assert KISHORA_NUMERATOR == 79, "KISHORA_NUMERATOR must be 79"
assert COSMIC_FRAME % NAKSHATRA_UNIT == 0, "Nakshatra divides evenly"
assert COSMIC_FRAME % JIVA_CYCLE == 0, "Jiva divides evenly"

__all__ = [
    "NAKSHATRAS",
    "COSMIC_FRAME",
    "NAKSHATRA_UNIT",
    "TITHI_UNIT",
    "PADA_UNIT",
    "QUARTER_UNIT",
    "JIVA_QUALITIES",
    # Prana Timing (DERIVED from COSMIC_FRAME × QUARTERS)
    "SECONDS_PER_DAY",
    "PRANA_DURATION_S",
    "PRANA_DURATION_MS",
    "TICK_INTERVAL_MS",
    # Epoch & History
    "GOLDEN_AGE_DURATION",
    "EPOCH_KEY",
    "CHAITANYA_BIRTH",
    "KISHORA_NUMERATOR",
]
