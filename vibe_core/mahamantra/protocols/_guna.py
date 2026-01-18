"""
GUNA PROTOCOL - The Modes of Material Nature
============================================

"traigunya-visaya veda nistraigunyo bhavarjuna"
"The Vedas deal with the three modes of material nature.
O Arjuna, become transcendental to these three modes."
— Bhagavad Gita 2.45

This protocol defines the QUALITIES (Gunas) of every entity.
Derived from the 3 Holy Names, but applied to Matter (Prakriti).

LOCATION: vibe_core.mahamantra.protocols._guna (THE LAW)
"""

from typing import Protocol, runtime_checkable

# SSOT: Guna from substrate/guna.py
from vibe_core.mahamantra.substrate.guna import Guna


@runtime_checkable
class GunaAware(Protocol):
    """
    Protocol for entities that have a Guna.
    """

    @property
    def guna(self) -> Guna:
        """The dominant mode of this entity."""
        ...


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "Guna",
    "GunaAware",
]
