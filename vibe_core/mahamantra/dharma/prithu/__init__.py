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

from typing import Final

POSITION: Final[int] = 4
QUARTER: Final[str] = "dharma"
OPCODE: Final[str] = "ASSERT_TRUTH"
PARAMPARA_VECTOR: Final[int] = 185


def execute(input_text: str, context: dict = None) -> dict:
    """PRITHU EXECUTION - Assert Truth (Position 4, HEAD)"""
    return {
        "success": True,
        "action": "assert_truth",
        "mahajana": __mahajana__,
        "position": __position__,
        "quarter": QUARTER,
        "opcode": OPCODE,
        "input": input_text,
        "message": f"Prithu [{OPCODE}]: '{input_text}'",
    }


_fractal_getattr_fn = None
_MISSING = object()


def __getattr__(name: str):
    """Protocol re-exports (lazy) + fractal discovery."""
    try:
        from vibe_core.protocols.mahajanas import prithu as _proto

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
