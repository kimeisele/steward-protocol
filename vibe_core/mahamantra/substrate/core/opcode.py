"""
OPCODE - Die 16 OpCodes des Mahamantra
======================================

"Hare Krishna Hare Krishna Krishna Krishna Hare Hare
 Hare Rama Hare Rama Rama Rama Hare Hare"

16 Worte = 16 OpCodes = 16 Positionen = komplettes Instruction Set.

SINGLE SOURCE OF TRUTH:
    from vibe_core.mahamantra.substrate.opcode import MantraOpCode

REVERTED TO TRUTH (Post-Legacy Clean Slate).

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

from vibe_core.mahamantra.protocols._seed import (
    HALVES,
    HARE_COUNT,
    KSETRAJNA,
    MAHAJANA_COUNT,
    NAVA,
    PANCHA,
    QUARTERS,
    SEVEN,
    SHARANAGATI,
    TEN,
    TRINITY,
)

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0xa2b509db"  # GenesisByte: parampara % 37 == 0

from enum import IntEnum
from typing import Dict, Final, FrozenSet

from vibe_core.mahamantra.substrate.mahajana import Quarter
from vibe_core.mahamantra.substrate.seed import MAHAMANTRA, PARAMPARA, WORDS

# =============================================================================
# THE 16 OPCODES - SSOT (The New Truth)
# =============================================================================


class MantraOpCode(IntEnum):
    """
    Die 16 OpCodes des Mahamantra.

    Jeder OpCode entspricht einer Position (0-15) und einem Mahajana.
    Der OpCode IST die Instruktion, die Position IST das Routing.

    GENESIS Quarter (0-3): System startup und creation
    DHARMA Quarter (4-7): Gesetz, Analyse, Governance
    KARMA Quarter (8-11): Aktion, Execution, Commitment
    MOKSHA Quarter (12-15): Befreiung, Output, Completion
    """

    # === GENESIS Quarter (Hare Krishna Hare Krishna) ===
    SYS_WAKE = 0  # VYASA: System awakening, boot (Genesis HEAD)
    LOAD_ROOT = KSETRAJNA  # Brahma: Load root configuration, DI
    ALLOC_MEM = HALVES  # Narada: Allocate memory, communication
    INIT_THREAD = TRINITY  # Shambhu: Initialize thread, destruction ready

    # === DHARMA Quarter (Krishna Krishna Hare Hare) ===
    COMPILE_AST = QUARTERS  # PRITHU: Compile AST, encode knowledge (Dharma HEAD)
    BIND_SYMBOL = PANCHA  # Kumaras: Bind symbol, memory, cognition
    TYPE_CHECK = SHARANAGATI  # Kapila: Type check, analysis
    DHARMA_TEST = SEVEN  # Manu: Dharma test, law check

    # === KARMA Quarter (Hare Rama Hare Rama) ===
    EXEC_OP = HARE_COUNT  # Parashurama: Execute operation
    EXTEND_CAP = NAVA  # Prahlada: Extend capability, plugins
    STATE_SYNC = TEN  # Janaka: Sync state, kernel
    LEDGER_SIGN = 11  # Bhishma: Sign ledger, commitment

    # === MOKSHA Quarter (Rama Rama Hare Hare) ===
    YIELD_CPU = MAHAJANA_COUNT  # Nrisimha: Yield CPU, protection
    IO_FLUSH = 13  # Bali: Flush I/O, resources
    LOG_EMIT = 14  # Shuka: Emit log, output
    AUDIT_SEAL = 15  # Yamaraja: Seal audit, judgment


# =============================================================================
# OPCODE NAMES - Lookup table
# =============================================================================

OPCODE_NAMES: Final[Dict[int, str]] = {op.value: op.name for op in MantraOpCode}


# =============================================================================
# MAHAJANA TO OPCODE - Mapping
# =============================================================================

MAHAJANA_OPCODES: Final[Dict[str, MantraOpCode]] = {
    # === Aligned with seed.py ALL_GUARDIANS (SSOT) ===
    # Genesis Quarter (0-3)
    "vyasa": MantraOpCode.SYS_WAKE,  # Position 0 - Genesis HEAD
    "brahma": MantraOpCode.LOAD_ROOT,  # Position 1
    "narada": MantraOpCode.ALLOC_MEM,  # Position 2
    "shambhu": MantraOpCode.INIT_THREAD,  # Position 3
    # Dharma Quarter (4-7)
    "prithu": MantraOpCode.COMPILE_AST,  # Position 4 - Dharma HEAD
    "kumaras": MantraOpCode.BIND_SYMBOL,  # Position 5
    "kapila": MantraOpCode.TYPE_CHECK,  # Position 6
    "manu": MantraOpCode.DHARMA_TEST,  # Position 7
    # Karma Quarter (8-11)
    "parashurama": MantraOpCode.EXEC_OP,  # Position 8 - Karma HEAD
    "prahlada": MantraOpCode.EXTEND_CAP,  # Position 9
    "janaka": MantraOpCode.STATE_SYNC,  # Position 10
    "bhishma": MantraOpCode.LEDGER_SIGN,  # Position 11
    # Moksha Quarter (12-15)
    "nrisimha": MantraOpCode.YIELD_CPU,  # Position 12 - Moksha HEAD
    "bali": MantraOpCode.IO_FLUSH,  # Position 13
    "shuka": MantraOpCode.LOG_EMIT,  # Position 14
    "yamaraja": MantraOpCode.AUDIT_SEAL,  # Position 15
}


# =============================================================================
# QUARTER TO OPCODES - By Quarter
# =============================================================================

GENESIS_OPCODES: Final[FrozenSet[MantraOpCode]] = frozenset(
    {
        MantraOpCode.SYS_WAKE,
        MantraOpCode.LOAD_ROOT,
        MantraOpCode.ALLOC_MEM,
        MantraOpCode.INIT_THREAD,
    }
)

DHARMA_OPCODES: Final[FrozenSet[MantraOpCode]] = frozenset(
    {
        MantraOpCode.COMPILE_AST,
        MantraOpCode.BIND_SYMBOL,
        MantraOpCode.TYPE_CHECK,
        MantraOpCode.DHARMA_TEST,
    }
)

KARMA_OPCODES: Final[FrozenSet[MantraOpCode]] = frozenset(
    {
        MantraOpCode.EXEC_OP,
        MantraOpCode.EXTEND_CAP,
        MantraOpCode.STATE_SYNC,
        MantraOpCode.LEDGER_SIGN,
    }
)

MOKSHA_OPCODES: Final[FrozenSet[MantraOpCode]] = frozenset(
    {
        MantraOpCode.YIELD_CPU,
        MantraOpCode.IO_FLUSH,
        MantraOpCode.LOG_EMIT,
        MantraOpCode.AUDIT_SEAL,
    }
)

QUARTER_OPCODES: Final[Dict[Quarter, FrozenSet[MantraOpCode]]] = {
    Quarter.GENESIS: GENESIS_OPCODES,
    Quarter.DHARMA: DHARMA_OPCODES,
    Quarter.KARMA: KARMA_OPCODES,
    Quarter.MOKSHA: MOKSHA_OPCODES,
}


# =============================================================================
# FUNCTIONS - Pure, typed, no side effects
# =============================================================================


def get_opcode(position: int) -> MantraOpCode:
    """Get the opcode for a position (0-15)."""
    if not 0 <= position <= 15:
        raise ValueError(f"Position must be 0-15, got {position}")
    return MantraOpCode(position)


def get_opcode_name(position: int) -> str:
    """Get the opcode name for a position."""
    return OPCODE_NAMES.get(position, "UNKNOWN")


def get_mahajana_opcode(mahajana: str) -> MantraOpCode:
    """Get the opcode for a mahajana name."""
    opcode = MAHAJANA_OPCODES.get(mahajana.lower())
    if opcode is None:
        raise ValueError(f"Unknown mahajana: {mahajana}")
    return opcode


def get_opcode_quarter(opcode: MantraOpCode) -> Quarter:
    """Get the quarter for an opcode."""
    position = opcode.value
    if position < QUARTERS:
        return Quarter.GENESIS
    if position < HARE_COUNT:
        return Quarter.DHARMA
    if position < MAHAJANA_COUNT:
        return Quarter.KARMA
    return Quarter.MOKSHA


def get_quarter_opcodes(quarter: Quarter) -> FrozenSet[MantraOpCode]:
    """Get all opcodes for a quarter."""
    return QUARTER_OPCODES[quarter]


# =============================================================================
# PARAMPARA VECTORS - For each opcode (PARAMPARA imported from acintya.py SSOT)
# =============================================================================

OPCODE_PARAMPARA: Final[Dict[MantraOpCode, int]] = {
    opcode: (opcode.value + KSETRAJNA) * PARAMPARA for opcode in MantraOpCode
}


def get_opcode_parampara(opcode: MantraOpCode) -> int:
    """Get the parampara vector for an opcode."""
    return OPCODE_PARAMPARA[opcode]


def verify_opcode_parampara(opcode: MantraOpCode, vector: int) -> bool:
    """Verify a parampara vector for an opcode."""
    expected = get_opcode_parampara(opcode)
    return vector == expected and vector % PARAMPARA == 0


# =============================================================================
# THE LIVING SEQUENCE - Nrisimha reads from here, not dead protocols/substrate
# =============================================================================
# Derived from seed.py MAHAMANTRA - the ONE SOURCE
# "nrisimhaḥ kesarī śārdūlo vyāghro vāraṇa-puṅgavaḥ"

MAHAMANTRA_SEQUENCE: Final[tuple] = tuple((MAHAMANTRA[i].name.capitalize(), MantraOpCode(i)) for i in range(WORDS))


# =============================================================================
# EXPORTS - Explicit is better than implicit
# =============================================================================

__all__ = [
    # The OpCode enum
    "MantraOpCode",
    # Lookup tables
    "OPCODE_NAMES",
    "MAHAJANA_OPCODES",
    # Quarter groupings
    "GENESIS_OPCODES",
    "DHARMA_OPCODES",
    "KARMA_OPCODES",
    "MOKSHA_OPCODES",
    "QUARTER_OPCODES",
    # Functions
    "get_opcode",
    "get_opcode_name",
    "get_mahajana_opcode",
    "get_opcode_quarter",
    "get_quarter_opcodes",
    # Parampara
    "PARAMPARA",
    "OPCODE_PARAMPARA",
    "get_opcode_parampara",
    "verify_opcode_parampara",
    # The Living Sequence
    "MAHAMANTRA_SEQUENCE",
]
