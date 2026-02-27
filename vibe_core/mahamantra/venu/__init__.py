"""
VENU RUNTIME - Krishna's Flute (Stateful)
=========================================

"venum kvanantam aravinda-dalayataksham"
"Krishna plays His flute, with lotus-petal eyes"
— Brahma-samhita 5.30

This is the RUNTIME layer - stateful implementations.

ARCHITECTURE:
    protocols/_venu.py  = THE LAW (interfaces)
    substrate/venu.py   = Pure math (stateless)
    venu/               = Runtime (stateful) ← YOU ARE HERE

COMPONENTS:
    MantraTick  - The heartbeat (tick counter)
    MantraVoice - Parallel execution channel
    MantraClock - The master scheduler
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 4
__genesis__ = "0xa7fe2cf6"  # GenesisByte: parampara % 37 == 0

from vibe_core.mahamantra.venu.clock import MantraClock
from vibe_core.mahamantra.venu.tick import MantraTick
from vibe_core.mahamantra.venu.voice import MantraVoice


def __getattr__(name: str):
    """
    Fractal routing: folder IS wiring.
    "EIN IMPORT. KRISHNA ROUTET ALLES."
    """
    import importlib
    from pathlib import Path

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


__all__ = [
    "MantraTick",
    "MantraVoice",
    "MantraClock",
]
