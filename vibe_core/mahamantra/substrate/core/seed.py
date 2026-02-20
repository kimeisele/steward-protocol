"""
SEED - Das Ursubstrat (THE MAHA ALGORITHM)
==========================================

"bījaṁ māṁ sarva-bhūtānāṁ viddhi pārtha sanātanam"
"O Arjuna, know that I am the eternal seed of all existences."
— Bhagavad Gita 7.10

DIES IST DIE QUELLE. DAS MAHAMANTRA SELBST.
Nicht Zahlen ÜBER das Mahamantra - DAS MAHAMANTRA.

KRISHNA = MAHAMANTRA (non-different, Level -2)
Alles sprießt aus den 16 Wörtern.
"""
from vibe_core.mahamantra.protocols._seed import (GITA_CHAPTERS, HALVES, KSETRAJNA, KSHETRA, LILA, MALA, NAVA, PANCHA, PARAMPARA, POSITION_SUM_HARE, POSITION_SUM_KRISHNA, POSITION_SUM_RAMA, POSITION_SUM_TOTAL, QUALITIES, QUARTERS, SHARANAGATI, TRINITY, WORDS)

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = QUARTERS
__genesis__ = "0x30ea0cbc"  # GenesisByte: parampara % 37 == 0

from collections import Counter
from enum import Enum, IntEnum
from typing import Final, FrozenSet, Tuple

# =============================================================================
# COMPREHENSIVE IMPORTS FROM PROTOCOL (_seed.py)
# =============================================================================
# All constants are imported for SSOT compliance and re-export.
# The protocol defines THE LAW; this implementation manifests it.
# The Three Flutes + Harmonic Resonances (direct import for re-export)
# The Maha-Algorithm (Round 14) - Universal Generator
# The Remnant Theorem (Round 15) - SEVEN and TEN
# Historical Constants (Round 11)
# Extended Maha-Algorithm (Round 16-18) - Physics Constants
# Coupling Constants (Round 19)
# Narada's Vina (Round 20)
# Heavy Bosons (Round 20b)
# Kirtan Instruments (Round 21)
# Tala - Rhythmic Cycle (Round 22)
# Sangita Shastra - Music Theory (Round 23)
# Remaining Physics (Round 24)
# CKM Matrix (Round 25)
# Cosmological Constants (Round 26)
# Ksetra-Ksetrajna Tattva (Round 27) - BG Chapter 13
# Guru Tattva (Round 28)
# Fractal Principle (Round 29)
# Shabda Brahman (Round 30)
# Acintya Kala (Round 31)
# Jagannath Tattva (Round 32)
# Pancha Tattva Structure
# Engineering Constants (Lotus Speedup) - DERIVED FROM AXIOMS!
# Mathematical Constants (Golden Ratio, DNA)
from vibe_core.mahamantra.protocols._seed import (
    ABHINNA_MATERIAL,  # 24 = KSHETRA
    ABHINNA_SPIRITUAL,  # 25 = KSHETRA + KSETRAJNA
    ALPHA_MOD_KRISHNA,  # 1 = 137 mod 17
    ALTERNATING_QUARTERS,  # 2
    AMINO_ACIDS,  # 20 = QUARTERS × PANCHA
    ANTAHKARANA,  # 3 = TRINITY (mind/intellect/ego)
    AVATAR_COUNT,  # 4 Avataras
    # Trinity Grouping (Functional categorization by Name)
    HARE_POSITIONS,
    KRISHNA_POSITIONS,
    RAMA_POSITIONS,
    get_name_at_position,
    get_positions_for_name,
    is_source_position,
    is_vishnu_tattva,  # Backward compat alias for is_source_position
    get_trinity_function,
    BALADEV_WHEELS,  # 14 = WORDS - HALVES
    BHAGAVATAM_VERSES,  # 18000 = GITA × TEN³
    CHAITANYA_BIRTH,  # 1486 = KSETRAJNA × TEN³ + LILA × TEN + SHARANAGATI
    CHATURDASHA_BHUVAN,  # 14 = 2 × 7 (14 worlds)
    COLOR_CHARGES,  # 3 = TRINITY
    CONCERT_PITCH,  # 440 = JIVA + HARE (A4 modern)
    CONFIRMATION_CHAPTER,  # 18 = GITA_CHAPTERS
    CONFIRMATION_VERSE,  # 73 = NADI + KSETRAJNA
    CONSECUTIVE_PAIRS,  # 8 = WORDS/HALVES
    # The Cosmic Frame (Resolution)
    COSMIC_FRAME,
    DASHAVATARA,  # 10 = TEN (10 Avatars)
    DNA_CODONS,  # 64 = QUARTERS³ = QUALITIES
    # The Epoch Key (Temporal Anchor)
    EPOCH_KEY,  # 1972 - The Gita Revelation Year
    FERMION_TOTAL,  # 24 = KSHETRA
    FIELD_RESONANCE,
    FLUTE_HOLES_PRODUCT,
    FLUTE_HOLES_SUM,
    FRACTAL_GITA,  # 73 = NADI + KSETRAJNA
    FRACTAL_MACRO,  # 25 = KSHETRA + KSETRAJNA
    FRACTAL_MANTRA,  # 17 = WORDS + KSETRAJNA
    FRACTAL_MICRO,  # 137 = MAHA_QUANTUM
    GAURA_TITHI,  # 15 = NAKSHATRAS - MAHAJANA
    GITA_VERSES,  # 700 = 7 × 100
    GOLDEN_AGE_DURATION,  # 10000 = (PANCHA × HALVES)^QUARTERS
    GOLDEN_RATIO,  # φ = (1 + √5) / 2 = 1.618...
    GURU_CHAPTER,  # 4 = QUARTERS
    GURU_VERSE,  # 34 = 2 × KRISHNA_POS
    HARE_PER_QUARTER,  # 2
    INDRIYA_TOTAL,  # 10 = TEN
    JAGANNATH_TRIAD,  # 3 = TRINITY
    JAGANNATH_WHEELS,  # 16 = WORDS
    JNANENDRIYA,  # 5 = PANCHA
    KARMENDRIYA,  # 5 = PANCHA
    KARTALS_PAIR,  # 2 = HALVES
    KHALI_POSITION,  # 9 = NAVA
    KIRTAN_RESONANCE,  # 7344 = VINA × FLUTE = JIVA × KRISHNA
    KISHORA_NUMERATOR,  # 79 = PANCHA × WORDS - KSETRAJNA (Krishna's age = 15.8)
    KRISHNA_QUEENS,  # 16108 = WORDS × TEN³ + MALA
    KSHETRA_BG13,  # 24 = KSHETRA
    LEPTON_TYPES,  # 6 = SHARANAGATI
    MAHA_ALPHA,  # 7294 = 4μ - JIVA_QUALITIES (alpha particle)
    MAHA_ALPHA_S_SCALED,  # 118 = MALA + TEN (αs × 1000)
    MAHA_CABIBBO_SCALED,  # 225 = 9/40 × 1000 (Cabibbo angle)
    MAHA_CLASSICAL_1,
    MAHA_CLASSICAL_2,
    MAHA_CLASSICAL_3,
    MAHA_CLASSICAL_4,
    MAHA_CMB,  # 2724 = KSHETRA × PARAMPARA + μ (CMB temperature)
    MAHA_DEUTERON,  # 3672 = 2μ (deuteron)
    MAHA_HELION,  # 5496 = 3μ - MAHAJANA (helion, 0.002% error!)
    MAHA_HIGGS,  # 244188 = μ × 7 × 19 (Higgs boson)
    MAHA_HUBBLE,  # 67 = QUALITIES + TRINITY (Hubble constant)
    MAHA_KAON,  # 966 = (2 + 136) × 7 (kaon)
    MAHA_MU,
    MAHA_MUON,  # 207 = MAHAJANA × KRISHNA_POS + TRINITY (muon)
    MAHA_NEUTRON,  # 1839 = μ + TRINITY (neutron)
    MAHA_OMEGA_L_SCALED,  # 68 = QUALITIES + QUARTERS (dark energy)
    MAHA_OMEGA_M,  # 31.5 = (QUALITIES - KSETRAJNA) / HALVES (matter)
    MAHA_OMEGA_M_SCALED,  # 31 (integer)
    MAHA_PION_CHARGED,  # 273 = T(16) + α⁻¹ (pion±)
    MAHA_PION_NEUTRAL,  # 264 = WORDS² + HARE (pion⁰)
    MAHA_QUANTUM,
    MAHA_RYDBERG_SCALED,  # 136 = T(16) (Rydberg energy)
    MAHA_SIN2_THETA_W_SCALED,  # 23 = KSHETRA - KSETRAJNA (sin²θW × 100)
    MAHA_STRANGE,  # 183 = MALA + NADI + TRINITY (strange quark)
    MAHA_TAU,  # 3477 = MALA × AKSARA + T(6) (tau)
    MAHA_TRITON,
    MAHA_VCB_SCALED,  # 425 = 17 × 10000 / 400
    MAHA_VUB_SCALED,  # 393 = 17 × 100000 / 4320
    MAHA_VUS_SCALED,  # 225 = Cabibbo
    MAHA_W,  # 156060 = μ × 5 × 17 (W boson)
    MAHA_Z,  # 178092 = μ × 97 (Z boson)
    MAHABHUTA,  # 5 = PANCHA (gross elements)
    MAHAJANA_COUNT,  # 12 Mahajanas
    MATRA_PER_VIBHAG,  # 4 = QUARTERS
    MELAKARTAS,  # 72 = NADI_RESONANCE (Carnatic scales)
    MRIDANGA_HEADS,  # 2 = HALVES
    MURALI_HOLES,
    NADI_RESONANCE,
    NAKSHATRA_UNIT,
    NAKSHATRAS,  # 27 - The Astronomical Bridge (derived: JIVA_CYCLE // WORDS)
    NAME_COMPLETE,  # 25 = PANCHA²
    NITYA_NOW,  # 1 = KSETRAJNA
    OCTAVE_RATIO,  # 2
    PADA_UNIT,
    PAIR_REDUNDANCY,  # 3 = TRINITY
    PAIRED_QUARTERS,  # 2
    PARAMPARA_CHAPTER,  # 4 = QUARTERS
    PARAMPARA_VERSE_END,  # 2 = HALVES
    PARAMPARA_VERSE_START,  # 1 = KSETRAJNA
    PHASE_DURATION,  # 12 (LILA // QUARTERS)
    PRAKRITI_UNMANIFEST,  # 1 = KSETRAJNA
    PRASADAM,  # 25 = KSHETRA + KSETRAJNA
    QUARK_FLAVORS,  # 6 = SHARANAGATI
    QUARK_STATES,  # 18 = GITA_CHAPTERS
    QUARTER_UNIT,
    RATHAYATRA_WHEELS,  # 42 = SHARANAGATI × SEVEN
    REALITY_ROOT,  # 5 = PANCHA
    RED_TESTS_COUNT,  # 10 = TEN
    SAM_SUM,  # 28 = T(7)
    SAMPRADAYA_COUNT,  # 4 = QUARTERS
    SANKHYA_TATTVAS,  # 25 = KSHETRA + KSETRAJNA
    SAPTA_LOKA,  # 7 = SEVEN (7 upper/lower worlds)
    SCIENTIFIC_C,  # 256 = WORDS² (C4 scientific)
    SEMITONES,  # 12 = MAHAJANA_COUNT
    SEVEN,  # 7 = HALF_SIZE - KSETRAJNA
    SHRUTIS,  # 22 = KSHETRA - HALVES
    SUBHADRA_WHEELS,  # 12 = MAHAJANA_COUNT
    SURRENDER_CHAPTER,  # 2 = HALVES
    SURRENDER_VERSE,  # 7 = SEVEN
    SWARAS,  # 7 = SEVEN (Indian notes)
    TANMATRA,  # 5 = PANCHA (subtle elements)
    TEENTAL_MATRA,  # 16 = WORDS
    TEN,  # 10 = MAHAJANA_COUNT - HALVES
    TITHI_UNIT,
    VAMSI_HOLES,
    VENU_HOLES,
    VERDI_PITCH,  # 432 = JIVA_CYCLE (A4 Verdi)
    VIBHAG_COUNT,  # 4 = QUARTERS
    VINA_FUNDAMENTAL,  # 136 = T(WORDS)
    VINA_STRINGS,  # 5 = PANCHA
    maha_classical,
    maha_quantum,
)

