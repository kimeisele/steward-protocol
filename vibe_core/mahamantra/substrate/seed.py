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

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 4
__genesis__ = "0x30ea0cbc"  # GenesisByte: parampara % 37 == 0

from collections import Counter
from enum import Enum, IntEnum
from typing import Final, FrozenSet, Tuple

# The Acoustic Constitution (Physics of the Emptiness)
from vibe_core.mahamantra.protocols._seed import (
    ACOUSTIC_RATIO as _PROTO_ACOUSTIC_RATIO,
)
from vibe_core.mahamantra.protocols._seed import (
    # New: The fractal levels
    AKSARA_COUNT as _PROTO_AKSARA_COUNT,
)

# The Three Flutes + Harmonic Resonances (direct import for re-export)
# The Maha-Algorithm (Round 14) - Universal Generator
from vibe_core.mahamantra.protocols._seed import (
    AVATAR_COUNT,  # 4 Avataras
    # The Cosmic Frame (Resolution)
    COSMIC_FRAME,
    # The Epoch Key (Temporal Anchor)
    EPOCH_KEY,  # 1972 - The Gita Revelation Year
    FIELD_RESONANCE,
    FLUTE_HOLES_PRODUCT,
    FLUTE_HOLES_SUM,
    MAHA_CLASSICAL_1,
    MAHA_CLASSICAL_2,
    MAHA_CLASSICAL_3,
    MAHA_CLASSICAL_4,
    MAHA_MU,
    MAHA_QUANTUM,
    MAHA_TRITON,
    MAHAJANA_COUNT,  # 12 Mahajanas
    MURALI_HOLES,
    NADI_RESONANCE,
    NAKSHATRA_UNIT,
    NAKSHATRAS,  # 27 - The Astronomical Bridge (derived: JIVA_CYCLE // WORDS)
    PADA_UNIT,
    PHASE_DURATION,  # 12 (LILA // QUARTERS)
    QUARTER_UNIT,
    TITHI_UNIT,
    VAMSI_HOLES,
    VENU_HOLES,
    maha_classical,
    maha_quantum,
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
from vibe_core.mahamantra.protocols._seed import (
    PRANA_DURATION_MS as _PROTO_PRANA_DURATION_MS,
)
from vibe_core.mahamantra.protocols._seed import (
    PRANA_DURATION_S as _PROTO_PRANA_DURATION_S,
)
from vibe_core.mahamantra.protocols._seed import (
    QUALITIES as _PROTO_QUALITIES,
)
from vibe_core.mahamantra.protocols._seed import (
    QUARTERS as _PROTO_QUARTERS,
)
from vibe_core.mahamantra.protocols._seed import (
    RAMA_COUNT as _PROTO_RAMA_COUNT,
)
from vibe_core.mahamantra.protocols._seed import (
    SECONDS_PER_DAY as _PROTO_SECONDS_PER_DAY,
)
from vibe_core.mahamantra.protocols._seed import (
    SHARANAGATI as _PROTO_SHARANAGATI,
)
from vibe_core.mahamantra.protocols._seed import (
    TICK_INTERVAL_MS as _PROTO_TICK_INTERVAL_MS,
)
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
    """Die drei Namen - Basis der Realität."""

    HARE = 0  # Shakti (Energie/Ressourcen)
    KRISHNA = 1  # Source (Identität/Kern)
    RAMA = 2  # Ananda (Stabilität/Sicherheit)


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

# Die Wörter
WORDS: Final[int] = len(MAHAMANTRA)  # 16

# Die drei Namen
TRINITY: Final[int] = len(set(MAHAMANTRA))  # 3

# Counts pro Name
_counts = Counter(MAHAMANTRA)
HARE_COUNT: Final[int] = _counts[HolyName.HARE]  # 8
KRISHNA_COUNT: Final[int] = _counts[HolyName.KRISHNA]  # 4
RAMA_COUNT: Final[int] = _counts[HolyName.RAMA]  # 4

# Die zwei Hälften
HALVES: Final[int] = 2
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
    hare_sum = sum(i + 1 for i, name in enumerate(MAHAMANTRA) if name == HolyName.HARE)
    krishna_sum = sum(i + 1 for i, name in enumerate(MAHAMANTRA) if name == HolyName.KRISHNA)
    rama_sum = sum(i + 1 for i, name in enumerate(MAHAMANTRA) if name == HolyName.RAMA)
    return hare_sum, krishna_sum, rama_sum


_pos_hare, _pos_krishna, _pos_rama = _compute_position_sums()

POSITION_SUM_HARE: Final[int] = _pos_hare  # 70 = 7 × 10
POSITION_SUM_KRISHNA: Final[int] = _pos_krishna  # 17 (prime)
POSITION_SUM_RAMA: Final[int] = _pos_rama  # 49 = 7²
POSITION_SUM_TOTAL: Final[int] = POSITION_SUM_HARE + POSITION_SUM_KRISHNA + POSITION_SUM_RAMA  # 136

# VERIFICATION: Position sums
assert POSITION_SUM_HARE == 70, "Hare position sum must be 70"
assert POSITION_SUM_KRISHNA == 17, "Krishna position sum must be 17 (prime)"
assert POSITION_SUM_RAMA == 49, "Rama position sum must be 49 (7²)"
assert POSITION_SUM_TOTAL == 136, "Total must be 136"

# VERIFICATION: Triangular number property
# Σ(1..n) = n(n+1)/2 → Σ(1..16) = 16×17/2 = 136
_triangular_16 = WORDS * (WORDS + 1) // 2
assert POSITION_SUM_TOTAL == _triangular_16, "Position sum = Triangular(16)"

# VERIFICATION: Structural properties
assert POSITION_SUM_HARE % 7 == 0, "70 is divisible by 7"
assert POSITION_SUM_RAMA == 7 * 7, "49 = 7²"
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
    return tuple((MAHAMANTRA[i], MAHAMANTRA[i + 1]) for i in range(0, WORDS, 2))


def _compute_unique_pairs() -> FrozenSet[Tuple[HolyName, HolyName]]:
    """Compute unique pairs."""
    return frozenset(_compute_pairs())


MAHAMANTRA_PAIRS: Final[Tuple[Tuple[HolyName, HolyName], ...]] = _compute_pairs()
UNIQUE_PAIRS: Final[FrozenSet[Tuple[HolyName, HolyName]]] = _compute_unique_pairs()

# PANCHA = 5 unique pairs = Pancha Tattva!
PANCHA: Final[int] = len(UNIQUE_PAIRS)  # 5

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
    DHARMA = 1  # Positionen 4-7:  VERIFY - Parse, Link, Check, Test
    KARMA = 2  # Positionen 8-11: EXECUTE - Run, Scale, Sync, Commit
    MOKSHA = 3  # Positionen 12-15: OUTPUT - Yield, Flush, Log, Exit


QUARTERS: Final[int] = len(Quarter)  # 4
QUARTER_NAMES: Final[Tuple[str, ...]] = ("genesis", "dharma", "karma", "moksha")
WORDS_PER_QUARTER: Final[int] = WORDS // QUARTERS  # 4


# =============================================================================
# DERIVED: KSHETRA (24) - Das Feld
# =============================================================================
# KSHETRA = WORDS + HARE_COUNT = 16 + 8 = 24
# Das ist die Mathematik: Das Mahamantra (16) plus die Shakti (8 Hares)

KSHETRA: Final[int] = WORDS + HARE_COUNT  # 24


# =============================================================================
# PRIMARY: SHARANAGATI (6) - Die 6 Glieder der Hingabe
# =============================================================================
# SHARANAGATI = 6 - PRIMARY from Shastra (Bhakti-rasamrta-sindhu 1.2.234)
# "anukulyasya sankalpah pratikulyasya varjanam..."
# The 6 limbs of surrender - NOT derived from math, FROM KRISHNA'S TEACHING.
#
# NOTE: That KSHETRA//QUARTERS also equals 6 is Krishna's arrangement (Acintya),
# NOT a derivation. We import from _seed.py which holds this as PRIMARY.

SHARANAGATI: Final[int] = _PROTO_SHARANAGATI  # 6 (from shastra, SSOT)


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

NAVA: Final[int] = HARE_COUNT + KSETRAJNA  # 8 + 1 = 9


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
PARAMPARA: Final[int] = KSHETRA + MAHAJANA_COUNT + KSETRAJNA  # 24 + 12 + 1 = 37

# Verification: Sankhya path
assert PARAMPARA == 37, "PARAMPARA must be 37 (Sankhya: 24 + 12 + 1)"


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

LILA: Final[int] = WORDS * TRINITY  # 48
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

QUALITIES: Final[int] = WORDS * QUARTERS  # 64
HIDDEN_RESERVE: Final[int] = QUALITIES - LILA  # 64 - 48 = 16

# Verification: Hidden Reserve = WORDS (the seed itself)
assert HIDDEN_RESERVE == WORDS, "Hidden reserve must equal WORDS (16)"


# =============================================================================
# DERIVED: MALA (108) - Der Zyklus
# =============================================================================
# 108 = MAHAJANA_COUNT × NAVA = 12 × 9
# The 12 Mahajanas (authorities) × 9 Processes (devotional service) = 108 Beads
# Alternative path: 108 = (KSHETRA + PARAMPARA + LILA - 1) = 24 + 37 + 48 - 1 = 108

MALA: Final[int] = MAHAJANA_COUNT * NAVA  # 12 × 9 = 108
ROUNDS: Final[int] = WORDS  # 16 Runden pro Tag
DAILY_MANTRAS: Final[int] = MALA * ROUNDS  # 1728


# =============================================================================
# DERIVED: GITA_CHAPTERS (18) - Der Master Regulator
# =============================================================================
# Bhagavad Gita has 18 chapters. Kurukshetra battle was 18 days.
# 18 = SHARANAGATI × TRINITY = 6 × 3 (The 6 limbs acting through 3 Names)
# All resonances divide by 18: 72/4, 108/6, 144/8, 432/24 = 18

GITA_CHAPTERS: Final[int] = SHARANAGATI * TRINITY  # 18

# Verification: 18er-Harmonik
assert GITA_CHAPTERS == 18, "GITA_CHAPTERS must be 18"
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
assert PRANA_DURATION_S == 4, "1 Prana must be 4 seconds"
assert TICK_INTERVAL_MS == 250, "1 Tick must be 250ms"
assert MALA * PRANA_DURATION_S == JIVA_CYCLE, "1 Mala in seconds must equal JIVA_CYCLE"


# =============================================================================
# VERIFICATION - Alle Ableitungen müssen stimmen
# =============================================================================

assert WORDS == 16, "Mahamantra hat 16 Wörter"
assert TRINITY == 3, "3 Namen: Hare, Krishna, Rama"
assert PANCHA == 5, "5 unique Paare = Pancha Tattva"
assert SHARANAGATI == 6, "6 Glieder der Verbindung"
assert QUARTERS == 4, "4 Quarters"
assert KSHETRA == 24, "Feld = 16 + 8"
# NOTE: KSHETRA_GAD (36) REMOVED - was Shaiva, not Gaudiya Vaishnava
assert PARAMPARA == 37, "Parampara = 24 + 12 + 1 (Sankhya path)"
assert LILA == 48, "Chaitanya Lila = 16 × 3"
assert QUALITIES == 64, "Qualities = 16 × 4"
assert NAVA == 9, "Nava = 8 + 1 (Navadha Bhakti)"
assert MALA == 108, "Mala = 12 × 9"
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
assert PRANA_DURATION_S == _PROTO_PRANA_DURATION_S, "SSOT violation: PRANA_DURATION_S != protocols/_seed.py"
assert PRANA_DURATION_MS == _PROTO_PRANA_DURATION_MS, "SSOT violation: PRANA_DURATION_MS != protocols/_seed.py"
assert TICK_INTERVAL_MS == _PROTO_TICK_INTERVAL_MS, "SSOT violation: TICK_INTERVAL_MS != protocols/_seed.py"
assert HALVES == _PROTO_HALVES, "SSOT violation: HALVES != protocols/_seed.py"
assert HALF_SIZE == _PROTO_HALF_SIZE, "SSOT violation: HALF_SIZE != protocols/_seed.py"
assert HARE_COUNT == _PROTO_HARE_COUNT, "SSOT violation: HARE_COUNT != protocols/_seed.py"
assert KRISHNA_COUNT == _PROTO_KRISHNA_COUNT, "SSOT violation: KRISHNA_COUNT != protocols/_seed.py"
assert KSETRAJNA == _PROTO_KSETRAJNA, "SSOT violation: KSETRAJNA != protocols/_seed.py"
assert RAMA_COUNT == _PROTO_RAMA_COUNT, "SSOT violation: RAMA_COUNT != protocols/_seed.py"
assert SECONDS_PER_DAY == _PROTO_SECONDS_PER_DAY, "SSOT violation: SECONDS_PER_DAY != protocols/_seed.py"

# AKSARA_COUNT: 32 syllables (2 per word)
AKSARA_COUNT: Final[int] = WORDS * 2  # 32
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
assert MURALI_FREQ * 2 == VENU_FREQ * 3, "Quinten-Kette: 108×2 = 72×3"
assert VENU_FREQ * 2 == VAMSI_FREQ * 3, "Quinten-Kette: 72×2 = 48×3"

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
        raise ValueError(f"Position must be 0-{WORDS - 1}, got {position}")
    return Quarter(position // WORDS_PER_QUARTER)


def get_quarter_name(position: int) -> str:
    """Get folder name for a position."""
    return QUARTER_NAMES[get_quarter(position)]


def get_word_at(position: int) -> HolyName:
    """Get the HolyName at a position in the Mahamantra."""
    if not 0 <= position < WORDS:
        raise ValueError(f"Position must be 0-{WORDS - 1}, got {position}")
    return MAHAMANTRA[position]


def get_pair_at(position: int) -> Tuple[HolyName, HolyName]:
    """Get the pair starting at position (must be even)."""
    if position % 2 != 0:
        raise ValueError(f"Position must be even, got {position}")
    return MAHAMANTRA_PAIRS[position // 2]


def verify_parampara(value: int) -> bool:
    """Verify connection to Parampara."""
    return value % PARAMPARA == 0


# =============================================================================
# POSITION MAPPING - Mahajana zu Position
# =============================================================================

# Alle 16 Guardians in Order
ALL_GUARDIANS: Final[Tuple[str, ...]] = (
    # Genesis Quarter (0-3)
    "vyasa",
    "brahma",
    "narada",
    "shambhu",
    # Dharma Quarter (4-7)
    "prithu",
    "kumaras",
    "kapila",
    "manu",
    # Karma Quarter (8-11)
    "parashurama",
    "prahlada",
    "janaka",
    "bhishma",
    # Moksha Quarter (12-15)
    "nrisimha",
    "bali",
    "shuka",
    "yamaraja",
)

MAHAJANA_TO_POSITION: Final[dict] = {name: pos for pos, name in enumerate(ALL_GUARDIANS)}

POSITION_TO_MAHAJANA: Final[dict] = {pos: name for pos, name in enumerate(ALL_GUARDIANS)}


def get_mahajana_position(name: str) -> int:
    """Get position for a mahajana name."""
    return MAHAJANA_TO_POSITION.get(name.lower(), -1)


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
    genesis_byte = f"0x{parampara_hash:02x}{(parampara_hash * 37) % 256:02x}{(position * 17) % 256:02x}{(quarter.value * 67) % 256:02x}"

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
        return int(genesis_hex, 16) % PARAMPARA == 0
    except ValueError:
        return False


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # The Source
    "KRISHNA_IS",
    "MAHAMANTRA",
    "HolyName",
    # Primary Derivations
    "WORDS",
    "TRINITY",
    "HARE_COUNT",
    "KRISHNA_COUNT",
    "RAMA_COUNT",
    "HALVES",
    "HALF_SIZE",
    # Pancha (5)
    "MAHAMANTRA_PAIRS",
    "UNIQUE_PAIRS",
    "PANCHA",
    "PANCHA_PAIR_NAMES",
    # Quarters (4)
    "Quarter",
    "QUARTERS",
    "QUARTER_NAMES",
    "WORDS_PER_QUARTER",
    # Sharanagati (6)
    "SharanagatiLimb",
    "SHARANAGATI",
    # Nava (9)
    "NavaBhakti",
    "NAVA",
    # Gita Chapters (18) - Master Regulator
    "GITA_CHAPTERS",
    # Kshetra (24)
    "KSHETRA",
    "KSETRAJNA",
    # Parampara (37)
    "PARAMPARA",
    "MAHAJANA_COUNT",
    # Guardians (16)
    "AVATAR_COUNT",
    "AVATARAS",
    "AVATARS",  # backward-compat alias
    "MAHAJANAS",
    "ALL_GUARDIANS",
    "MAHAJANA_TO_POSITION",
    "POSITION_TO_MAHAJANA",
    # Lila (48)
    "LILA",
    "NAVADVIPA",
    "PURI",
    "PHASE_DURATION",
    # Dharma (4) + Kali Yuga
    "DharmaPillar",
    "DHARMA_PILLARS",
    "KALI_YUGA_LEG",
    # Qualities (64) + Hidden Reserve
    "HIDDEN_RESERVE",
    "QUALITIES",
    "AKSARA_COUNT",
    # Mala (108)
    "MALA",
    "ROUNDS",
    "DAILY_MANTRAS",
    # Jiva (50) - Part and Parcel of Krishna
    "JIVA_CYCLE",
    "JIVA_QUALITIES",
    # Prana (The Breath - Timing)
    "SECONDS_PER_DAY",
    "PRANA_DURATION_S",
    "PRANA_DURATION_MS",
    "TICK_INTERVAL_MS",
    # The Cosmic Frame (Resolution)
    "COSMIC_FRAME",
    "NAKSHATRA_UNIT",
    "TITHI_UNIT",
    "PADA_UNIT",
    "QUARTER_UNIT",
    # The Epoch Key (Temporal Anchor)
    "EPOCH_KEY",
    # The Acoustic Constitution
    "ACOUSTIC_RATIO",
    "END_CORRECTION",
    "VENU_FREQ",
    "VAMSI_FREQ",
    "MURALI_FREQ",
    "CUTOFF_CONSTANT",
    # The Three Flutes (Persons)
    "VENU_HOLES",
    "VAMSI_HOLES",
    "MURALI_HOLES",
    "FLUTE_HOLES_SUM",
    "FLUTE_HOLES_PRODUCT",
    # Harmonic Resonances
    "NADI_RESONANCE",
    "FIELD_RESONANCE",
    # Astronomical Bridge (27)
    "NAKSHATRAS",
    # Position Sums (Mahamantra Signatures)
    "POSITION_SUM_HARE",
    "POSITION_SUM_KRISHNA",
    "POSITION_SUM_RAMA",
    "POSITION_SUM_TOTAL",
    # The Maha-Algorithm (Universal Generator)
    "maha_quantum",
    "maha_classical",
    "MAHA_QUANTUM",  # 137 = T(16) + KSETRAJNA
    "MAHA_MU",  # 1836 = MALA × KRISHNA_POS
    "MAHA_TRITON",  # 5508 = KRISHNA_POS × GITA²
    "MAHA_CLASSICAL_1",
    "MAHA_CLASSICAL_2",
    "MAHA_CLASSICAL_3",
    "MAHA_CLASSICAL_4",
    # Lotus Functions
    "get_quarter",
    "get_quarter_name",
    "get_positions_in_quarter",
    "get_word_at",
    "get_pair_at",
    "verify_parampara",
    "get_mahajana_position",
    "get_position_mahajana",
    "get_guardian_quarter",
    # Lotus Transport
    "lotus_declaration",
    "verify_lotus",
]
