"""
YAMARAJA - Position 15
=======================

Quarter: MOKSHA
OpCode: AUDIT_SEAL
Type: WORKER

MAHAMANTRA AS LENS:
    Structure defined here. Implementation re-exported from protocols/mahajanas.
    Samskara will migrate implementations over time.

PARAMPARA: 592 (% 37 == 0 -> CONNECTED)
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x8fd1e5e1"  # GenesisByte: parampara % 37 == 0

from typing import Final

POSITION: Final[int] = 15
QUARTER: Final[str] = "moksha"
OPCODE: Final[str] = "AUDIT_SEAL"
PARAMPARA_VECTOR: Final[int] = 592


_service_instance = None


def get_service():
    """Get the singleton SamskaraService. Lazy-loaded, no new layer."""
    global _service_instance
    if _service_instance is None:
        from vibe_core.mahamantra.moksha.yamaraja.samskara_service import SamskaraService
        _service_instance = SamskaraService()
    return _service_instance


def execute(input_text: str, context: dict = None) -> dict:
    """YAMARAJA EXECUTION - Delegates to real SamskaraService."""
    svc = get_service()
    if hasattr(svc, 'execute'):
        result = svc.execute(input_text)
    else:
        result = {"success": True, "output_repr": "executed"}
    return {
        "success": result.get("success", True) if isinstance(result, dict) else True,
        "action": OPCODE.lower(),
        "mahajana": __mahajana__,
        "position": __position__,
        "quarter": QUARTER,
        "opcode": OPCODE,
        "input": input_text,
        "execution": result,
        "message": f"Yamaraja [{OPCODE}]: executed '{input_text[:50]}'",
    }


_fractal_getattr_fn = None
_MISSING = object()


def __getattr__(name: str):
    """Explicit exports + protocol re-exports + fractal discovery."""
    if name == "SamskaraService":
        from vibe_core.mahamantra.moksha.yamaraja.samskara_service import SamskaraService

        return SamskaraService

    # Backward-compat alias: guardian called it YamarajaBase, protocol calls it YamarajaProtocolBase
    if name == "YamarajaBase":
        from vibe_core.protocols.mahajanas.yamaraja import YamarajaProtocolBase

        return YamarajaProtocolBase

    # Lazy protocol re-export (all types, NullYamaraja, etc.)
    try:
        from vibe_core.protocols.mahajanas import yamaraja as _proto

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
