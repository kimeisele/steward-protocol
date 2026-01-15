"""
KALA PROTOCOL - The Time (Cycles & Ticks)
=========================================

"kalo 'smi loka-ksaya-krt pravrddho"
"Time I am, the great destroyer of the worlds..."
— Bhagavad Gita 11.32

POSITION: Hare Rama (Nityananda - The Sustainer/Time)
FUNCTION: Clock, Cycles, Heartbeat.

This protocol defines the RHYTHM of the system.
Derived from seed.py constants (MALA, ROUNDS).

LOCATION: vibe_core.mahamantra.protocols._kala (THE LAW)
"""

from typing import Protocol, runtime_checkable
from vibe_core.mahamantra.protocols._pancha import PanchaTattvaProtocol, TattvaDict
from vibe_core.mahamantra.protocols._seed import MALA, ROUNDS

@runtime_checkable
class KalaProtocol(PanchaTattvaProtocol, Protocol):
    """
    The Time Protocol.
    Defines the heartbeat and cyclical nature of the system.
    """

    @property
    def __tattva__(self) -> TattvaDict:
        return {
            "chaitanya": "Time Protocol",
            "nityananda": "Seed Protocol",
            "advaita": "Clock Logic",
            "gadadhara": "Tick Flow",
            "srivasa": "Self-Regulated",
        }

    @property
    def current_tick(self) -> int:
        """Current tick in the cycle (0 to ROUNDS-1)."""
        ...

    @property
    def current_mala(self) -> int:
        """Current mala count (0 to MALA-1)."""
        ...

    def tick(self) -> int:
        """Advance time by one tick. Returns new tick."""
        ...

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "KalaProtocol",
    "MALA",
    "ROUNDS",
]
