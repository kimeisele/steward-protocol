"""
NARADA - Position 2
===================

Quarter: GENESIS
OpCode: ALLOC_MEM
Type: WORKER

MAHAMANTRA AS LENS:
    Structure defined here. Implementation re-exported from protocols/mahajanas.
    Samskara will migrate implementations over time.

PARAMPARA: 111 (% 37 == 0 -> CONNECTED)
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0xdd4f22d7"  # GenesisByte

from typing import Final

POSITION: Final[int] = 2
QUARTER: Final[str] = "genesis"
OPCODE: Final[str] = "ALLOC_MEM"
PARAMPARA_VECTOR: Final[int] = 111


def execute(input_text: str, context: dict = None) -> dict:
    """
    NARADA EXECUTION - Observation & Communication

    Stateless execution via NullNarada.
    """
    from vibe_core.protocols.mahajanas.narada import NullNarada

    narada = NullNarada()
    intent = input_text.lower().strip()

    if "broadcast" in intent or "pulse" in intent:
        result = narada.broadcast_cli(input_text)
        return {
            "success": True,
            "action": "broadcast",
            "result": result,
            "message": f"Narada [{OPCODE}]: broadcast sent",
        }

    if "observe" in intent:
        narada.observe("user", "request", input_text)
        return {
            "success": True,
            "action": "observe",
            "recorded": True,
            "message": f"Narada [{OPCODE}]: observation recorded",
        }

    if "state" in intent or "status" in intent:
        state = narada.get_state()
        return {"success": True, "action": "get_state", "state": state, "message": f"Narada [{OPCODE}]: state report"}

    # Default: return state
    return {
        "success": True,
        "action": "introspect",
        "position": POSITION,
        "quarter": QUARTER,
        "opcode": OPCODE,
        "message": f"Narada hears: '{input_text}'. Try 'broadcast', 'observe', or 'state'.",
    }


_fractal_getattr_fn = None
_MISSING = object()


def __getattr__(name: str):
    """Protocol re-exports (lazy) + fractal discovery."""
    try:
        from vibe_core.protocols.mahajanas import narada as _proto

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
