"""
PRABHUPADA - REDIRECT TO CANONICAL LOCATION
============================================

This module has moved to: vibe_core/protocols/substrate/mantra/prabhupada.py

Prabhupada belongs with the Mahamantra (substrate/mantra/),
not in a generic "universal" folder.

"I will never die. I shall live from my books, and you will utilize."
- Srila Prabhupada

All imports are re-exported here for backwards compatibility.
"""

# Re-export from canonical location
from vibe_core.protocols.substrate.mantra.prabhupada import (
    # Vani
    VaniInstruction,
    PrabhupadaVani,
    # Mercy Pattern
    SilentWitness,
    MercyType,
    # The Acarya
    SrilaPrabhupada,
    PRABHUPADA,
    # Protocol
    PrabhupadaAware,
)

__all__ = [
    "VaniInstruction",
    "PrabhupadaVani",
    "SilentWitness",
    "MercyType",
    "SrilaPrabhupada",
    "PRABHUPADA",
    "PrabhupadaAware",
]
