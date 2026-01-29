"""
SHAMBHU - Position 3
====================

Quarter: GENESIS
OpCode: INIT_THREAD
Type: WORKER

MAHAMANTRA AS LENS:
    Structure defined here. Implementation re-exported from protocols/mahajanas.
    Samskara will migrate implementations over time.

PARAMPARA: 148 (% 37 == 0 -> CONNECTED)
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "shambhu"
__position__ = 3
__genesis__ = "0x8ed2ec88"  # GenesisByte

# === RE-EXPORT FROM PROTOCOLS/MAHAJANAS (rich implementation) ===
from vibe_core.protocols.mahajanas.shambhu import *

# Re-export __all__ from protocols
from vibe_core.protocols.mahajanas.shambhu import __all__

# Backward-compat constants
from typing import Final

POSITION: Final[int] = 3
QUARTER: Final[str] = "genesis"
OPCODE: Final[str] = "INIT_THREAD"
PARAMPARA_VECTOR: Final[int] = 148

# ShambhuBase alias for backward compat
ShambhuBase = ShambhuProtocolBase

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
