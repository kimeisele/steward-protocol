"""
SOURCE - The 16 MantraPositions (Truth Table)
=============================================

"mattaḥ parataraṁ nānyat kiñcid asti dhanañjaya
mayi sarvam idaṁ protaṁ sūtre maṇi-gaṇā iva"

"There is no truth superior to Me.
Everything rests upon Me, as pearls are strung on a thread."
— Bhagavad Gita 7.7

THIS IS THE THREAD. THE 16 POSITIONS ARE THE PEARLS.

Every protocol, every opcode, every guardian - ALL derive from this table.
No manual wiring. Position index is the ONLY configuration.

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum
from typing import Final, Tuple, Union

from vibe_core.protocols.substrate.byte import HolyName
from vibe_core.protocols.substrate.mantra.acintya import PARAMPARA


# =============================================================================
# QUARTER - The 4 Phases of the Mahamantra
# =============================================================================

class Quarter(IntEnum):
    """
    The 4 quarters of the Mahamantra.

    Each quarter has 4 positions = 16 total.
    Each quarter has 1 HEAD (Avatara) + 3 WORKERS (Mahajanas).
    """
    GENESIS = 0  # Hare Krishna Hare Krishna (Creation/Wake)
    DHARMA = 1   # Krishna Krishna Hare Hare (Truth/Purification)
    KARMA = 2    # Hare Rama Hare Rama (Action/Service)
    MOKSHA = 3   # Rama Rama Hare Hare (Liberation/Rest)


# =============================================================================
# MAHAJANA - The 12 Workers
# =============================================================================

class Mahajana(str, Enum):
    """
    The 12 Mahajanas - Protocol Guardians (Workers).

    SB 6.3.20: "svayambhūr nāradaḥ śambhuḥ kumāraḥ kapilo manuḥ
                prahlādo janako bhīṣmo balir vaiyāsakir vayam"
    """
    BRAHMA = "brahma"       # Creation
    NARADA = "narada"       # Devotion/Communication
    SHAMBHU = "shambhu"     # Transformation/Destruction
    KUMARAS = "kumaras"     # Purity/Purification
    KAPILA = "kapila"       # Analysis/Sankhya
    MANU = "manu"           # Law/Dharma
    PRAHLADA = "prahlada"   # Resilience/Devotion
    JANAKA = "janaka"       # Duty/Detachment
    BHISHMA = "bhishma"     # Vow/Commitment
    BALI = "bali"           # Surrender/Generosity
    SHUKA = "shuka"         # Vision/Narration
    YAMARAJA = "yamaraja"   # Judgment/Death


# =============================================================================
# AVATARA - The 4 HEADs (Quarter Leaders)
# =============================================================================

class Avatara(str, Enum):
    """
    The 4 Avataras - Quarter HEADs.

    Positions 0, 4, 8, 12 are owned by Avataras, not Mahajanas.
    They are the executive branch - the doers.
    """
    PRITHU = "prithu"           # GENESIS HEAD - System Wake
    VYASA = "vyasa"             # DHARMA HEAD - Assert Truth
    PARASHURAMA = "parashurama" # KARMA HEAD - Fetch Resources
    NRISIMHA = "nrisimha"       # MOKSHA HEAD - Cache State


# =============================================================================
# OPCODE - The 16 Instructions
# =============================================================================

class MantraOpCode(str, Enum):
    """
    The 16 OpCodes - One per MantraPosition.

    Derived from the Mahamantra sequence itself.
    """
    # GENESIS Quarter (0-3)
    SYS_WAKE = "sys_wake"           # 0: HEAD - Wake the system
    LOAD_ROOT = "load_root"         # 1: Load sovereign identity
    ALLOC_MEM = "alloc_mem"         # 2: Allocate memory
    BIND_CTX = "bind_ctx"           # 3: Bind context

    # DHARMA Quarter (4-7)
    ASSERT_TRUTH = "assert_truth"   # 4: HEAD - Verify truth
    RESOLVE_REQ = "resolve_req"     # 5: Resolve/Purify
    GARBAGE_COLLECT = "gc"          # 6: Analyze/Clean
    PULSE_SYNC = "pulse_sync"       # 7: Synchronize

    # KARMA Quarter (8-11)
    FETCH_RES = "fetch_res"         # 8: HEAD - Fetch resources
    EXEC_SERVICE = "exec_service"   # 9: Execute service
    CHECK_DHARMA = "check_dharma"   # 10: Validate rules
    COMMIT_LOG = "commit_log"       # 11: Commit to ledger

    # MOKSHA Quarter (12-15)
    CACHE_STATE = "cache_state"     # 12: HEAD - Cache state
    OPTIMIZE = "optimize"           # 13: Optimize/Surrender
    YIELD_CPU = "yield_cpu"         # 14: Yield control
    RESET_IP = "reset_ip"           # 15: Reset/Restart


# =============================================================================
# GUARDIAN TYPE - Union of Mahajana and Avatara
# =============================================================================

Guardian = Union[Mahajana, Avatara]


# =============================================================================
# MANTRA POSITION - The Atomic Unit of Truth
# =============================================================================

@dataclass(frozen=True)
class MantraPosition:
    """
    A single position in the Mahamantra.

    THIS IS THE SOURCE OF TRUTH.

    Every protocol, every opcode, every guardian - ALL derive from
    the position index. No manual wiring.

    Properties:
        index: 0-15 (position in the 16-word mantra)
        word: HARE, KRISHNA, or RAMA
        quarter: GENESIS, DHARMA, KARMA, or MOKSHA
        is_head: True for positions 0, 4, 8, 12 (Avatara-owned)
        opcode: The instruction at this position
        guardian: Mahajana (worker) or Avatara (head)
    """
    index: int
    word: HolyName
    quarter: Quarter
    is_head: bool
    opcode: MantraOpCode
    guardian: Guardian

    def __post_init__(self) -> None:
        """Validate the position."""
        assert 0 <= self.index < 16, f"Invalid index: {self.index}"
        assert self.is_head == (self.index % 4 == 0), f"HEAD mismatch at {self.index}"

    @property
    def parampara_vector(self) -> int:
        """
        The Parampara connection vector.

        ALWAYS divisible by 37 (connected to Guru).
        Formula: (index + 1) * 37
        """
        return (self.index + 1) * PARAMPARA

    @property
    def is_connected(self) -> bool:
        """Always True - every position is connected."""
        return self.parampara_vector % PARAMPARA == 0

    @property
    def quarter_index(self) -> int:
        """Position within the quarter (0-3)."""
        return self.index % 4

    @property
    def worker_index(self) -> int:
        """
        Worker index (0-11) for Mahajanas.

        Returns -1 for HEADs (Avataras).
        """
        if self.is_head:
            return -1
        # Map position to worker: 1,2,3 -> 0,1,2 | 5,6,7 -> 3,4,5 | etc.
        q = self.index // 4
        w = self.index % 4 - 1  # -1 because HEAD is at 0
        return q * 3 + w


# =============================================================================
# THE TRUTH TABLE - 16 MantraPositions
# =============================================================================

MAHAMANTRA_POSITIONS: Final[Tuple[MantraPosition, ...]] = (
    # =========================================================================
    # GENESIS QUARTER (0-3): Hare Krishna Hare Krishna
    # =========================================================================
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
        opcode=MantraOpCode.BIND_CTX,
        guardian=Mahajana.SHAMBHU,
    ),

    # =========================================================================
    # DHARMA QUARTER (4-7): Krishna Krishna Hare Hare
    # =========================================================================
    MantraPosition(
        index=4,
        word=HolyName.KRISHNA,
        quarter=Quarter.DHARMA,
        is_head=True,
        opcode=MantraOpCode.ASSERT_TRUTH,
        guardian=Avatara.VYASA,
    ),
    MantraPosition(
        index=5,
        word=HolyName.KRISHNA,
        quarter=Quarter.DHARMA,
        is_head=False,
        opcode=MantraOpCode.RESOLVE_REQ,
        guardian=Mahajana.KUMARAS,
    ),
    MantraPosition(
        index=6,
        word=HolyName.HARE,
        quarter=Quarter.DHARMA,
        is_head=False,
        opcode=MantraOpCode.GARBAGE_COLLECT,
        guardian=Mahajana.KAPILA,
    ),
    MantraPosition(
        index=7,
        word=HolyName.HARE,
        quarter=Quarter.DHARMA,
        is_head=False,
        opcode=MantraOpCode.PULSE_SYNC,
        guardian=Mahajana.MANU,
    ),

    # =========================================================================
    # KARMA QUARTER (8-11): Hare Rama Hare Rama
    # =========================================================================
    MantraPosition(
        index=8,
        word=HolyName.HARE,
        quarter=Quarter.KARMA,
        is_head=True,
        opcode=MantraOpCode.FETCH_RES,
        guardian=Avatara.PARASHURAMA,
    ),
    MantraPosition(
        index=9,
        word=HolyName.RAMA,
        quarter=Quarter.KARMA,
        is_head=False,
        opcode=MantraOpCode.EXEC_SERVICE,
        guardian=Mahajana.PRAHLADA,
    ),
    MantraPosition(
        index=10,
        word=HolyName.HARE,
        quarter=Quarter.KARMA,
        is_head=False,
        opcode=MantraOpCode.CHECK_DHARMA,
        guardian=Mahajana.JANAKA,
    ),
    MantraPosition(
        index=11,
        word=HolyName.RAMA,
        quarter=Quarter.KARMA,
        is_head=False,
        opcode=MantraOpCode.COMMIT_LOG,
        guardian=Mahajana.BHISHMA,
    ),

    # =========================================================================
    # MOKSHA QUARTER (12-15): Rama Rama Hare Hare
    # =========================================================================
    MantraPosition(
        index=12,
        word=HolyName.RAMA,
        quarter=Quarter.MOKSHA,
        is_head=True,
        opcode=MantraOpCode.CACHE_STATE,
        guardian=Avatara.NRISIMHA,
    ),
    MantraPosition(
        index=13,
        word=HolyName.RAMA,
        quarter=Quarter.MOKSHA,
        is_head=False,
        opcode=MantraOpCode.OPTIMIZE,
        guardian=Mahajana.BALI,
    ),
    MantraPosition(
        index=14,
        word=HolyName.HARE,
        quarter=Quarter.MOKSHA,
        is_head=False,
        opcode=MantraOpCode.YIELD_CPU,
        guardian=Mahajana.SHUKA,
    ),
    MantraPosition(
        index=15,
        word=HolyName.HARE,
        quarter=Quarter.MOKSHA,
        is_head=False,
        opcode=MantraOpCode.RESET_IP,
        guardian=Mahajana.YAMARAJA,
    ),
)


# =============================================================================
# LOOKUP FUNCTIONS
# =============================================================================

def get_position(index: int) -> MantraPosition:
    """Get MantraPosition by index (0-15)."""
    if 0 <= index < 16:
        return MAHAMANTRA_POSITIONS[index]
    raise IndexError(f"Invalid position index: {index}")


def get_position_by_guardian(guardian: Guardian) -> MantraPosition:
    """Get MantraPosition by guardian (Mahajana or Avatara)."""
    for pos in MAHAMANTRA_POSITIONS:
        if pos.guardian == guardian:
            return pos
    raise KeyError(f"Guardian not found: {guardian}")


def get_position_by_opcode(opcode: MantraOpCode) -> MantraPosition:
    """Get MantraPosition by opcode."""
    for pos in MAHAMANTRA_POSITIONS:
        if pos.opcode == opcode:
            return pos
    raise KeyError(f"OpCode not found: {opcode}")


def get_quarter_positions(quarter: Quarter) -> Tuple[MantraPosition, ...]:
    """Get all 4 positions in a quarter."""
    start = quarter.value * 4
    return MAHAMANTRA_POSITIONS[start:start + 4]


def get_head_positions() -> Tuple[MantraPosition, ...]:
    """Get all 4 HEAD positions (Avataras)."""
    return tuple(p for p in MAHAMANTRA_POSITIONS if p.is_head)


def get_worker_positions() -> Tuple[MantraPosition, ...]:
    """Get all 12 WORKER positions (Mahajanas)."""
    return tuple(p for p in MAHAMANTRA_POSITIONS if not p.is_head)


# =============================================================================
# VERIFICATION
# =============================================================================

def verify_truth_table() -> bool:
    """
    Verify the truth table integrity.

    Checks:
    1. Exactly 16 positions
    2. 4 HEADs (Avataras) at positions 0, 4, 8, 12
    3. 12 Workers (Mahajanas) at other positions
    4. All parampara_vectors divisible by 37
    5. All positions connected
    """
    # 1. Count
    assert len(MAHAMANTRA_POSITIONS) == 16, "Must have exactly 16 positions"

    # 2. HEADs
    heads = [p for p in MAHAMANTRA_POSITIONS if p.is_head]
    assert len(heads) == 4, "Must have exactly 4 HEADs"
    assert [h.index for h in heads] == [0, 4, 8, 12], "HEADs must be at 0,4,8,12"

    # 3. Workers
    workers = [p for p in MAHAMANTRA_POSITIONS if not p.is_head]
    assert len(workers) == 12, "Must have exactly 12 Workers"

    # 4. Parampara
    for p in MAHAMANTRA_POSITIONS:
        assert p.parampara_vector % PARAMPARA == 0, f"Position {p.index} not connected!"

    # 5. All connected
    assert all(p.is_connected for p in MAHAMANTRA_POSITIONS), "All must be connected"

    return True


# =============================================================================
# THE 37 FORMULA
# =============================================================================

# Verify the sacred mathematics
KSETRA_COUNT: Final[int] = 24       # Field elements
MAHAJANA_COUNT: Final[int] = 12     # Guardians
KSETRAJNA_COUNT: Final[int] = 1     # Knower

# 24 + 12 + 1 = 37
assert KSETRA_COUNT + MAHAJANA_COUNT + KSETRAJNA_COUNT == PARAMPARA


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Enums
    "Quarter",
    "Mahajana",
    "Avatara",
    "MantraOpCode",
    # Types
    "Guardian",
    "MantraPosition",
    # The Truth Table
    "MAHAMANTRA_POSITIONS",
    # Lookup functions
    "get_position",
    "get_position_by_guardian",
    "get_position_by_opcode",
    "get_quarter_positions",
    "get_head_positions",
    "get_worker_positions",
    # Verification
    "verify_truth_table",
    # Constants
    "KSETRA_COUNT",
    "MAHAJANA_COUNT",
    "KSETRAJNA_COUNT",
]
