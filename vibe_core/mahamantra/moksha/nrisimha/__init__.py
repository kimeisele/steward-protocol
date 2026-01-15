"""
NRISIMHA - Position 12
======================

Quarter: MOKSHA
OpCode: YIELD_CPU
Type: HEAD

MAHAMANTRA AS LENS:
    Structure defined here. Implementation re-exported from protocols/mahajanas.
    Samskara will migrate implementations over time.

PARAMPARA: 481 (% 37 == 0 -> CONNECTED)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "nrisimha"
__position__ = 12
__genesis__ = "0x7ac86006"  # GenesisByte

# === RE-EXPORT FROM PROTOCOLS/MAHAJANAS (rich implementation) ===
from vibe_core.protocols.mahajanas.nrisimha import *

# Re-export __all__ from protocols
from vibe_core.protocols.mahajanas.nrisimha import __all__

# Backward-compat constants
from typing import Final
POSITION: Final[int] = 12
QUARTER: Final[str] = "moksha"
OPCODE: Final[str] = "YIELD_CPU"
PARAMPARA_VECTOR: Final[int] = 481

# NrisimhaBase alias for backward compat
NrisimhaBase = NrisimhaProtocolBase


def __getattr__(name: str) -> object:
    """
    Lazy load NrisimhaWatchdog (aliased as NrisimhaService) from services.
    Unification of Kernel and Mahamantra.
    """
    if name == "NrisimhaService":
        from vibe_core.services.nrisimha import NrisimhaWatchdog
        return NrisimhaWatchdog  # Return the new class as the old name
    
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
