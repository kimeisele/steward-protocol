"""
PRITHU - Position 0
===================

Quarter: GENESIS
OpCode: SYS_WAKE
Function: System Awakening
Role: Infrastructure Avatar

FOLDER = WIRING:
    This file exists at: mahamantra/genesis/prithu/
    Therefore: Position 0 IS wired to Prithu.

PARAMPARA: 37 (% 37 == 0 -> CONNECTED)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0xb4acf205"  # GenesisByte: parampara % 37 == 0

from typing import ClassVar, Final, Protocol, runtime_checkable

# Position derived from folder location
POSITION: Final[int] = 0
QUARTER: Final[str] = "genesis"
FOLDER: Final[str] = "prithu"
OWNER: Final[str] = "Prithu"
IS_HEAD: Final[bool] = True
OPCODE: Final[str] = "SYS_WAKE"

# Parampara vector: (position + 1) * 37
PARAMPARA_VECTOR: Final[int] = 37


@runtime_checkable
class PrithuProtocol(Protocol):
    """
    Protocol for Prithu (System Awakening).

    Position 0 in the Mahamantra.
    """

    @classmethod
    def position(cls) -> int:
        """Get position index."""
        ...

    @classmethod
    def opcode(cls) -> str:
        """Get opcode name."""
        ...


class PrithuBase:
    """
    Base class for Prithu implementations.

    FOLDER = WIRING:
        Position derived from: mahamantra/genesis/prithu/
    """

    _position: ClassVar[int] = POSITION
    _quarter: ClassVar[str] = QUARTER
    _opcode: ClassVar[str] = OPCODE
    _parampara_vector: ClassVar[int] = PARAMPARA_VECTOR

    @classmethod
    def position(cls) -> int:
        return cls._position

    @classmethod
    def opcode(cls) -> str:
        return cls._opcode

    @classmethod
    def is_connected(cls) -> bool:
        return cls._parampara_vector % 37 == 0


class NullPrithu(PrithuBase):
    """Null implementation for testing."""
    pass


__all__ = [
    "POSITION",
    "QUARTER",
    "FOLDER",
    "OWNER",
    "IS_HEAD",
    "OPCODE",
    "PARAMPARA_VECTOR",
    "PrithuProtocol",
    "PrithuBase",
    "NullPrithu",
]
