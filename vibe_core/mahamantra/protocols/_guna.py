"""
GUNA PROTOCOL - The Modes of Material Nature
============================================

"traigunya-visaya veda nistraigunyo bhavarjuna"
"The Vedas deal with the three modes of material nature.
O Arjuna, become transcendental to these three modes."
— Bhagavad Gita 2.45

This protocol defines the QUALITIES (Gunas) of every entity.
Derived from the 3 Holy Names, but applied to Matter (Prakriti).

SSOT: vibe_core.mahamantra.substrate.guna
This file re-exports for protocol-layer access.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x8a89fdb5"  # GenesisByte: parampara % 37 == 0

from typing import Protocol, runtime_checkable

# SSOT: Re-export from substrate
from vibe_core.mahamantra.substrate.guna import Guna, VISHUDDHA_SATTVA


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
    "VISHUDDHA_SATTVA",
]
