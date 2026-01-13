"""
BALI - Position 13
===================

Quarter: MOKSHA
OpCode: IO_FLUSH
Type: WORKER
Role: Worker

MANTRA PROTOCOL DERIVATION:
    Position index is the ONLY configuration.
    All properties derived from MAHAMANTRA_POSITIONS.

PARAMPARA: 518 (% 37 == 0 -> CONNECTED)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "bali"
__position__ = 13
__genesis__ = "0x699b2aea"  # GenesisByte: parampara % 37 == 0

from typing import Final, Protocol, runtime_checkable

from vibe_core.mahamantra.substrate.protocol import WorkerProtocol

# === BACKWARD-COMPATIBLE CONSTANTS (derived from MantraProtocol) ===
POSITION: Final[int] = 13
QUARTER: Final[str] = "moksha"
OPCODE: Final[str] = "IO_FLUSH"
PARAMPARA_VECTOR: Final[int] = 518


@runtime_checkable
class BaliProtocol(Protocol):
    """
    Protocol for Bali (IO_FLUSH).

    Position 13 in the Mahamantra.
    """

    @classmethod
    def position_index(cls) -> int:
        """Get position index."""
        ...

    @classmethod
    def opcode_name(cls) -> str:
        """Get opcode name."""
        ...


class BaliBase(WorkerProtocol):
    """
    Base class for Bali implementations.

    MANTRA PROTOCOL DERIVATION:
        _position_index = 13  # That's ALL!
        Everything else derived from MAHAMANTRA_POSITIONS.
    """

    _position_index = 13


class NullBali(BaliBase):
    """Null implementation for testing."""
    pass


__all__ = [
    # Backward-compatible constants
    "POSITION",
    "QUARTER",
    "OPCODE",
    "PARAMPARA_VECTOR",
    # Protocol classes
    "BaliProtocol",
    "BaliBase",
    "NullBali",
]
