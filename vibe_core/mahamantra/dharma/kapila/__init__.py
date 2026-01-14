"""
KAPILA - Position 6
===================

Quarter: DHARMA
OpCode: TYPE_CHECK
Type: WORKER

MAHAMANTRA AS LENS:
    Structure defined here. Implementation re-exported from protocols/mahajanas.
    Samskara will migrate implementations over time.

PARAMPARA: 259 (% 37 == 0 -> CONNECTED)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"
__position__ = 6
__genesis__ = "0x25d36ba1"  # GenesisByte

# === RE-EXPORT FROM PROTOCOLS/MAHAJANAS (rich implementation) ===
from vibe_core.protocols.mahajanas.kapila import *

# Re-export __all__ from protocols
from vibe_core.protocols.mahajanas.kapila import __all__

# Backward-compat constants
from typing import Final
POSITION: Final[int] = 6
QUARTER: Final[str] = "dharma"
OPCODE: Final[str] = "TYPE_CHECK"
PARAMPARA_VECTOR: Final[int] = 259

# KapilaBase alias for backward compat
KapilaBase = KapilaProtocolBase
