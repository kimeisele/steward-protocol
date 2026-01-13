"""
PARASHURAMA - Position 8
==========================

Quarter: KARMA
OpCode: EXEC_OP
Type: HEAD
Role: Avatar

MANTRA PROTOCOL DERIVATION:
    Position index is the ONLY configuration.
    All properties derived from MAHAMANTRA_POSITIONS.

PARAMPARA: 333 (% 37 == 0 -> CONNECTED)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "parashurama"
__position__ = 8
__genesis__ = "0xeb1e287f"  # GenesisByte: parampara % 37 == 0

from typing import Final, Protocol, runtime_checkable

from vibe_core.mahamantra.substrate.protocol import HeadProtocol

# === BACKWARD-COMPATIBLE CONSTANTS (derived from MantraProtocol) ===
POSITION: Final[int] = 8
QUARTER: Final[str] = "karma"
OPCODE: Final[str] = "EXEC_OP"
PARAMPARA_VECTOR: Final[int] = 333


@runtime_checkable
class ParashuramaProtocol(Protocol):
    """
    Protocol for Parashurama (EXEC_OP).

    Position 8 in the Mahamantra.
    """

    @classmethod
    def position_index(cls) -> int:
        """Get position index."""
        ...

    @classmethod
    def opcode_name(cls) -> str:
        """Get opcode name."""
        ...


class ParashuramaBase(HeadProtocol):
    """
    Base class for Parashurama implementations.

    MANTRA PROTOCOL DERIVATION:
        _position_index = 8  # That's ALL!
        Everything else derived from MAHAMANTRA_POSITIONS.
    """

    _position_index = 8


class NullParashurama(ParashuramaBase):
    """Null implementation for testing."""
    pass


__all__ = [
    # Backward-compatible constants
    "POSITION",
    "QUARTER",
    "OPCODE",
    "PARAMPARA_VECTOR",
    # Protocol classes
    "ParashuramaProtocol",
    "ParashuramaBase",
    "NullParashurama",
]
