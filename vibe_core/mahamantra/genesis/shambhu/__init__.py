"""
SHAMBHU - Position 3
====================

Quarter: GENESIS
OpCode: INIT_THREAD
Type: WORKER

MAHAMANTRA AS LENS:
    Structure defined here. Implementation re-exported from protocols/mahajanas.
    Samskara will migrate implementations over time.

PARAMPARA: 148 (% 37 == 0 -> CONNECTED)
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "shambhu"
__position__ = 3
__genesis__ = "0x8ed2ec88"  # GenesisByte

# === RE-EXPORT FROM PROTOCOLS/MAHAJANAS (rich implementation) ===
from vibe_core.protocols.mahajanas.shambhu import *

# Re-export __all__ from protocols
from vibe_core.protocols.mahajanas.shambhu import __all__

# Backward-compat constants
from typing import Final

POSITION: Final[int] = 3
QUARTER: Final[str] = "genesis"
OPCODE: Final[str] = "INIT_THREAD"
PARAMPARA_VECTOR: Final[int] = 148

# ShambhuBase alias for backward compat
ShambhuBase = ShambhuProtocolBase
