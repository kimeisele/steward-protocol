"""
OPUS-200/201: Sanskrit Quantum Reactor

The Resonance-Based Computation Engine.

This module provides:
- VarnaTensor: 4D encoding of intent (atom.py)
- AgniEngine: Resonance computation with constitutional anchors (agni.py)

Integration Points:
- Binds to manas_awareness.json (Biorhythm)
- Guard function for TaskKernel
- Semantic keyword matching (not phonetic)

Usage:
    from vibe_core.reactor import encode_intent, ignite_intent, get_agni

    # Simple usage
    status = ignite_intent("create_file", salt="session123", context_hash="ledger_v1")

    # Advanced usage
    tensor = encode_intent("kernel_boot", "session123")
    engine = get_agni()
    result = engine.check_resonance(tensor, "ledger_v1")

    # TaskKernel integration
    from vibe_core.reactor import create_resonance_guard
    guard = create_resonance_guard()
    if guard(tensor, context_hash):
        # Proceed with execution
        pass
"""

from .agni import (
    CONSTITUTIONAL_ANCHORS,
    AgniEngine,
    ConstitutionalAnchor,
    ResonanceResult,
    create_resonance_guard,
    get_agni,
    ignite_intent,
)
from .atom import (
    KEYWORDS_ANTARSTHA,
    KEYWORDS_CAVARGA,
    KEYWORDS_DANGEROUS,
    KEYWORDS_KAVARGA,
    KEYWORDS_PAVARGA,
    KEYWORDS_TAVARGA,
    Guna,
    Varga,
    VarnaTensor,
    check_dangerous,
    encode_intent,
    infer_guna,
    infer_varga,
)

__all__ = [
    # Atom (VarnaTensor)
    "Guna",
    "Varga",
    "VarnaTensor",
    "encode_intent",
    "infer_guna",
    "infer_varga",
    "check_dangerous",
    "KEYWORDS_KAVARGA",
    "KEYWORDS_CAVARGA",
    "KEYWORDS_TAVARGA",
    "KEYWORDS_PAVARGA",
    "KEYWORDS_ANTARSTHA",
    "KEYWORDS_DANGEROUS",
    # Agni (Engine)
    "AgniEngine",
    "ResonanceResult",
    "ConstitutionalAnchor",
    "CONSTITUTIONAL_ANCHORS",
    "get_agni",
    "ignite_intent",
    "create_resonance_guard",
]

__version__ = "2.0.0"  # REFINED version
