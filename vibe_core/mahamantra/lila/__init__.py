"""
LILA - The Divine Play (Level +1: Application Logic)
=====================================================

"lila-vilasa-vigrahah"
"Whose form is the embodiment of transcendental pastimes."
— Brahma-samhita 5.30

Lila is the "play" - the dynamic execution of the Mahamantra.
While Substrate provides the physics, Lila provides the drama.

MODULES:
========

- adoption.py: Mounting services onto OrbitalReactors
- migration.py: Migrating legacy code to Mahamantra patterns
- jiva_shadow.py: Computing personality reflections from seeds

LEVEL: +1 (Application Logic)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"  # The divine musician who facilitates Lila
__position__ = 2
__genesis__ = "0xe6ae6e5a"  # GenesisByte: parampara % 37 == 0

from vibe_core.mahamantra.lila.adhikara import (
    # Core computation
    compute_required_bitmap,
    find_best_shadow,
    # Reporting
    get_position_adhikara_report,
    get_required_count,
    get_required_qualities,
    # Shadow matching
    shadow_can_execute,
    shadow_match_score,
    # Varnashrama spawn (THE CORRECT WAY)
    spawn_shadow_for_position,
)
from vibe_core.mahamantra.lila.adoption import (
    analyze_source,
)
from vibe_core.mahamantra.lila.jiva_shadow import (
    # Constants
    QUALITY_DESCRIPTIONS,
    GunaState,
    # Core types
    JivaQuality,
    JivaShadow,
    # Factory functions
    spawn_shadow,
    spawn_shadow_from_string,
    # Verification
    verify_shadow_lineage,
)
from vibe_core.mahamantra.lila.registry import (
    # Constants
    MAX_SHADOWS,
    RETIRE_AFTER_SERVICES,
    RegistryEntry,
    # Registry
    ShadowRegistry,
    # Types
    ShadowStatus,
    # Singleton
    get_registry,
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
    # Adoption
    "analyze_source",
    # JivaShadow
    "JivaQuality",
    "GunaState",
    "JivaShadow",
    "spawn_shadow",
    "spawn_shadow_from_string",
    "verify_shadow_lineage",
    "QUALITY_DESCRIPTIONS",
    # Adhikara (Mahamantra-derived qualification)
    "compute_required_bitmap",
    "get_required_qualities",
    "get_required_count",
    "shadow_can_execute",
    "shadow_match_score",
    "find_best_shadow",
    "spawn_shadow_for_position",
    "get_position_adhikara_report",
    # Registry (The Ashrama)
    "MAX_SHADOWS",
    "RETIRE_AFTER_SERVICES",
    "ShadowStatus",
    "RegistryEntry",
    "ShadowRegistry",
    "get_registry",
]
