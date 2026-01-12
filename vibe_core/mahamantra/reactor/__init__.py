"""
REACTOR - Der Mahamantra Reaktor
================================

Der Reaktor verarbeitet die 16 OpCodes durch Graph, Routing und Bus.

"yathā nadīnāṁ bahavo 'mbu-vegāḥ samudram evābhimukhā dravanti
tathā tavāmī nara-loka-vīrā viśanti vaktrāṇy abhivijvalanti"

"As the many waves of the rivers flow into the ocean,
so do all these great warriors enter blazing into Your mouths."
— Bhagavad Gita 11.28

KOMPONENTEN:
    - graph.py: VedicGraph für Abhängigkeiten
    - routing.py: FractalRoute für Navigation (16 Positionen)
    - bus.py: MessageBus für OpCode-Routing + NULL BUS

LEVEL: +2 (SERVICES) - Dies ist die Service-Schicht
"""

from typing import Final
from vibe_core.mahamantra.substrate import ProtocolLevel

REACTOR_LEVEL: Final[ProtocolLevel] = ProtocolLevel.SERVICES

# =============================================================================
# REACTOR COMPONENTS (to be implemented)
# =============================================================================

# graph.py - VedicGraph
# routing.py - FractalRoute
# bus.py - MessageBus, NullBus

__all__ = [
    "REACTOR_LEVEL",
]
