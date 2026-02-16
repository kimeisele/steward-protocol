"""
BHISHMA - Position 11
=====================

Quarter: KARMA
OpCode: LEDGER_SIGN
Type: WORKER

MAHAMANTRA AS LENS:
    Structure defined here. Implementation re-exported from protocols/mahajanas.
    Samskara will migrate implementations over time.

PARAMPARA: 444 (% 37 == 0 -> CONNECTED)
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "bhishma"
__position__ = 11
__genesis__ = "0x030295b1"  # GenesisByte

from typing import Final

POSITION: Final[int] = 11
QUARTER: Final[str] = "karma"
OPCODE: Final[str] = "LEDGER_SIGN"
PARAMPARA_VECTOR: Final[int] = 444


_service_instance = None


def get_service():
    """Get the singleton BhishmaService. Lazy-loaded, no new layer."""
    global _service_instance
    if _service_instance is None:
        from vibe_core.protocols.mahajanas.bhishma.service import BhishmaService
        from vibe_core.protocols.mahajanas.bhishma.ledger import LedgerProtocol
        try:
            from vibe_core.di import ServiceRegistry
            ledger = ServiceRegistry.get(LedgerProtocol)
        except Exception:
            ledger = None
        if ledger is None:
            from vibe_core.protocols.mahajanas.bhishma.ledger import NullLedger
            ledger = NullLedger()
        _service_instance = BhishmaService(ledger=ledger)
    return _service_instance


def execute(input_text: str, context: dict = None) -> dict:
    """BHISHMA EXECUTION - Delegates to real BhishmaService."""
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
        "message": f"Bhishma [{OPCODE}]: executed '{input_text[:50]}'",
    }


_fractal_getattr_fn = None
_MISSING = object()


def __getattr__(name: str):
    """Protocol re-exports (lazy) + fractal discovery."""
    try:
        from vibe_core.protocols.mahajanas import bhishma as _proto

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
