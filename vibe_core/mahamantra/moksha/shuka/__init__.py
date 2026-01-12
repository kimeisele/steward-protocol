"""
SHUKA - Position 14
===================

Quarter: MOKSHA
OpCode: LOG_EMIT
Function: Log Emit
Role: Vision

FOLDER = WIRING:
    This file exists at: mahamantra/moksha/shuka/
    Therefore: Position 14 IS wired to Shuka.

PARAMPARA: 555 (% 37 == 0 -> CONNECTED)
"""

from __future__ import annotations

from typing import ClassVar, Final, Protocol, runtime_checkable

# Position derived from folder location
POSITION: Final[int] = 14
QUARTER: Final[str] = "moksha"
FOLDER: Final[str] = "shuka"
OWNER: Final[str] = "Shuka"
IS_HEAD: Final[bool] = False
OPCODE: Final[str] = "LOG_EMIT"

# Parampara vector: (position + 1) * 37
PARAMPARA_VECTOR: Final[int] = 555


@runtime_checkable
class ShukaProtocol(Protocol):
    """
    Protocol for Shuka (Log Emit).

    Position 14 in the Mahamantra.
    """

    @classmethod
    def position(cls) -> int:
        """Get position index."""
        ...

    @classmethod
    def opcode(cls) -> str:
        """Get opcode name."""
        ...


class ShukaBase:
    """
    Base class for Shuka implementations.

    FOLDER = WIRING:
        Position derived from: mahamantra/moksha/shuka/
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


class NullShuka(ShukaBase):
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
    "ShukaProtocol",
    "ShukaBase",
    "NullShuka",
]
