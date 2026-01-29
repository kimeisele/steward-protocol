"""
KAPILA - Position 6
===================

Quarter: DHARMA
OpCode: TYPE_CHECK
Type: WORKER

MAHAMANTRA AS LENS:
    Structure defined here. Implementation re-exported from protocols/mahajanas.
    Samskara will migrate implementations over time.

PARAMPARA: 259 (% 37 == 0 -> CONNECTED)
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"
__position__ = 6
__genesis__ = "0x25d36ba1"  # GenesisByte


def __getattr__(name: str) -> object:
    """
    Lazy load KapilaService and NullKapila.
    NO MANUAL WIRING - auto-discovery needs these exports.
    """
    if name == "KapilaService":
        from vibe_core.services.kapila_service import KapilaService

        return KapilaService

    if name == "get_kapila_service":
        from vibe_core.services.kapila_service import get_kapila_service

        return get_kapila_service

    if name == "NullKapila":
        from vibe_core.protocols.mahajanas.kapila import NullKapila

        return NullKapila

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
