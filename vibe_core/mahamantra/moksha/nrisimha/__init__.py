"""
NRISIMHA - Position 12
======================

Quarter: MOKSHA
OpCode: YIELD_CPU
Function: Yield CPU
Role: Protection Avatar

FOLDER = WIRING:
    This file exists at: mahamantra/moksha/nrisimha/
    Therefore: Position 12 IS wired to Nrisimha.

PARAMPARA: 481 (% 37 == 0 -> CONNECTED)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "nrisimha"
__position__ = 12
__genesis__ = "0xc6ebdc06"  # GenesisByte: parampara % 37 == 0

from typing import ClassVar, Final, Protocol, runtime_checkable

# Position derived from folder location
POSITION: Final[int] = 12
QUARTER: Final[str] = "moksha"
FOLDER: Final[str] = "nrisimha"
OWNER: Final[str] = "Nrisimha"
IS_HEAD: Final[bool] = True
OPCODE: Final[str] = "YIELD_CPU"

# Parampara vector: (position + 1) * 37
PARAMPARA_VECTOR: Final[int] = 481


@runtime_checkable
class NrisimhaProtocol(Protocol):
    """
    Protocol for Nrisimha (Yield CPU).

    Position 12 in the Mahamantra.
    """

    @classmethod
    def position(cls) -> int:
        """Get position index."""
        ...

    @classmethod
    def opcode(cls) -> str:
        """Get opcode name."""
        ...


class NrisimhaBase:
    """
    Base class for Nrisimha implementations.

    FOLDER = WIRING:
        Position derived from: mahamantra/moksha/nrisimha/
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


class NullNrisimha(NrisimhaBase):
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
    "NrisimhaProtocol",
    "NrisimhaBase",
    "NullNrisimha",
]
