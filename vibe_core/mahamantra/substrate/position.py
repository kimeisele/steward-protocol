"""
POSITION - Die 16 MantraPositionen (Wahrheitstabelle)
=====================================================

"mattaḥ parataraṁ nānyat kiñcid asti dhanañjaya
mayi sarvam idaṁ protaṁ sūtre maṇi-gaṇā iva"

"Es gibt keine Wahrheit, die Mir überlegen wäre.
Alles ruht auf Mir, wie Perlen auf einem Faden aufgereiht."
— Bhagavad Gita 7.7

DAS IST DER FADEN. DIE 16 POSITIONEN SIND DIE PERLEN.

SINGLE SOURCE OF TRUTH:
    from vibe_core.mahamantra.substrate.position import MantraPosition

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final, Tuple, Union

from vibe_core.mahamantra.substrate.mahajana import (
    Mahajana,
    Avatara,
    Quarter,
)
from vibe_core.mahamantra.substrate.byte import HolyName
from vibe_core.mahamantra.substrate.opcode import MantraOpCode


# =============================================================================
# GUARDIAN TYPE - Union of Mahajana and Avatara
# =============================================================================

Guardian = Union[Mahajana, Avatara]


# =============================================================================
# PARAMPARA - Die 37
# =============================================================================

PARAMPARA: Final[int] = 37


# =============================================================================
# MANTRA POSITION - The Atomic Unit of Truth
# =============================================================================

@dataclass(frozen=True)
class MantraPosition:
    """
    Eine einzelne Position im Mahamantra.

    DAS IST DIE QUELLE DER WAHRHEIT.

    Jedes Protokoll, jeder OpCode, jeder Guardian - ALLES leitet sich
    vom Position Index ab. Kein manuelles Wiring.

    Properties:
        index: 0-15 (Position im 16-Wort-Mantra)
        word: HARE, KRISHNA, oder RAMA
        quarter: GENESIS, DHARMA, KARMA, oder MOKSHA
        is_head: True für Positionen 0, 4, 8, 12 (Avatara-owned)
        opcode: Die Instruktion an dieser Position
        guardian: Mahajana oder Avatara
        parampara_vector: (index + 1) * 37
    """

    index: int
    word: HolyName
    quarter: Quarter
    is_head: bool
    opcode: MantraOpCode
    guardian: Guardian

    @property
    def parampara_vector(self) -> int:
        """Parampara vector: (index + 1) * 37."""
        return (self.index + 1) * PARAMPARA

    @property
    def is_connected(self) -> bool:
        """True wenn parampara_vector % 37 == 0."""
        return self.parampara_vector % PARAMPARA == 0


# =============================================================================
# THE 16 POSITIONS - THE TRUTH TABLE
# =============================================================================

MAHAMANTRA_POSITIONS: Final[Tuple[MantraPosition, ...]] = (
    # === GENESIS Quarter (0-3) ===
    MantraPosition(
        index=0,
        word=HolyName.HARE,
        quarter=Quarter.GENESIS,
        is_head=True,
        opcode=MantraOpCode.SYS_WAKE,
        guardian=Avatara.PRITHU,
    ),
    MantraPosition(
        index=1,
        word=HolyName.KRISHNA,
        quarter=Quarter.GENESIS,
        is_head=False,
        opcode=MantraOpCode.LOAD_ROOT,
        guardian=Mahajana.BRAHMA,
    ),
    MantraPosition(
        index=2,
        word=HolyName.HARE,
        quarter=Quarter.GENESIS,
        is_head=False,
        opcode=MantraOpCode.ALLOC_MEM,
        guardian=Mahajana.NARADA,
    ),
    MantraPosition(
        index=3,
        word=HolyName.KRISHNA,
        quarter=Quarter.GENESIS,
        is_head=False,
        opcode=MantraOpCode.INIT_THREAD,  # Fixed: BIND_CTX -> INIT_THREAD
        guardian=Mahajana.SHAMBHU,
    ),
    # === DHARMA Quarter (4-7) ===
    MantraPosition(
        index=4,
        word=HolyName.KRISHNA,
        quarter=Quarter.DHARMA,
        is_head=True,
        opcode=MantraOpCode.COMPILE_AST,  # Fixed: ASSERT_TRUTH -> COMPILE_AST
        guardian=Avatara.VYASA,
    ),
    MantraPosition(
        index=5,
        word=HolyName.KRISHNA,
        quarter=Quarter.DHARMA,
        is_head=False,
        opcode=MantraOpCode.BIND_SYMBOL,  # Fixed: RESOLVE_REQ -> BIND_SYMBOL
        guardian=Mahajana.KUMARAS,
    ),
    MantraPosition(
        index=6,
        word=HolyName.HARE,
        quarter=Quarter.DHARMA,
        is_head=False,
        opcode=MantraOpCode.TYPE_CHECK,  # Fixed: GARBAGE_COLLECT -> TYPE_CHECK
        guardian=Mahajana.KAPILA,
    ),
    MantraPosition(
        index=7,
        word=HolyName.HARE,
        quarter=Quarter.DHARMA,
        is_head=False,
        opcode=MantraOpCode.DHARMA_TEST,  # Fixed: PULSE_SYNC -> DHARMA_TEST
        guardian=Mahajana.MANU,
    ),
    # === KARMA Quarter (8-11) ===
    MantraPosition(
        index=8,
        word=HolyName.HARE,
        quarter=Quarter.KARMA,
        is_head=True,
        opcode=MantraOpCode.EXEC_OP,  # Fixed: FETCH_RES -> EXEC_OP
        guardian=Avatara.PARASHURAMA,
    ),
    MantraPosition(
        index=9,
        word=HolyName.RAMA,
        quarter=Quarter.KARMA,
        is_head=False,
        opcode=MantraOpCode.EXTEND_CAP,  # Fixed: EXEC_SERVICE -> EXTEND_CAP
        guardian=Mahajana.PRAHLADA,
    ),
    MantraPosition(
        index=10,
        word=HolyName.HARE,
        quarter=Quarter.KARMA,
        is_head=False,
        opcode=MantraOpCode.STATE_SYNC,  # Fixed: CHECK_DHARMA -> STATE_SYNC
        guardian=Mahajana.JANAKA,
    ),
    MantraPosition(
        index=11,
        word=HolyName.RAMA,
        quarter=Quarter.KARMA,
        is_head=False,
        opcode=MantraOpCode.LEDGER_SIGN,  # Fixed: COMMIT_LOG -> LEDGER_SIGN
        guardian=Mahajana.BHISHMA,
    ),
    # === MOKSHA Quarter (12-15) ===
    MantraPosition(
        index=12,
        word=HolyName.RAMA,
        quarter=Quarter.MOKSHA,
        is_head=True,
        opcode=MantraOpCode.YIELD_CPU,  # Fixed: CACHE_STATE -> YIELD_CPU
        guardian=Avatara.NRISIMHA,
    ),
    MantraPosition(
        index=13,
        word=HolyName.RAMA,
        quarter=Quarter.MOKSHA,
        is_head=False,
        opcode=MantraOpCode.IO_FLUSH,  # Fixed: OPTIMIZE -> IO_FLUSH
        guardian=Mahajana.BALI,
    ),
    MantraPosition(
        index=14,
        word=HolyName.HARE,
        quarter=Quarter.MOKSHA,
        is_head=False,
        opcode=MantraOpCode.LOG_EMIT,  # Fixed: YIELD_CPU -> LOG_EMIT
        guardian=Mahajana.SHUKA,
    ),
    MantraPosition(
        index=15,
        word=HolyName.HARE,
        quarter=Quarter.MOKSHA,
        is_head=False,
        opcode=MantraOpCode.AUDIT_SEAL,  # Fixed: RESET_IP -> AUDIT_SEAL
        guardian=Mahajana.YAMARAJA,
    ),
)


# =============================================================================
# LOOKUP FUNCTIONS - Pure, typed, no side effects
# =============================================================================

def get_position(index: int) -> MantraPosition:
    """Get position by index (0-15)."""
    if not 0 <= index <= 15:
        raise ValueError(f"Position index must be 0-15, got {index}")
    return MAHAMANTRA_POSITIONS[index]


def get_position_by_guardian(guardian: Guardian) -> MantraPosition:
    """Get position by guardian (Mahajana or Avatara)."""
    for pos in MAHAMANTRA_POSITIONS:
        if pos.guardian == guardian:
            return pos
    raise ValueError(f"Unknown guardian: {guardian}")


def get_position_by_opcode(opcode: MantraOpCode) -> MantraPosition:
    """Get position by opcode."""
    return MAHAMANTRA_POSITIONS[opcode.value]


# Quarter to index mapping
QUARTER_INDEX: dict = {
    Quarter.GENESIS: 0,
    Quarter.DHARMA: 1,
    Quarter.KARMA: 2,
    Quarter.MOKSHA: 3,
}


def get_positions_by_quarter(quarter: Quarter) -> Tuple[MantraPosition, ...]:
    """Get all positions in a quarter."""
    idx = QUARTER_INDEX[quarter]
    start = idx * 4
    return MAHAMANTRA_POSITIONS[start:start + 4]


def get_head_position(quarter: Quarter) -> MantraPosition:
    """Get the HEAD position for a quarter."""
    idx = QUARTER_INDEX[quarter]
    return MAHAMANTRA_POSITIONS[idx * 4]


def get_worker_positions_for_quarter(quarter: Quarter) -> Tuple[MantraPosition, ...]:
    """Get the WORKER positions for a quarter (3 per quarter)."""
    idx = QUARTER_INDEX[quarter]
    start = idx * 4
    return MAHAMANTRA_POSITIONS[start + 1:start + 4]


# Alias for backward compatibility
get_worker_positions = get_worker_positions_for_quarter


def get_all_head_positions() -> Tuple[MantraPosition, ...]:
    """Get all 4 HEAD positions (Avataras at 0, 4, 8, 12)."""
    return tuple(p for p in MAHAMANTRA_POSITIONS if p.is_head)


def get_all_worker_positions() -> Tuple[MantraPosition, ...]:
    """Get all 12 WORKER positions (Mahajanas)."""
    return tuple(p for p in MAHAMANTRA_POSITIONS if not p.is_head)


# Alias for singularity.py compatibility
get_quarter_positions = get_positions_by_quarter


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Types
    "Guardian",
    # Constants
    "PARAMPARA",
    # Position
    "MantraPosition",
    "MAHAMANTRA_POSITIONS",
    # Functions
    "get_position",
    "get_position_by_guardian",
    "get_position_by_opcode",
    "get_positions_by_quarter",
    "get_head_position",
    "get_worker_positions",
    "get_worker_positions_for_quarter",
    "get_all_head_positions",
    "get_all_worker_positions",
    # Aliases
    "get_quarter_positions",
]