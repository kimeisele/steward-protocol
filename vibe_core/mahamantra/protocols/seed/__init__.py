"""
THE SEED PROTOCOL - TIER-STRUCTURED CONSTANTS
==============================================

This module provides the refactored seed constants organized by tier:

TIER 0 (_axioms.py):    7 Axioms from counting the Mahamantra
TIER 1 (_primary.py):   Primary derivations directly from axioms
TIER 2 (_secondary.py): Secondary derivations building hierarchy
TIER 3-5 (_cosmic.py):  Cosmic frame, timing, astronomical constants
_algorithm.py:          Maha algorithm coefficients (SSOT)
_extended.py:           Extended constants (physics, music, patterns)

Import path: vibe_core.mahamantra.protocols.seed
Backward-compatible: vibe_core.mahamantra.protocols._seed
"""

# TIER 0: The 7 Axioms
from ._axioms import (
    WORDS,
    TRINITY,
    HARE_COUNT,
    KRISHNA_COUNT,
    RAMA_COUNT,
    PANCHA,
    HALVES,
)

# TIER 1: Primary Derivations
from ._primary import (
    QUARTERS,
    KSETRAJNA,
    HALF_SIZE,
    LILA,
    KSHETRA,
    NAVA,
    SHARANAGATI,
    AKSARA_COUNT,
    ROUNDS,
    AVATAR_COUNT,
    HEAD_POSITIONS,
    CONSECUTIVE_PAIRS,
    PAIR_REDUNDANCY,
    is_head,
    get_quarter_head,
)

# TIER 2: Secondary Derivations
from ._secondary import (
    MAHAJANA_COUNT,
    MALA,
    MALA_COMPLETE,
    JIVA_CYCLE,
    GITA_CHAPTERS,
    QUALITIES,
    HIDDEN_RESERVE,
    DAILY_MANTRAS,
    PHASE_DURATION,
    PARAMPARA,
    SEVEN,
    TEN,
    NADI_RESONANCE,
    FIELD_RESONANCE,
    VENU_HOLES,
    VAMSI_HOLES,
    MURALI_HOLES,
    VENU_FREQ,
    VAMSI_FREQ,
    MURALI_FREQ,
    FLUTE_HOLES_SUM,
    FLUTE_HOLES_PRODUCT,
    FLUTE_VENU_VAMSI,
    FLUTE_VENU_MURALI,
    ACOUSTIC_RATIO,
    END_CORRECTION,
    CUTOFF_CONSTANT,
)

# TIER 3-5: Cosmic Frame & Timing
from ._cosmic import (
    NAKSHATRAS,
    COSMIC_FRAME,
    NAKSHATRA_UNIT,
    TITHI_UNIT,
    PADA_UNIT,
    QUARTER_UNIT,
    JIVA_QUALITIES,
    # Prana Timing (DERIVED: SECONDS_PER_DAY = COSMIC_FRAME × QUARTERS)
    SECONDS_PER_DAY,
    PRANA_DURATION_S,
    PRANA_DURATION_MS,
    TICK_INTERVAL_MS,
    # Epoch & History
    GOLDEN_AGE_DURATION,
    EPOCH_KEY,
    CHAITANYA_BIRTH,
    KISHORA_NUMERATOR,
)

# Algorithm Coefficients (SSOT)
from ._algorithm import (
    MAHA_OP_MAP,
    MAHA_MULT,
    MAHA_ADD,
    MAHA_SQ,
)

