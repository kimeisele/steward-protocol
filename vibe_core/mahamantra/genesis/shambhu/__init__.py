"""
SHAMBHU - Position 3
======================

Quarter: GENESIS
OpCode: INIT_THREAD
Type: WORKER
Role: Worker

MANTRA PROTOCOL DERIVATION:
    Position index is the ONLY configuration.
    All properties derived from MAHAMANTRA_POSITIONS.

PARAMPARA: 148 (% 37 == 0 -> CONNECTED)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "shambhu"
__position__ = 3
__genesis__ = "0x8ed2ec88"  # GenesisByte: parampara % 37 == 0

from typing import Final, Protocol, runtime_checkable

from vibe_core.mahamantra.substrate.protocol import WorkerProtocol

# === BACKWARD-COMPATIBLE CONSTANTS (derived from MantraProtocol) ===
POSITION: Final[int] = 3
QUARTER: Final[str] = "genesis"
OPCODE: Final[str] = "INIT_THREAD"
PARAMPARA_VECTOR: Final[int] = 148


@runtime_checkable
class ShambhuProtocol(Protocol):
    """
    Protocol for Shambhu (INIT_THREAD).

    Position 3 in the Mahamantra.
    """

    @classmethod
    def position_index(cls) -> int:
        """Get position index."""
        ...

    @classmethod
    def opcode_name(cls) -> str:
        """Get opcode name."""
        ...


class ShambhuBase(WorkerProtocol):
    """
    Base class for Shambhu implementations.

    MANTRA PROTOCOL DERIVATION:
        _position_index = 3  # That's ALL!
        Everything else derived from MAHAMANTRA_POSITIONS.
    """

    _position_index = 3


class NullShambhu(ShambhuBase):
    """Null implementation for testing."""
    pass


__all__ = [
    # Backward-compatible constants
    "POSITION",
    "QUARTER",
    "OPCODE",
    "PARAMPARA_VECTOR",
    # Protocol classes
    "ShambhuProtocol",
    "ShambhuBase",
    "NullShambhu",
]
