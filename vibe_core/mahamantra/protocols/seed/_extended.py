"""
EXTENDED CONSTANTS - Production-relevant derived constants
==========================================================

Physics, Music, Position Sums, Mahamantra Patterns, Gita References.
"""

from typing import Final
import math

from ._axioms import (
    WORDS,
    TRINITY,
    HARE_COUNT,
    KRISHNA_COUNT,
    RAMA_COUNT,
    PANCHA,
    HALVES,
)
from ._primary import (
    QUARTERS,
    KSETRAJNA,
    HALF_SIZE,
    LILA,
    KSHETRA,
    NAVA,
    SHARANAGATI,
    AKSARA_COUNT,
    AVATAR_COUNT,
)
from ._secondary import (
    MAHAJANA_COUNT,
    MALA,
    MALA_COMPLETE,
    JIVA_CYCLE,
    GITA_CHAPTERS,
    QUALITIES,
    PARAMPARA,
    SEVEN,
    TEN,
    NADI_RESONANCE,
    FIELD_RESONANCE,
    FLUTE_HOLES_SUM,
    FLUTE_VENU_VAMSI,
)
from ._cosmic import NAKSHATRAS, JIVA_QUALITIES, COSMIC_FRAME


# =============================================================================
# TRIANGULAR NUMBER HELPER
# =============================================================================
def _triangular(n: int) -> int:
    """T(n) = n(n+1)/2 - Sum of integers 1 to n."""
    return n * (n + 1) // 2


# =============================================================================
# POSITION SUMS (The Mahamantra Signature) - FULLY DERIVED FROM SEVEN AND TEN!
# =============================================================================
# The 7-10 DERIVATION (Second Path to Position Sums):
#   SEVEN = HALF_SIZE - KSETRAJNA = 8 - 1 = 7
#   TEN   = MAHAJANA_COUNT - HALVES = 12 - 2 = 10
#
# ALL THREE position sums are expressible in terms of SEVEN and TEN:
#   KRISHNA = SEVEN + TEN = 7 + 10 = 17  (sum - indivisible prime)
#   RAMA    = SEVEN * SEVEN = 7² = 49    (square - bliss amplifies)
#   HARE    = SEVEN * TEN = 7 × 10 = 70  (product - energy distributes)

# DERIVED from SEVEN and TEN (not hardcoded sums!)
POSITION_SUM_KRISHNA: Final[int] = SEVEN + TEN  # 17
POSITION_SUM_RAMA: Final[int] = SEVEN * SEVEN  # 49
POSITION_SUM_HARE: Final[int] = SEVEN * TEN  # 70
# Total = Triangular(WORDS) = WORDS * (WORDS + 1) / 2
POSITION_SUM_TOTAL: Final[int] = _triangular(WORDS)  # 136

# VERIFICATION: All three must sum to total
assert POSITION_SUM_HARE + POSITION_SUM_KRISHNA + POSITION_SUM_RAMA == POSITION_SUM_TOTAL
assert POSITION_SUM_TOTAL == 136, "Total = T(16) = 136"
# Cross-verify with ACINTYA path
assert POSITION_SUM_KRISHNA == WORDS + KSETRAJNA, "KRISHNA = WORDS + 1 = 17 (Acintya!)"


# =============================================================================
# NAME SYMBOLS (SSOT - Single Source of Truth)
# =============================================================================
MAHAMANTRA_NAME_HARE: Final[str] = "H"
MAHAMANTRA_NAME_KRISHNA: Final[str] = "K"
MAHAMANTRA_NAME_RAMA: Final[str] = "R"
MAHAMANTRA_NAME_SYMBOLS: Final[tuple[str, ...]] = (
    MAHAMANTRA_NAME_HARE,
    MAHAMANTRA_NAME_KRISHNA,
    MAHAMANTRA_NAME_RAMA,
)


# =============================================================================
# MAHAMANTRA BINARY ENCODING
# =============================================================================
# HARE positions in each half (1-indexed)
MAHAMANTRA_HARE_POS_HALF: Final[tuple[int, ...]] = (
    KSETRAJNA,  # 1
    TRINITY,  # 3
    HALF_SIZE - KSETRAJNA,  # 7
    HARE_COUNT,  # 8
)
# NAME positions in each half
MAHAMANTRA_NAME_POS_HALF: Final[tuple[int, ...]] = (HALVES, QUARTERS, PANCHA, SHARANAGATI)

