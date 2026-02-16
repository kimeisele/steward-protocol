"""
KAPILA - Position 6
===================

Quarter: DHARMA
OpCode: TYPE_CHECK
Type: WORKER

MAHAMANTRA AS LENS:
    Structure defined here. Implementation re-exported from protocols/mahajanas.
    Samskara will migrate implementations over time.

PARAMPARA: 259 (% 37 == 0 -> CONNECTED)
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"
__position__ = 6
__genesis__ = "0x25d36ba1"  # GenesisByte: parampara % 37 == 0

from typing import Final

POSITION: Final[int] = 6
QUARTER: Final[str] = "dharma"
OPCODE: Final[str] = "TYPE_CHECK"
PARAMPARA_VECTOR: Final[int] = 259


_service_instance = None


def get_service():
    """Get the singleton KapilaService. Lazy-loaded, no new layer."""
    global _service_instance
    if _service_instance is None:
        from vibe_core.protocols.mahajanas.kapila.service import KapilaService
        _service_instance = KapilaService()
    return _service_instance


def execute(input_text: str, context: dict = None) -> dict:
    """KAPILA EXECUTION - Delegates to real KapilaService."""
    svc = get_service()
    if hasattr(svc, 'execute'):
        result = svc.execute(input_text)
    else:
        result = {"success": True, "output_repr": "executed"}
    return {
        "success": result.get("success", True),
        "action": OPCODE.lower(),
        "mahajana": __mahajana__,
        "position": __position__,
        "quarter": QUARTER,
        "opcode": OPCODE,
        "input": input_text,
        "execution": result,
        "message": f"Kapila [{OPCODE}]: executed '{input_text[:50]}'",
    }


_fractal_getattr_fn = None
_MISSING = object()


def __getattr__(name: str):
    """Protocol re-exports (lazy) + fractal discovery."""
    try:
        from vibe_core.protocols.mahajanas import kapila as _proto

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