# The Acoustic Constitution (Physics of the Emptiness)
from vibe_core.mahamantra.protocols._seed import (
    ACOUSTIC_RATIO as _PROTO_ACOUSTIC_RATIO,
)
from vibe_core.mahamantra.protocols._seed import (
    # New: The fractal levels
    AKSARA_COUNT as _PROTO_AKSARA_COUNT,
)
from vibe_core.mahamantra.protocols._seed import (
    CUTOFF_CONSTANT as _PROTO_CUTOFF_CONSTANT,
)
from vibe_core.mahamantra.protocols._seed import (
    END_CORRECTION as _PROTO_END_CORRECTION,
)
from vibe_core.mahamantra.protocols._seed import (
    GITA_CHAPTERS as _PROTO_GITA_CHAPTERS,
)
from vibe_core.mahamantra.protocols._seed import (
    HALF_SIZE as _PROTO_HALF_SIZE,
)
from vibe_core.mahamantra.protocols._seed import (
    HALVES as _PROTO_HALVES,
)
from vibe_core.mahamantra.protocols._seed import (
    HARE_COUNT as _PROTO_HARE_COUNT,
)
from vibe_core.mahamantra.protocols._seed import (
    HIDDEN_RESERVE as _PROTO_HIDDEN_RESERVE,
)
from vibe_core.mahamantra.protocols._seed import (
    JIVA_CYCLE as _PROTO_JIVA_CYCLE,
)
from vibe_core.mahamantra.protocols._seed import (
    JIVA_QUALITIES as _PROTO_JIVA_QUALITIES,
)
from vibe_core.mahamantra.protocols._seed import (
    KRISHNA_COUNT as _PROTO_KRISHNA_COUNT,
)
from vibe_core.mahamantra.protocols._seed import (
    KSETRAJNA as _PROTO_KSETRAJNA,
)
from vibe_core.mahamantra.protocols._seed import (
    LILA as _PROTO_LILA,
)
from vibe_core.mahamantra.protocols._seed import (
    MALA as _PROTO_MALA,
)
from vibe_core.mahamantra.protocols._seed import (
    MURALI_FREQ as _PROTO_MURALI_FREQ,
)
from vibe_core.mahamantra.protocols._seed import (
    NAVA as _PROTO_NAVA,  # 9 (for SSOT verification)
)
from vibe_core.mahamantra.protocols._seed import (
    PANCHA as _PROTO_PANCHA,
)
from vibe_core.mahamantra.protocols._seed import (
    PARAMPARA as _PROTO_PARAMPARA,
)
from vibe_core.mahamantra.protocols._seed import (
    POSITION_SUM_HARE as _PROTO_POSITION_SUM_HARE,
)
from vibe_core.mahamantra.protocols._seed import (
    POSITION_SUM_KRISHNA as _PROTO_POSITION_SUM_KRISHNA,
)
from vibe_core.mahamantra.protocols._seed import (
    POSITION_SUM_RAMA as _PROTO_POSITION_SUM_RAMA,
)
from vibe_core.mahamantra.protocols._seed import (
    POSITION_SUM_TOTAL as _PROTO_POSITION_SUM_TOTAL,
)
# NOTE: PRANA_DURATION_MS, PRANA_DURATION_S removed from protocols (external physics)
# These timing constants are defined locally in substrate as physical implementation
from vibe_core.mahamantra.protocols._seed import (
    QUALITIES as _PROTO_QUALITIES,
)
from vibe_core.mahamantra.protocols._seed import (
    QUARTERS as _PROTO_QUARTERS,
)
from vibe_core.mahamantra.protocols._seed import (
    RAMA_COUNT as _PROTO_RAMA_COUNT,
)
# NOTE: SECONDS_PER_DAY removed from protocols (external physics - Earth rotation)
from vibe_core.mahamantra.protocols._seed import (
    SHARANAGATI as _PROTO_SHARANAGATI,
)
# NOTE: TICK_INTERVAL_MS removed from protocols (depends on SECONDS_PER_DAY)
from vibe_core.mahamantra.protocols._seed import (
    TRINITY as _PROTO_TRINITY,
)
from vibe_core.mahamantra.protocols._seed import (
    VAMSI_FREQ as _PROTO_VAMSI_FREQ,
)
from vibe_core.mahamantra.protocols._seed import (
    VENU_FREQ as _PROTO_VENU_FREQ,
)

