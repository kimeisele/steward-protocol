"""
PARASHURAMA - Position 8
========================

Quarter: KARMA
OpCode: EXEC_OP
Type: HEAD

MAHAMANTRA AS LENS:
    Structure defined here. Implementation re-exported from protocols/mahajanas.
    Samskara will migrate implementations over time.

PARAMPARA: 333 (% 37 == 0 -> CONNECTED)
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "parashurama"
__position__ = 8
__genesis__ = "0xeb1e287f"  # GenesisByte

# === RE-EXPORT FROM PROTOCOLS/MAHAJANAS (rich implementation) ===
from vibe_core.protocols.mahajanas.parashurama import *

# Re-export __all__ from protocols
from vibe_core.protocols.mahajanas.parashurama import __all__

# Backward-compat constants
from typing import Final

POSITION: Final[int] = 8
QUARTER: Final[str] = "karma"
OPCODE: Final[str] = "EXEC_OP"
PARAMPARA_VECTOR: Final[int] = 333

# ParashuramaBase alias for backward compat
ParashuramaBase = ParashuramaProtocolBase
