"""
BALI - Position 13
==================

Quarter: MOKSHA
OpCode: IO_FLUSH
Type: WORKER

MAHAMANTRA AS LENS:
    Structure defined here. Implementation re-exported from protocols/mahajanas.
    Samskara will migrate implementations over time.

PARAMPARA: 518 (% 37 == 0 -> CONNECTED)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "bali"
__position__ = 13
__genesis__ = "0x699b2aea"  # GenesisByte

# === RE-EXPORT FROM PROTOCOLS/MAHAJANAS (rich implementation) ===
from vibe_core.protocols.mahajanas.bali import *

# Re-export __all__ from protocols
from vibe_core.protocols.mahajanas.bali import __all__

# Backward-compat constants
from typing import Final
POSITION: Final[int] = 13
QUARTER: Final[str] = "moksha"
OPCODE: Final[str] = "IO_FLUSH"
PARAMPARA_VECTOR: Final[int] = 518

# BaliBase alias for backward compat
BaliBase = BaliProtocolBase
