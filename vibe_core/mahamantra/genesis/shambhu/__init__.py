"""
SHAMBHU - Position 3
====================

Quarter: GENESIS
OpCode: INIT_THREAD
Function: Initialize Thread
Role: Destruction

FOLDER = WIRING:
    This file exists at: mahamantra/genesis/shambhu/
    Therefore: Position 3 IS wired to Shambhu.

PARAMPARA: 148 (% 37 == 0 -> CONNECTED)
"""

from __future__ import annotations

from typing import ClassVar, Final, Protocol, runtime_checkable

# Position derived from folder location
POSITION: Final[int] = 3
QUARTER: Final[str] = "genesis"
FOLDER: Final[str] = "shambhu"
OWNER: Final[str] = "Shambhu"
IS_HEAD: Final[bool] = False
OPCODE: Final[str] = "INIT_THREAD"

# Parampara vector: (position + 1) * 37
PARAMPARA_VECTOR: Final[int] = 148


@runtime_checkable
class ShambhuProtocol(Protocol):
    """
    Protocol for Shambhu (Initialize Thread).

    Position 3 in the Mahamantra.
    """

    @classmethod
    def position(cls) -> int:
        """Get position index."""
        ...

    @classmethod
    def opcode(cls) -> str:
        """Get opcode name."""
        ...


class ShambhuBase:
    """
    Base class for Shambhu implementations.

    FOLDER = WIRING:
        Position derived from: mahamantra/genesis/shambhu/
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


class NullShambhu(ShambhuBase):
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
    "ShambhuProtocol",
    "ShambhuBase",
    "NullShambhu",
]
