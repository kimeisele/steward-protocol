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
__genesis__ = "0xb1c9f8d3"  # GenesisByte: parampara % 37 == 0

from vibe_core.mahamantra.lila.adoption import (
    analyze_source,
)

from vibe_core.mahamantra.lila.jiva_shadow import (
    # Core types
    JivaQuality,
    GunaState,
    JivaShadow,
    # Factory functions
    spawn_shadow,
    spawn_shadow_from_string,
    # Verification
    verify_shadow_lineage,
    # Constants
    QUALITY_DESCRIPTIONS,
)

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
]
