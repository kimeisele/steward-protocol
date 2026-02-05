"""
NRISIMHA - Position 12
======================

Quarter: MOKSHA
OpCode: YIELD_CPU
Type: HEAD

MAHAMANTRA AS LENS:
    Structure defined here. Implementation re-exported from protocols/mahajanas.
    Samskara will migrate implementations over time.

PARAMPARA: 481 (% 37 == 0 -> CONNECTED)
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "nrisimha"
__position__ = 12
__genesis__ = "0x7ac86006"  # GenesisByte

# === RE-EXPORT FROM PROTOCOLS/MAHAJANAS (rich implementation) ===
# Backward-compat constants
from typing import Final

from vibe_core.protocols.mahajanas.nrisimha import *

# Re-export __all__ from protocols
from vibe_core.protocols.mahajanas.nrisimha import __all__

POSITION: Final[int] = 12
QUARTER: Final[str] = "moksha"
OPCODE: Final[str] = "YIELD_CPU"
PARAMPARA_VECTOR: Final[int] = 481

# NrisimhaBase alias for backward compat
NrisimhaBase = NrisimhaProtocolBase


def execute(input_text: str, context: dict = None) -> dict:
    """NRISIMHA EXECUTION - Yield CPU (Position 12, HEAD)"""
    return {
        "success": True,
        "mahajana": __mahajana__,
        "position": __position__,
        "quarter": QUARTER,
        "opcode": OPCODE,
        "input": input_text,
    }


_fractal_getattr_fn = None


def __getattr__(name: str) -> object:
    """Explicit exports + fractal discovery fallback."""
    if name == "NrisimhaService":
        from vibe_core.protocols.mahajanas.nrisimha.service import NrisimhaService

        return NrisimhaService

    global _fractal_getattr_fn
    if _fractal_getattr_fn is None:
        from vibe_core.mahamantra.substrate.wiring import fractal_getattr

        _fractal_getattr_fn = fractal_getattr(__file__)
    return _fractal_getattr_fn(name)
