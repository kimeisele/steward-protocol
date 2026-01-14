"""
KUMARAS - Position 5
====================

Quarter: DHARMA
OpCode: BIND_SYMBOL
Type: WORKER

MAHAMANTRA AS LENS:
    Structure defined here. Implementation re-exported from protocols/mahajanas.
    Samskara will migrate implementations over time.

PARAMPARA: 222 (% 37 == 0 -> CONNECTED)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kumaras"
__position__ = 5
__genesis__ = "0xfe9a70b8"  # GenesisByte

# === RE-EXPORT FROM PROTOCOLS/MAHAJANAS (rich implementation) ===
from vibe_core.protocols.mahajanas.kumaras import *

# Re-export __all__ from protocols
from vibe_core.protocols.mahajanas.kumaras import __all__

# Backward-compat constants
from typing import Final
POSITION: Final[int] = 5
QUARTER: Final[str] = "dharma"
OPCODE: Final[str] = "BIND_SYMBOL"
PARAMPARA_VECTOR: Final[int] = 222

# KumarasBase alias for backward compat
KumarasBase = KumarasProtocolBase
