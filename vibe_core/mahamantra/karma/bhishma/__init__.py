"""
BHISHMA - Position 11
=====================

Quarter: KARMA
OpCode: LEDGER_SIGN
Type: WORKER

MAHAMANTRA AS LENS:
    Structure defined here. Implementation lazily loaded from services layer.
    Unification of Kernel and Mahamantra.

PARAMPARA: 444 (% 37 == 0 -> CONNECTED)
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "bhishma"
__position__ = 11
__genesis__ = "0x2ed4af5cfeb3b037cb7bf596f6bfd244f9820ba86efd85da163eb8495b0856b4"  # GenesisByte

from typing import Final

# Constants
POSITION: Final[int] = 11
QUARTER: Final[str] = "karma"
OPCODE: Final[str] = "LEDGER_SIGN"
PARAMPARA_VECTOR: Final[int] = 444


def __getattr__(name: str) -> object:
    """
    Lazy load BhishmaService and NullBhishma.
    NO MANUAL WIRING - auto-discovery needs these exports.
    """
    if name == "BhishmaService":
        from vibe_core.services.bhishma_service import BhishmaService

        return BhishmaService

    if name == "NullBhishma":
        from vibe_core.protocols.mahajanas.bhishma import NullBhishma

        return NullBhishma

    # Fallback to protocol definitions if needed (for types)
    try:
        import importlib

        module = importlib.import_module("vibe_core.mahamantra.karma.bhishma.protocol")
        return getattr(module, name)
    except (ImportError, AttributeError):
        pass

    # ==========================================================================
    # FRACTAL ROUTING: "EIN IMPORT. KRISHNA ROUTET ALLES."
    # ==========================================================================
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


__all__ = ["BhishmaService", "POSITION", "QUARTER", "OPCODE", "PARAMPARA_VECTOR"]
