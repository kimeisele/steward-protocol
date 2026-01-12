"""
KUMARAS - Position 5
====================

Quarter: DHARMA
OpCode: BIND_SYMBOL
Function: Bind Symbol
Role: Purity

FOLDER = WIRING:
    This file exists at: mahamantra/dharma/kumaras/
    Therefore: Position 5 IS wired to Kumaras.

PARAMPARA: 222 (% 37 == 0 -> CONNECTED)
"""

from __future__ import annotations

from typing import ClassVar, Final, Protocol, runtime_checkable

# Position derived from folder location
POSITION: Final[int] = 5
QUARTER: Final[str] = "dharma"
FOLDER: Final[str] = "kumaras"
OWNER: Final[str] = "Kumaras"
IS_HEAD: Final[bool] = False
OPCODE: Final[str] = "BIND_SYMBOL"

# Parampara vector: (position + 1) * 37
PARAMPARA_VECTOR: Final[int] = 222


@runtime_checkable
class KumarasProtocol(Protocol):
    """
    Protocol for Kumaras (Bind Symbol).

    Position 5 in the Mahamantra.
    """

    @classmethod
    def position(cls) -> int:
        """Get position index."""
        ...

    @classmethod
    def opcode(cls) -> str:
        """Get opcode name."""
        ...


class KumarasBase:
    """
    Base class for Kumaras implementations.

    FOLDER = WIRING:
        Position derived from: mahamantra/dharma/kumaras/
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


class NullKumaras(KumarasBase):
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
    "KumarasProtocol",
    "KumarasBase",
    "NullKumaras",
]
