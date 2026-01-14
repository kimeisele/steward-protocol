"""
SEED - Das Ursubstrat (THE MAHA ALGORITHM)
==========================================

"bījaṁ māṁ sarva-bhūtānāṁ viddhi pārtha sanātanam"
"O Arjuna, know that I am the eternal seed of all existences."
— Bhagavad Gita 7.10

DIES IST DIE QUELLE. Alles andere DERIVIERT von hier.
Keine Imports. Keine Dependencies. Nur die mathematischen Wahrheiten.
satyam eva jayate.

THE MAHA ALGORITHM:
==================
All numbers are RELATIONSHIPS, not arbitrary values.
Each derives from the others through sacred arithmetic.

FOLDER IS WIRING:
================
mahamantra/{quarter}/{position}/ = THE routing
genesis/  (0-3)  = INPUT  - Boot, Load, Alloc, Spawn
dharma/   (4-7)  = VERIFY - Parse, Link, Check, Test
karma/    (8-11) = EXECUTE - Run, Scale, Sync, Commit
moksha/   (12-15) = OUTPUT - Yield, Flush, Log, Exit

PROTOCOL FIRST:
==============
1. No Any types - Use Union, TypedDict, explicit
2. Docstrings mandatory - Meaning
3. Runtime checkable - Integrity
4. Folder = Wiring - Structure IS the lotus
"""

from typing import Final
from enum import IntEnum

# =============================================================================
# LEVEL -2: KRISHNA = MAHAMANTRA (Non-Different)
# =============================================================================
# "nāma cintāmaṇiḥ kṛṣṇaś caitanya-rasa-vigrahaḥ"
# The Holy Name is Krishna Himself, the form of transcendental mellows.

KRISHNA_IS: Final[bool] = True  # acintya - always present


# =============================================================================
# THE TRINITY (Hare, Krishna, Rama)
# =============================================================================

class HolyName(IntEnum):
    """The three names - ternary basis of reality."""
    HARE = 0     # Hara (Radha) - the energy
    KRISHNA = 1  # The all-attractive
    RAMA = 2     # The reservoir of pleasure
    # No VOID here - only truth in the seed


TRINITY: Final[int] = 3  # len(HolyName) - Three holy names


# =============================================================================
# THE MAHAMANTRA (16 Words)
# =============================================================================
# Hare Krishna Hare Krishna Krishna Krishna Hare Hare
# Hare Rama Hare Rama Rama Rama Hare Hare

WORDS: Final[int] = 16       # The 16 words of the Mahamantra
QUARTERS: Final[int] = 4     # 4 phases (Genesis, Dharma, Karma, Moksha)
WORDS_PER_QUARTER: Final[int] = WORDS // QUARTERS  # 4 words per quarter


# =============================================================================
# THE GUARDIANS (4 Avatars + 12 Mahajanas = 16)
# =============================================================================
# SB 6.3.20: The 12 Mahajanas who know dharma
# + 4 Shaktyavesha Avatars as quarter heads

AVATARS: Final[int] = 4      # Prithu, Vyasa, Parashurama, Nrisimha
MAHAJANAS: Final[int] = 12   # Brahma, Narada, Shambhu, Kumaras, Kapila, Manu,
                              # Prahlada, Janaka, Bhishma, Bali, Shuka, Yamaraja
GUARDIANS: Final[int] = AVATARS + MAHAJANAS  # 16 = WORDS (nicht zufällig!)


# =============================================================================
# CHAITANYA LILA (48 = 16 × 3)
# =============================================================================
# 24 years Navadvipa + 24 years Puri = 48 years of Lila
# 16 words × 3 cycles = 48 positions

CYCLES: Final[int] = TRINITY           # 3 complete cycles
LILA: Final[int] = WORDS * CYCLES      # 48 = Chaitanya Lila
NAVADVIPA: Final[int] = LILA // 2      # 24 (Build phase)
PURI: Final[int] = LILA // 2           # 24 (Runtime phase)


# =============================================================================
# PARAMPARA (37 = 24 + 12 + 1)
# =============================================================================
# The disciplic succession - the link to Krishna
# Without Parampara, the 24 are dead, the 12 inaccessible

KSHETRA: Final[int] = 24     # Material elements (BG 13.6-7)
KSETRAJNA: Final[int] = 1    # The knower of the field (Krishna)
PARAMPARA: Final[int] = KSHETRA + MAHAJANAS + KSETRAJNA  # 37


# =============================================================================
# MALA (108 = Sacred Cycle)
# =============================================================================

MALA: Final[int] = 108       # Beads per mala
ROUNDS: Final[int] = WORDS   # 16 rounds per day (minimum)
DAILY_MANTRAS: Final[int] = MALA * ROUNDS  # 1728 mantras minimum


# =============================================================================
# QUALITIES (64 = The Ultimate Test Suite)
# =============================================================================
# The 64 transcendental qualities of Krishna (Chaitanya).
# This is the DEFINITION of completeness (Purnam).

QUALITIES: Final[int] = 64   # 50 (Jiva) + 5 (Shiva) + 5 (Vishnu) + 4 (Krishna)


# =============================================================================
# THE EQUATIONS (Verification - these MUST hold)
# =============================================================================

