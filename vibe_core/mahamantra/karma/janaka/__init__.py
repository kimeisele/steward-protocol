"""
JANAKA - Position 10
=====================

Quarter: KARMA
OpCode: STATE_SYNC
Type: WORKER
Role: Worker

MANTRA PROTOCOL DERIVATION:
    Position index is the ONLY configuration.
    All properties derived from MAHAMANTRA_POSITIONS.

PARAMPARA: 407 (% 37 == 0 -> CONNECTED)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0xe12cdf3a"  # GenesisByte: parampara % 37 == 0

from typing import Final, Protocol, runtime_checkable

from vibe_core.mahamantra.substrate.protocol import WorkerProtocol

# === BACKWARD-COMPATIBLE CONSTANTS (derived from MantraProtocol) ===
POSITION: Final[int] = 10
QUARTER: Final[str] = "karma"
OPCODE: Final[str] = "STATE_SYNC"
PARAMPARA_VECTOR: Final[int] = 407


@runtime_checkable
class JanakaProtocol(Protocol):
    """
    Protocol for Janaka (STATE_SYNC).

    Position 10 in the Mahamantra.
    """

    @classmethod
    def position_index(cls) -> int:
        """Get position index."""
        ...

    @classmethod
    def opcode_name(cls) -> str:
        """Get opcode name."""
        ...


class JanakaBase(WorkerProtocol):
    """
    Base class for Janaka implementations.

    MANTRA PROTOCOL DERIVATION:
        _position_index = 10  # That's ALL!
        Everything else derived from MAHAMANTRA_POSITIONS.
    """

    _position_index = 10


class NullJanaka(JanakaBase):
    """Null implementation for testing."""
    pass


__all__ = [
    # Backward-compatible constants
    "POSITION",
    "QUARTER",
    "OPCODE",
    "PARAMPARA_VECTOR",
    # Protocol classes
    "JanakaProtocol",
    "JanakaBase",
    "NullJanaka",
]
