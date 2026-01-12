"""
VYASA - Position 4
==================

Quarter: DHARMA
OpCode: COMPILE_AST
Function: Compile AST
Role: Documentation Avatar

FOLDER = WIRING:
    This file exists at: mahamantra/dharma/vyasa/
    Therefore: Position 4 IS wired to Vyasa.

PARAMPARA: 185 (% 37 == 0 -> CONNECTED)
"""

from __future__ import annotations

from typing import ClassVar, Final, Protocol, runtime_checkable

# Position derived from folder location
POSITION: Final[int] = 4
QUARTER: Final[str] = "dharma"
FOLDER: Final[str] = "vyasa"
OWNER: Final[str] = "Vyasa"
IS_HEAD: Final[bool] = True
OPCODE: Final[str] = "COMPILE_AST"

# Parampara vector: (position + 1) * 37
PARAMPARA_VECTOR: Final[int] = 185


@runtime_checkable
class VyasaProtocol(Protocol):
    """
    Protocol for Vyasa (Compile AST).

    Position 4 in the Mahamantra.
    """

    @classmethod
    def position(cls) -> int:
        """Get position index."""
        ...

    @classmethod
    def opcode(cls) -> str:
        """Get opcode name."""
        ...


class VyasaBase:
    """
    Base class for Vyasa implementations.

    FOLDER = WIRING:
        Position derived from: mahamantra/dharma/vyasa/
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


class NullVyasa(VyasaBase):
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
    "VyasaProtocol",
    "VyasaBase",
    "NullVyasa",
]
