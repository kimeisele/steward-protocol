"""
🕉️ OPUS-200: Sanskrit Reactor - Breaking the Binary

The Reactor module implements a new computational paradigm where:
- Meaning is encoded as 4D VarnaTensors (not ASCII strings)
- Decisions are computed via resonance (not boolean logic)
- Crypto properties participate in computation (not just verification)

Components:
- atom.py: VarnaTensor - The atomic unit of Sanskrit computation
- agni.py: AgniEngine - The resonance reactor

This is a STANDALONE plugin that does not modify existing systems.
It provides an alternative computation path that can be integrated
where quantum-style resonance is preferred over binary logic.

Usage:
    from vibe_core.reactor import encode_intent, ignite_intent

    # Simple: Encode and ignite
    status = ignite_intent("deploy_production", salt="session123")

    # Advanced: Full control
    from vibe_core.reactor import VarnaTensor, AgniEngine

    engine = AgniEngine()
    tensor = encode_intent("create_backup", "session_salt")
    result = engine.check_resonance(tensor, context_hash="ledger_hash")
"""

from .agni import (
    AgniEngine,
    ResonanceResult,
    get_agni,
    ignite_intent,
)
from .atom import (
    Guna,
    Varga,
    VarnaTensor,
    calculate_entropy,
    encode_context,
    encode_intent,
    infer_guna,
    infer_varga,
)

__all__ = [
    # Atom (VarnaTensor)
    "Varga",
    "Guna",
    "VarnaTensor",
    "encode_intent",
    "encode_context",
    "infer_varga",
    "infer_guna",
    "calculate_entropy",
    # Agni (Reactor Engine)
    "AgniEngine",
    "ResonanceResult",
    "get_agni",
    "ignite_intent",
]
