"""
BRAHMA - Position 1
===================

Quarter: GENESIS
OpCode: LOAD_ROOT
Type: WORKER

MAHAMANTRA AS LENS:
    Structure defined here. Implementation re-exported from protocols/mahajanas.
    Samskara will migrate implementations over time.

PARAMPARA: 74 (% 37 == 0 -> CONNECTED)
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x96910869"  # GenesisByte

from typing import Final

# Backward-compat constants
POSITION: Final[int] = 1
QUARTER: Final[str] = "genesis"
OPCODE: Final[str] = "LOAD_ROOT"
PARAMPARA_VECTOR: Final[int] = 74


def execute(input_text: str, context: dict = None) -> dict:
    """BRAHMA EXECUTION - Load Root (Position 1)"""
    return {
        "success": True,
        "action": OPCODE.lower(),
        "mahajana": __mahajana__,
        "position": __position__,
        "quarter": QUARTER,
        "opcode": OPCODE,
        "input": input_text,
        "message": f"Brahma [{OPCODE}]: '{input_text}'",
    }


_fractal_getattr_fn = None


def __getattr__(name: str) -> object:
    """Explicit exports + fractal discovery fallback."""
    if name == "BrahmaService":
        from vibe_core.protocols.mahajanas.brahma import BrahmaService

        return BrahmaService

    if name == "NullBrahma":
        from vibe_core.protocols.mahajanas.brahma import NullBrahma

        return NullBrahma

    global _fractal_getattr_fn
    if _fractal_getattr_fn is None:
        from vibe_core.mahamantra.substrate.wiring import fractal_getattr

        _fractal_getattr_fn = fractal_getattr(__file__)
    return _fractal_getattr_fn(name)
