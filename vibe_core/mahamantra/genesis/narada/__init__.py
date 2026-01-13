"""
NARADA - Position 2
===================

Quarter: GENESIS
OpCode: ALLOC_MEM
Function: Allocate Memory
Role: Communication

FOLDER = WIRING:
    This file exists at: mahamantra/genesis/narada/
    Therefore: Position 2 IS wired to Narada.

PARAMPARA: 111 (% 37 == 0 -> CONNECTED)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x1713de06"  # GenesisByte: parampara % 37 == 0

from typing import ClassVar, Final, Protocol, runtime_checkable

# Position derived from folder location
POSITION: Final[int] = 2
QUARTER: Final[str] = "genesis"
FOLDER: Final[str] = "narada"
OWNER: Final[str] = "Narada"
IS_HEAD: Final[bool] = False
OPCODE: Final[str] = "ALLOC_MEM"

# Parampara vector: (position + 1) * 37
PARAMPARA_VECTOR: Final[int] = 111


@runtime_checkable
class NaradaProtocol(Protocol):
    """
    Protocol for Narada (Allocate Memory).

    Position 2 in the Mahamantra.
    """

    @classmethod
    def position(cls) -> int:
        """Get position index."""
        ...

    @classmethod
    def opcode(cls) -> str:
        """Get opcode name."""
        ...


class NaradaBase:
    """
    Base class for Narada implementations.

    FOLDER = WIRING:
        Position derived from: mahamantra/genesis/narada/
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


class NullNarada(NaradaBase):
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
    "NaradaProtocol",
    "NaradaBase",
    "NullNarada",
]
