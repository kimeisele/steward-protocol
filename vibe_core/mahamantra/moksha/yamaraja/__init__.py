"""
YAMARAJA - Position 15
======================

Quarter: MOKSHA
OpCode: AUDIT_SEAL
Function: Audit Seal
Role: Judgment

FOLDER = WIRING:
    This file exists at: mahamantra/moksha/yamaraja/
    Therefore: Position 15 IS wired to Yamaraja.

PARAMPARA: 592 (% 37 == 0 -> CONNECTED)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x8e064e37"  # GenesisByte: parampara % 37 == 0

from typing import ClassVar, Final, Protocol, runtime_checkable

# Position derived from folder location
POSITION: Final[int] = 15
QUARTER: Final[str] = "moksha"
FOLDER: Final[str] = "yamaraja"
OWNER: Final[str] = "Yamaraja"
IS_HEAD: Final[bool] = False
OPCODE: Final[str] = "AUDIT_SEAL"

# Parampara vector: (position + 1) * 37
PARAMPARA_VECTOR: Final[int] = 592


@runtime_checkable
class YamarajaProtocol(Protocol):
    """
    Protocol for Yamaraja (Audit Seal).

    Position 15 in the Mahamantra.
    """

    @classmethod
    def position(cls) -> int:
        """Get position index."""
        ...

    @classmethod
    def opcode(cls) -> str:
        """Get opcode name."""
        ...


class YamarajaBase:
    """
    Base class for Yamaraja implementations.

    FOLDER = WIRING:
        Position derived from: mahamantra/moksha/yamaraja/
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


class NullYamaraja(YamarajaBase):
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
    "YamarajaProtocol",
    "YamarajaBase",
    "NullYamaraja",
]