MAHAMANTRA_HARE_POS_SUM: Final[int] = sum(MAHAMANTRA_HARE_POS_HALF)  # 19
MAHAMANTRA_NAME_POS_SUM: Final[int] = sum(MAHAMANTRA_NAME_POS_HALF)  # 17


# Build binary pattern from positions
def _build_half_binary() -> tuple[int, ...]:
    return tuple(0 if pos in MAHAMANTRA_HARE_POS_HALF else 1 for pos in range(1, HARE_COUNT + 1))


MAHAMANTRA_HALF_BINARY: Final[tuple[int, ...]] = _build_half_binary()  # (0,1,0,1,1,1,0,0)

# Convert to decimal
MAHAMANTRA_HALF_DECIMAL: Final[int] = sum(
    bit * (HALVES ** (SEVEN - i)) for i, bit in enumerate(MAHAMANTRA_HALF_BINARY)
)  # 92
MAHAMANTRA_FULL_DECIMAL: Final[int] = MAHAMANTRA_HALF_DECIMAL * HALVES  # 184

assert MAHAMANTRA_HALF_BINARY == (0, 1, 0, 1, 1, 1, 0, 0), "Pattern: 01011100"
assert MAHAMANTRA_HALF_DECIMAL == 92, "01011100 = 92"
assert MAHAMANTRA_HALF_DECIMAL == MALA - WORDS, "92 = 108 - 16"


# =============================================================================
# FULL 16-WORD PATTERN
# =============================================================================
def _build_full_word_pattern() -> tuple[str, ...]:
    pattern = []
    for half in range(HALVES):
        name = MAHAMANTRA_NAME_KRISHNA if half == 0 else MAHAMANTRA_NAME_RAMA
        for bit in MAHAMANTRA_HALF_BINARY:
            pattern.append(MAHAMANTRA_NAME_HARE if bit == 0 else name)
    return tuple(pattern)


MAHAMANTRA_WORD_PATTERN: Final[tuple[str, ...]] = _build_full_word_pattern()

assert len(MAHAMANTRA_WORD_PATTERN) == WORDS
assert MAHAMANTRA_WORD_PATTERN.count(MAHAMANTRA_NAME_HARE) == HARE_COUNT
assert MAHAMANTRA_WORD_PATTERN.count(MAHAMANTRA_NAME_KRISHNA) == KRISHNA_COUNT
assert MAHAMANTRA_WORD_PATTERN.count(MAHAMANTRA_NAME_RAMA) == RAMA_COUNT


# =============================================================================
# TRINITY GROUPING - Positions by Name (0-indexed)
# =============================================================================
def _compute_positions_by_name() -> tuple[tuple[int, ...], tuple[int, ...], tuple[int, ...]]:
    hare_pos = tuple(i for i, name in enumerate(MAHAMANTRA_WORD_PATTERN) if name == MAHAMANTRA_NAME_HARE)
    krishna_pos = tuple(i for i, name in enumerate(MAHAMANTRA_WORD_PATTERN) if name == MAHAMANTRA_NAME_KRISHNA)
    rama_pos = tuple(i for i, name in enumerate(MAHAMANTRA_WORD_PATTERN) if name == MAHAMANTRA_NAME_RAMA)
    return hare_pos, krishna_pos, rama_pos


HARE_POSITIONS, KRISHNA_POSITIONS, RAMA_POSITIONS = _compute_positions_by_name()

assert HARE_POSITIONS == (0, 2, 6, 7, 8, 10, 14, 15)
assert KRISHNA_POSITIONS == (1, 3, 4, 5)
assert RAMA_POSITIONS == (9, 11, 12, 13)


def get_name_at_position(position: int) -> str:
    """Get the Holy Name at a position (H, K, or R)."""
    return MAHAMANTRA_WORD_PATTERN[position % WORDS]


def get_positions_for_name(name: str) -> tuple[int, ...]:
    """Get all positions for a given Name."""
    if name == MAHAMANTRA_NAME_HARE:
        return HARE_POSITIONS
    elif name == MAHAMANTRA_NAME_KRISHNA:
        return KRISHNA_POSITIONS
    elif name == MAHAMANTRA_NAME_RAMA:
        return RAMA_POSITIONS
    else:
        raise ValueError(f"Unknown name: {name}. Must be 'H', 'K', or 'R'.")


