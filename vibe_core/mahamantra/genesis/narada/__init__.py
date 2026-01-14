"""
NARADA - Position 2
===================

Quarter: GENESIS
OpCode: ALLOC_MEM
Type: WORKER

MAHAMANTRA AS LENS:
    Structure defined here. Implementation re-exported from protocols/mahajanas.
    Samskara will migrate implementations over time.

PARAMPARA: 111 (% 37 == 0 -> CONNECTED)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0xdd4f22d7"  # GenesisByte

# === RE-EXPORT FROM PROTOCOLS/MAHAJANAS (rich implementation) ===
from vibe_core.protocols.mahajanas.narada import *

# Re-export __all__ from protocols
from vibe_core.protocols.mahajanas.narada import __all__

# Backward-compat constants
from typing import Final
POSITION: Final[int] = 2
QUARTER: Final[str] = "genesis"
OPCODE: Final[str] = "ALLOC_MEM"
PARAMPARA_VECTOR: Final[int] = 111

# NaradaBase alias for backward compat
NaradaBase = NaradaProtocolBase
