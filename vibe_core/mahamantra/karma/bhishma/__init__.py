"""
BHISHMA - Position 11
=====================

Quarter: KARMA
OpCode: LEDGER_SIGN
Type: WORKER

MAHAMANTRA AS LENS:
    Structure defined here. Implementation re-exported from protocols/mahajanas.
    Samskara will migrate implementations over time.

PARAMPARA: 444 (% 37 == 0 -> CONNECTED)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "bhishma"
__position__ = 11
__genesis__ = "0x030295b1"  # GenesisByte

# === RE-EXPORT FROM PROTOCOLS/MAHAJANAS (rich implementation) ===
from vibe_core.protocols.mahajanas.bhishma import *

# Re-export __all__ from protocols
from vibe_core.protocols.mahajanas.bhishma import __all__

# Backward-compat constants
from typing import Final
POSITION: Final[int] = 11
QUARTER: Final[str] = "karma"
OPCODE: Final[str] = "LEDGER_SIGN"
PARAMPARA_VECTOR: Final[int] = 444

# BhishmaBase alias for backward compat
BhishmaBase = BhishmaProtocolBase
