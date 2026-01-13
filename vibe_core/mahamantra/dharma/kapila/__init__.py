"""
KAPILA - Position 6
=====================

Quarter: DHARMA
OpCode: TYPE_CHECK
Type: WORKER
Role: Worker

MANTRA PROTOCOL DERIVATION:
    Position index is the ONLY configuration.
    All properties derived from MAHAMANTRA_POSITIONS.

PARAMPARA: 259 (% 37 == 0 -> CONNECTED)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"
__position__ = 6
__genesis__ = "0x25d36ba1"  # GenesisByte: parampara % 37 == 0

from typing import Final, Protocol, runtime_checkable

from vibe_core.mahamantra.substrate.protocol import WorkerProtocol

# === BACKWARD-COMPATIBLE CONSTANTS (derived from MantraProtocol) ===
POSITION: Final[int] = 6
QUARTER: Final[str] = "dharma"
OPCODE: Final[str] = "TYPE_CHECK"
PARAMPARA_VECTOR: Final[int] = 259


@runtime_checkable
class KapilaProtocol(Protocol):
    """
    Protocol for Kapila (TYPE_CHECK).

    Position 6 in the Mahamantra.
    """

    @classmethod
    def position_index(cls) -> int:
        """Get position index."""
        ...

    @classmethod
    def opcode_name(cls) -> str:
        """Get opcode name."""
        ...


class KapilaBase(WorkerProtocol):
    """
    Base class for Kapila implementations.

    MANTRA PROTOCOL DERIVATION:
        _position_index = 6  # That's ALL!
        Everything else derived from MAHAMANTRA_POSITIONS.
    """

    _position_index = 6


class NullKapila(KapilaBase):
    """Null implementation for testing."""
    pass


__all__ = [
    # Backward-compatible constants
    "POSITION",
    "QUARTER",
    "OPCODE",
    "PARAMPARA_VECTOR",
    # Protocol classes
    "KapilaProtocol",
    "KapilaBase",
    "NullKapila",
]
