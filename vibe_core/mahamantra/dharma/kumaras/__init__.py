"""
KUMARAS - Position 5
======================

Quarter: DHARMA
OpCode: BIND_SYMBOL
Type: WORKER
Role: Worker

MANTRA PROTOCOL DERIVATION:
    Position index is the ONLY configuration.
    All properties derived from MAHAMANTRA_POSITIONS.

PARAMPARA: 222 (% 37 == 0 -> CONNECTED)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kumaras"
__position__ = 5
__genesis__ = "0xfe9a70b8"  # GenesisByte: parampara % 37 == 0

from typing import Final, Protocol, runtime_checkable

from vibe_core.mahamantra.substrate.protocol import WorkerProtocol

# === BACKWARD-COMPATIBLE CONSTANTS (derived from MantraProtocol) ===
POSITION: Final[int] = 5
QUARTER: Final[str] = "dharma"
OPCODE: Final[str] = "BIND_SYMBOL"
PARAMPARA_VECTOR: Final[int] = 222


@runtime_checkable
class KumarasProtocol(Protocol):
    """
    Protocol for Kumaras (BIND_SYMBOL).

    Position 5 in the Mahamantra.
    """

    @classmethod
    def position_index(cls) -> int:
        """Get position index."""
        ...

    @classmethod
    def opcode_name(cls) -> str:
        """Get opcode name."""
        ...


class KumarasBase(WorkerProtocol):
    """
    Base class for Kumaras implementations.

    MANTRA PROTOCOL DERIVATION:
        _position_index = 5  # That's ALL!
        Everything else derived from MAHAMANTRA_POSITIONS.
    """

    _position_index = 5


class NullKumaras(KumarasBase):
    """Null implementation for testing."""
    pass


__all__ = [
    # Backward-compatible constants
    "POSITION",
    "QUARTER",
    "OPCODE",
    "PARAMPARA_VECTOR",
    # Protocol classes
    "KumarasProtocol",
    "KumarasBase",
    "NullKumaras",
]
