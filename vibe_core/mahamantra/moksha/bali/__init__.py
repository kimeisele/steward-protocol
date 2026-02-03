"""
BALI - Position 13
==================

Quarter: MOKSHA
OpCode: IO_FLUSH
Type: WORKER

MAHAMANTRA AS LENS:
    Structure defined here. Implementation re-exported from protocols/mahajanas.
    Samskara will migrate implementations over time.

PARAMPARA: 518 (% 37 == 0 -> CONNECTED)
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "bali"
__position__ = 13
__genesis__ = "0x699b2aea"  # GenesisByte

# === RE-EXPORT FROM PROTOCOLS/MAHAJANAS (rich implementation) ===
from vibe_core.protocols.mahajanas.bali import *

# Re-export __all__ from protocols
from vibe_core.protocols.mahajanas.bali import __all__

# Backward-compat constants
from typing import Final

POSITION: Final[int] = 13
QUARTER: Final[str] = "moksha"
OPCODE: Final[str] = "IO_FLUSH"
PARAMPARA_VECTOR: Final[int] = 518

# BaliBase alias for backward compat
BaliBase = BaliProtocolBase


def execute(input_text: str, context: dict = None) -> dict:
    """BALI EXECUTION - IO Flush (Position 13)"""
    return {
        "success": True,
        "mahajana": __mahajana__,
        "position": __position__,
        "quarter": QUARTER,
        "opcode": OPCODE,
        "input": input_text,
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
