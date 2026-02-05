"""
PARASHURAMA - Position 8
========================

Quarter: KARMA
OpCode: EXEC_OP
Type: HEAD

MAHAMANTRA AS LENS:
    Structure defined here. Implementation re-exported from protocols/mahajanas.
    Samskara will migrate implementations over time.

PARAMPARA: 333 (% 37 == 0 -> CONNECTED)
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "parashurama"
__position__ = 8
__genesis__ = "0xeb1e287f"  # GenesisByte

# === RE-EXPORT FROM PROTOCOLS/MAHAJANAS (rich implementation) ===
# Backward-compat constants
from typing import Final

from vibe_core.protocols.mahajanas.parashurama import *

# Re-export __all__ from protocols
from vibe_core.protocols.mahajanas.parashurama import __all__

POSITION: Final[int] = 8
QUARTER: Final[str] = "karma"
OPCODE: Final[str] = "EXEC_OP"
PARAMPARA_VECTOR: Final[int] = 333

# ParashuramaBase alias for backward compat
ParashuramaBase = ParashuramaProtocolBase


def execute(input_text: str, context: dict = None) -> dict:
    """PARASHURAMA EXECUTION - Exec Op (Position 8, HEAD)"""
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