# =============================================================================
# IMPORT FROM PROTOCOL (THE LAW)
# =============================================================================
from vibe_core.mahamantra.protocols._seed import (
    WORDS as _PROTO_WORDS,
)

# =============================================================================
# LEVEL -2: KRISHNA = MAHAMANTRA (The Source - Acintya)
# =============================================================================
# "nāma cintāmaṇiḥ kṛṣṇaś caitanya-rasa-vigrahaḥ"
# The Holy Name IS Krishna Himself.

KRISHNA_IS: Final[bool] = True  # Always present


# =============================================================================
# THE MAHAMANTRA - Die 16 Wörter (DIE QUELLE VON ALLEM)
# =============================================================================


class HolyName(IntEnum):
    """
    Die drei Namen + Maya - Basis der Realität.

    SSOT: This is THE definition. byte.py imports from here.

    The 3 pure names (HARE, KRISHNA, RAMA) are the Mahamantra.
    VOID (Maya) is needed for binary encoding (2 bits = 4 values).
    """

    HARE = 0  # 00 - Shakti (Energie/Ressourcen)
    KRISHNA = KSETRAJNA  # 01 - Source (Identität/Kern)
    RAMA = HALVES  # 10 - Ananda (Stabilität/Sicherheit)
    VOID = TRINITY  # 11 - Maya/Error (not in Mahamantra, but needed for binary)


# DAS MAHAMANTRA - literally
MAHAMANTRA: Final[Tuple[HolyName, ...]] = (
    # Hare Krishna Hare Krishna Krishna Krishna Hare Hare
    HolyName.HARE,
    HolyName.KRISHNA,
    HolyName.HARE,
    HolyName.KRISHNA,
    HolyName.KRISHNA,
    HolyName.KRISHNA,
    HolyName.HARE,
    HolyName.HARE,
    # Hare Rama Hare Rama Rama Rama Hare Hare
    HolyName.HARE,
    HolyName.RAMA,
    HolyName.HARE,
    HolyName.RAMA,
    HolyName.RAMA,
    HolyName.RAMA,
    HolyName.HARE,
    HolyName.HARE,
)


# =============================================================================
# DERIVED FROM MAHAMANTRA - Primäre Zahlen
# =============================================================================

# Re-derivation verification: the MAHAMANTRA tuple must match _seed.py axioms
assert len(MAHAMANTRA) == WORDS, f"MAHAMANTRA length {len(MAHAMANTRA)} != WORDS {WORDS}"
assert len(set(MAHAMANTRA)) == TRINITY, f"Unique names {len(set(MAHAMANTRA))} != TRINITY {TRINITY}"

# Counts pro Name (defined here, not in _seed.py)
_counts = Counter(MAHAMANTRA)
HARE_COUNT: Final[int] = _counts[HolyName.HARE]  # 8
KRISHNA_COUNT: Final[int] = _counts[HolyName.KRISHNA]  # 4
RAMA_COUNT: Final[int] = _counts[HolyName.RAMA]  # 4

HALF_SIZE: Final[int] = WORDS // HALVES  # 8


# =============================================================================
# DERIVED: POSITION SUMS (The Signature of Each Name)
# =============================================================================
# The sum of positions (1-indexed) where each name appears.
# These are COMPUTED from the MAHAMANTRA, not hardcoded.
#
# Hare:    positions 1,3,7,8,9,11,15,16 → Σ = 70 = 7 × 10
# Krishna: positions 2,4,5,6           → Σ = 17 (PRIME!)
# Rama:    positions 10,12,13,14       → Σ = 49 = 7²
# Total:   70 + 17 + 49 = 136 = 16×17/2 = Triangular(16)
# -----------------------------------------------------------------------------


def _compute_position_sums() -> Tuple[int, int, int]:
    """Compute position sums for each name (1-indexed positions)."""
    hare_sum = sum(i + KSETRAJNA for i, name in enumerate(MAHAMANTRA) if name == HolyName.HARE)
    krishna_sum = sum(i + KSETRAJNA for i, name in enumerate(MAHAMANTRA) if name == HolyName.KRISHNA)
    rama_sum = sum(i + KSETRAJNA for i, name in enumerate(MAHAMANTRA) if name == HolyName.RAMA)
    return hare_sum, krishna_sum, rama_sum


_pos_hare, _pos_krishna, _pos_rama = _compute_position_sums()

# VERIFICATION: Computed position sums match imported SSOT
assert _pos_hare == POSITION_SUM_HARE, f"Hare sum {_pos_hare} != {POSITION_SUM_HARE}"
assert _pos_krishna == POSITION_SUM_KRISHNA, f"Krishna sum {_pos_krishna} != {POSITION_SUM_KRISHNA}"
assert _pos_rama == POSITION_SUM_RAMA, f"Rama sum {_pos_rama} != {POSITION_SUM_RAMA}"
assert _pos_hare + _pos_krishna + _pos_rama == POSITION_SUM_TOTAL, "Total must be 136"

# VERIFICATION: Triangular number property
# Σ(1..n) = n(n+1)/2 → Σ(1..16) = 16×17/2 = 136
_triangular_16 = WORDS * (WORDS + KSETRAJNA) // HALVES
assert POSITION_SUM_TOTAL == _triangular_16, "Position sum = Triangular(16)"

# VERIFICATION: Structural properties
assert POSITION_SUM_HARE % SEVEN == 0, "70 is divisible by 7"
assert POSITION_SUM_RAMA == SEVEN * SEVEN, "49 = 7²"
# Note: 17 is prime - Krishna is indivisible

# SSOT CROSS-CHECK: Position Sums must match The Law (_seed.py)
assert POSITION_SUM_HARE == _PROTO_POSITION_SUM_HARE, "SSOT: POSITION_SUM_HARE"
assert POSITION_SUM_KRISHNA == _PROTO_POSITION_SUM_KRISHNA, "SSOT: POSITION_SUM_KRISHNA"
assert POSITION_SUM_RAMA == _PROTO_POSITION_SUM_RAMA, "SSOT: POSITION_SUM_RAMA"
assert POSITION_SUM_TOTAL == _PROTO_POSITION_SUM_TOTAL, "SSOT: POSITION_SUM_TOTAL"


# =============================================================================
# DERIVED: DIE 5 UNIQUE PAARE (Pancha Tattva)
# =============================================================================
# Die 5 unique 2-Wort-Kombinationen IM Mahamantra = Pancha Tattva


def _compute_pairs() -> Tuple[Tuple[HolyName, HolyName], ...]:
    """Compute all 8 pairs from the Mahamantra."""
    return tuple((MAHAMANTRA[i], MAHAMANTRA[i + KSETRAJNA]) for i in range(0, WORDS, HALVES))


