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

from typing import Final, Tuple, FrozenSet
from enum import IntEnum, Enum
from collections import Counter

# =============================================================================
# IMPORT FROM PROTOCOL (THE LAW)
# =============================================================================
from vibe_core.mahamantra.protocols._seed import (
    WORDS,
    PARAMPARA,
    TRINITY,
    QUARTERS,
    PANCHA,
    SHARANAGATI,
    LILA,
    MALA,
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
    HARE = 0     # Shakti (Energie/Ressourcen)
    KRISHNA = 1  # Source (Identität/Kern)
    RAMA = 2     # Ananda (Stabilität/Sicherheit)


# DAS MAHAMANTRA - literally
MAHAMANTRA: Final[Tuple[HolyName, ...]] = (
    # Hare Krishna Hare Krishna Krishna Krishna Hare Hare
    HolyName.HARE, HolyName.KRISHNA, HolyName.HARE, HolyName.KRISHNA,
    HolyName.KRISHNA, HolyName.KRISHNA, HolyName.HARE, HolyName.HARE,
    # Hare Rama Hare Rama Rama Rama Hare Hare
    HolyName.HARE, HolyName.RAMA, HolyName.HARE, HolyName.RAMA,
    HolyName.RAMA, HolyName.RAMA, HolyName.HARE, HolyName.HARE,
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
HARE_COUNT: Final[int] = _counts[HolyName.HARE]      # 8
KRISHNA_COUNT: Final[int] = _counts[HolyName.KRISHNA]  # 4
RAMA_COUNT: Final[int] = _counts[HolyName.RAMA]      # 4

# Die zwei Hälften
HALVES: Final[int] = 2
HALF_SIZE: Final[int] = WORDS // HALVES  # 8


# =============================================================================
# DERIVED: DIE 5 UNIQUE PAARE (Pancha Tattva)
# =============================================================================
# Die 5 unique 2-Wort-Kombinationen IM Mahamantra = Pancha Tattva

def _compute_pairs() -> Tuple[Tuple[HolyName, HolyName], ...]:
    """Compute all 8 pairs from the Mahamantra."""
    return tuple(
        (MAHAMANTRA[i], MAHAMANTRA[i + 1])
        for i in range(0, WORDS, 2)
    )

def _compute_unique_pairs() -> FrozenSet[Tuple[HolyName, HolyName]]:
    """Compute unique pairs."""
    return frozenset(_compute_pairs())

MAHAMANTRA_PAIRS: Final[Tuple[Tuple[HolyName, HolyName], ...]] = _compute_pairs()
UNIQUE_PAIRS: Final[FrozenSet[Tuple[HolyName, HolyName]]] = _compute_unique_pairs()

# PANCHA = 5 unique pairs = Pancha Tattva!
PANCHA: Final[int] = len(UNIQUE_PAIRS)  # 5

# Die 5 Paare mit Namen
PANCHA_PAIR_NAMES: Final[Tuple[str, ...]] = (
    "HARE KRISHNA",    # Chaitanya (×2)
    "HARE RAMA",       # Nityananda (×2)
    "HARE HARE",       # Gadadhara (×2)
    "KRISHNA KRISHNA", # Advaita (×1)
    "RAMA RAMA",       # Srivasa (×1)
)


# =============================================================================
# DERIVED: QUARTERS (4) - Die 4 Phasen
# =============================================================================

class Quarter(IntEnum):
    """Die 4 Quarters - Folder names derive from here."""
    GENESIS = 0   # Positionen 0-3:  INPUT  - Boot, Load, Alloc, Spawn
    DHARMA = 1    # Positionen 4-7:  VERIFY - Parse, Link, Check, Test
    KARMA = 2     # Positionen 8-11: EXECUTE - Run, Scale, Sync, Commit
    MOKSHA = 3    # Positionen 12-15: OUTPUT - Yield, Flush, Log, Exit


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
# DERIVED: SHARANAGATI (6) - Die Minimum Connection
# =============================================================================
# SHARANAGATI = KSHETRA / QUARTERS = 24 / 4 = 6
# Die 6 Glieder der Verbindung

SHARANAGATI: Final[int] = KSHETRA // QUARTERS  # 6

class SharanagatiLimb(str, Enum):
    """Die 6 Glieder der Verbindung - Der Mindest-Vertrag eines Agenten."""
    ANUKULYA = "acceptance"  # Akzeptanz des Förderlichen (Composability)
    PRATIKULYA = "rejection" # Ablehnung des Widrigen (Parseability)
    VISHVASA = "faith"       # Vertrauen in den Schutz (Recoverability)
    VARANAM = "guardianship" # Annahme des Wächters (Discoverability)
    NIKSHEPA = "surrender"   # Selbstübergabe (Observability)
    KARPANYA = "humility"    # Demut/Kein Eigen-Karma (Idempotency)

assert len(SharanagatiLimb) == SHARANAGATI  # 6


# =============================================================================
# DERIVED: KSHETRA_GAD (36) - Das operationale Feld
# =============================================================================
# 6 × 6 = 36 = Die GAD Matrix

KSHETRA_GAD: Final[int] = SHARANAGATI * SHARANAGATI  # 36


# =============================================================================
# DERIVED: PARAMPARA (37) - Der Link
# =============================================================================
# Zwei Wege zur selben Wahrheit (Acintya):
# - Sankhya-Weg: KSHETRA + MAHAJANA_COUNT + KSETRAJNA = 24 + 12 + 1 = 37
# - Sharanagati-Weg: KSHETRA_GAD + KSETRAJNA = 36 + 1 = 37

KSETRAJNA: Final[int] = 1  # Der Knower (Krishna)
MAHAJANA_COUNT: Final[int] = 12  # Die 12 Mahajanas

PARAMPARA: Final[int] = KSHETRA_GAD + KSETRAJNA  # 36 + 1 = 37

# Verification: Beide Wege = 37
assert KSHETRA + MAHAJANA_COUNT + KSETRAJNA == PARAMPARA  # 24 + 12 + 1 = 37
assert KSHETRA_GAD + KSETRAJNA == PARAMPARA  # 36 + 1 = 37


# =============================================================================
# DERIVED: GUARDIANS (16) - 4 Avataras + 12 Mahajanas
# =============================================================================

AVATAR_COUNT: Final[int] = QUARTERS  # 4 Heads

# Die 4 Avataras (Heads) - Geben was fehlt (Yoga-Kshema)
AVATARAS: Final[Tuple[str, ...]] = (
    "prithu",      # Genesis Head: Infrastruktur
    "vyasa",       # Dharma Head: Wissen/Docs
    "parashurama", # Karma Head: Durchsetzung
    "nrisimha",    # Moksha Head: Schutz
)

# Die 12 Mahajanas (Workers) - Bewahren was ist
MAHAJANAS: Final[Tuple[str, ...]] = (
    "brahma", "narada", "shambhu",      # Genesis Workers
    "kumaras", "kapila", "manu",        # Dharma Workers
    "prahlada", "janaka", "bhishma",    # Karma Workers
    "bali", "shuka", "yamaraja"         # Moksha Workers
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
    """Die 4 Säulen des Dharma - Der Integritätscheck."""
    DAYA = "mercy"       # Keine korrupten Daten
    SATYAM = "truth"     # Keine Halluzination
    TAPAS = "austerity"  # Keine Ressourcen-Verschwendung
    SAUCAM = "purity"    # Keine unautorisierten Verbindungen

DHARMA_PILLARS: Final[int] = len(DharmaPillar)  # 4
assert DHARMA_PILLARS == QUARTERS  # 4


# =============================================================================
# DERIVED: QUALITIES (64) - Die Vollständigkeit
# =============================================================================
# 64 = WORDS × QUARTERS = 16 × 4

QUALITIES: Final[int] = WORDS * QUARTERS  # 64


# =============================================================================
# DERIVED: MALA (108) - Der Zyklus
# =============================================================================
# 108 = MAHAJANA_COUNT × 9 = 12 × 9
# Oder: 108 = (KSHETRA + PARAMPARA + LILA - 1) = 24 + 37 + 48 - 1 = 108

MALA: Final[int] = 108
ROUNDS: Final[int] = WORDS  # 16 Runden pro Tag
DAILY_MANTRAS: Final[int] = MALA * ROUNDS  # 1728


# =============================================================================
# VERIFICATION - Alle Ableitungen müssen stimmen
# =============================================================================

assert WORDS == 16, "Mahamantra hat 16 Wörter"
assert TRINITY == 3, "3 Namen: Hare, Krishna, Rama"
assert PANCHA == 5, "5 unique Paare = Pancha Tattva"
assert SHARANAGATI == 6, "6 Glieder der Verbindung"
assert QUARTERS == 4, "4 Quarters"
assert KSHETRA == 24, "Feld = 16 + 8"
assert KSHETRA_GAD == 36, "GAD Feld = 6 × 6"
assert PARAMPARA == 37, "Parampara = 36 + 1"
assert LILA == 48, "Chaitanya Lila = 16 × 3"
assert QUALITIES == 64, "Qualities = 16 × 4"


# =============================================================================
# LOTUS FUNCTIONS - Routing durch den Lotus
# =============================================================================

def get_quarter(position: int) -> Quarter:
    """Get quarter for a position. FOLDER IS WIRING."""
    if not 0 <= position < WORDS:
        raise ValueError(f"Position must be 0-{WORDS-1}, got {position}")
    return Quarter(position // WORDS_PER_QUARTER)


def get_quarter_name(position: int) -> str:
    """Get folder name for a position."""
    return QUARTER_NAMES[get_quarter(position)]


def get_word_at(position: int) -> HolyName:
    """Get the HolyName at a position in the Mahamantra."""
    if not 0 <= position < WORDS:
        raise ValueError(f"Position must be 0-{WORDS-1}, got {position}")
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
    "prithu", "brahma", "narada", "shambhu",
    # Dharma Quarter (4-7)
    "vyasa", "kumaras", "kapila", "manu",
    # Karma Quarter (8-11)
    "parashurama", "prahlada", "janaka", "bhishma",
    # Moksha Quarter (12-15)
    "nrisimha", "bali", "shuka", "yamaraja",
)

MAHAJANA_TO_POSITION: Final[dict] = {
    name: pos for pos, name in enumerate(ALL_GUARDIANS)
}

POSITION_TO_MAHAJANA: Final[dict] = {
    pos: name for pos, name in enumerate(ALL_GUARDIANS)
}


def get_mahajana_position(name: str) -> int:
    """Get position for a mahajana name."""
    return MAHAJANA_TO_POSITION.get(name.lower(), -1)


def get_position_mahajana(position: int) -> str:
    """Get mahajana name for a position."""
    return POSITION_TO_MAHAJANA.get(position, "unknown")


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
    # Kshetra (24, 36)
    "KSHETRA",
    "KSHETRA_GAD",
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
    # Dharma (4)
    "DharmaPillar",
    "DHARMA_PILLARS",
    # Qualities (64)
    "QUALITIES",
    # Mala (108)
    "MALA",
    "ROUNDS",
    "DAILY_MANTRAS",
    # Lotus Functions
    "get_quarter",
    "get_quarter_name",
    "get_positions_in_quarter",
    "get_word_at",
    "get_pair_at",
    "verify_parampara",
    "get_mahajana_position",
    "get_position_mahajana",
    # Lotus Transport
    "lotus_declaration",
    "verify_lotus",
]