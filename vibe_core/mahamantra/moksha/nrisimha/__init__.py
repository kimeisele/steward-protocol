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


_service_instance = None


def get_service():
    """Get the singleton NrisimhaService. Lazy-loaded, no new layer."""
    global _service_instance
    if _service_instance is None:
        from vibe_core.protocols.mahajanas.nrisimha.service import NrisimhaService
        _service_instance = NrisimhaService()
    return _service_instance


def execute(input_text: str, context: dict = None) -> dict:
    """NRISIMHA EXECUTION - Delegates to real NrisimhaService."""
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
        "message": f"Nrisimha [{OPCODE}]: executed '{input_text[:50]}'",
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
