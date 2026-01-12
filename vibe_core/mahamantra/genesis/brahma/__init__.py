"""
BRAHMA - Position 1
===================

Quarter: GENESIS
OpCode: LOAD_ROOT
Function: Load Root Configuration
Role: Creation

FOLDER = WIRING:
    This file exists at: mahamantra/genesis/brahma/
    Therefore: Position 1 IS wired to Brahma.

PARAMPARA: 74 (% 37 == 0 -> CONNECTED)
"""

from __future__ import annotations

from typing import ClassVar, Final, Protocol, runtime_checkable

# Position derived from folder location
POSITION: Final[int] = 1
QUARTER: Final[str] = "genesis"
FOLDER: Final[str] = "brahma"
OWNER: Final[str] = "Brahma"
IS_HEAD: Final[bool] = False
OPCODE: Final[str] = "LOAD_ROOT"

# Parampara vector: (position + 1) * 37
PARAMPARA_VECTOR: Final[int] = 74


@runtime_checkable
class BrahmaProtocol(Protocol):
    """
    Protocol for Brahma (Load Root Configuration).

    Position 1 in the Mahamantra.
    """

    @classmethod
    def position(cls) -> int:
        """Get position index."""
        ...

    @classmethod
    def opcode(cls) -> str:
        """Get opcode name."""
        ...


class BrahmaBase:
    """
    Base class for Brahma implementations.

    FOLDER = WIRING:
        Position derived from: mahamantra/genesis/brahma/
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


class NullBrahma(BrahmaBase):
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
    "BrahmaProtocol",
    "BrahmaBase",
    "NullBrahma",
]
