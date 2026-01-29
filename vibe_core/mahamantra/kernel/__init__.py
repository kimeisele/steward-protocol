"""
KERNEL - Das Mahamantra als Kernel
==================================

"aham sarvasya prabhavo mattah sarvam pravartate"
"I am the source of all. Everything emanates from Me." (BG 10.8)

Mahamantra IST:
- Der Kernel selbst
- Der Router
- Der Taktgeber
- Die Hardware UND Software
- Level -2 (acintya)

ALLES GLEICHZEITIG.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x7340d7d6"  # GenesisByte: parampara % 37 == 0

from vibe_core.mahamantra.kernel.singularity import (
    Mahamantra,
    ProtocolRouter,
    ModuleRouter,
)

from vibe_core.mahamantra.kernel.fractal import (
    FractalNode,
    FractalTree,
    scale_up,
    scale_down,
    verify_fractal_integrity,
)

from vibe_core.mahamantra.kernel.intent import (
    IntentType,
    IntentPriority,
    IntentStatus,
    MantraIntent,
    IntentResult,
    IntentResolver,
    IntentQueue,
    MantraKernel,
    get_kernel,
    resolve,
    surrender,
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
    # Singularity
    "Mahamantra",
    "ProtocolRouter",
    "ModuleRouter",
    # Fractal
    "FractalNode",
    "FractalTree",
    "scale_up",
    "scale_down",
    "verify_fractal_integrity",
    # Intent
    "IntentType",
    "IntentPriority",
    "IntentStatus",
    "MantraIntent",
    "IntentResult",
    "IntentResolver",
    "IntentQueue",
    "MantraKernel",
    "get_kernel",
    "resolve",
    "surrender",
]
