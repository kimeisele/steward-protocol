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

from enum import IntEnum, unique
from typing import Final, Protocol, runtime_checkable


@unique
class Guna(IntEnum):
    """
    The 3 Modes of Material Nature.
    """

    SATTVA = 1  # Goodness, Knowledge, Maintenance, Purity
    RAJAS = 2  # Passion, Creation, Action, Motion
    TAMAS = 3  # Ignorance, Destruction, Inertia, Storage

    # Transcendental (Not material)
    VISHUDDHA_SATTVA = 4  # Pure Goodness (The Holy Name)


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
