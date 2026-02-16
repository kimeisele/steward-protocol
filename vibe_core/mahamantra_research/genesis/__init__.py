"""
GENESIS - Positions 1-4: Hare Krishna Hare Krishna
==================================================

The BEGINNING. Seed axioms, foundational constants, shabda (sound) foundations.

From _seed.py:
    QUARTER_SUM_GENESIS = 1 + 2 + 3 + 4 = 10 = TEN

Contents:
    - Axiom re-exports from protocols/_seed.py
    - Shabda (sound) translation foundations
    - Phoneme mappings
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0xa45d8a78"  # GenesisByte: parampara % 37 == 0

from vibe_core.mahamantra.protocols._seed import (
    HALVES,
    HARE_COUNT,
    KRISHNA_COUNT,
    KSETRAJNA,
    PANCHA,
    # Primary derivations
    QUARTERS,
    RAMA_COUNT,
    TRINITY,
    # The 7 Axioms
    WORDS,
)

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


__all__ = [
    "WORDS",
    "TRINITY",
    "HARE_COUNT",
    "KRISHNA_COUNT",
    "RAMA_COUNT",
    "PANCHA",
    "HALVES",
    "QUARTERS",
    "KSETRAJNA",
]
