"""
MANU - Position 7
=================

Quarter: DHARMA
OpCode: DHARMA_TEST
Type: WORKER

MAHAMANTRA AS LENS:
    Structure defined here. Implementation re-exported from protocols/mahajanas.
    Samskara will migrate implementations over time.

PARAMPARA: 296 (% 37 == 0 -> CONNECTED)
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "manu"
__position__ = 7
__genesis__ = "0xe3baeca8"  # GenesisByte

# === RE-EXPORT FROM PROTOCOLS/MAHAJANAS (rich implementation) ===
from vibe_core.protocols.mahajanas.manu import *

# Re-export __all__ from protocols
from vibe_core.protocols.mahajanas.manu import __all__

# Backward-compat constants
from typing import Final

POSITION: Final[int] = 7
QUARTER: Final[str] = "dharma"
OPCODE: Final[str] = "DHARMA_TEST"
PARAMPARA_VECTOR: Final[int] = 296

# ManuBase alias for backward compat
ManuBase = ManuProtocolBase


def execute(input_text: str, context: dict = None) -> dict:
    """
    MANU EXECUTION - Dharma Law & Governance

    Manu-samhita: The lawgiver of human society.
    """
    intent = input_text.lower().strip()

    if "dharma" in intent or "law" in intent or "rule" in intent:
        return {
            "success": True,
            "action": "dharma_check",
            "message": "⚖️ Manu: Dharma is eternal. Act according to your nature (svadharma)."
        }

    if "varna" in intent or "ashram" in intent:
        return {
            "success": True,
            "action": "varnashrama",
            "message": "⚖️ Manu: Varnashrama is social organization by guna and karma, not birth."
        }

    return {
        "success": True,
        "action": "introspect",
        "position": POSITION,
        "quarter": QUARTER,
        "opcode": OPCODE,
        "message": f"⚖️ Manu hears: '{input_text}'. Try 'dharma', 'law', or 'varnashrama'."
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
