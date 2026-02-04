"""
SANKALPA - The Will Protocol.

SHASTRA: _seed.py defines SHARANAGATI[6] = "anukulyasya sankalpah"
(The acceptance of the favorable - the first step of surrender)

This is NOT ego-will (Ahankara). This is Dharma-will.
The system acts because Shastra dictates, not because it "wants".
NISHKAMA KARMA - Action without attachment.

ADVAITA: All execution goes through ChatProtocol.
Internal voice (Sankalpa) and external voice (User) enter the same gate.
"""
from vibe_core.mahamantra.protocols._seed import (NAVA)

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = NAVA
__genesis__ = "0xebbc13e9"

from .types import (
    # Mission types
    MissionPriority,
    MissionStatus,
    SankalpaIntent,
    SankalpaMission,
    SankalpaResult,
    SankalpaStatus,
    SankalpaStrategy,
    SankalpaTrigger,
    StrategyFrequency,
    TriggerType,
    # Conscience types (extracted from DharmaSense)
    Ashrama,
    GunaState,
    ConscienceVerdict,
    ASHRAMA_PERMISSIONS,
    INTENT_PERMISSION_MAP,
    # Protocol
    SankalpaOrchestratorProtocol,
)
# IMPL MOVED TO SUBSTRATE (vibe_core.mahamantra.substrate.sankalpa)
# from .will import ... (REMOVED FOR PURITY)

def __getattr__(name: str):
    """
    Fractal routing: folder IS wiring.
    "EIN IMPORT. KRISHNA ROUTET ALLES."
    """
    # Route to substrate implementation
    if name in ("handle_sankalpa_query", "SankalpaOrchestrator", "get_sankalpa"):
        from vibe_core.mahamantra.substrate.sankalpa import will
        return getattr(will, name)

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
    # Mission types
    "MissionPriority",
    "MissionStatus",
    "SankalpaIntent",
    "SankalpaMission",
    "SankalpaResult",
    "SankalpaStatus",
    "SankalpaStrategy",
    "SankalpaTrigger",
    "StrategyFrequency",
    "TriggerType",
    # Conscience (Buddhi function)
    "Ashrama",
    "GunaState",
    "ConscienceVerdict",
    "ASHRAMA_PERMISSIONS",
    "INTENT_PERMISSION_MAP",
    "SankalpaOrchestratorProtocol",
    # Implementation Logic moved to substrate.sankalpa
    # "check_conscience", "SankalpaOrchestrator", etc. REMOVED.
]
