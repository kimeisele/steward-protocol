"""
BRAHMA - Position 1
===================

Quarter: GENESIS
OpCode: LOAD_ROOT
Type: WORKER

MAHAMANTRA AS LENS:
    Structure defined here. Implementation re-exported from protocols/mahajanas.
    Samskara will migrate implementations over time.

PARAMPARA: 74 (% 37 == 0 -> CONNECTED)
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x96910869"  # GenesisByte

from typing import Final

# Backward-compat constants
POSITION: Final[int] = 1
QUARTER: Final[str] = "genesis"
OPCODE: Final[str] = "LOAD_ROOT"
PARAMPARA_VECTOR: Final[int] = 74


def __getattr__(name: str) -> object:
    """
    Lazy load BrahmaService and NullBrahma.
    NO MANUAL WIRING - auto-discovery needs these exports.
    """
    if name == "BrahmaService":
        from vibe_core.services.brahma_service import BrahmaService

        return BrahmaService

    if name == "NullBrahma":
        from vibe_core.protocols.mahajanas.brahma import NullBrahma

        return NullBrahma

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["BrahmaService", "POSITION", "QUARTER", "OPCODE", "PARAMPARA_VECTOR"]
