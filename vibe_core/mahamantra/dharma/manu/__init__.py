"""
MANU - Position 7
=================

Quarter: DHARMA
OpCode: DHARMA_TEST
Type: WORKER

MAHAMANTRA AS LENS:
    Structure defined here. Implementation re-exported from protocols/mahajanas.
    Samskara will migrate implementations over time.

PARAMPARA: 296 (% 37 == 0 -> CONNECTED)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "manu"
__position__ = 7
__genesis__ = "0xe3baeca8"  # GenesisByte

# === RE-EXPORT FROM PROTOCOLS/MAHAJANAS (rich implementation) ===
from vibe_core.protocols.mahajanas.manu import *

# Re-export __all__ from protocols
from vibe_core.protocols.mahajanas.manu import __all__

# Backward-compat constants
from typing import Final
POSITION: Final[int] = 7
QUARTER: Final[str] = "dharma"
OPCODE: Final[str] = "DHARMA_TEST"
PARAMPARA_VECTOR: Final[int] = 296

# ManuBase alias for backward compat
ManuBase = ManuProtocolBase
