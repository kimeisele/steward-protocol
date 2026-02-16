"""
JANAKA - Position 10
=====================

Quarter: KARMA
OpCode: STATE_SYNC
Type: WORKER

MAHAMANTRA AS LENS:
    Structure defined here. Implementation lazily loaded from protocols/mahajanas.
    Samskara will migrate implementations over time.

PARAMPARA: 407 (% 37 == 0 -> CONNECTED)
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0xe12cdf3a"  # GenesisByte: parampara % 37 == 0

from typing import Final

POSITION: Final[int] = 10
QUARTER: Final[str] = "karma"
OPCODE: Final[str] = "STATE_SYNC"
PARAMPARA_VECTOR: Final[int] = 407


_service_instance = None


def get_service():
    """Get the singleton JanakaService. Lazy-loaded, no new layer."""
    global _service_instance
    if _service_instance is None:
        from vibe_core.protocols.mahajanas.janaka.service import JanakaService
        _service_instance = JanakaService()
    return _service_instance


def execute(input_text: str, context: dict = None) -> dict:
    """JANAKA EXECUTION - Delegates to real JanakaService."""
    svc = get_service()
    task_id = svc.submit(
        name=input_text[:50],
        task_input=input_text,
        sovereign_id="mahamantra.karma.janaka",
    )
    result = svc.execute(task_id)
    return {
        "success": result.get("success", False),
        "action": OPCODE.lower(),
        "mahajana": __mahajana__,
        "position": __position__,
        "quarter": QUARTER,
        "opcode": OPCODE,
        "input": input_text,
        "task_id": task_id,
        "execution": result,
        "message": f"Janaka [{OPCODE}]: executed '{input_text[:50]}'",
    }


_fractal_getattr_fn = None
_MISSING = object()


def __getattr__(name: str) -> object:
    """Explicit exports + protocol re-exports + fractal discovery."""
    if name == "JanakaService":
        from vibe_core.protocols.mahajanas.janaka.service import JanakaService

        return JanakaService

    # Lazy protocol re-export (replaces 50+ eager imports)
    try:
        from vibe_core.protocols.mahajanas import janaka as _proto

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