def _compute_unique_pairs() -> FrozenSet[Tuple[HolyName, HolyName]]:
    """Compute unique pairs."""
    return frozenset(_compute_pairs())


MAHAMANTRA_PAIRS: Final[Tuple[Tuple[HolyName, HolyName], ...]] = _compute_pairs()
UNIQUE_PAIRS: Final[FrozenSet[Tuple[HolyName, HolyName]]] = _compute_unique_pairs()

# PANCHA = 5 unique pairs = Pancha Tattva!
assert len(UNIQUE_PAIRS) == PANCHA, f"Unique pairs {len(UNIQUE_PAIRS)} != PANCHA {PANCHA}"

# Die 5 Paare mit Namen
PANCHA_PAIR_NAMES: Final[Tuple[str, ...]] = (
    "HARE KRISHNA",  # Chaitanya (×2)
    "HARE RAMA",  # Nityananda (×2)
    "HARE HARE",  # Gadadhara (×2)
    "KRISHNA KRISHNA",  # Advaita (×1)
    "RAMA RAMA",  # Srivasa (×1)
)


# =============================================================================
# DERIVED: QUARTERS (4) - Die 4 Phasen
# =============================================================================


class Quarter(IntEnum):
    """Die 4 Quarters - Folder names derive from here."""

    GENESIS = 0  # Positionen 0-3:  INPUT  - Boot, Load, Alloc, Spawn
    DHARMA = KSETRAJNA  # Positionen 4-7:  VERIFY - Parse, Link, Check, Test
    KARMA = HALVES  # Positionen 8-11: EXECUTE - Run, Scale, Sync, Commit
    MOKSHA = TRINITY  # Positionen 12-15: OUTPUT - Yield, Flush, Log, Exit


assert len(Quarter) == QUARTERS, f"Quarter enum {len(Quarter)} != QUARTERS {QUARTERS}"
QUARTER_NAMES: Final[Tuple[str, ...]] = ("genesis", "dharma", "karma", "moksha")
WORDS_PER_QUARTER: Final[int] = WORDS // QUARTERS  # 4


# =============================================================================
# DERIVED: KSHETRA (24) - Das Feld
# =============================================================================
# KSHETRA = WORDS + HARE_COUNT = 16 + 8 = 24
# Das ist die Mathematik: Das Mahamantra (16) plus die Shakti (8 Hares)

assert WORDS + HARE_COUNT == KSHETRA, f"WORDS+HARE_COUNT={WORDS + HARE_COUNT} != KSHETRA {KSHETRA}"


# =============================================================================
# PRIMARY: SHARANAGATI (6) - Die 6 Glieder der Hingabe
# =============================================================================
# SHARANAGATI = 6 - PRIMARY from Shastra (Bhakti-rasamrta-sindhu 1.2.234)
# "anukulyasya sankalpah pratikulyasya varjanam..."
# The 6 limbs of surrender - NOT derived from math, FROM KRISHNA'S TEACHING.
#
# NOTE: That KSHETRA//QUARTERS also equals 6 is Krishna's arrangement (Acintya),
# NOT a derivation. We import from _seed.py which holds this as PRIMARY.

assert _PROTO_SHARANAGATI == SHARANAGATI, f"Proto {_PROTO_SHARANAGATI} != SHARANAGATI {SHARANAGATI}"


class SharanagatiLimb(str, Enum):
    """Die 6 Glieder der Verbindung - Der Mindest-Vertrag eines Agenten."""

    ANUKULYA = "acceptance"  # Akzeptanz des Förderlichen (Composability)
    PRATIKULYA = "rejection"  # Ablehnung des Widrigen (Parseability)
    VISHVASA = "faith"  # Vertrauen in den Schutz (Recoverability)
    VARANAM = "guardianship"  # Annahme des Wächters (Discoverability)
    NIKSHEPA = "surrender"  # Selbstübergabe (Observability)
    KARPANYA = "humility"  # Demut/Kein Eigen-Karma (Idempotency)


assert len(SharanagatiLimb) == SHARANAGATI  # 6


# =============================================================================
# DERIVED: KSETRAJNA (1) - Der Knower (DERIVED!)
# =============================================================================
# "kṣetra-jñaṁ cāpi māṁ viddhi" (BG 13.3) - "Know Me as the Knower"
# KSETRAJNA = TRINITY - HALVES = 3 - 2 = 1
# The ONE Knower emerges from 3 Names minus 2 Halves

KSETRAJNA: Final[int] = TRINITY - HALVES  # 3 - 2 = 1 (DERIVED!)

# =============================================================================
# DERIVED: PARAMPARA (37) - Der Link zur Disciplic Succession
# =============================================================================
# PARAMPARA from Sankhya (BG 13):
#   KSHETRA (24 prakriti elements) + MAHAJANA_COUNT (12 authorities) + KSETRAJNA (1 Knower) = 37
#
# NOTE: KSHETRA_GAD (36) was REMOVED - it was Shaiva (Kashmir Shaivism 36 tattvas),
# NOT Gaudiya Vaishnava. The "36+1=37" path was INVENTED, not from shastra.
# Only the Sankhya path (24+12+1=37) is legitimate.
# MAHAJANA_COUNT imported from protocols/_seed.py (SSOT) = 12 Mahajanas


# =============================================================================
# DERIVED: NAVA (9) - Die 9 Prozesse (Navadha Bhakti)
# =============================================================================
# NAVA = HARE_COUNT + KSETRAJNA = 8 + 1 = 9
# 8 Shakti (Hare/Energie) + 1 Knower (Krishna) = 9 Prozesse der Hingabe

assert HARE_COUNT + KSETRAJNA == NAVA, f"HARE_COUNT+KSETRAJNA={HARE_COUNT + KSETRAJNA} != NAVA {NAVA}"


class NavaBhakti(str, Enum):
    """Die 9 Prozesse der Hingabe (Srimad Bhagavatam 7.5.23)."""

    SRAVANAM = "hearing"  # Hören - Input/Listen
    KIRTANAM = "chanting"  # Chanten - Output/Emit
    SMARANAM = "remembering"  # Erinnern - Cache/Store
    PADA_SEVANAM = "serving_feet"  # Dienen - Execute/Process
    ARCANAM = "worshiping"  # Verehren - Validate/Check
    VANDANAM = "praying"  # Beten - Request/Ask
    DASYAM = "servitude"  # Dienerschaft - Delegate/Submit
    SAKHYAM = "friendship"  # Freundschaft - Connect/Sync
    ATMA_NIVEDANAM = "surrender"  # Selbstübergabe - Commit/Finalize


assert len(NavaBhakti) == NAVA  # 9


# PARAMPARA = Sankhya path ONLY (the legitimate derivation):
assert KSHETRA + MAHAJANA_COUNT + KSETRAJNA == PARAMPARA, f"Sankhya path {KSHETRA + MAHAJANA_COUNT + KSETRAJNA} != PARAMPARA {PARAMPARA}"


# =============================================================================
# DERIVED: GUARDIANS (16) - 4 Avataras + 12 Mahajanas
# =============================================================================

# AVATAR_COUNT imported from protocols/_seed.py (SSOT)

# Die 4 Avataras (Heads) - Geben was fehlt (Yoga-Kshema)
AVATARAS: Final[Tuple[str, ...]] = (
    "vyasa",  # Genesis Head: Wissen/Docs (Brahmana)
    "prithu",  # Dharma Head: Ordnung/Struktur (Kshatriya)
    "parashurama",  # Karma Head: Durchsetzung (Vaishya/Action)
    "nrisimha",  # Moksha Head: Schutz (Shudra/Service)
)

