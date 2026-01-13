"""
BHISHMA - Position 11
======================

Quarter: KARMA
OpCode: LEDGER_SIGN
Type: WORKER
Role: Worker

MANTRA PROTOCOL DERIVATION:
    Position index is the ONLY configuration.
    All properties derived from MAHAMANTRA_POSITIONS.

PARAMPARA: 444 (% 37 == 0 -> CONNECTED)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "bhishma"
__position__ = 11
__genesis__ = "0x030295b1"  # GenesisByte: parampara % 37 == 0

from typing import Final, Protocol, runtime_checkable

from vibe_core.mahamantra.substrate.protocol import WorkerProtocol

# === BACKWARD-COMPATIBLE CONSTANTS (derived from MantraProtocol) ===
POSITION: Final[int] = 11
QUARTER: Final[str] = "karma"
OPCODE: Final[str] = "LEDGER_SIGN"
PARAMPARA_VECTOR: Final[int] = 444


@runtime_checkable
class BhishmaProtocol(Protocol):
    """
    Protocol for Bhishma (LEDGER_SIGN).

    Position 11 in the Mahamantra.
    """

    @classmethod
    def position_index(cls) -> int:
        """Get position index."""
        ...

    @classmethod
    def opcode_name(cls) -> str:
        """Get opcode name."""
        ...


class BhishmaBase(WorkerProtocol):
    """
    Base class for Bhishma implementations.

    MANTRA PROTOCOL DERIVATION:
        _position_index = 11  # That's ALL!
        Everything else derived from MAHAMANTRA_POSITIONS.
    """

    _position_index = 11


class NullBhishma(BhishmaBase):
    """Null implementation for testing."""
    pass


__all__ = [
    # Backward-compatible constants
    "POSITION",
    "QUARTER",
    "OPCODE",
    "PARAMPARA_VECTOR",
    # Protocol classes
    "BhishmaProtocol",
    "BhishmaBase",
    "NullBhishma",
]