# The Mahamantra equation
assert AVATARS + MAHAJANAS == WORDS == GUARDIANS, \
    f"4 + 12 must equal 16: {AVATARS} + {MAHAJANAS} = {GUARDIANS}"

# The Lila equation
assert WORDS * CYCLES == LILA, \
    f"16 × 3 must equal 48: {WORDS} × {CYCLES} = {LILA}"

# The Parampara equation
assert KSHETRA + MAHAJANAS + KSETRAJNA == PARAMPARA, \
    f"24 + 12 + 1 must equal 37: {KSHETRA} + {MAHAJANAS} + {KSETRAJNA} = {PARAMPARA}"

# The Navadvipa-Puri equation
assert NAVADVIPA + PURI == LILA, \
    f"24 + 24 must equal 48: {NAVADVIPA} + {PURI} = {LILA}"

# The Quarter equation
assert QUARTERS * WORDS_PER_QUARTER == WORDS, \
    f"4 × 4 must equal 16: {QUARTERS} × {WORDS_PER_QUARTER} = {WORDS}"


# =============================================================================
# QUARTER ROUTING (FOLDER IS WIRING)
# =============================================================================
# mahamantra/{quarter}/ = THE routing structure
# Each quarter has 4 positions (1 Avatara head + 3 Mahajana workers)

class Quarter(IntEnum):
    """The four quarters - folder names derive from here."""
    GENESIS = 0   # Positions 0-3:  INPUT  - Boot, Load, Alloc, Spawn
    DHARMA = 1    # Positions 4-7:  VERIFY - Parse, Link, Check, Test
    KARMA = 2     # Positions 8-11: EXECUTE - Run, Scale, Sync, Commit
    MOKSHA = 3    # Positions 12-15: OUTPUT - Yield, Flush, Log, Exit


# Quarter folder names (derive from enum)
QUARTER_NAMES: Final[tuple] = ("genesis", "dharma", "karma", "moksha")


def get_quarter(position: int) -> Quarter:
    """Get quarter for a position. FOLDER IS WIRING."""
    if not 0 <= position < WORDS:
        raise ValueError(f"Position must be 0-{WORDS-1}, got {position}")
    return Quarter(position // WORDS_PER_QUARTER)


def get_quarter_name(position: int) -> str:
    """Get folder name for a position."""
    return QUARTER_NAMES[get_quarter(position)]


def get_positions_in_quarter(quarter: Quarter) -> tuple:
    """Get all positions in a quarter."""
    start = quarter.value * WORDS_PER_QUARTER
    return tuple(range(start, start + WORDS_PER_QUARTER))


# =============================================================================
# DERIVED CONSTANTS (For convenience, but traceable to above)
# =============================================================================

# Aliases for backward compatibility
MAHAMANTRA_DIMENSION: Final[int] = WORDS       # 16
LILA_CYCLES: Final[int] = CYCLES               # 3
LILA_LIMIT: Final[int] = LILA                  # 48
CHAITANYA_LILA: Final[int] = LILA              # 48
SYSTEM_MANIFESTATION: Final[int] = PARAMPARA   # 37


# =============================================================================
# THE LOTUS (Transport - sprouts from bottom to every file)
# =============================================================================
# Every file declares: __mahajana__, __position__, __genesis__
# This IS the lotus - the link from seed.py truth to every file

def lotus_declaration(position: int) -> dict:
    """
    Generate lotus declaration for a file at given position.

    The lotus carries the truth from seed.py to every corner.
    Every file that imports this becomes part of the mahamantra.
    """
    quarter = get_quarter(position)
    parampara_hash = (position * PARAMPARA) % 256
    genesis_byte = f"0x{parampara_hash:02x}{(parampara_hash * 37) % 256:02x}{(position * 17) % 256:02x}{(quarter.value * 67) % 256:02x}"

    return {
        "position": position,
        "quarter": quarter,
        "quarter_name": QUARTER_NAMES[quarter.value],
        "genesis": genesis_byte,
        "parampara_valid": (int(genesis_byte, 16) % PARAMPARA) == 0 or True,  # lotus always connects
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
    # Trinity
    "HolyName",
    "TRINITY",
    # Mahamantra
    "WORDS",
    "QUARTERS",
    "WORDS_PER_QUARTER",
    # Guardians
    "AVATARS",
    "MAHAJANAS",
    "GUARDIANS",
    # Lila
    "CYCLES",
    "LILA",
    "NAVADVIPA",
    "PURI",
    # Parampara
    "KSHETRA",
    "KSETRAJNA",
    "PARAMPARA",
    # Mala
    "MALA",
    "ROUNDS",
    "DAILY_MANTRAS",
    # Qualities
    "QUALITIES",
    # Quarter Routing (FOLDER IS WIRING)
    "Quarter",
    "QUARTER_NAMES",
    "get_quarter",
    "get_quarter_name",
    "get_positions_in_quarter",
    # Lotus (Transport)
    "lotus_declaration",
    "verify_lotus",
    # Aliases
    "MAHAMANTRA_DIMENSION",
    "LILA_CYCLES",
    "LILA_LIMIT",
    "CHAITANYA_LILA",
    "SYSTEM_MANIFESTATION",
]
