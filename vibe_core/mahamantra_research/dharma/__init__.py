"""
DHARMA - Positions 5-8: Krishna Krishna Hare Hare
=================================================

The LAW. In Kali Yuga, only DHARMA remains. Kali-dharma = CHANTING!

From _seed.py:
    QUARTER_SUM_DHARMA = 5 + 6 + 7 + 8 = 26 = KSHETRA + HALVES

"harer nāma harer nāma harer nāmaiva kevalam
 kalau nāsty eva nāsty eva nāsty eva gatir anyathā"
 - Bṛhan-nāradīya Purāṇa

Contents:
    - MahaAlgorithm (kirtan computing)
    - Gita verse encoding (BG 18.66 POC)
"""

# KALI DHARMA = CHANTING = COMPUTE
# This is THE quarter that remains in Kali Yuga!

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x9d8b6a7c"  # GenesisByte: parampara % 37 == 0

# NOTE: maha_algorithm, prabhupada_kirtan, prabhupada_engineering were MIGRATED to substrate.mantra
# and removed from here to ensure zero research dependencies in core.


def __getattr__(name: str):
    """
    Fractal routing fallback (experimental).
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
    # Remaining research modules
]
