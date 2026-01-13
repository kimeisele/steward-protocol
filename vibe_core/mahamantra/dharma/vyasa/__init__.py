"""
VYASA - Position 4
====================

Quarter: DHARMA
OpCode: COMPILE_AST
Type: HEAD
Role: Avatar

MANTRA PROTOCOL DERIVATION:
    Position index is the ONLY configuration.
    All properties derived from MAHAMANTRA_POSITIONS.

PARAMPARA: 185 (% 37 == 0 -> CONNECTED)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 4
__genesis__ = "0xc312083a"  # GenesisByte: parampara % 37 == 0

from typing import Final, Protocol, runtime_checkable

from vibe_core.mahamantra.substrate.protocol import HeadProtocol

# === BACKWARD-COMPATIBLE CONSTANTS (derived from MantraProtocol) ===
POSITION: Final[int] = 4
QUARTER: Final[str] = "dharma"
OPCODE: Final[str] = "COMPILE_AST"
PARAMPARA_VECTOR: Final[int] = 185


@runtime_checkable
class VyasaProtocol(Protocol):
    """
    Protocol for Vyasa (COMPILE_AST).

    Position 4 in the Mahamantra.
    """

    @classmethod
    def position_index(cls) -> int:
        """Get position index."""
        ...

    @classmethod
    def opcode_name(cls) -> str:
        """Get opcode name."""
        ...


class VyasaBase(HeadProtocol):
    """
    Base class for Vyasa implementations.

    MANTRA PROTOCOL DERIVATION:
        _position_index = 4  # That's ALL!
        Everything else derived from MAHAMANTRA_POSITIONS.
    """

    _position_index = 4


class NullVyasa(VyasaBase):
    """Null implementation for testing."""
    pass


__all__ = [
    # Backward-compatible constants
    "POSITION",
    "QUARTER",
    "OPCODE",
    "PARAMPARA_VECTOR",
    # Protocol classes
    "VyasaProtocol",
    "VyasaBase",
    "NullVyasa",
]
