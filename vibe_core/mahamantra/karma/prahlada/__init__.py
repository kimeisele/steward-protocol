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

from typing import Final

POSITION: Final[int] = 9
QUARTER: Final[str] = "karma"
OPCODE: Final[str] = "EXTEND_CAP"
PARAMPARA_VECTOR: Final[int] = 370


def execute(input_text: str, context: dict = None) -> dict:
    """
    PRAHLADA EXECUTION - Devotion & Fearlessness

    The great devotee who was protected by Nrisimhadeva.
    Represents unwavering faith even in adversity.
    """
    intent = input_text.lower().strip()

    if "devot" in intent or "bhakti" in intent or "faith" in intent:
        return {
            "success": True,
            "action": "devotion",
            "message": "Prahlada: 'nama-sankirtanam' - The Name is the only shelter.",
        }

    if "fear" in intent or "protect" in intent:
        return {
            "success": True,
            "action": "protection",
            "message": "Prahlada: Fear not. Nrisimhadeva protects all devotees.",
        }

    if "chitta" in intent or "mind" in intent or "smriti" in intent:
        return {
            "success": True,
            "action": "chitta_smriti",
            "message": "Prahlada: Fix your mind on Krishna. This is smriti (remembrance).",
        }

    return {
        "success": True,
        "action": "introspect",
        "position": POSITION,
        "quarter": QUARTER,
        "opcode": OPCODE,
        "message": f"Prahlada hears: '{input_text}'. Try 'devotion', 'protect', or 'mind'.",
    }


_fractal_getattr_fn = None
_MISSING = object()


def __getattr__(name: str):
    """Protocol re-exports (lazy) + fractal discovery."""
    try:
        from vibe_core.protocols.mahajanas import prahlada as _proto

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
