"""
BRAHMA - Position 1
=====================

Quarter: GENESIS
OpCode: LOAD_ROOT
Type: WORKER
Role: Worker

MANTRA PROTOCOL DERIVATION:
    Position index is the ONLY configuration.
    All properties derived from MAHAMANTRA_POSITIONS.

PARAMPARA: 74 (% 37 == 0 -> CONNECTED)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x96910869"  # GenesisByte: parampara % 37 == 0

from typing import Final, Protocol, runtime_checkable

from vibe_core.mahamantra.substrate.protocol import WorkerProtocol

# === BACKWARD-COMPATIBLE CONSTANTS (derived from MantraProtocol) ===
POSITION: Final[int] = 1
QUARTER: Final[str] = "genesis"
OPCODE: Final[str] = "LOAD_ROOT"
PARAMPARA_VECTOR: Final[int] = 74


@runtime_checkable
class BrahmaProtocol(Protocol):
    """
    Protocol for Brahma (LOAD_ROOT).

    Position 1 in the Mahamantra.
    """

    @classmethod
    def position_index(cls) -> int:
        """Get position index."""
        ...

    @classmethod
    def opcode_name(cls) -> str:
        """Get opcode name."""
        ...


class BrahmaBase(WorkerProtocol):
    """
    Base class for Brahma implementations.

    MANTRA PROTOCOL DERIVATION:
        _position_index = 1  # That's ALL!
        Everything else derived from MAHAMANTRA_POSITIONS.
    """

    _position_index = 1


class NullBrahma(BrahmaBase):
    """Null implementation for testing."""
    pass


__all__ = [
    # Backward-compatible constants
    "POSITION",
    "QUARTER",
    "OPCODE",
    "PARAMPARA_VECTOR",
    # Protocol classes
    "BrahmaProtocol",
    "BrahmaBase",
    "NullBrahma",
]