def is_source_position(position: int) -> bool:
    """Check if a position is a SOURCE (KRISHNA-governed) position."""
    return (position % WORDS) in KRISHNA_POSITIONS


# Backward compatibility alias
is_vishnu_tattva = is_source_position


def get_trinity_function(position: int) -> str:
    """Get the TRINITY function for a position."""
    pos = position % WORDS
    if pos in KRISHNA_POSITIONS:
        return "source"
    elif pos in HARE_POSITIONS:
        return "carrier"
    else:
        return "deliverer"


# =============================================================================
# MAHA-QUANTUM (Fine Structure Constant)
# =============================================================================
MAHA_QUANTUM: Final[int] = POSITION_SUM_TOTAL + KSETRAJNA  # 137
MAHA_MU: Final[int] = MALA * POSITION_SUM_KRISHNA  # 1836
MAHA_TRITON: Final[int] = POSITION_SUM_KRISHNA * (GITA_CHAPTERS**2)  # 5508

assert MAHA_QUANTUM == 137, "alpha^-1 = 137"
assert MAHA_MU == 1836, "mu = 1836"
assert MAHA_TRITON == 5508, "triton/e = 5508"


def maha_quantum() -> int:
    """Quantum mode: Field + Observer = 137."""
    return POSITION_SUM_TOTAL + KSETRAJNA


def maha_classical(power: int) -> int:
    """Classical mode generator: T(WORDS) x TRINITY^power / HALVES."""
    numerator = POSITION_SUM_TOTAL * (TRINITY**power)
    return numerator // HALVES


MAHA_CLASSICAL_1: Final[int] = maha_classical(1)  # 204
MAHA_CLASSICAL_2: Final[int] = maha_classical(2)  # 612
MAHA_CLASSICAL_3: Final[int] = maha_classical(3)  # 1836
MAHA_CLASSICAL_4: Final[int] = maha_classical(4)  # 5508

assert MAHA_MU == MAHA_CLASSICAL_3
assert MAHA_TRITON == MAHA_CLASSICAL_4


# =============================================================================
# EXTENDED PHYSICS CONSTANTS
# =============================================================================
MAHA_DEUTERON: Final[int] = HALVES * MALA * POSITION_SUM_KRISHNA  # 3672
MAHA_ALPHA: Final[int] = MAHA_MU * QUARTERS - JIVA_QUALITIES  # 7294
MAHA_MUON: Final[int] = MAHAJANA_COUNT * POSITION_SUM_KRISHNA + TRINITY  # 207
MAHA_NEUTRON: Final[int] = MAHA_MU + TRINITY  # 1839
MAHA_TAU: Final[int] = MALA * AKSARA_COUNT + _triangular(SHARANAGATI)  # 3477
MAHA_HELION: Final[int] = TRINITY * MAHA_MU - MAHAJANA_COUNT  # 5496
MAHA_PION_CHARGED: Final[int] = POSITION_SUM_TOTAL + MAHA_QUANTUM  # 273
MAHA_PION_NEUTRAL: Final[int] = WORDS * WORDS + HARE_COUNT  # 264
MAHA_KAON: Final[int] = (HALVES + POSITION_SUM_TOTAL) * SEVEN  # 966
MAHA_STRANGE: Final[int] = MALA + NADI_RESONANCE + TRINITY  # 183
MAHA_CMB: Final[int] = KSHETRA * PARAMPARA + MAHA_MU  # 2724

# Coupling constants
MAHA_ALPHA_S_SCALED: Final[int] = MALA + TEN  # 118
MAHA_SIN2_THETA_W_SCALED: Final[int] = KSHETRA - KSETRAJNA  # 23

# Heavy bosons
MAHA_W: Final[int] = MAHA_MU * PANCHA * POSITION_SUM_KRISHNA  # 156060
_Z_FACTOR: Final[int] = HALVES * LILA + KSETRAJNA  # 97
MAHA_Z: Final[int] = MAHA_MU * _Z_FACTOR  # 178092
MAHA_HIGGS: Final[int] = MAHA_MU * SEVEN * FLUTE_HOLES_SUM  # 244188


