"""
PRAHLADA - Position 9
=====================

Quarter: KARMA
OpCode: EXTEND_CAP
Type: WORKER

MAHAMANTRA AS LENS:
    Structure defined here. Implementation re-exported from protocols/mahajanas.
    Samskara will migrate implementations over time.

PARAMPARA: 370 (% 37 == 0 -> CONNECTED)
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xf6cf0c05"  # GenesisByte

# === RE-EXPORT FROM PROTOCOLS/MAHAJANAS (rich implementation) ===
from vibe_core.protocols.mahajanas.prahlada import *

# Re-export __all__ from protocols
from vibe_core.protocols.mahajanas.prahlada import __all__

# Backward-compat constants
from typing import Final

POSITION: Final[int] = 9
QUARTER: Final[str] = "karma"
OPCODE: Final[str] = "EXTEND_CAP"
PARAMPARA_VECTOR: Final[int] = 370

# PrahladaBase alias for backward compat
PrahladaBase = PrahladaProtocolBase
