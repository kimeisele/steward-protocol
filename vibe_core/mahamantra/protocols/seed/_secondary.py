"""
TIER 2: SECONDARY DERIVATIONS - Building the Hierarchy
=======================================================

These constants are derived from TIER 1 primary derivations.
"""

from typing import Final

from ._axioms import HALVES, HARE_COUNT, TRINITY, WORDS
from ._primary import (
    HALF_SIZE,
    KSETRAJNA,
    KSHETRA,
    LILA,
    NAVA,
    QUARTERS,
    SHARANAGATI,
)

# MAHAJANA_COUNT = KSHETRA // HALVES = 24 // 2 = 12
# The 12 Mahajanas (great authorities)
MAHAJANA_COUNT: Final[int] = KSHETRA // HALVES  # 12

# MALA = MAHAJANA_COUNT x NAVA = 12 x 9 = 108
# The 108 beads of the japa mala
MALA: Final[int] = MAHAJANA_COUNT * NAVA  # 108

# MALA_COMPLETE = MALA + KSETRAJNA = 108 + 1 = 109
# The complete mala with sumeru bead
MALA_COMPLETE: Final[int] = MALA + KSETRAJNA  # 109

# JIVA_CYCLE = MALA x QUARTERS = 108 x 4 = 432
# The soul's harmonic frequency
JIVA_CYCLE: Final[int] = MALA * QUARTERS  # 432

# GITA_CHAPTERS = SHARANAGATI x TRINITY = 6 x 3 = 18
GITA_CHAPTERS: Final[int] = SHARANAGATI * TRINITY  # 18

# QUALITIES = WORDS x QUARTERS = 16 x 4 = 64
# Krishna's 64 qualities
QUALITIES: Final[int] = WORDS * QUARTERS  # 64

# HIDDEN_RESERVE = QUALITIES - LILA = 64 - 48 = 16 = WORDS
HIDDEN_RESERVE: Final[int] = QUALITIES - LILA  # 16

# DAILY_MANTRAS = MALA x ROUNDS = 108 x 16 = 1728
DAILY_MANTRAS: Final[int] = MALA * WORDS  # 1728

# PHASE_DURATION = LILA // QUARTERS = 48 // 4 = 12
PHASE_DURATION: Final[int] = LILA // QUARTERS  # 12

# PARAMPARA = KSHETRA + MAHAJANA_COUNT + KSETRAJNA = 24 + 12 + 1 = 37
PARAMPARA: Final[int] = KSHETRA + MAHAJANA_COUNT + KSETRAJNA  # 37

# SEVEN = HALF_SIZE - KSETRAJNA = 8 - 1 = 7
SEVEN: Final[int] = HALF_SIZE - KSETRAJNA  # 7

# TEN = MAHAJANA_COUNT - HALVES = 12 - 2 = 10
TEN: Final[int] = MAHAJANA_COUNT - HALVES  # 10

# NADI_RESONANCE = JIVA_CYCLE // SHARANAGATI = 432 // 6 = 72
NADI_RESONANCE: Final[int] = JIVA_CYCLE // SHARANAGATI  # 72

# FIELD_RESONANCE = MAHAJANA_COUNT^2 = 12 x 12 = 144
FIELD_RESONANCE: Final[int] = MAHAJANA_COUNT * MAHAJANA_COUNT  # 144

# Flute constants (derived)
VENU_HOLES: Final[int] = SHARANAGATI  # 6
VAMSI_HOLES: Final[int] = NAVA  # 9
MURALI_HOLES: Final[int] = QUARTERS  # 4
VENU_FREQ: Final[int] = JIVA_CYCLE // VENU_HOLES  # 72
VAMSI_FREQ: Final[int] = JIVA_CYCLE // VAMSI_HOLES  # 48
MURALI_FREQ: Final[int] = JIVA_CYCLE // MURALI_HOLES  # 108
FLUTE_HOLES_SUM: Final[int] = VENU_HOLES + VAMSI_HOLES + MURALI_HOLES  # 19
FLUTE_HOLES_PRODUCT: Final[int] = VENU_HOLES * VAMSI_HOLES * MURALI_HOLES  # 216
FLUTE_VENU_VAMSI: Final[int] = VENU_HOLES * VAMSI_HOLES  # 54
FLUTE_VENU_MURALI: Final[int] = VENU_HOLES * MURALI_HOLES  # 24

# Acoustic constants
ACOUSTIC_RATIO: Final[int] = GITA_CHAPTERS  # 18
END_CORRECTION: Final[int] = HARE_COUNT  # 8
CUTOFF_CONSTANT: Final[int] = (TRINITY * HALVES) * MAHAJANA_COUNT  # 72

# VERIFICATION
assert MAHAJANA_COUNT == 12, "MAHAJANA_COUNT must be 12"
assert MALA == 108, "MALA must be 108"
assert MALA_COMPLETE == 109, "MALA_COMPLETE must be 109"
assert JIVA_CYCLE == 432, "JIVA_CYCLE must be 432"
assert GITA_CHAPTERS == 18, "GITA_CHAPTERS must be 18"
assert PARAMPARA == 37, "PARAMPARA must be 37"
assert SEVEN == 7, "SEVEN must be 7"
assert TEN == 10, "TEN must be 10"
assert NADI_RESONANCE == 72, "NADI_RESONANCE must be 72"
assert FIELD_RESONANCE == 144, "FIELD_RESONANCE must be 144"
assert PHASE_DURATION == MAHAJANA_COUNT, "Time/Person holographic principle"
assert HIDDEN_RESERVE == WORDS, "HIDDEN_RESERVE must equal WORDS"
assert JIVA_CYCLE == LILA * NAVA, "JIVA_CYCLE must equal LILA x NAVA"
assert VENU_FREQ == NADI_RESONANCE, "VENU produces NADI_RESONANCE"
assert VAMSI_FREQ == LILA, "VAMSI produces LILA"
assert MURALI_FREQ == MALA, "MURALI produces MALA"

__all__ = [
    "MAHAJANA_COUNT",
    "MALA",
    "MALA_COMPLETE",
    "JIVA_CYCLE",
    "GITA_CHAPTERS",
    "QUALITIES",
    "HIDDEN_RESERVE",
    "DAILY_MANTRAS",
    "PHASE_DURATION",
    "PARAMPARA",
    "SEVEN",
    "TEN",
    "NADI_RESONANCE",
    "FIELD_RESONANCE",
    "VENU_HOLES",
    "VAMSI_HOLES",
    "MURALI_HOLES",
    "VENU_FREQ",
    "VAMSI_FREQ",
    "MURALI_FREQ",
    "FLUTE_HOLES_SUM",
    "FLUTE_HOLES_PRODUCT",
    "FLUTE_VENU_VAMSI",
    "FLUTE_VENU_MURALI",
    "ACOUSTIC_RATIO",
    "END_CORRECTION",
    "CUTOFF_CONSTANT",
]