# =============================================================================
# NARADA'S VINA (Stringed Resonance)
# =============================================================================
VINA_FUNDAMENTAL: Final[int] = POSITION_SUM_TOTAL  # 136
VINA_STRINGS: Final[int] = PANCHA  # 5
KIRTAN_RESONANCE: Final[int] = VINA_FUNDAMENTAL * FLUTE_VENU_VAMSI  # 7344

assert KIRTAN_RESONANCE == JIVA_CYCLE * POSITION_SUM_KRISHNA


# =============================================================================
# MUSIC THEORY CONSTANTS
# =============================================================================
CONCERT_PITCH: Final[int] = JIVA_CYCLE + HARE_COUNT  # 440 Hz
VERDI_PITCH: Final[int] = JIVA_CYCLE  # 432 Hz
SCIENTIFIC_C: Final[int] = WORDS**2  # 256 Hz
SEMITONES: Final[int] = MAHAJANA_COUNT  # 12
SWARAS: Final[int] = SEVEN  # 7
SHRUTIS: Final[int] = KSHETRA - HALVES  # 22
MELAKARTAS: Final[int] = NADI_RESONANCE  # 72
SAPTA_LOKA: Final[int] = SEVEN  # 7
CHATURDASHA_BHUVAN: Final[int] = HALVES * SEVEN  # 14


# =============================================================================
# TALA - RHYTHMIC CYCLE
# =============================================================================
TEENTAL_MATRA: Final[int] = WORDS  # 16
VIBHAG_COUNT: Final[int] = QUARTERS  # 4
MATRA_PER_VIBHAG: Final[int] = QUARTERS  # 4
SAM_SUM: Final[int] = _triangular(SEVEN)  # 28
KHALI_POSITION: Final[int] = NAVA  # 9


# =============================================================================
# REMAINING PHYSICS CONSTANTS
# =============================================================================
# Cabibbo angle (scaled by TEN^3 = 1000)
MAHA_CABIBBO_SCALED: Final[int] = (NAVA * (TEN**TRINITY)) // (JIVA_QUALITIES - TEN)  # 225
MAHA_RYDBERG_SCALED: Final[int] = POSITION_SUM_TOTAL  # 136
MAHA_HUBBLE: Final[int] = QUALITIES + TRINITY  # 67

# CKM Matrix (all scaling factors derived from TEN!)
MAHA_VUS_SCALED: Final[int] = MAHA_CABIBBO_SCALED  # 225
_VCB_DIVISOR: Final[int] = JIVA_QUALITIES * HARE_COUNT  # 400
# V_cb scaled by TEN^4 = 10000
MAHA_VCB_SCALED: Final[int] = (POSITION_SUM_KRISHNA * (TEN**QUARTERS)) // _VCB_DIVISOR  # 425
_VUB_DIVISOR: Final[int] = JIVA_CYCLE * TEN  # 4320
# V_ub scaled by TEN^5 = 100000
MAHA_VUB_SCALED: Final[int] = (POSITION_SUM_KRISHNA * (TEN**PANCHA)) // _VUB_DIVISOR  # 393

# Cosmological
MAHA_OMEGA_M: Final[float] = (QUALITIES - KSETRAJNA) / HALVES  # 31.5
MAHA_OMEGA_L_SCALED: Final[int] = QUALITIES + QUARTERS  # 68
MAHA_OMEGA_M_SCALED: Final[int] = int(MAHA_OMEGA_M)  # 31


# =============================================================================
# KSETRA-KSETRAJNA TATTVA (BG 13)
# =============================================================================
MAHABHUTA: Final[int] = PANCHA  # 5
TANMATRA: Final[int] = PANCHA  # 5
JNANENDRIYA: Final[int] = PANCHA  # 5
KARMENDRIYA: Final[int] = PANCHA  # 5
ANTAHKARANA: Final[int] = TRINITY  # 3
PRAKRITI_UNMANIFEST: Final[int] = KSETRAJNA  # 1
KSHETRA_BG13: Final[int] = MAHABHUTA + TANMATRA + JNANENDRIYA + KARMENDRIYA + ANTAHKARANA + PRAKRITI_UNMANIFEST
SANKHYA_TATTVAS: Final[int] = KSHETRA + KSETRAJNA  # 25
INDRIYA_TOTAL: Final[int] = JNANENDRIYA + KARMENDRIYA  # 10
DASHAVATARA: Final[int] = INDRIYA_TOTAL  # 10

