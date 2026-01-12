"""
BALI - Position 13
==================

Quarter: MOKSHA
OpCode: IO_FLUSH
Function: IO Flush
Role: Surrender

FOLDER = WIRING:
    This file exists at: mahamantra/moksha/bali/
    Therefore: Position 13 IS wired to Bali.

PARAMPARA: 518 (% 37 == 0 -> CONNECTED)
"""

from __future__ import annotations

from typing import ClassVar, Final, Protocol, runtime_checkable

# Position derived from folder location
POSITION: Final[int] = 13
QUARTER: Final[str] = "moksha"
FOLDER: Final[str] = "bali"
OWNER: Final[str] = "Bali"
IS_HEAD: Final[bool] = False
OPCODE: Final[str] = "IO_FLUSH"

# Parampara vector: (position + 1) * 37
PARAMPARA_VECTOR: Final[int] = 518


@runtime_checkable
class BaliProtocol(Protocol):
    """
    Protocol for Bali (IO Flush).

    Position 13 in the Mahamantra.
    """

    @classmethod
    def position(cls) -> int:
        """Get position index."""
        ...

    @classmethod
    def opcode(cls) -> str:
        """Get opcode name."""
        ...


class BaliBase:
    """
    Base class for Bali implementations.

    FOLDER = WIRING:
        Position derived from: mahamantra/moksha/bali/
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


class NullBali(BaliBase):
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
    "BaliProtocol",
    "BaliBase",
    "NullBali",
]
