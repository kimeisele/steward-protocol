"""
PRITHU - Position 0
=====================

Quarter: GENESIS
OpCode: SYS_WAKE
Type: HEAD
Role: Avatar

MANTRA PROTOCOL DERIVATION:
    Position index is the ONLY configuration.
    All properties derived from MAHAMANTRA_POSITIONS.

PARAMPARA: 37 (% 37 == 0 -> CONNECTED)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0x2f04d413"  # GenesisByte: parampara % 37 == 0

from typing import Final, Protocol, runtime_checkable

from vibe_core.mahamantra.substrate.protocol import HeadProtocol

# === BACKWARD-COMPATIBLE CONSTANTS (derived from MantraProtocol) ===
POSITION: Final[int] = 0
QUARTER: Final[str] = "genesis"
OPCODE: Final[str] = "SYS_WAKE"
PARAMPARA_VECTOR: Final[int] = 37


@runtime_checkable
class PrithuProtocol(Protocol):
    """
    Protocol for Prithu (SYS_WAKE).

    Position 0 in the Mahamantra.
    """

    @classmethod
    def position_index(cls) -> int:
        """Get position index."""
        ...

    @classmethod
    def opcode_name(cls) -> str:
        """Get opcode name."""
        ...


class PrithuBase(HeadProtocol):
    """
    Base class for Prithu implementations.

    MANTRA PROTOCOL DERIVATION:
        _position_index = 0  # That's ALL!
        Everything else derived from MAHAMANTRA_POSITIONS.
    """

    _position_index = 0


class NullPrithu(PrithuBase):
    """Null implementation for testing."""
    pass


__all__ = [
    # Backward-compatible constants
    "POSITION",
    "QUARTER",
    "OPCODE",
    "PARAMPARA_VECTOR",
    # Protocol classes
    "PrithuProtocol",
    "PrithuBase",
    "NullPrithu",
]
