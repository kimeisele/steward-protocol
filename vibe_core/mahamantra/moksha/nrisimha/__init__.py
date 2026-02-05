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

from typing import Final

POSITION: Final[int] = 12
QUARTER: Final[str] = "moksha"
OPCODE: Final[str] = "YIELD_CPU"
PARAMPARA_VECTOR: Final[int] = 481


def execute(input_text: str, context: dict = None) -> dict:
    """NRISIMHA EXECUTION - Yield CPU (Position 12, HEAD)"""
    return {
        "success": True,
        "action": "yield_cpu",
        "mahajana": __mahajana__,
        "position": __position__,
        "quarter": QUARTER,
        "opcode": OPCODE,
        "input": input_text,
        "message": f"Nrisimha [{OPCODE}]: '{input_text}'",
    }


_fractal_getattr_fn = None
_MISSING = object()


def __getattr__(name: str) -> object:
    """Explicit exports + protocol re-exports + fractal discovery."""
    if name == "NrisimhaService":
        from vibe_core.protocols.mahajanas.nrisimha.service import NrisimhaService

        return NrisimhaService

    try:
        from vibe_core.protocols.mahajanas import nrisimha as _proto

        _val = getattr(_proto, name, _MISSING)
        if _val is not _MISSING:
            return _val
    except ImportError:
        pass

    global _fractal_getattr_fn
    if _fractal_getattr_fn is None:
        from vibe_core.mahamantra.substrate.wiring import fractal_getattr

        _fractal_getattr_fn = fractal_getattr(__file__)
    return _fractal_getattr_fn(name)
