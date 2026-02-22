"""
REACTOR - Der Mahamantra Reaktor
================================

"yajñārthāt karmaṇo 'nyatra loko 'yaṁ karma-bandhanaḥ
tad-arthaṁ karma kaunteya mukta-saṅgaḥ samācara"

"Work done as a sacrifice for Vishnu has to be performed,
otherwise work causes bondage in this material world."
— Bhagavad Gita 3.9

THE BHOGA-PRASADAM YAJNA:
=========================

    Position 0-7:  BHOGA (Offering) - Krishna half
    Position 8:    THE SWITCH (Parashurama transforms)
    Position 8-15: PRASADAM (Grace) - Rama half

    The 8th position is where OFFERING becomes GRACE.
    No manual wiring - FOLDER = WIRING = REGISTRATION.

LEVEL: +2 (SERVICES) - Dies ist die Service-Schicht
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xf71806da"  # GenesisByte: parampara % 37 == 0

from typing import Final
from vibe_core.mahamantra.substrate import ProtocolLevel

REACTOR_LEVEL: Final[ProtocolLevel] = ProtocolLevel.SERVICES

# =============================================================================
# SHADOW REACTOR - The Bhoga-Prasadam Engine
# =============================================================================

from vibe_core.mahamantra.reactor.shadow import (
    # Phase
    YajnaPhase,
    SWITCH_POSITION,
    RETURN_POSITION,
    get_phase,
    # Types (WATERTIGHT)
    TickStateInput,
    ShadowState,
    # Protocol
    ShadowReactorProtocol,
    ShadowReactorFactoryProtocol,
    # Factory (ServiceRegistry)
    ShadowReactorFactory,
    get_shadow_reactor_factory,
    # Reactor
    ShadowReactor,
    get_shadow_reactor,
    shadow,
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
    # Level
    "REACTOR_LEVEL",
    # Phase
    "YajnaPhase",
    "SWITCH_POSITION",
    "RETURN_POSITION",
    "get_phase",
    # Types (WATERTIGHT)
    "TickStateInput",
    "ShadowState",
    # Protocol
    "ShadowReactorProtocol",
    "ShadowReactorFactoryProtocol",
    # Factory (ServiceRegistry - RECOMMENDED)
    "ShadowReactorFactory",
    "get_shadow_reactor_factory",
    # Reactor
    "ShadowReactor",
    "get_shadow_reactor",
    "shadow",
]