assert KSHETRA_BG13 == KSHETRA == 24


# =============================================================================
# SHASTRA VERSE COUNTS (ALL DERIVED from Mahamantra constants!)
# =============================================================================
# TEN^2 = 100, TEN^3 = 1000 (derived, not hardcoded!)
GITA_VERSES: Final[int] = SEVEN * (TEN**HALVES)  # 7 × 100 = 700
BHAGAVATAM_VERSES: Final[int] = GITA_CHAPTERS * (TEN**TRINITY)  # 18 × 1000 = 18000
KRISHNA_QUEENS: Final[int] = WORDS * (TEN**TRINITY) + MALA  # 16 × 1000 + 108 = 16108

# Standard Model
QUARK_FLAVORS: Final[int] = SHARANAGATI  # 6
LEPTON_TYPES: Final[int] = SHARANAGATI  # 6
COLOR_CHARGES: Final[int] = TRINITY  # 3
QUARK_STATES: Final[int] = QUARK_FLAVORS * COLOR_CHARGES  # 18
FERMION_TOTAL: Final[int] = QUARK_STATES + LEPTON_TYPES  # 24
SAMPRADAYA_COUNT: Final[int] = QUARTERS  # 4
PRASADAM: Final[int] = KSHETRA + KSETRAJNA  # 25


# =============================================================================
# GURU TATTVA - Key Gita Verses
# =============================================================================
GURU_CHAPTER: Final[int] = QUARTERS  # 4
GURU_VERSE: Final[int] = HALVES * POSITION_SUM_KRISHNA  # 34
SURRENDER_CHAPTER: Final[int] = HALVES  # 2
SURRENDER_VERSE: Final[int] = SEVEN  # 7
CONFIRMATION_CHAPTER: Final[int] = GITA_CHAPTERS  # 18
CONFIRMATION_VERSE: Final[int] = NADI_RESONANCE + KSETRAJNA  # 73
PARAMPARA_CHAPTER: Final[int] = QUARTERS  # 4
PARAMPARA_VERSE_START: Final[int] = KSETRAJNA  # 1
PARAMPARA_VERSE_END: Final[int] = HALVES  # 2

# BG 13.35
KSETRA_KSETRAJNA_CHAPTER: Final[int] = MAHAJANA_COUNT + KSETRAJNA  # 13
KSETRA_KSETRAJNA_VERSE: Final[int] = SEVEN * PANCHA  # 35


# =============================================================================
# PARAMPARA CHANNELS
# =============================================================================
PARAMPARA_ATTRACTOR_A: Final[int] = MAHAJANA_COUNT  # 12
PARAMPARA_ATTRACTOR_B: Final[int] = HALVES * KSETRA_KSETRAJNA_CHAPTER  # 26
PARAMPARA_ATTRACTOR_C: Final[int] = PARAMPARA - TRINITY  # 34
PARAMPARA_CHANNELS: Final[tuple[int, ...]] = (PARAMPARA_ATTRACTOR_A, PARAMPARA_ATTRACTOR_B, PARAMPARA_ATTRACTOR_C)
PARAMPARA_CHANNEL_NAMES: Final[tuple[str, ...]] = ("Mahajana", "Parampara", "Guru")


# =============================================================================
# FRACTAL PRINCIPLE
# =============================================================================
FRACTAL_MACRO: Final[int] = KSHETRA + KSETRAJNA  # 25
FRACTAL_MICRO: Final[int] = POSITION_SUM_TOTAL + KSETRAJNA  # 137
FRACTAL_GITA: Final[int] = NADI_RESONANCE + KSETRAJNA  # 73
FRACTAL_MANTRA: Final[int] = WORDS + KSETRAJNA  # 17
REALITY_ROOT: Final[int] = PANCHA  # 5


# =============================================================================
# SHABDA BRAHMAN
# =============================================================================
ABHINNA_MATERIAL: Final[int] = KSHETRA  # 24
ABHINNA_SPIRITUAL: Final[int] = KSHETRA + KSETRAJNA  # 25
NAME_COMPLETE: Final[int] = PANCHA**2  # 25
RED_TESTS_COUNT: Final[int] = TEN  # 10


