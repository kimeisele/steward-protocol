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

POSITION: Final[int] = 1
QUARTER: Final[str] = "genesis"
OPCODE: Final[str] = "LOAD_ROOT"
PARAMPARA_VECTOR: Final[int] = 74


_service_instance = None


def get_service():
    """Get the singleton BrahmaService. Lazy-loaded, no new layer."""
    global _service_instance
    if _service_instance is None:
        from vibe_core.protocols.mahajanas.brahma.service import BrahmaService
        from vibe_core.protocols.ledger import VibeLedger
        try:
            from vibe_core.di import ServiceRegistry
            ledger = ServiceRegistry.get(VibeLedger)
        except Exception:
            ledger = None
        if ledger is None:
            from vibe_core.protocols.mahajanas.bhishma.ledger import NullLedger
            ledger = NullLedger()
        _service_instance = BrahmaService(ledger=ledger)
    return _service_instance


def execute(input_text: str, context: dict = None) -> dict:
    """BRAHMA EXECUTION - Delegates to real BrahmaService."""
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
        "message": f"Brahma [{OPCODE}]: executed '{input_text[:50]}'",
    }


_fractal_getattr_fn = None
_MISSING = object()


def __getattr__(name: str):
    """Protocol re-exports (lazy) + fractal discovery."""
    try:
        from vibe_core.protocols.mahajanas import brahma as _proto

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
