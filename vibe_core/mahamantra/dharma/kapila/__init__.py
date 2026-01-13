"""
KAPILA - Position 6
===================

Quarter: DHARMA
OpCode: TYPE_CHECK
Function: Type Check
Role: Analysis

FOLDER = WIRING:
    This file exists at: mahamantra/dharma/kapila/
    Therefore: Position 6 IS wired to Kapila.

PARAMPARA: 259 (% 37 == 0 -> CONNECTED)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x53b9e54f"  # GenesisByte: parampara % 37 == 0

from typing import ClassVar, Final, Protocol, runtime_checkable

# Position derived from folder location
POSITION: Final[int] = 6
QUARTER: Final[str] = "dharma"
FOLDER: Final[str] = "kapila"
OWNER: Final[str] = "Kapila"
IS_HEAD: Final[bool] = False
OPCODE: Final[str] = "TYPE_CHECK"

# Parampara vector: (position + 1) * 37
PARAMPARA_VECTOR: Final[int] = 259


@runtime_checkable
class KapilaProtocol(Protocol):
    """
    Protocol for Kapila (Type Check).

    Position 6 in the Mahamantra.
    """

    @classmethod
    def position(cls) -> int:
        """Get position index."""
        ...

    @classmethod
    def opcode(cls) -> str:
        """Get opcode name."""
        ...


class KapilaBase:
    """
    Base class for Kapila implementations.

    FOLDER = WIRING:
        Position derived from: mahamantra/dharma/kapila/
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


class NullKapila(KapilaBase):
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
    "KapilaProtocol",
    "KapilaBase",
    "NullKapila",
]
