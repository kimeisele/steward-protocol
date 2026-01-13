"""
NRISIMHA - Position 12
=======================

Quarter: MOKSHA
OpCode: YIELD_CPU
Type: HEAD
Role: Avatar

MANTRA PROTOCOL DERIVATION:
    Position index is the ONLY configuration.
    All properties derived from MAHAMANTRA_POSITIONS.

PARAMPARA: 481 (% 37 == 0 -> CONNECTED)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "nrisimha"
__position__ = 12
__genesis__ = "0x7ac86006"  # GenesisByte: parampara % 37 == 0

from typing import Final, Protocol, runtime_checkable

from vibe_core.mahamantra.substrate.protocol import HeadProtocol

# === BACKWARD-COMPATIBLE CONSTANTS (derived from MantraProtocol) ===
POSITION: Final[int] = 12
QUARTER: Final[str] = "moksha"
OPCODE: Final[str] = "YIELD_CPU"
PARAMPARA_VECTOR: Final[int] = 481


@runtime_checkable
class NrisimhaProtocol(Protocol):
    """
    Protocol for Nrisimha (YIELD_CPU).

    Position 12 in the Mahamantra.
    """

    @classmethod
    def position_index(cls) -> int:
        """Get position index."""
        ...

    @classmethod
    def opcode_name(cls) -> str:
        """Get opcode name."""
        ...


class NrisimhaBase(HeadProtocol):
    """
    Base class for Nrisimha implementations.

    MANTRA PROTOCOL DERIVATION:
        _position_index = 12  # That's ALL!
        Everything else derived from MAHAMANTRA_POSITIONS.
    """

    _position_index = 12


class NullNrisimha(NrisimhaBase):
    """Null implementation for testing."""
    pass


__all__ = [
    # Backward-compatible constants
    "POSITION",
    "QUARTER",
    "OPCODE",
    "PARAMPARA_VECTOR",
    # Protocol classes
    "NrisimhaProtocol",
    "NrisimhaBase",
    "NullNrisimha",
]
