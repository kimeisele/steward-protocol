"""
VYASA - Position 0
==================

Quarter: GENESIS
OpCode: SYS_WAKE
Type: HEAD

MAHAMANTRA AS LENS:
    Structure defined here. Implementation re-exported from protocols/mahajanas.
    Samskara will migrate implementations over time.

PARAMPARA: 37 (% 37 == 0 -> CONNECTED)
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x00000000"  # GenesisByte

# === RE-EXPORT FROM PROTOCOLS/MAHAJANAS (rich implementation) ===
from vibe_core.protocols.mahajanas.vyasa import *

# Re-export __all__ from protocols
from vibe_core.protocols.mahajanas.vyasa import __all__

# Backward-compat constants
from typing import Final

POSITION: Final[int] = 0
QUARTER: Final[str] = "genesis"
OPCODE: Final[str] = "SYS_WAKE"
PARAMPARA_VECTOR: Final[int] = 37

# VyasaBase alias for backward compat
VyasaBase = VyasaProtocolBase
