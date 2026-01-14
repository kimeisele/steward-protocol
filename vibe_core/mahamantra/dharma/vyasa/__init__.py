"""
VYASA - Position 4
==================

Quarter: DHARMA
OpCode: COMPILE_AST
Type: HEAD

MAHAMANTRA AS LENS:
    Structure defined here. Implementation re-exported from protocols/mahajanas.
    Samskara will migrate implementations over time.

PARAMPARA: 185 (% 37 == 0 -> CONNECTED)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 4
__genesis__ = "0xc312083a"  # GenesisByte

# === RE-EXPORT FROM PROTOCOLS/MAHAJANAS (rich implementation) ===
from vibe_core.protocols.mahajanas.vyasa import *

# Re-export __all__ from protocols
from vibe_core.protocols.mahajanas.vyasa import __all__

# Backward-compat constants
from typing import Final
POSITION: Final[int] = 4
QUARTER: Final[str] = "dharma"
OPCODE: Final[str] = "COMPILE_AST"
PARAMPARA_VECTOR: Final[int] = 185

# VyasaBase alias for backward compat
VyasaBase = VyasaProtocolBase
