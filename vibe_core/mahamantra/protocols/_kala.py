"""
KALA PROTOCOL - The Science of Time
===================================

"kālo 'smi loka-kṣaya-kṛt pravṛddho"
"Time I am, the great destroyer of the worlds."
— Bhagavad Gita 11.32

This protocol defines the translation of atomic ticks (SPANDANA)
into cyclical cosmic time (KALA).

HIERARCHY:
    1. TICK (Spandana)  : The Atom (1 Word)
    2. MANTRA (Japa)    : 16 Ticks (1 Cycle)
    3. LILA (Quarter)   : 48 Ticks (3 Mantras - Past/Present/Future)
    4. MALA (Round)     : 1728 Ticks (108 Mantras)

"""

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

@dataclass
class KalaTime:
    """The current point in Cosmic Time."""
    total_ticks: int
    tick_in_mantra: int  # 0-15
    mantra_in_mala: int  # 0-107
    lila_position: int     # 0-47 (Cycle of 3 Mantras)
    mala_count: int      # Total completed rounds

    @property
    def mantra_completion(self) -> float:
        """Percentage of current mantra completed (0.0 - 1.0)."""
        return (self.tick_in_mantra + 1) / 16.0

    @property
    def mala_completion(self) -> float:
        """Percentage of current mala completed (0.0 - 1.0)."""
        return (self.mantra_in_mala * 16 + self.tick_in_mantra + 1) / 1728.0

    def __str__(self) -> str:
        return (
            f"Kala(Mala={self.mala_count}, "
            f"Mantra={self.mantra_in_mala}, "
            f"Tick={self.tick_in_mantra})"
        )

@runtime_checkable
class KalaProtocol(Protocol):
    """
    Interface for the Time Keeper.
    """
    
    def advance(self) -> KalaTime:
        """Advance time by one tick."""
        ...

    def tick(self) -> KalaTime:
        """Alias for advance() - The Heartbeat."""
        ...

    def get_time(self) -> KalaTime:
        """Get current cosmic time."""
        ...
