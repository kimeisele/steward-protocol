"""
YAMARAJA - Position 15
=======================

Quarter: MOKSHA
OpCode: AUDIT_SEAL
Type: WORKER
Role: Worker

MANTRA PROTOCOL DERIVATION:
    Position index is the ONLY configuration.
    All properties derived from MAHAMANTRA_POSITIONS.

PARAMPARA: 592 (% 37 == 0 -> CONNECTED)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x8fd1e5e1"  # GenesisByte: parampara % 37 == 0

from typing import Final, Protocol, runtime_checkable

from vibe_core.mahamantra.substrate.protocol import WorkerProtocol

# === BACKWARD-COMPATIBLE CONSTANTS (derived from MantraProtocol) ===
POSITION: Final[int] = 15
QUARTER: Final[str] = "moksha"
OPCODE: Final[str] = "AUDIT_SEAL"
PARAMPARA_VECTOR: Final[int] = 592


@runtime_checkable
class YamarajaProtocol(Protocol):
    """
    Protocol for Yamaraja (AUDIT_SEAL).

    Position 15 in the Mahamantra.
    """

    @classmethod
    def position_index(cls) -> int:
        """Get position index."""
        ...

    @classmethod
    def opcode_name(cls) -> str:
        """Get opcode name."""
        ...


class YamarajaBase(WorkerProtocol):
    """
    Base class for Yamaraja implementations.

    MANTRA PROTOCOL DERIVATION:
        _position_index = 15  # That's ALL!
        Everything else derived from MAHAMANTRA_POSITIONS.
    """

    _position_index = 15


class NullYamaraja(YamarajaBase):
    """Null implementation for testing."""
    pass


# =============================================================================
# SAMSKARA SERVICE - Migration Engine
# =============================================================================

from vibe_core.mahamantra.moksha.yamaraja.samskara_service import SamskaraService


__all__ = [
    # Backward-compatible constants
    "POSITION",
    "QUARTER",
    "OPCODE",
    "PARAMPARA_VECTOR",
    # Protocol classes
    "YamarajaProtocol",
    "YamarajaBase",
    "NullYamaraja",
    # Samskara (Migration)
    "SamskaraService",
]
