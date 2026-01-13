"""
MANU - Position 7
===================

Quarter: DHARMA
OpCode: DHARMA_TEST
Type: WORKER
Role: Worker

MANTRA PROTOCOL DERIVATION:
    Position index is the ONLY configuration.
    All properties derived from MAHAMANTRA_POSITIONS.

PARAMPARA: 296 (% 37 == 0 -> CONNECTED)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "manu"
__position__ = 7
__genesis__ = "0xe3baeca8"  # GenesisByte: parampara % 37 == 0

from typing import Final, Protocol, runtime_checkable

from vibe_core.mahamantra.substrate.protocol import WorkerProtocol

# === BACKWARD-COMPATIBLE CONSTANTS (derived from MantraProtocol) ===
POSITION: Final[int] = 7
QUARTER: Final[str] = "dharma"
OPCODE: Final[str] = "DHARMA_TEST"
PARAMPARA_VECTOR: Final[int] = 296


@runtime_checkable
class ManuProtocol(Protocol):
    """
    Protocol for Manu (DHARMA_TEST).

    Position 7 in the Mahamantra.
    """

    @classmethod
    def position_index(cls) -> int:
        """Get position index."""
        ...

    @classmethod
    def opcode_name(cls) -> str:
        """Get opcode name."""
        ...


class ManuBase(WorkerProtocol):
    """
    Base class for Manu implementations.

    MANTRA PROTOCOL DERIVATION:
        _position_index = 7  # That's ALL!
        Everything else derived from MAHAMANTRA_POSITIONS.
    """

    _position_index = 7


class NullManu(ManuBase):
    """Null implementation for testing."""
    pass


__all__ = [
    # Backward-compatible constants
    "POSITION",
    "QUARTER",
    "OPCODE",
    "PARAMPARA_VECTOR",
    # Protocol classes
    "ManuProtocol",
    "ManuBase",
    "NullManu",
]