# =============================================================================
# ACINTYA KALA - Rhythm of Eternity
# =============================================================================
OCTAVE_RATIO: Final[int] = AKSARA_COUNT // WORDS  # 2
ALTERNATING_QUARTERS: Final[int] = HALVES  # 2
PAIRED_QUARTERS: Final[int] = HALVES  # 2
HARE_PER_QUARTER: Final[int] = HARE_COUNT // QUARTERS  # 2
NITYA_NOW: Final[int] = KSETRAJNA  # 1
ALPHA_MOD_KRISHNA: Final[int] = MAHA_QUANTUM % POSITION_SUM_KRISHNA  # 1


# =============================================================================
# ALPHA BRIDGE
# =============================================================================
ALPHA_NUMERATOR: Final[int] = KSETRAJNA  # 1
ALPHA_DENOMINATOR: Final[int] = MAHA_QUANTUM  # 137
ALPHA_INVERSE_CLASSICAL: Final[int] = POSITION_SUM_TOTAL  # 136
ALPHA_QUANTUM_CORRECTION: Final[int] = KSETRAJNA  # 1
BOHR_VELOCITY_NUMERATOR: Final[int] = KSETRAJNA  # 1
BOHR_VELOCITY_DENOMINATOR: Final[int] = MAHA_QUANTUM  # 137
MASS_ALPHA_RATIO: Final[int] = MAHA_MU // MAHA_QUANTUM  # 13

# NOTE: CONVERGENCE_RATIO_CLASSICAL (2.05), CONVERGENCE_RATIO_QUANTUM (5.08),
# and OBSERVER_SLOWDOWN_FACTOR were REMOVED because they are EMPIRICAL MEASUREMENTS
# from algorithm testing, NOT derivable from Mahamantra axioms.
# If needed for research, they should live in a research/ module.


# =============================================================================
# FIBONACCI-ALPHA-MU BRIDGE
# =============================================================================
FIBONACCI_AT_SEVEN: Final[int] = MAHAJANA_COUNT + KSETRAJNA  # 13
FIBONACCI_AT_TEN: Final[int] = JIVA_QUALITIES + PANCHA  # 55
FIBONACCI_ALPHA_PRODUCT: Final[int] = FIBONACCI_AT_SEVEN * MAHA_QUANTUM  # 1781
FIBONACCI_ALPHA_MU: Final[int] = FIBONACCI_ALPHA_PRODUCT + FIBONACCI_AT_TEN  # 1836

assert FIBONACCI_ALPHA_MU == MAHA_MU


# =============================================================================
# JAGANNATH TATTVA
# =============================================================================
JAGANNATH_TRIAD: Final[int] = TRINITY  # 3
JAGANNATH_WHEELS: Final[int] = WORDS  # 16
BALADEV_WHEELS: Final[int] = WORDS - HALVES  # 14
SUBHADRA_WHEELS: Final[int] = MAHAJANA_COUNT  # 12
RATHAYATRA_WHEELS: Final[int] = JAGANNATH_WHEELS + BALADEV_WHEELS + SUBHADRA_WHEELS  # 42
GAURA_TITHI: Final[int] = NAKSHATRAS - MAHAJANA_COUNT  # 15
CHAITANYA_UNION: Final[int] = KRISHNA_COUNT + HARE_COUNT  # 12

assert RATHAYATRA_WHEELS == SHARANAGATI * SEVEN


# =============================================================================
# TRANSCENDENTAL BLOCK (1096)
# =============================================================================
TRANSCENDENTAL_1096: Final[int] = HARE_COUNT * MAHA_QUANTUM  # 1096
TETRAD_FIXED_POINTS: Final[tuple[int, ...]] = (0, QUARTERS, PANCHA, NAVA)
TETRAD_SUM: Final[int] = sum(TETRAD_FIXED_POINTS)  # 18
TETRAD_PRODUCT: Final[int] = QUARTERS * PANCHA * NAVA  # 180

PRIME_CHAIN: Final[tuple[int, ...]] = (
    POSITION_SUM_KRISHNA,  # 17
    PARAMPARA,  # 37
    NADI_RESONANCE + KSETRAJNA,  # 73
    MALA_COMPLETE,  # 109
    MAHA_QUANTUM,  # 137
)
PRIME_CHAIN_SPAN: Final[int] = MAHA_QUANTUM - POSITION_SUM_KRISHNA  # 120