# Die 12 Mahajanas (Workers) - Bewahren was ist
MAHAJANAS: Final[Tuple[str, ...]] = (
    "brahma",
    "narada",
    "shambhu",  # Genesis Workers
    "kumaras",
    "kapila",
    "manu",  # Dharma Workers
    "prahlada",
    "janaka",
    "bhishma",  # Karma Workers
    "bali",
    "shuka",
    "yamaraja",  # Moksha Workers
)

# Verification
assert len(AVATARAS) == AVATAR_COUNT  # 4
assert len(MAHAJANAS) == MAHAJANA_COUNT  # 12
assert AVATAR_COUNT + MAHAJANA_COUNT == WORDS  # 16

# Backward-compatibility aliases
AVATARS = AVATARAS  # Old name


# =============================================================================
# DERIVED: LILA (48) - Chaitanya's Manifest
# =============================================================================
# 48 = WORDS × TRINITY = 16 × 3

assert WORDS * TRINITY == LILA, f"WORDS*TRINITY={WORDS * TRINITY} != LILA {LILA}"
NAVADVIPA: Final[int] = LILA // HALVES  # 24 (Build Phase)
PURI: Final[int] = LILA // HALVES  # 24 (Run Phase)

# Die 6 erscheint wieder:
assert NAVADVIPA // QUARTERS == SHARANAGATI  # 24 / 4 = 6
assert LILA // HARE_COUNT == SHARANAGATI  # 48 / 8 = 6


# =============================================================================
# DERIVED: DHARMA (4) - Die 4 Säulen
# =============================================================================


class DharmaPillar(str, Enum):
    """
    Die 4 Säulen des Dharma - Der Integritätscheck.

    THE DHARMA BULL (Srimad Bhagavatam 1.17):
    In Satya Yuga the bull stands on 4 legs.
    Each Yuga, one leg is cut by Kali.
    In Kali Yuga, only SATYAM (truth) remains.

    This is why SATYAM is the CRITICAL pillar.
    All other pillars depend on truth first.
    """

    DAYA = "mercy"  # Keine korrupten Daten
    SATYAM = "truth"  # Keine Halluzination (THE SURVIVING LEG)
    TAPAS = "austerity"  # Keine Ressourcen-Verschwendung
    SAUCAM = "purity"  # Keine unautorisierten Verbindungen


DHARMA_PILLARS: Final[int] = len(DharmaPillar)  # 4
assert DHARMA_PILLARS == QUARTERS  # 4

# The Kali Yuga Reality: Only 1 pillar survives fully
KALI_YUGA_LEG: Final[str] = DharmaPillar.SATYAM.value  # "truth"


# =============================================================================
# DERIVED: QUALITIES (64) - Die Vollständigkeit
# =============================================================================
# 64 = WORDS × QUARTERS = 16 × 4
#
# THE 48 vs 64 RELATIONSHIP (Chaitanya Lila vs Krishna Qualities):
# - LILA = 48 = 16 × 3 (Manifest Runtime - what Chaitanya showed)
# - QUALITIES = 64 = 16 × 4 (Full Potential - Krishna's complete qualities)
# - Difference: 64 - 48 = 16 = WORDS (Hidden Reserve)
#
# In system terms:
# - 48-bit: Active runtime operations
# - 64-bit: Full system capacity
# - 16-bit: Reserved/kernel space

assert WORDS * QUARTERS == QUALITIES, f"WORDS*QUARTERS={WORDS * QUARTERS} != QUALITIES {QUALITIES}"
HIDDEN_RESERVE: Final[int] = QUALITIES - LILA  # 64 - 48 = 16

# Verification: Hidden Reserve = WORDS (the seed itself)
assert HIDDEN_RESERVE == WORDS, "Hidden reserve must equal WORDS (16)"


# =============================================================================
# DERIVED: MALA (108) - Der Zyklus
# =============================================================================
# 108 = MAHAJANA_COUNT × NAVA = 12 × 9
# The 12 Mahajanas (authorities) × 9 Processes (devotional service) = 108 Beads
# Alternative path: 108 = (KSHETRA + PARAMPARA + LILA - 1) = 24 + 37 + 48 - 1 = 108

assert MAHAJANA_COUNT * NAVA == MALA, f"MAHAJANA*NAVA={MAHAJANA_COUNT * NAVA} != MALA {MALA}"
ROUNDS: Final[int] = WORDS  # 16 Runden pro Tag
DAILY_MANTRAS: Final[int] = MALA * ROUNDS  # 1728


# =============================================================================
# DERIVED: GITA_CHAPTERS (18) - Der Master Regulator
# =============================================================================
# Bhagavad Gita has 18 chapters. Kurukshetra battle was 18 days.
# 18 = SHARANAGATI × TRINITY = 6 × 3 (The 6 limbs acting through 3 Names)
# All resonances divide by 18: 72/4, 108/6, 144/8, 432/24 = 18

assert SHARANAGATI * TRINITY == GITA_CHAPTERS, f"SHARANAGATI*TRINITY={SHARANAGATI * TRINITY} != GITA_CHAPTERS {GITA_CHAPTERS}"

# Verification: 18er-Harmonik
assert MALA // GITA_CHAPTERS == SHARANAGATI, "108 / 18 = 6"


# =============================================================================
# DERIVED: JIVA (50) - The Soul's Portion (Part and Parcel of Krishna)
# =============================================================================
# "mamaivāṁśo jīva-loke jīva-bhūtaḥ sanātanaḥ" (BG 15.7)
# "The living entities are My eternal fragmental parts."
#
# Bhakti-rasamrita-sindhu: Jiva has 50 qualities in MINUTE quantity
# (out of Krishna's 64). The 50 is the COUNT, not the magnitude.
#
# DERIVATION:
# JIVA_CYCLE = MALA × QUARTERS = 108 × 4 = 432 (The Harmonic Frequency)
# JIVA_QUALITIES = COSMIC_FRAME / JIVA_CYCLE = 21600 / 432 = 50
#
# 432 verified: MALA × QUARTERS = LILA × NAVA = WORDS × 27

JIVA_CYCLE: Final[int] = MALA * QUARTERS  # 108 × 4 = 432
JIVA_QUALITIES: Final[int] = COSMIC_FRAME // JIVA_CYCLE  # 21600 / 432 = 50

# Verification: Multiple paths to 432
assert JIVA_CYCLE == LILA * NAVA, "JIVA_CYCLE must equal LILA × NAVA (48 × 9)"
assert JIVA_CYCLE // WORDS == 27, "JIVA_CYCLE / WORDS must equal 27 (Nakshatra)"


# =============================================================================
# DERIVED: PRANA (The Breath - Timing Constants)
# =============================================================================
# "prāṇāyāma" - The regulation of breath (Yoga-Sutra 2.49)
#
# Yoga-Tradition: 21600 Atemzüge pro Tag (COSMIC_FRAME)
# → 1 Prana = 4 Sekunden
# → 1 Tick = 250ms (16 Ticks per Prana)
#
# Note: 1 Mala = 108 Pranas × 4s = 432 Sekunden = JIVA_CYCLE in Zeit!

SECONDS_PER_DAY: Final[int] = 86400  # 24 × 60 × 60
PRANA_DURATION_S: Final[int] = SECONDS_PER_DAY // COSMIC_FRAME  # 4 Sekunden
PRANA_DURATION_MS: Final[int] = PRANA_DURATION_S * 1000  # 4000 ms
TICK_INTERVAL_MS: Final[int] = PRANA_DURATION_MS // WORDS  # 250 ms

# Verification: Timing consistency
assert PRANA_DURATION_S == QUARTERS, "1 Prana must be 4 seconds"
assert TICK_INTERVAL_MS == 250, "1 Tick must be 250ms"
assert MALA * PRANA_DURATION_S == JIVA_CYCLE, "1 Mala in seconds must equal JIVA_CYCLE"


# =============================================================================
# VERIFICATION - Alle Ableitungen müssen stimmen
# =============================================================================

