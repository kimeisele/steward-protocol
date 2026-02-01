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

# === RE-EXPORT FROM PROTOCOLS/MAHAJANAS (rich implementation) ===
from vibe_core.protocols.mahajanas.narada import *

# Re-export __all__ from protocols
from vibe_core.protocols.mahajanas.narada import __all__

# Backward-compat constants
from typing import Final

POSITION: Final[int] = 2
QUARTER: Final[str] = "genesis"
OPCODE: Final[str] = "ALLOC_MEM"
PARAMPARA_VECTOR: Final[int] = 111

# NaradaBase alias for backward compat
NaradaBase = NaradaProtocolBase


def execute(input_text: str, context: dict = None) -> dict:
    """
    NARADA EXECUTION - Observation & Communication

    Stateless execution via NullNarada.
    """
    narada = NullNarada()
    intent = input_text.lower().strip()

    if "broadcast" in intent or "pulse" in intent:
        result = narada.broadcast_cli(input_text)
        return {"success": True, "action": "broadcast", "result": result}

    if "observe" in intent:
        narada.observe("user", "request", input_text)
        return {"success": True, "action": "observe", "recorded": True}

    if "state" in intent or "status" in intent:
        state = narada.get_state()
        return {"success": True, "action": "get_state", "state": state}

    # Default: return state
    return {
        "success": True,
        "action": "introspect",
        "position": POSITION,
        "quarter": QUARTER,
        "opcode": OPCODE,
        "message": f"🎵 Narada hears: '{input_text}'. Try 'broadcast', 'observe', or 'state'."
    }

def __getattr__(name: str):
    """
    Fractal routing: folder IS wiring.
    "EIN IMPORT. KRISHNA ROUTET ALLES."
    """
    from pathlib import Path
    import importlib

    pkg_root = Path(__file__).parent

    # Check for subpackage (folder with __init__.py)
    subpkg_path = pkg_root / name
    if subpkg_path.is_dir() and (subpkg_path / "__init__.py").exists():
        return importlib.import_module(f"{__name__}.{name}")

    # Check for module (.py file)
    module_path = pkg_root / f"{name}.py"
    if module_path.exists():
        return importlib.import_module(f"{__name__}.{name}")

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
