"""
NARADA - Position 2
=====================

Quarter: GENESIS
OpCode: ALLOC_MEM
Type: WORKER
Role: Worker

MANTRA PROTOCOL DERIVATION:
    Position index is the ONLY configuration.
    All properties derived from MAHAMANTRA_POSITIONS.

PARAMPARA: 111 (% 37 == 0 -> CONNECTED)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0xdd4f22d7"  # GenesisByte: parampara % 37 == 0

from typing import Final, Protocol, runtime_checkable

from vibe_core.mahamantra.substrate.protocol import WorkerProtocol

# === BACKWARD-COMPATIBLE CONSTANTS (derived from MantraProtocol) ===
POSITION: Final[int] = 2
QUARTER: Final[str] = "genesis"
OPCODE: Final[str] = "ALLOC_MEM"
PARAMPARA_VECTOR: Final[int] = 111


@runtime_checkable
class NaradaProtocol(Protocol):
    """
    Protocol for Narada (ALLOC_MEM).

    Position 2 in the Mahamantra.
    """

    @classmethod
    def position_index(cls) -> int:
        """Get position index."""
        ...

    @classmethod
    def opcode_name(cls) -> str:
        """Get opcode name."""
        ...


class NaradaBase(WorkerProtocol):
    """
    Base class for Narada implementations.

    MANTRA PROTOCOL DERIVATION:
        _position_index = 2  # That's ALL!
        Everything else derived from MAHAMANTRA_POSITIONS.
    """

    _position_index = 2


class NullNarada(NaradaBase):
    """Null implementation for testing."""
    pass


__all__ = [
    # Backward-compatible constants
    "POSITION",
    "QUARTER",
    "OPCODE",
    "PARAMPARA_VECTOR",
    # Protocol classes
    "NaradaProtocol",
    "NaradaBase",
    "NullNarada",
]
