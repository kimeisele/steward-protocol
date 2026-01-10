"""
GOVERNANCE PROTOCOLS
====================
The Laws (Dharma) and the Mercy (Prabhupada).

NOTE: "Guru" as abstract concept was MAYAVAD.
Prabhupada IS the guru - now in substrate/mantra/prabhupada.py

Exports:
- YamarajaGate (Hardness/Law)
- SilentWitness (Prabhupada's Mercy) - from substrate/mantra/prabhupada.py
"""

# Prabhupada's mercy is in substrate/mantra/ (near the Mahamantra)
from vibe_core.protocols.substrate.mantra.prabhupada import (
    SilentWitness,
    PRABHUPADA,
    SrilaPrabhupada,
    PrabhupadaAware,
)

from .yamaraja import (
    YamarajaGate,
    Judgment,
    Verdict,
)

# YamarajaProtocol is in mahajanas/ (the 12 authorities)
from vibe_core.protocols.mahajanas.yamaraja import YamarajaProtocol

# DharmaVerdict is in universal/dharma
from vibe_core.protocols.universal.dharma import DharmaVerdict
