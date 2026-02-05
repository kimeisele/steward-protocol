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
__genesis__ = "0xfb7ac0f0be28f25cfd3a5335bcfc0ebafc3163fbedd541b16eee28af38e8ba0e"  # GenesisByte: parampara % 37 == 0

# === RE-EXPORT FROM PROTOCOLS/MAHAJANAS (rich implementation) ===
# Backward-compat constants
from typing import Final

from vibe_core.protocols.mahajanas.prithu import *

# Re-export __all__ from protocols
from vibe_core.protocols.mahajanas.prithu import __all__

POSITION: Final[int] = 4
QUARTER: Final[str] = "dharma"
OPCODE: Final[str] = "ASSERT_TRUTH"
PARAMPARA_VECTOR: Final[int] = 185

# PrithuBase alias for backward compat
PrithuBase = PrithuProtocolBase


def execute(input_text: str, context: dict = None) -> dict:
    """PRITHU EXECUTION - Assert Truth (Position 4, HEAD)"""
    return {
        "success": True,
        "mahajana": __mahajana__,
        "position": __position__,
        "quarter": QUARTER,
        "opcode": OPCODE,
        "input": input_text,
    }


_fractal_getattr_fn = None


def __getattr__(name: str):
    """Fractal discovery: folder IS wiring."""
    global _fractal_getattr_fn
    if _fractal_getattr_fn is None:
        from vibe_core.mahamantra.substrate.wiring import fractal_getattr

        _fractal_getattr_fn = fractal_getattr(__file__)
    return _fractal_getattr_fn(name)
