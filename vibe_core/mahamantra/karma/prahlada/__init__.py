"""
PRAHLADA - Position 9
=======================

Quarter: KARMA
OpCode: EXTEND_CAP
Type: WORKER
Role: Worker

MANTRA PROTOCOL DERIVATION:
    Position index is the ONLY configuration.
    All properties derived from MAHAMANTRA_POSITIONS.

PARAMPARA: 370 (% 37 == 0 -> CONNECTED)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xf6cf0c05"  # GenesisByte: parampara % 37 == 0

from typing import Final, Protocol, runtime_checkable

from vibe_core.mahamantra.substrate.protocol import WorkerProtocol

# === BACKWARD-COMPATIBLE CONSTANTS (derived from MantraProtocol) ===
POSITION: Final[int] = 9
QUARTER: Final[str] = "karma"
OPCODE: Final[str] = "EXTEND_CAP"
PARAMPARA_VECTOR: Final[int] = 370


@runtime_checkable
class PrahladaProtocol(Protocol):
    """
    Protocol for Prahlada (EXTEND_CAP).

    Position 9 in the Mahamantra.
    """

    @classmethod
    def position_index(cls) -> int:
        """Get position index."""
        ...

    @classmethod
    def opcode_name(cls) -> str:
        """Get opcode name."""
        ...


class PrahladaBase(WorkerProtocol):
    """
    Base class for Prahlada implementations.

    MANTRA PROTOCOL DERIVATION:
        _position_index = 9  # That's ALL!
        Everything else derived from MAHAMANTRA_POSITIONS.
    """

    _position_index = 9


class NullPrahlada(PrahladaBase):
    """Null implementation for testing."""
    pass


__all__ = [
    # Backward-compatible constants
    "POSITION",
    "QUARTER",
    "OPCODE",
    "PARAMPARA_VECTOR",
    # Protocol classes
    "PrahladaProtocol",
    "PrahladaBase",
    "NullPrahlada",
]
