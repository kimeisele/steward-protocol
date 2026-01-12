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
