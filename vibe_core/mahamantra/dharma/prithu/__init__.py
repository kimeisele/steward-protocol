"""
PRITHU - Position 4
===================

Quarter: DHARMA
OpCode: ASSERT_TRUTH
Type: HEAD

MAHAMANTRA AS LENS:
    Structure defined here. Implementation re-exported from protocols/mahajanas.
    Samskara will migrate implementations over time.

PARAMPARA: 185 (% 37 == 0 -> CONNECTED)
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 4
__genesis__ = "0x94644443"  # GenesisByte

# === RE-EXPORT FROM PROTOCOLS/MAHAJANAS (rich implementation) ===
from vibe_core.protocols.mahajanas.prithu import *

# Re-export __all__ from protocols
from vibe_core.protocols.mahajanas.prithu import __all__

# Backward-compat constants
from typing import Final

POSITION: Final[int] = 4
QUARTER: Final[str] = "dharma"
OPCODE: Final[str] = "ASSERT_TRUTH"
PARAMPARA_VECTOR: Final[int] = 185

# PrithuBase alias for backward compat
PrithuBase = PrithuProtocolBase