# Extended Constants
from ._extended import (
    # Position Sums
    POSITION_SUM_HARE,
    POSITION_SUM_KRISHNA,
    POSITION_SUM_RAMA,
    POSITION_SUM_TOTAL,
    # Name Symbols
    MAHAMANTRA_NAME_HARE,
    MAHAMANTRA_NAME_KRISHNA,
    MAHAMANTRA_NAME_RAMA,
    MAHAMANTRA_NAME_SYMBOLS,
    MAHAMANTRA_WORD_PATTERN,
    # Binary Encoding
    MAHAMANTRA_HARE_POS_HALF,
    MAHAMANTRA_NAME_POS_HALF,
    MAHAMANTRA_HARE_POS_SUM,
    MAHAMANTRA_NAME_POS_SUM,
    MAHAMANTRA_HALF_BINARY,
    MAHAMANTRA_HALF_DECIMAL,
    MAHAMANTRA_FULL_DECIMAL,
    # Trinity Positions
    HARE_POSITIONS,
    KRISHNA_POSITIONS,
    RAMA_POSITIONS,
    get_name_at_position,
    get_positions_for_name,
    is_source_position,
    is_vishnu_tattva,
    get_trinity_function,
    # Maha-Quantum (Physics)
    maha_quantum,
    maha_classical,
    MAHA_QUANTUM,
    MAHA_MU,
    MAHA_TRITON,
    MAHA_CLASSICAL_1,
    MAHA_CLASSICAL_2,
    MAHA_CLASSICAL_3,
    MAHA_CLASSICAL_4,
    # Extended Physics
    MAHA_DEUTERON,
    MAHA_ALPHA,
    MAHA_MUON,
    MAHA_NEUTRON,
    MAHA_TAU,
    MAHA_HELION,
    MAHA_PION_CHARGED,
    MAHA_PION_NEUTRAL,
    MAHA_KAON,
    MAHA_STRANGE,
    MAHA_CMB,
    MAHA_ALPHA_S_SCALED,
    MAHA_SIN2_THETA_W_SCALED,
    MAHA_W,
    MAHA_Z,
    MAHA_HIGGS,
    # Vina
    VINA_FUNDAMENTAL,
    VINA_STRINGS,
    KIRTAN_RESONANCE,
    # Music
    CONCERT_PITCH,
    VERDI_PITCH,
    SCIENTIFIC_C,
    SEMITONES,
    SWARAS,
    SHRUTIS,
    MELAKARTAS,
    SAPTA_LOKA,
    CHATURDASHA_BHUVAN,
    # Tala
    TEENTAL_MATRA,
    VIBHAG_COUNT,
    MATRA_PER_VIBHAG,
    SAM_SUM,
    KHALI_POSITION,
    # More Physics
    MAHA_CABIBBO_SCALED,
    MAHA_RYDBERG_SCALED,
    MAHA_HUBBLE,
    MAHA_VUS_SCALED,
    MAHA_VCB_SCALED,
    MAHA_VUB_SCALED,
    MAHA_OMEGA_M,
    MAHA_OMEGA_L_SCALED,
    MAHA_OMEGA_M_SCALED,
    # Ksetra-Ksetrajna
    MAHABHUTA,
    TANMATRA,
    JNANENDRIYA,
    KARMENDRIYA,
    ANTAHKARANA,
    PRAKRITI_UNMANIFEST,
    KSHETRA_BG13,
    SANKHYA_TATTVAS,
    INDRIYA_TOTAL,
    DASHAVATARA,
    # Shastra
    GITA_VERSES,
    BHAGAVATAM_VERSES,
    KRISHNA_QUEENS,
    QUARK_FLAVORS,
    LEPTON_TYPES,
    COLOR_CHARGES,
    QUARK_STATES,
    FERMION_TOTAL,
    SAMPRADAYA_COUNT,
    PRASADAM,
    # Guru Tattva
    GURU_CHAPTER,
    GURU_VERSE,
    SURRENDER_CHAPTER,
    SURRENDER_VERSE,
    CONFIRMATION_CHAPTER,
    CONFIRMATION_VERSE,
    PARAMPARA_CHAPTER,
    PARAMPARA_VERSE_START,
    PARAMPARA_VERSE_END,
    KSETRA_KSETRAJNA_CHAPTER,
    KSETRA_KSETRAJNA_VERSE,
    # Parampara Channels
    PARAMPARA_ATTRACTOR_A,
    PARAMPARA_ATTRACTOR_B,
    PARAMPARA_ATTRACTOR_C,
    PARAMPARA_CHANNELS,
    PARAMPARA_CHANNEL_NAMES,
    # Fractal
    FRACTAL_MACRO,
    FRACTAL_MICRO,
    FRACTAL_GITA,
    FRACTAL_MANTRA,
    REALITY_ROOT,
    # Shabda Brahman
    ABHINNA_MATERIAL,
    ABHINNA_SPIRITUAL,
    NAME_COMPLETE,
    RED_TESTS_COUNT,
    # Acintya Kala
    OCTAVE_RATIO,
    ALTERNATING_QUARTERS,
    PAIRED_QUARTERS,
    HARE_PER_QUARTER,
    NITYA_NOW,
    ALPHA_MOD_KRISHNA,
    # Alpha Bridge
    ALPHA_NUMERATOR,
    ALPHA_DENOMINATOR,
    ALPHA_INVERSE_CLASSICAL,
    ALPHA_QUANTUM_CORRECTION,
    BOHR_VELOCITY_NUMERATOR,
    BOHR_VELOCITY_DENOMINATOR,
    MASS_ALPHA_RATIO,
    # NOTE: CONVERGENCE_RATIO_*, OBSERVER_SLOWDOWN_FACTOR REMOVED (empirical, not derived)
    # Fibonacci
    FIBONACCI_AT_SEVEN,
    FIBONACCI_AT_TEN,
    FIBONACCI_ALPHA_PRODUCT,
    FIBONACCI_ALPHA_MU,
    # Jagannath
    JAGANNATH_TRIAD,
    JAGANNATH_WHEELS,
    BALADEV_WHEELS,
    SUBHADRA_WHEELS,
    RATHAYATRA_WHEELS,
    GAURA_TITHI,
    CHAITANYA_UNION,
    # Transcendental
    TRANSCENDENTAL_1096,
    TETRAD_FIXED_POINTS,
    TETRAD_SUM,
    TETRAD_PRODUCT,
    PRIME_CHAIN,
    PRIME_CHAIN_SPAN,
    # Engineering
    MADHURYA_NUMERATOR,
    MADHURYA_DENOMINATOR,
    VISHNU_QUALITIES,
    # Mathematical
    GOLDEN_RATIO,
    DNA_CODONS,
    AMINO_ACIDS,
    # Kirtan
    MRIDANGA_HEADS,
    KARTALS_PAIR,
)