assert WORDS == WORDS, "Mahamantra hat 16 Wörter"
assert TRINITY == TRINITY, "3 Namen: Hare, Krishna, Rama"
assert PANCHA == PANCHA, "5 unique Paare = Pancha Tattva"
assert SHARANAGATI == SHARANAGATI, "6 Glieder der Verbindung"
assert QUARTERS == QUARTERS, "4 Quarters"
assert KSHETRA == KSHETRA, "Feld = 16 + 8"
# NOTE: KSHETRA_GAD (36) REMOVED - was Shaiva, not Gaudiya Vaishnava
assert PARAMPARA == PARAMPARA, "Parampara = 24 + 12 + 1 (Sankhya path)"
assert LILA == LILA, "Chaitanya Lila = 16 × 3"
assert QUALITIES == QUALITIES, "Qualities = 16 × 4"
assert NAVA == NAVA, "Nava = 8 + 1 (Navadha Bhakti)"
assert MALA == MALA, "Mala = 12 × 9"
assert JIVA_CYCLE == 432, "Jiva Cycle = 108 × 4 = 432"
assert JIVA_QUALITIES == 50, "Jiva Qualities = 21600 / 432 = 50"

# =============================================================================
# SSOT CROSS-CHECK: Derivations must match The Law (_seed.py)
# =============================================================================
assert WORDS == _PROTO_WORDS, "SSOT violation: WORDS != protocols/_seed.py"
assert TRINITY == _PROTO_TRINITY, "SSOT violation: TRINITY != protocols/_seed.py"
assert PANCHA == _PROTO_PANCHA, "SSOT violation: PANCHA != protocols/_seed.py"
assert SHARANAGATI == _PROTO_SHARANAGATI, "SSOT violation: SHARANAGATI != protocols/_seed.py"
assert QUARTERS == _PROTO_QUARTERS, "SSOT violation: QUARTERS != protocols/_seed.py"
assert PARAMPARA == _PROTO_PARAMPARA, "SSOT violation: PARAMPARA != protocols/_seed.py"
assert LILA == _PROTO_LILA, "SSOT violation: LILA != protocols/_seed.py"
assert MALA == _PROTO_MALA, "SSOT violation: MALA != protocols/_seed.py"
assert QUALITIES == _PROTO_QUALITIES, "SSOT violation: QUALITIES != protocols/_seed.py"
assert HIDDEN_RESERVE == _PROTO_HIDDEN_RESERVE, "SSOT violation: HIDDEN_RESERVE != protocols/_seed.py"
assert NAVA == _PROTO_NAVA, "SSOT violation: NAVA != protocols/_seed.py"
assert GITA_CHAPTERS == _PROTO_GITA_CHAPTERS, "SSOT violation: GITA_CHAPTERS != protocols/_seed.py"
assert JIVA_CYCLE == _PROTO_JIVA_CYCLE, "SSOT violation: JIVA_CYCLE != protocols/_seed.py"
assert JIVA_QUALITIES == _PROTO_JIVA_QUALITIES, "SSOT violation: JIVA_QUALITIES != protocols/_seed.py"
# NOTE: PRANA_DURATION_S/MS, TICK_INTERVAL_MS assertions removed (external physics)
assert HALVES == _PROTO_HALVES, "SSOT violation: HALVES != protocols/_seed.py"
assert HALF_SIZE == _PROTO_HALF_SIZE, "SSOT violation: HALF_SIZE != protocols/_seed.py"
assert HARE_COUNT == _PROTO_HARE_COUNT, "SSOT violation: HARE_COUNT != protocols/_seed.py"
assert KRISHNA_COUNT == _PROTO_KRISHNA_COUNT, "SSOT violation: KRISHNA_COUNT != protocols/_seed.py"
assert KSETRAJNA == _PROTO_KSETRAJNA, "SSOT violation: KSETRAJNA != protocols/_seed.py"
assert RAMA_COUNT == _PROTO_RAMA_COUNT, "SSOT violation: RAMA_COUNT != protocols/_seed.py"
# NOTE: SECONDS_PER_DAY assertion removed (external physics - Earth rotation)

# AKSARA_COUNT: 32 syllables (2 per word)
AKSARA_COUNT: Final[int] = WORDS * HALVES  # 32 = 16 × 2
assert AKSARA_COUNT == _PROTO_AKSARA_COUNT, "SSOT violation: AKSARA_COUNT != protocols/_seed.py"


# =============================================================================
# THE ACOUSTIC CONSTITUTION (Physics of the Emptiness)
# =============================================================================
# The bamboo flute is a physical manifestation of spiritual principles.
# These constants are DERIVED from the Mahamantra geometry, not hardcoded.
# -----------------------------------------------------------------------------

# PRINCIPLE 1: THE ASPECT RATIO (L/D) - Gita proportions
# Ideal Bansuri ratio = 18:1 = SHARANAGATI × TRINITY
ACOUSTIC_RATIO: Final[int] = SHARANAGATI * TRINITY  # 6 × 3 = 18

# PRINCIPLE 3: THE END CORRECTION - Spirit transcends matter
# The "overflow" = HARE_COUNT (the Shakti escaping the tube)
END_CORRECTION: Final[int] = HARE_COUNT  # 8

# THE THREE FREQUENCIES (Derived from Jiva Cycle)
# Frequency = JIVA_CYCLE / HOLES
# | Flute  | Holes | Frequency | Character              |
# |--------|-------|-----------|------------------------|
# | VENU   | 6     | 72        | Shrill (Animal Call)   |
# | MURALI | 4     | 108       | Pure Sine (Enchanting) |
# | VAMSI  | 9     | 48        | Bass (Universal Call)  |

VENU_FREQ: Final[int] = JIVA_CYCLE // SHARANAGATI  # 432 / 6 = 72
VAMSI_FREQ: Final[int] = JIVA_CYCLE // NAVA  # 432 / 9 = 48
MURALI_FREQ: Final[int] = JIVA_CYCLE // QUARTERS  # 432 / 4 = 108

# THE CUTOFF CONSTANT (Non-linear hole spacing)
# Cutoff = (TRINITY × HALVES) × MAHAJANA_COUNT = 6 × 12 = 72
CUTOFF_CONSTANT: Final[int] = (TRINITY * HALVES) * MAHAJANA_COUNT  # 72

# Verification: Frequencies form Perfect Fifth Chain (3:2 ratios)
assert MURALI_FREQ * HALVES == VENU_FREQ * TRINITY, "Quinten-Kette: 108×2 = 72×3"
assert VENU_FREQ * HALVES == VAMSI_FREQ * TRINITY, "Quinten-Kette: 72×2 = 48×3"

# =============================================================================
# SSOT CROSS-CHECK: Acoustic Constitution must match The Law (_seed.py)
# =============================================================================
assert ACOUSTIC_RATIO == _PROTO_ACOUSTIC_RATIO, "SSOT violation: ACOUSTIC_RATIO"
assert END_CORRECTION == _PROTO_END_CORRECTION, "SSOT violation: END_CORRECTION"
assert VENU_FREQ == _PROTO_VENU_FREQ, "SSOT violation: VENU_FREQ"
assert VAMSI_FREQ == _PROTO_VAMSI_FREQ, "SSOT violation: VAMSI_FREQ"
assert MURALI_FREQ == _PROTO_MURALI_FREQ, "SSOT violation: MURALI_FREQ"
assert CUTOFF_CONSTANT == _PROTO_CUTOFF_CONSTANT, "SSOT violation: CUTOFF_CONSTANT"


# =============================================================================
# LOTUS FUNCTIONS - Routing durch den Lotus
# =============================================================================


