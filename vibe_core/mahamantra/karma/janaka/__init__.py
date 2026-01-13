"""
JANAKA - Position 10
====================

Quarter: KARMA
OpCode: STATE_SYNC
Function: State Sync
Role: Duty

FOLDER = WIRING:
    This file exists at: mahamantra/karma/janaka/
    Therefore: Position 10 IS wired to Janaka.

PARAMPARA: 407 (% 37 == 0 -> CONNECTED)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x9965a096"  # GenesisByte: parampara % 37 == 0

from typing import ClassVar, Final, Protocol, runtime_checkable

# Position derived from folder location
POSITION: Final[int] = 10
QUARTER: Final[str] = "karma"
FOLDER: Final[str] = "janaka"
OWNER: Final[str] = "Janaka"
IS_HEAD: Final[bool] = False
OPCODE: Final[str] = "STATE_SYNC"

# Parampara vector: (position + 1) * 37
PARAMPARA_VECTOR: Final[int] = 407


@runtime_checkable
class JanakaProtocol(Protocol):
    """
    Protocol for Janaka (State Sync).

    Position 10 in the Mahamantra.
    """

    @classmethod
    def position(cls) -> int:
        """Get position index."""
        ...

    @classmethod
    def opcode(cls) -> str:
        """Get opcode name."""
        ...


class JanakaBase:
    """
    Base class for Janaka implementations.

    FOLDER = WIRING:
        Position derived from: mahamantra/karma/janaka/
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


class NullJanaka(JanakaBase):
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
    "JanakaProtocol",
    "JanakaBase",
    "NullJanaka",
]
