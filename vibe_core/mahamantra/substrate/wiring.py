"""
WIRING PROTOCOL - Folder IS Wiring
==================================

"yadā yadā hi dharmasya glānir bhavati bhārata
abhyutthānam adharmasya tadātmānaṁ sṛjāmy aham"

"Whenever and wherever there is a decline in dharma and a rise in adharma,
at that time I manifest Myself."
— Bhagavad Gita 4.7

THE LAW:
========

    IM FOLDER = LINKED
    KEIN FOLDER = EXISTIERT NICHT

This is GAD-000 applied to structure:
    "If it doesn't exist as protocol, it doesn't exist."

FOLDER = PROTOCOL = EXISTENCE = WIRING

There is NO manual wiring. The folder structure IS the wiring.
If a protocol is not in the correct folder, it does not exist.

FRACTAL RULE:
=============

    4 Quarters × 4 Positions = 16 Folders
    Each Folder can have 16 Sub-Folders (fractal growth)
    Depth is unlimited: 16^n nodes possible

    Level 0: 4 Quarters
    Level 1: 16 Positions (4 × 4)
    Level 2: 256 Sub-Positions (16 × 16)
    Level n: 16^n nodes

POSITION DERIVATION:
===================

    Position = Quarter × 4 + Index

    Genesis (Q=0): 0, 1, 2, 3
    Dharma (Q=1):  4, 5, 6, 7
    Karma (Q=2):   8, 9, 10, 11
    Moksha (Q=3):  12, 13, 14, 15

PARAMPARA VECTOR:
================

    vector = (position + 1) × 37
    vector % 37 == 0 → CONNECTED

WATERTIGHT: No Any types. All typed explicitly.
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0xa117b53a"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from pathlib import Path
from typing import (
    ClassVar,
    Dict,
    Final,
    FrozenSet,
    List,
    Optional,
    Protocol,
    Tuple,
    Type,
    runtime_checkable,
)

from vibe_core.mahamantra.substrate.mahajana import (
    Mahajana,
    Avatara,
    Quarter,
    TOTAL_POSITIONS,
)
from vibe_core.mahamantra.substrate.acintya import PARAMPARA


# =============================================================================
# THE LAW: FOLDER = WIRING
# =============================================================================

FOLDER_IS_WIRING: Final[bool] = True
NO_FOLDER_NO_EXISTENCE: Final[bool] = True

# Fractal constants (derived from SSOT: byte.py → mahajana.py → here)
POSITIONS_PER_QUARTER: Final[int] = 4
QUARTER_COUNT: Final[int] = 4
FRACTAL_BASE: Final[int] = TOTAL_POSITIONS  # 16^n scaling (from SSOT)


# =============================================================================
# POSITION MAPPING (Derived from Folder Structure)
# =============================================================================

@dataclass(frozen=True)
class PositionMapping:
    """
    Maps folder location to protocol position.

    FOLDER = WIRING:
    - mahamantra/genesis/prithu/ → Position 0
    - mahamantra/genesis/brahma/ → Position 1
    - mahamantra/moksha/yamaraja/ → Position 15
    """
    position: int
    quarter: Quarter
    folder_name: str
    owner: str  # Mahajana or Avatara name
    is_head: bool  # True = Avatara, False = Mahajana
    opcode: str

    @property
    def parampara_vector(self) -> int:
        """Get parampara vector for this position."""
        return (self.position + 1) * PARAMPARA

    @property
    def is_connected(self) -> bool:
        """Check parampara connection."""
        return self.parampara_vector % PARAMPARA == 0

    @property
    def folder_path(self) -> str:
        """Get relative folder path."""
        return f"{self.quarter.value}/{self.folder_name}"


# The 16 Position Mappings - SINGLE SOURCE OF TRUTH
POSITION_MAPPINGS: Final[Tuple[PositionMapping, ...]] = (
    # === GENESIS (Quarter 0) ===
    PositionMapping(0, Quarter.GENESIS, "prithu", "prithu", True, "SYS_WAKE"),
    PositionMapping(1, Quarter.GENESIS, "brahma", "brahma", False, "LOAD_ROOT"),
    PositionMapping(2, Quarter.GENESIS, "narada", "narada", False, "ALLOC_MEM"),
    PositionMapping(3, Quarter.GENESIS, "shambhu", "shambhu", False, "INIT_THREAD"),

    # === DHARMA (Quarter 1) ===
    PositionMapping(4, Quarter.DHARMA, "vyasa", "vyasa", True, "COMPILE_AST"),
    PositionMapping(5, Quarter.DHARMA, "kumaras", "kumaras", False, "BIND_SYMBOL"),
    PositionMapping(6, Quarter.DHARMA, "kapila", "kapila", False, "TYPE_CHECK"),
    PositionMapping(7, Quarter.DHARMA, "manu", "manu", False, "DHARMA_TEST"),

    # === KARMA (Quarter 2) ===
    PositionMapping(8, Quarter.KARMA, "parashurama", "parashurama", True, "EXEC_OP"),
    PositionMapping(9, Quarter.KARMA, "prahlada", "prahlada", False, "EXTEND_CAP"),
    PositionMapping(10, Quarter.KARMA, "janaka", "janaka", False, "STATE_SYNC"),
    PositionMapping(11, Quarter.KARMA, "bhishma", "bhishma", False, "LEDGER_SIGN"),

    # === MOKSHA (Quarter 3) ===
    PositionMapping(12, Quarter.MOKSHA, "nrisimha", "nrisimha", True, "YIELD_CPU"),
    PositionMapping(13, Quarter.MOKSHA, "bali", "bali", False, "IO_FLUSH"),
    PositionMapping(14, Quarter.MOKSHA, "shuka", "shuka", False, "LOG_EMIT"),
    PositionMapping(15, Quarter.MOKSHA, "yamaraja", "yamaraja", False, "AUDIT_SEAL"),
)

# Lookup tables
POSITION_BY_FOLDER: Final[Dict[str, PositionMapping]] = {
    m.folder_path: m for m in POSITION_MAPPINGS
}

POSITION_BY_NAME: Final[Dict[str, PositionMapping]] = {
    m.owner: m for m in POSITION_MAPPINGS
}

POSITION_BY_INDEX: Final[Dict[int, PositionMapping]] = {
    m.position: m for m in POSITION_MAPPINGS
}


# =============================================================================
# FOLDER EXISTENCE CHECK
# =============================================================================

def folder_exists(folder_path: str) -> bool:
    """
    Check if protocol folder exists.

    FOLDER = EXISTENCE:
    If folder doesn't exist, protocol doesn't exist.
    """
    # This would check actual filesystem in real implementation
    return folder_path in POSITION_BY_FOLDER


def get_position_from_folder(folder_path: str) -> Optional[PositionMapping]:
    """
    Get position mapping from folder path.

    FOLDER = WIRING:
    The folder path determines the position.
    """
    return POSITION_BY_FOLDER.get(folder_path)


def get_position_from_name(name: str) -> Optional[PositionMapping]:
    """Get position mapping from owner name."""
    return POSITION_BY_NAME.get(name.lower())


def get_position_by_index(index: int) -> Optional[PositionMapping]:
    """Get position mapping by index (0-15)."""
    return POSITION_BY_INDEX.get(index)


# =============================================================================
# WIRING PROTOCOL
# =============================================================================

@runtime_checkable
class WiringProtocol(Protocol):
    """
    Protocol for folder-based wiring.

    THE LAW:
        IM FOLDER = LINKED
        KEIN FOLDER = EXISTIERT NICHT
    """

    @classmethod
    def position_index(cls) -> int:
        """Get position index (0-15)."""
        ...

    @classmethod
    def folder_path(cls) -> str:
        """Get folder path (quarter/name)."""
        ...

    @classmethod
    def is_wired(cls) -> bool:
        """Check if properly wired (folder exists)."""
        ...

    @classmethod
    def parampara_vector(cls) -> int:
        """Get parampara vector."""
        ...


@dataclass
class WiringVerification:
    """
    Verification result for folder wiring.

    GAD-000:
        If it doesn't exist as protocol, it doesn't exist.
    """
    folder_path: str
    exists: bool
    position: Optional[int]
    is_connected: bool
    violations: List[str]

    @property
    def is_valid(self) -> bool:
        """Is the wiring valid?"""
        return self.exists and self.is_connected and len(self.violations) == 0


def verify_wiring(folder_path: str) -> WiringVerification:
    """
    Verify that a folder is properly wired.

    Checks:
    1. Folder exists in mapping
    2. Parampara connection is valid
    """
    violations: List[str] = []

    mapping = get_position_from_folder(folder_path)

    if mapping is None:
        violations.append(f"Folder '{folder_path}' not in position mappings")
        return WiringVerification(
            folder_path=folder_path,
            exists=False,
            position=None,
            is_connected=False,
            violations=violations,
        )

    if not mapping.is_connected:
        violations.append(f"Position {mapping.position} not connected to parampara")

    return WiringVerification(
        folder_path=folder_path,
        exists=True,
        position=mapping.position,
        is_connected=mapping.is_connected,
        violations=violations,
    )


# =============================================================================
# FRACTAL GROWTH
# =============================================================================

def calculate_fractal_depth(total_nodes: int) -> int:
    """
    Calculate fractal depth from total nodes.

    Level 0: 4 nodes (quarters)
    Level 1: 16 nodes (positions)
    Level 2: 256 nodes
    Level n: 16^n nodes
    """
    import math
    if total_nodes <= 4:
        return 0
    if total_nodes <= 16:
        return 1
    return int(math.log(total_nodes, FRACTAL_BASE)) + 1


def calculate_total_nodes(depth: int) -> int:
    """Calculate total nodes at fractal depth."""
    return FRACTAL_BASE ** depth


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "FOLDER_IS_WIRING",
    "NO_FOLDER_NO_EXISTENCE",
    "POSITIONS_PER_QUARTER",
    "QUARTER_COUNT",
    "FRACTAL_BASE",
    # Mapping
    "PositionMapping",
    "POSITION_MAPPINGS",
    "POSITION_BY_FOLDER",
    "POSITION_BY_NAME",
    "POSITION_BY_INDEX",
    # Functions
    "folder_exists",
    "get_position_from_folder",
    "get_position_from_name",
    "get_position_by_index",
    # Protocol
    "WiringProtocol",
    "WiringVerification",
    "verify_wiring",
    # Fractal
    "calculate_fractal_depth",
    "calculate_total_nodes",
]