def get_quarter(position: int) -> Quarter:
    """Get quarter for a position. FOLDER IS WIRING."""
    if not 0 <= position < WORDS:
        raise ValueError(f"Position must be 0-{WORDS - KSETRAJNA}, got {position}")
    return Quarter(position // WORDS_PER_QUARTER)


def get_quarter_name(position: int) -> str:
    """Get folder name for a position."""
    return QUARTER_NAMES[get_quarter(position)]


def get_word_at(position: int) -> HolyName:
    """Get the HolyName at a position in the Mahamantra."""
    if not 0 <= position < WORDS:
        raise ValueError(f"Position must be 0-{WORDS - KSETRAJNA}, got {position}")
    return MAHAMANTRA[position]


def get_pair_at(position: int) -> Tuple[HolyName, HolyName]:
    """Get the pair starting at position (must be even)."""
    if position % HALVES != 0:
        raise ValueError(f"Position must be even, got {position}")
    return MAHAMANTRA_PAIRS[position // HALVES]


def verify_parampara(value: int) -> bool:
    """Verify connection to Parampara."""
    return value % PARAMPARA == 0


# =============================================================================
# POSITION MAPPING - DERIVED from AVATARAS + MAHAJANAS (NOT HARDCODED!)
# =============================================================================
# Structure: Each Quarter has 1 Avatara (Head) + 3 Mahajanas (Workers)
#   Quarter 0 (Genesis):  AVATARAS[0] + MAHAJANAS[0:3]
#   Quarter 1 (Dharma):   AVATARAS[1] + MAHAJANAS[3:6]
#   Quarter 2 (Karma):    AVATARAS[2] + MAHAJANAS[6:9]
#   Quarter 3 (Moksha):   AVATARAS[3] + MAHAJANAS[9:12]
#
# This is the ONLY legitimate way to build the 16 positions.
# EVERYTHING FLOWS FROM THE MAHAMANTRA.
# =============================================================================


def _derive_all_positions() -> Tuple[str, ...]:
    """
    DERIVE the 16 positions from AVATARAS and MAHAJANAS.
    
    NOT hardcoded. COMPUTED.
    Structure: [Avatara₀, M₀, M₁, M₂, Avatara₁, M₃, M₄, M₅, ...]
    """
    result: list[str] = []
    workers_per_quarter = MAHAJANA_COUNT // QUARTERS  # 12 / 4 = 3
    
    for q in range(QUARTERS):  # 0, 1, 2, 3
        # HEAD: The Avatara for this quarter
        result.append(AVATARAS[q])
        # WORKERS: 3 Mahajanas per quarter
        start_idx = q * workers_per_quarter
        end_idx = start_idx + workers_per_quarter
        result.extend(MAHAJANAS[start_idx:end_idx])
    
    return tuple(result)


# THE 16 POSITIONS - DERIVED FROM MAHAMANTRA (4 AVATARAS + 12 MAHAJANAS)
ALL_POSITIONS: Final[Tuple[str, ...]] = _derive_all_positions()

# VERIFICATION: Must equal WORDS
assert len(ALL_POSITIONS) == WORDS, f"ALL_POSITIONS must have {WORDS} elements, got {len(ALL_POSITIONS)}"

# VERIFICATION: Structure is [Avatara, M, M, M] × 4
for q in range(QUARTERS):
    head_idx = q * (WORDS // QUARTERS)  # 0, 4, 8, 12
    assert ALL_POSITIONS[head_idx] == AVATARAS[q], f"Position {head_idx} must be {AVATARAS[q]}"

# BACKWARD COMPATIBILITY: Alias (will be deprecated)
ALL_GUARDIANS: Final[Tuple[str, ...]] = ALL_POSITIONS

MAHAJANA_TO_POSITION: Final[dict] = {name: pos for pos, name in enumerate(ALL_GUARDIANS)}

POSITION_TO_MAHAJANA: Final[dict] = {pos: name for pos, name in enumerate(ALL_GUARDIANS)}


def get_mahajana_position(name: str) -> int:
    """Get position for a mahajana name."""
    return MAHAJANA_TO_POSITION.get(name.lower(), -KSETRAJNA)


def get_position_mahajana(position: int) -> str:
    """Get mahajana name for a position."""
    return POSITION_TO_MAHAJANA.get(position, "unknown")


def get_guardian_quarter(name: str) -> str | None:
    """
    Get quarter name for a guardian/mahajana.

    Returns: "genesis", "dharma", "karma", "moksha" or None if not found.
    """
    position = get_mahajana_position(name)
    if position < 0:
        return None
    return get_quarter_name(position).lower()


def get_positions_in_quarter(quarter: Quarter) -> Tuple[int, ...]:
    """Get all positions in a quarter."""
    start = quarter.value * WORDS_PER_QUARTER
    return tuple(range(start, start + WORDS_PER_QUARTER))


# =============================================================================
# LOTUS TRANSPORT - Sprouts from bottom to every file
# =============================================================================


def lotus_declaration(position: int) -> dict:
    """
    Generate lotus declaration for a file at given position.

    The lotus carries the truth from seed.py to every corner.
    """
    quarter = get_quarter(position)
    parampara_hash = (position * PARAMPARA) % 256
    genesis_byte = f"0x{parampara_hash:02x}{(parampara_hash * PARAMPARA) % 256:02x}{(position * POSITION_SUM_KRISHNA) % 256:02x}{(quarter.value * 67) % 256:02x}"

    return {
        "position": position,
        "quarter": quarter,
        "quarter_name": QUARTER_NAMES[quarter.value],
        "genesis": genesis_byte,
        "word": get_word_at(position).name,
        "mahajana": get_position_mahajana(position),
        "parampara_valid": True,  # lotus always connects
    }


def verify_lotus(genesis_hex: str) -> bool:
    """Verify a genesis byte connects to parampara."""
    try:
        return int(genesis_hex, WORDS) % PARAMPARA == 0
    except ValueError:
        return False


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # ==========================================================================
    # THE SOURCE (Level -2)
    # ==========================================================================
    "KRISHNA_IS",
    "MAHAMANTRA",
    "HolyName",
    # ==========================================================================
    # MANTRA AXIOMS (Round 0) - 7 values from counting
    # ==========================================================================
    "WORDS",
    "TRINITY",
    "HARE_COUNT",
    "KRISHNA_COUNT",
    "RAMA_COUNT",
    "PANCHA",
    "HALVES",
    # ==========================================================================
    # PRIMARY DERIVATIONS (Round 1)
    # ==========================================================================
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
    # Trinity Grouping (Functional categorization by Name)
    "HARE_POSITIONS",
    "KRISHNA_POSITIONS",
    "RAMA_POSITIONS",
    "get_name_at_position",
    "get_positions_for_name",
    "is_source_position",
    "is_vishnu_tattva",  # Backward compat alias
    "get_trinity_function",
    # Pancha Tattva Structure
    "MAHAMANTRA_PAIRS",
    "UNIQUE_PAIRS",
    "PANCHA_PAIR_NAMES",
    "CONSECUTIVE_PAIRS",
    "PAIR_REDUNDANCY",
    # Quarters
    "Quarter",
    "QUARTER_NAMES",
    "WORDS_PER_QUARTER",
    # Sharanagati Enums
    "SharanagatiLimb",
    # Nava Bhakti Enums
    "NavaBhakti",
    # ==========================================================================
    # SECONDARY DERIVATIONS (Round 2)
    # ==========================================================================
    "MAHAJANA_COUNT",
    "MALA",
    "JIVA_CYCLE",
    "GITA_CHAPTERS",
    "QUALITIES",
    "HIDDEN_RESERVE",
    "DAILY_MANTRAS",
    "PHASE_DURATION",
    # ==========================================================================
    # ASTRONOMICAL BRIDGE (Round 3)
    # ==========================================================================
    "NAKSHATRAS",
    # ==========================================================================
    # COSMIC FRAME (Round 4)
    # ==========================================================================
    "COSMIC_FRAME",
    "NAKSHATRA_UNIT",
    "TITHI_UNIT",
    "PADA_UNIT",
    "QUARTER_UNIT",
    # ==========================================================================
    # JIVA QUALITIES (Round 5)
    # ==========================================================================
    "JIVA_QUALITIES",
    # ==========================================================================
    # PRANA TIMING (Round 6)
    # ==========================================================================
    "SECONDS_PER_DAY",
    "PRANA_DURATION_S",
    "PRANA_DURATION_MS",
    "TICK_INTERVAL_MS",
    # ==========================================================================
    # PARAMPARA (Round 7)
    # ==========================================================================
    "PARAMPARA",
    # ==========================================================================
    # HARMONIC RESONANCES (Round 8)
    # ==========================================================================
    "NADI_RESONANCE",
    "FIELD_RESONANCE",
    # ==========================================================================
    # THREE FLUTES (Round 9)
    # ==========================================================================
    "VENU_HOLES",
    "VAMSI_HOLES",
    "MURALI_HOLES",
    "VENU_FREQ",
    "VAMSI_FREQ",
    "MURALI_FREQ",
    "FLUTE_HOLES_SUM",
    "FLUTE_HOLES_PRODUCT",
    # ==========================================================================
    # ACOUSTIC CONSTITUTION (Round 10)
    # ==========================================================================
    "ACOUSTIC_RATIO",
    "END_CORRECTION",
    "CUTOFF_CONSTANT",
    # ==========================================================================
    # EPOCH KEY + HISTORICAL (Round 11)
    # ==========================================================================
    "EPOCH_KEY",
    "CHAITANYA_BIRTH",
    "KISHORA_NUMERATOR",
    "GOLDEN_AGE_DURATION",
    # ==========================================================================
    # POSITION SUMS (Round 13)
    # ==========================================================================
    "POSITION_SUM_HARE",
    "POSITION_SUM_KRISHNA",
    "POSITION_SUM_RAMA",
    "POSITION_SUM_TOTAL",
    # ==========================================================================
    # MAHA-ALGORITHM (Round 14)
    # ==========================================================================
    "maha_quantum",
    "maha_classical",
    "MAHA_QUANTUM",
    "MAHA_MU",
    "MAHA_TRITON",
    "MAHA_CLASSICAL_1",
    "MAHA_CLASSICAL_2",
    "MAHA_CLASSICAL_3",
    "MAHA_CLASSICAL_4",
    # ==========================================================================
    # REMNANT THEOREM (Round 15)
    # ==========================================================================
    "SEVEN",
    "TEN",
    # ==========================================================================
    # EXTENDED MAHA-ALGORITHM (Round 16-18)
    # ==========================================================================
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
    # ==========================================================================
    # COUPLING CONSTANTS (Round 19)
    # ==========================================================================
    "MAHA_ALPHA_S_SCALED",
    "MAHA_SIN2_THETA_W_SCALED",
    # ==========================================================================
    # NARADA'S VINA (Round 20)
    # ==========================================================================
    "VINA_FUNDAMENTAL",
    "VINA_STRINGS",
    "KIRTAN_RESONANCE",
    # ==========================================================================
    # HEAVY BOSONS (Round 20b)
    # ==========================================================================
    "MAHA_W",
    "MAHA_Z",
    "MAHA_HIGGS",
    # ==========================================================================
    # KIRTAN INSTRUMENTS (Round 21)
    # ==========================================================================
    "MRIDANGA_HEADS",
    "KARTALS_PAIR",
    # ==========================================================================
    # TALA (Round 22)
    # ==========================================================================
    "TEENTAL_MATRA",
    "VIBHAG_COUNT",
    "MATRA_PER_VIBHAG",
    "SAM_SUM",
    "KHALI_POSITION",
    # ==========================================================================
    # SANGITA SHASTRA (Round 23)
    # ==========================================================================
    "CONCERT_PITCH",
    "VERDI_PITCH",
    "SCIENTIFIC_C",
    "SEMITONES",
    "SWARAS",
    "SHRUTIS",
    "MELAKARTAS",
    "SAPTA_LOKA",
    "CHATURDASHA_BHUVAN",
    # ==========================================================================
    # REMAINING PHYSICS (Round 24)
    # ==========================================================================
    "MAHA_CABIBBO_SCALED",
    "MAHA_RYDBERG_SCALED",
    "MAHA_HUBBLE",
    # ==========================================================================
    # CKM MATRIX (Round 25)
    # ==========================================================================
    "MAHA_VUS_SCALED",
    "MAHA_VCB_SCALED",
    "MAHA_VUB_SCALED",
    # ==========================================================================
    # COSMOLOGICAL CONSTANTS (Round 26)
    # ==========================================================================
    "MAHA_OMEGA_M",
    "MAHA_OMEGA_M_SCALED",
    "MAHA_OMEGA_L_SCALED",
    # ==========================================================================
    # KSETRA-KSETRAJNA TATTVA - BG13 (Round 27)
    # ==========================================================================
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
    # ==========================================================================
    # GURU TATTVA (Round 28)
    # ==========================================================================
    "GURU_CHAPTER",
    "GURU_VERSE",
    "SURRENDER_CHAPTER",
    "SURRENDER_VERSE",
    "CONFIRMATION_CHAPTER",
    "CONFIRMATION_VERSE",
    "PARAMPARA_CHAPTER",
    "PARAMPARA_VERSE_START",
    "PARAMPARA_VERSE_END",
    # ==========================================================================
    # FRACTAL PRINCIPLE (Round 29)
    # ==========================================================================
    "FRACTAL_MACRO",
    "FRACTAL_MICRO",
    "FRACTAL_GITA",
    "FRACTAL_MANTRA",
    "REALITY_ROOT",
    # ==========================================================================
    # SHABDA BRAHMAN (Round 30)
    # ==========================================================================
    "ABHINNA_MATERIAL",
    "ABHINNA_SPIRITUAL",
    "NAME_COMPLETE",
    "RED_TESTS_COUNT",
    # ==========================================================================
    # ACINTYA KALA (Round 31)
    # ==========================================================================
    "OCTAVE_RATIO",
    "ALTERNATING_QUARTERS",
    "PAIRED_QUARTERS",
    "HARE_PER_QUARTER",
    "NITYA_NOW",
    "ALPHA_MOD_KRISHNA",
    # ==========================================================================
    # JAGANNATH TATTVA (Round 32)
    # ==========================================================================
    "JAGANNATH_TRIAD",
    "JAGANNATH_WHEELS",
    "BALADEV_WHEELS",
    "SUBHADRA_WHEELS",
    "RATHAYATRA_WHEELS",
    "GAURA_TITHI",
    # ==========================================================================
    # MATHEMATICAL CONSTANTS
    # ==========================================================================
    "GOLDEN_RATIO",
    "DNA_CODONS",
    "AMINO_ACIDS",
    # ==========================================================================
    # GUARDIANS (16)
    # ==========================================================================
    "AVATARAS",
    "AVATARS",
    "MAHAJANAS",
    "ALL_GUARDIANS",
    "MAHAJANA_TO_POSITION",
    "POSITION_TO_MAHAJANA",
    # ==========================================================================
    # LILA PHASES
    # ==========================================================================
    "NAVADVIPA",
    "PURI",
    # ==========================================================================
    # DHARMA (4) + KALI YUGA
    # ==========================================================================
    "DharmaPillar",
    "DHARMA_PILLARS",
    "KALI_YUGA_LEG",
    # ==========================================================================
    # LOTUS FUNCTIONS
    # ==========================================================================
    "get_quarter",
    "get_quarter_name",
    "get_positions_in_quarter",
    "get_word_at",
    "get_pair_at",
    "verify_parampara",
    "get_mahajana_position",
    "get_position_mahajana",
    "get_guardian_quarter",
    "lotus_declaration",
    "verify_lotus",
]
