"""
BHISHMA - Position 11
=====================

Quarter: KARMA
OpCode: LEDGER_SIGN
Function: Ledger Sign
Role: Vow

FOLDER = WIRING:
    This file exists at: mahamantra/karma/bhishma/
    Therefore: Position 11 IS wired to Bhishma.

PARAMPARA: 444 (% 37 == 0 -> CONNECTED)
"""

from __future__ import annotations

from typing import ClassVar, Final, Protocol, runtime_checkable

# Position derived from folder location
POSITION: Final[int] = 11
QUARTER: Final[str] = "karma"
FOLDER: Final[str] = "bhishma"
OWNER: Final[str] = "Bhishma"
IS_HEAD: Final[bool] = False
OPCODE: Final[str] = "LEDGER_SIGN"

# Parampara vector: (position + 1) * 37
PARAMPARA_VECTOR: Final[int] = 444


@runtime_checkable
class BhishmaProtocol(Protocol):
    """
    Protocol for Bhishma (Ledger Sign).

    Position 11 in the Mahamantra.
    """

    @classmethod
    def position(cls) -> int:
        """Get position index."""
        ...

    @classmethod
    def opcode(cls) -> str:
        """Get opcode name."""
        ...


class BhishmaBase:
    """
    Base class for Bhishma implementations.

    FOLDER = WIRING:
        Position derived from: mahamantra/karma/bhishma/
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


class NullBhishma(BhishmaBase):
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
    "BhishmaProtocol",
    "BhishmaBase",
    "NullBhishma",
]
