"""
MANU - Position 7
=================

Quarter: DHARMA
OpCode: DHARMA_TEST
Function: Dharma Test
Role: Law

FOLDER = WIRING:
    This file exists at: mahamantra/dharma/manu/
    Therefore: Position 7 IS wired to Manu.

PARAMPARA: 296 (% 37 == 0 -> CONNECTED)
"""

from __future__ import annotations

from typing import ClassVar, Final, Protocol, runtime_checkable

# Position derived from folder location
POSITION: Final[int] = 7
QUARTER: Final[str] = "dharma"
FOLDER: Final[str] = "manu"
OWNER: Final[str] = "Manu"
IS_HEAD: Final[bool] = False
OPCODE: Final[str] = "DHARMA_TEST"

# Parampara vector: (position + 1) * 37
PARAMPARA_VECTOR: Final[int] = 296


@runtime_checkable
class ManuProtocol(Protocol):
    """
    Protocol for Manu (Dharma Test).

    Position 7 in the Mahamantra.
    """

    @classmethod
    def position(cls) -> int:
        """Get position index."""
        ...

    @classmethod
    def opcode(cls) -> str:
        """Get opcode name."""
        ...


class ManuBase:
    """
    Base class for Manu implementations.

    FOLDER = WIRING:
        Position derived from: mahamantra/dharma/manu/
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


class NullManu(ManuBase):
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
    "ManuProtocol",
    "ManuBase",
    "NullManu",
]
