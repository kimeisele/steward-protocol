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

# === RE-EXPORT FROM PROTOCOLS/MAHAJANAS (rich implementation) ===
from vibe_core.protocols.mahajanas.brahma import *

# Re-export __all__ from protocols
from vibe_core.protocols.mahajanas.brahma import __all__

# Backward-compat constants
from typing import Final
POSITION: Final[int] = 1
QUARTER: Final[str] = "genesis"
OPCODE: Final[str] = "LOAD_ROOT"
PARAMPARA_VECTOR: Final[int] = 74

# BrahmaBase alias for backward compat
BrahmaBase = BrahmaProtocolBase


def __getattr__(name: str):
    """Lazy import for BrahmaService to avoid circular import."""
    if name == "BrahmaService":
        from vibe_core.protocols.mahajanas.brahma.service import BrahmaService
        return BrahmaService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
