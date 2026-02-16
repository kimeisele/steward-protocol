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


def execute(input_text: str, context: dict = None) -> dict:
    """YAMARAJA EXECUTION - Audit Seal (Position 15)"""
    return {
        "success": True,
        "action": OPCODE.lower(),
        "mahajana": __mahajana__,
        "position": __position__,
        "quarter": QUARTER,
        "opcode": OPCODE,
        "input": input_text,
        "message": f"Yamaraja [{OPCODE}]: '{input_text}'",
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