__all__ = [
    # Axioms (Round 0)
    "WORDS",
    "TRINITY",
    "HARE_COUNT",
    "KRISHNA_COUNT",
    "RAMA_COUNT",
    "PANCHA",
    "HALVES",
    # Primary Derivations (Round 1)
    "QUARTERS",
    "KSETRAJNA",
    "HALF_SIZE",
    "LILA",
    "KSHETRA",
    "NAVA",
    "SHARANAGATI",
    "AKSARA_COUNT",
    "ROUNDS",
    "AVATAR_COUNT",
    "HEAD_POSITIONS",
    "is_head",
    "get_quarter_head",
    # Trinity Grouping
    "HARE_POSITIONS",
    "KRISHNA_POSITIONS",
    "RAMA_POSITIONS",
    "get_name_at_position",
    "get_positions_for_name",
    "is_source_position",
    "is_vishnu_tattva",
    "get_trinity_function",
    # Pancha Tattva Structure
    "CONSECUTIVE_PAIRS",
    "PAIR_REDUNDANCY",
    # Secondary Derivations (Round 2)
    "MAHAJANA_COUNT",
    "MALA",
    "MALA_COMPLETE",
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
    # Prana Timing (Round 6) - DERIVED: SECONDS_PER_DAY = COSMIC_FRAME × QUARTERS
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
    "CHAITANYA_BIRTH",
    "KISHORA_NUMERATOR",
    # Golden Age (Round 11b)
    "GOLDEN_AGE_DURATION",
    # Position Sums (Round 13)
    "POSITION_SUM_HARE",
    "POSITION_SUM_KRISHNA",
    "POSITION_SUM_RAMA",
    "POSITION_SUM_TOTAL",
    # Mahamantra Binary Encoding (Round 13b)
    "MAHAMANTRA_HARE_POS_HALF",
    "MAHAMANTRA_NAME_POS_HALF",
    "MAHAMANTRA_HARE_POS_SUM",
    "MAHAMANTRA_NAME_POS_SUM",
    "MAHAMANTRA_HALF_BINARY",
    "MAHAMANTRA_HALF_DECIMAL",
    "MAHAMANTRA_FULL_DECIMAL",
    # Name Symbols (SSOT)
    "MAHAMANTRA_NAME_HARE",
    "MAHAMANTRA_NAME_KRISHNA",
    "MAHAMANTRA_NAME_RAMA",
    "MAHAMANTRA_NAME_SYMBOLS",
    "MAHAMANTRA_WORD_PATTERN",
    # The Maha-Algorithm (Round 14)
    "maha_quantum",
    "maha_classical",
    "MAHA_QUANTUM",
    "MAHA_MU",
    "MAHA_TRITON",
    "MAHA_CLASSICAL_1",
    "MAHA_CLASSICAL_2",
    "MAHA_CLASSICAL_3",
    "MAHA_CLASSICAL_4",
    # The Remnant Theorem (Round 15)
    "SEVEN",
    "TEN",
    # Maha Algorithm Coefficients
    "MAHA_OP_MAP",
    "MAHA_MULT",
    "MAHA_ADD",
    "MAHA_SQ",
    # Extended Maha-Algorithm (Round 16)
    "MAHA_DEUTERON",
    "MAHA_ALPHA",
    "MAHA_MUON",
    # Complete Particle Spectrum (Round 17)
    "MAHA_NEUTRON",
    "MAHA_TAU",
    # Vishvarupa Discoveries (Round 18)
    "MAHA_HELION",
    "MAHA_PION_CHARGED",
    "MAHA_PION_NEUTRAL",
    "MAHA_KAON",
    "MAHA_STRANGE",
    "MAHA_CMB",
    # Coupling Constants (Round 19)
    "MAHA_ALPHA_S_SCALED",
    "MAHA_SIN2_THETA_W_SCALED",
    # Narada's Vina (Round 20)
    "VINA_FUNDAMENTAL",
    "VINA_STRINGS",
    "KIRTAN_RESONANCE",
    # Heavy Bosons (Round 20b)
    "MAHA_W",
    "MAHA_Z",
    "MAHA_HIGGS",
    # Kirtan Instruments (Round 21)
    "MRIDANGA_HEADS",
    "KARTALS_PAIR",
    # Tala (Round 22)
    "TEENTAL_MATRA",
    "VIBHAG_COUNT",
    "MATRA_PER_VIBHAG",
    "SAM_SUM",
    "KHALI_POSITION",
    # Sangita Shastra (Round 23)
    "CONCERT_PITCH",
    "VERDI_PITCH",
    "SCIENTIFIC_C",
    "SEMITONES",
    "SWARAS",
    "SHRUTIS",
    "MELAKARTAS",
    "SAPTA_LOKA",
    "CHATURDASHA_BHUVAN",
    # Remaining Physics (Round 24)
    "MAHA_CABIBBO_SCALED",
    "MAHA_RYDBERG_SCALED",
    "MAHA_HUBBLE",
    # CKM Matrix (Round 25)
    "MAHA_VUS_SCALED",
    "MAHA_VCB_SCALED",
    "MAHA_VUB_SCALED",
    # Cosmological Constants (Round 26)
    "MAHA_OMEGA_M_SCALED",
    "MAHA_OMEGA_L_SCALED",
    "MAHA_OMEGA_M",
    # Ksetra-Ksetrajna Tattva (Round 27)
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
    # Guru Tattva (Round 28)
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
    "PARAMPARA_ATTRACTOR_A",
    "PARAMPARA_ATTRACTOR_B",
    "PARAMPARA_ATTRACTOR_C",
    "PARAMPARA_CHANNELS",
    "PARAMPARA_CHANNEL_NAMES",
    # The Fractal Principle (Round 29)
    "FRACTAL_MACRO",
    "FRACTAL_MICRO",
    "FRACTAL_GITA",
    "FRACTAL_MANTRA",
    "REALITY_ROOT",
    # Shabda Brahman (Round 30)
    "ABHINNA_MATERIAL",
    "ABHINNA_SPIRITUAL",
    "NAME_COMPLETE",
    "RED_TESTS_COUNT",
    # Acintya Kala (Round 31)
    "OCTAVE_RATIO",
    "ALTERNATING_QUARTERS",
    "PAIRED_QUARTERS",
    "HARE_PER_QUARTER",
    "NITYA_NOW",
    "ALPHA_MOD_KRISHNA",
    # Alpha Bridge (Round 19b)
    "ALPHA_NUMERATOR",
    "ALPHA_DENOMINATOR",
    "ALPHA_INVERSE_CLASSICAL",
    "ALPHA_QUANTUM_CORRECTION",
    "BOHR_VELOCITY_NUMERATOR",
    "BOHR_VELOCITY_DENOMINATOR",
    "MASS_ALPHA_RATIO",
    # NOTE: CONVERGENCE_RATIO_*, OBSERVER_SLOWDOWN_FACTOR REMOVED (empirical, not derived)
    # Fibonacci-Alpha-Mu Bridge
    "FIBONACCI_AT_SEVEN",
    "FIBONACCI_AT_TEN",
    "FIBONACCI_ALPHA_PRODUCT",
    "FIBONACCI_ALPHA_MU",
    # Jagannath Tattva (Round 32)
    "JAGANNATH_TRIAD",
    "JAGANNATH_WHEELS",
    "BALADEV_WHEELS",
    "SUBHADRA_WHEELS",
    "RATHAYATRA_WHEELS",
    "GAURA_TITHI",
    "CHAITANYA_UNION",
    # Transcendental Block (Round 33)
    "TRANSCENDENTAL_1096",
    "TETRAD_FIXED_POINTS",
    "TETRAD_SUM",
    "TETRAD_PRODUCT",
    "PRIME_CHAIN",
    "PRIME_CHAIN_SPAN",
    # Engineering Constants
    "MADHURYA_NUMERATOR",
    "MADHURYA_DENOMINATOR",
    "VISHNU_QUALITIES",
    # Mathematical Constants
    "GOLDEN_RATIO",
    "DNA_CODONS",
    "AMINO_ACIDS",
    # Internal helpers (for import compatibility)
    "FLUTE_VENU_VAMSI",
    "FLUTE_VENU_MURALI",
]
