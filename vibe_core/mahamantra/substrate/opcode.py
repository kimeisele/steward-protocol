"""
OPCODE - Die 16 OpCodes des Mahamantra
======================================

"Hare Krishna Hare Krishna Krishna Krishna Hare Hare
 Hare Rama Hare Rama Rama Rama Hare Hare"

16 Worte = 16 OpCodes = 16 Positionen = komplettes Instruction Set.

SINGLE SOURCE OF TRUTH:
    from vibe_core.mahamantra.substrate.opcode import MantraOpCode

KEIN DUPLIKAT MEHR. NUR DIESE DATEI.

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

from enum import IntEnum
from typing import Dict, Final, FrozenSet, Tuple

from vibe_core.mahamantra.substrate.mahajana import Quarter


# =============================================================================
# THE 16 OPCODES - SSOT
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
    SYS_WAKE = 0       # Prithu: System awakening, boot
    LOAD_ROOT = 1      # Brahma: Load root configuration, DI
    ALLOC_MEM = 2      # Narada: Allocate memory, communication
    INIT_THREAD = 3    # Shambhu: Initialize thread, destruction ready

    # === DHARMA Quarter (Krishna Krishna Hare Hare) ===
    COMPILE_AST = 4    # Vyasa: Compile AST, encode knowledge
    BIND_SYMBOL = 5    # Kumaras: Bind symbol, memory, cognition
    TYPE_CHECK = 6     # Kapila: Type check, analysis
    DHARMA_TEST = 7    # Manu: Dharma test, law check

    # === KARMA Quarter (Hare Rama Hare Rama) ===
    EXEC_OP = 8        # Parashurama: Execute operation
    EXTEND_CAP = 9     # Prahlada: Extend capability, plugins
    STATE_SYNC = 10    # Janaka: Sync state, kernel
    LEDGER_SIGN = 11   # Bhishma: Sign ledger, commitment

    # === MOKSHA Quarter (Rama Rama Hare Hare) ===
    YIELD_CPU = 12     # Nrisimha: Yield CPU, protection
    IO_FLUSH = 13      # Bali: Flush I/O, resources
    LOG_EMIT = 14      # Shuka: Emit log, output
    AUDIT_SEAL = 15    # Yamaraja: Seal audit, judgment


# =============================================================================
# OPCODE NAMES - Lookup table
# =============================================================================

OPCODE_NAMES: Final[Dict[int, str]] = {op.value: op.name for op in MantraOpCode}


# =============================================================================
# MAHAJANA TO OPCODE - Mapping
# =============================================================================

MAHAJANA_OPCODES: Final[Dict[str, MantraOpCode]] = {
    "prithu": MantraOpCode.SYS_WAKE,
    "brahma": MantraOpCode.LOAD_ROOT,
    "narada": MantraOpCode.ALLOC_MEM,
    "shambhu": MantraOpCode.INIT_THREAD,
    "vyasa": MantraOpCode.COMPILE_AST,
    "kumaras": MantraOpCode.BIND_SYMBOL,
    "kapila": MantraOpCode.TYPE_CHECK,
    "manu": MantraOpCode.DHARMA_TEST,
    "parashurama": MantraOpCode.EXEC_OP,
    "prahlada": MantraOpCode.EXTEND_CAP,
    "janaka": MantraOpCode.STATE_SYNC,
    "bhishma": MantraOpCode.LEDGER_SIGN,
    "nrisimha": MantraOpCode.YIELD_CPU,
    "bali": MantraOpCode.IO_FLUSH,
    "shuka": MantraOpCode.LOG_EMIT,
    "yamaraja": MantraOpCode.AUDIT_SEAL,
}


# =============================================================================
# QUARTER TO OPCODES - By Quarter
# =============================================================================

GENESIS_OPCODES: Final[FrozenSet[MantraOpCode]] = frozenset({
    MantraOpCode.SYS_WAKE,
    MantraOpCode.LOAD_ROOT,
    MantraOpCode.ALLOC_MEM,
    MantraOpCode.INIT_THREAD,
})

DHARMA_OPCODES: Final[FrozenSet[MantraOpCode]] = frozenset({
    MantraOpCode.COMPILE_AST,
    MantraOpCode.BIND_SYMBOL,
    MantraOpCode.TYPE_CHECK,
    MantraOpCode.DHARMA_TEST,
})

KARMA_OPCODES: Final[FrozenSet[MantraOpCode]] = frozenset({
    MantraOpCode.EXEC_OP,
    MantraOpCode.EXTEND_CAP,
    MantraOpCode.STATE_SYNC,
    MantraOpCode.LEDGER_SIGN,
})

MOKSHA_OPCODES: Final[FrozenSet[MantraOpCode]] = frozenset({
    MantraOpCode.YIELD_CPU,
    MantraOpCode.IO_FLUSH,
    MantraOpCode.LOG_EMIT,
    MantraOpCode.AUDIT_SEAL,
})

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
    if position < 4:
        return Quarter.GENESIS
    if position < 8:
        return Quarter.DHARMA
    if position < 12:
        return Quarter.KARMA
    return Quarter.MOKSHA


def get_quarter_opcodes(quarter: Quarter) -> FrozenSet[MantraOpCode]:
    """Get all opcodes for a quarter."""
    return QUARTER_OPCODES[quarter]


# =============================================================================
# PARAMPARA VECTORS - For each opcode
# =============================================================================

PARAMPARA: Final[int] = 37

OPCODE_PARAMPARA: Final[Dict[MantraOpCode, int]] = {
    opcode: (opcode.value + 1) * PARAMPARA
    for opcode in MantraOpCode
}


def get_opcode_parampara(opcode: MantraOpCode) -> int:
    """Get the parampara vector for an opcode."""
    return OPCODE_PARAMPARA[opcode]


def verify_opcode_parampara(opcode: MantraOpCode, vector: int) -> bool:
    """Verify a parampara vector for an opcode."""
    expected = get_opcode_parampara(opcode)
    return vector == expected and vector % PARAMPARA == 0


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
]
