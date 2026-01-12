"""
PARASHURAMA - Position 8
========================

Quarter: KARMA
OpCode: EXEC_OP
Function: Execute Operation
Role: Enforcement Avatar

FOLDER = WIRING:
    This file exists at: mahamantra/karma/parashurama/
    Therefore: Position 8 IS wired to Parashurama.

PARAMPARA: 333 (% 37 == 0 -> CONNECTED)
"""

from __future__ import annotations

from typing import ClassVar, Final, Protocol, runtime_checkable

# Position derived from folder location
POSITION: Final[int] = 8
QUARTER: Final[str] = "karma"
FOLDER: Final[str] = "parashurama"
OWNER: Final[str] = "Parashurama"
IS_HEAD: Final[bool] = True
OPCODE: Final[str] = "EXEC_OP"

# Parampara vector: (position + 1) * 37
PARAMPARA_VECTOR: Final[int] = 333


@runtime_checkable
class ParashuramaProtocol(Protocol):
    """
    Protocol for Parashurama (Execute Operation).

    Position 8 in the Mahamantra.
    """

    @classmethod
    def position(cls) -> int:
        """Get position index."""
        ...

    @classmethod
    def opcode(cls) -> str:
        """Get opcode name."""
        ...


class ParashuramaBase:
    """
    Base class for Parashurama implementations.

    FOLDER = WIRING:
        Position derived from: mahamantra/karma/parashurama/
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


class NullParashurama(ParashuramaBase):
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
    "ParashuramaProtocol",
    "ParashuramaBase",
    "NullParashurama",
]