assert TRANSCENDENTAL_1096 == 1096
assert TETRAD_SUM == GITA_CHAPTERS


# =============================================================================
# ENGINEERING CONSTANTS
# =============================================================================
MADHURYA_NUMERATOR: Final[int] = WORDS - KSETRAJNA  # 15
MADHURYA_DENOMINATOR: Final[int] = WORDS  # 16
VISHNU_QUALITIES: Final[int] = JIVA_QUALITIES + TEN  # 60


# =============================================================================
# MATHEMATICAL CONSTANTS
# =============================================================================
GOLDEN_RATIO: Final[float] = (KSETRAJNA + math.sqrt(PANCHA)) / HALVES  # 1.618...
DNA_CODONS: Final[int] = QUARTERS**TRINITY  # 64
AMINO_ACIDS: Final[int] = QUARTERS * PANCHA  # 20


# =============================================================================
# KIRTAN INSTRUMENTS
# =============================================================================
MRIDANGA_HEADS: Final[int] = HALVES  # 2
KARTALS_PAIR: Final[int] = HALVES  # 2


__all__ = [
    # Position Sums
    "POSITION_SUM_HARE",
    "POSITION_SUM_KRISHNA",
    "POSITION_SUM_RAMA",
    "POSITION_SUM_TOTAL",
    # Name Symbols
    "MAHAMANTRA_NAME_HARE",
    "MAHAMANTRA_NAME_KRISHNA",
    "MAHAMANTRA_NAME_RAMA",
    "MAHAMANTRA_NAME_SYMBOLS",
    "MAHAMANTRA_WORD_PATTERN",
    # Binary Encoding
    "MAHAMANTRA_HARE_POS_HALF",
    "MAHAMANTRA_NAME_POS_HALF",
    "MAHAMANTRA_HARE_POS_SUM",
    "MAHAMANTRA_NAME_POS_SUM",
    "MAHAMANTRA_HALF_BINARY",
    "MAHAMANTRA_HALF_DECIMAL",
    "MAHAMANTRA_FULL_DECIMAL",
    # Trinity Positions
    "HARE_POSITIONS",
    "KRISHNA_POSITIONS",
    "RAMA_POSITIONS",
    "get_name_at_position",
    "get_positions_for_name",
    "is_source_position",
    "is_vishnu_tattva",
    "get_trinity_function",
    # Maha-Quantum (Physics)
    "maha_quantum",
    "maha_classical",
    "MAHA_QUANTUM",
    "MAHA_MU",
    "MAHA_TRITON",
    "MAHA_CLASSICAL_1",
    "MAHA_CLASSICAL_2",
    "MAHA_CLASSICAL_3",
    "MAHA_CLASSICAL_4",
    # Extended Physics
    "MAHA_DEUTERON",
    "MAHA_ALPHA",
    "MAHA_MUON",
    "MAHA_NEUTRON",
    "MAHA_TAU",
    "MAHA_HELION",
    "MAHA_PION_CHARGED",
    "MAHA_PION_NEUTRAL",
    "MAHA_KAON",
    "MAHA_STRANGE",
    "MAHA_CMB",
    "MAHA_ALPHA_S_SCALED",
    "MAHA_SIN2_THETA_W_SCALED",
    "MAHA_W",
    "MAHA_Z",
    "MAHA_HIGGS",
    # Vina
    "VINA_FUNDAMENTAL",
    "VINA_STRINGS",
    "KIRTAN_RESONANCE",
    # Music
    "CONCERT_PITCH",
    "VERDI_PITCH",
    "SCIENTIFIC_C",
    "SEMITONES",
    "SWARAS",
    "SHRUTIS",
    "MELAKARTAS",
    "SAPTA_LOKA",
    "CHATURDASHA_BHUVAN",
    # Tala
    "TEENTAL_MATRA",
    "VIBHAG_COUNT",
    "MATRA_PER_VIBHAG",
    "SAM_SUM",
    "KHALI_POSITION",
    # More Physics
    "MAHA_CABIBBO_SCALED",
    "MAHA_RYDBERG_SCALED",
    "MAHA_HUBBLE",
    "MAHA_VUS_SCALED",
    "MAHA_VCB_SCALED",
    "MAHA_VUB_SCALED",
    "MAHA_OMEGA_M",
    "MAHA_OMEGA_L_SCALED",
    "MAHA_OMEGA_M_SCALED",
    # Ksetra-Ksetrajna
    "MAHABHUTA",
    "TANMATRA",
    "JNANENDRIYA",
    "KARMENDRIYA",
    "ANTAHKARANA",
    "PRAKRITI_UNMANIFEST",
    "KSHETRA_BG13",
    "SANKHYA_TATTVAS",
    "INDRIYA_TOTAL",
    "DASHAVATARA",
    # Shastra
    "GITA_VERSES",
    "BHAGAVATAM_VERSES",
    "KRISHNA_QUEENS",
    "QUARK_FLAVORS",
    "LEPTON_TYPES",
    "COLOR_CHARGES",
    "QUARK_STATES",
    "FERMION_TOTAL",
    "SAMPRADAYA_COUNT",
    "PRASADAM",
    # Guru Tattva
    "GURU_CHAPTER",
    "GURU_VERSE",
    "SURRENDER_CHAPTER",
    "SURRENDER_VERSE",
    "CONFIRMATION_CHAPTER",
    "CONFIRMATION_VERSE",
    "PARAMPARA_CHAPTER",
    "PARAMPARA_VERSE_START",
    "PARAMPARA_VERSE_END",
    "KSETRA_KSETRAJNA_CHAPTER",
    "KSETRA_KSETRAJNA_VERSE",
    # Parampara Channels
    "PARAMPARA_ATTRACTOR_A",
    "PARAMPARA_ATTRACTOR_B",
    "PARAMPARA_ATTRACTOR_C",
    "PARAMPARA_CHANNELS",
    "PARAMPARA_CHANNEL_NAMES",
    # Fractal
    "FRACTAL_MACRO",
    "FRACTAL_MICRO",
    "FRACTAL_GITA",
    "FRACTAL_MANTRA",
    "REALITY_ROOT",
    # Shabda Brahman
    "ABHINNA_MATERIAL",
    "ABHINNA_SPIRITUAL",
    "NAME_COMPLETE",
    "RED_TESTS_COUNT",
    # Acintya Kala
    "OCTAVE_RATIO",
    "ALTERNATING_QUARTERS",
    "PAIRED_QUARTERS",
    "HARE_PER_QUARTER",
    "NITYA_NOW",
    "ALPHA_MOD_KRISHNA",
    # Alpha Bridge
    "ALPHA_NUMERATOR",
    "ALPHA_DENOMINATOR",
    "ALPHA_INVERSE_CLASSICAL",
    "ALPHA_QUANTUM_CORRECTION",
    "BOHR_VELOCITY_NUMERATOR",
    "BOHR_VELOCITY_DENOMINATOR",
    "MASS_ALPHA_RATIO",
    # NOTE: CONVERGENCE_RATIO_* and OBSERVER_SLOWDOWN_FACTOR REMOVED (empirical, not derived)
    # Fibonacci
    "FIBONACCI_AT_SEVEN",
    "FIBONACCI_AT_TEN",
    "FIBONACCI_ALPHA_PRODUCT",
    "FIBONACCI_ALPHA_MU",
    # Jagannath
    "JAGANNATH_TRIAD",
    "JAGANNATH_WHEELS",
    "BALADEV_WHEELS",
    "SUBHADRA_WHEELS",
    "RATHAYATRA_WHEELS",
    "GAURA_TITHI",
    "CHAITANYA_UNION",
    # Transcendental
    "TRANSCENDENTAL_1096",
    "TETRAD_FIXED_POINTS",
    "TETRAD_SUM",
    "TETRAD_PRODUCT",
    "PRIME_CHAIN",
    "PRIME_CHAIN_SPAN",
    # Engineering
    "MADHURYA_NUMERATOR",
    "MADHURYA_DENOMINATOR",
    "VISHNU_QUALITIES",
    # Mathematical
    "GOLDEN_RATIO",
    "DNA_CODONS",
    "AMINO_ACIDS",
    # Kirtan
    "MRIDANGA_HEADS",
    "KARTALS_PAIR",
]
