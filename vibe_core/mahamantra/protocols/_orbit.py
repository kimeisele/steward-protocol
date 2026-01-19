"""
ORBIT PROTOCOL - The Science of Lagna (Phase) and Kaksha (Orbit)
================================================================

"grahāṇāṁ jyotir-anīkāni"
"The army of luminaries moves in their respective orbits."

This protocol defines the rules for ORBITAL MECHANICS within the Mahamantra.
Instead of a "Flat Earth" where everyone reacts to Tick 0, entities
move in specific Orbits (Kaksha) and Phases (Lagna).

CONCEPTS:
    1. LAGNA (Phase Offset): The personal "Starting Point".
       Derived from Entity Identity (Hash).
       Ensures Load Balancing (Round Robin).

    2. KAKSHA (Frequency): The "Speed" of the orbit.
       - MANTRA (16 Ticks)
       - LILA (48 Ticks)
       - MALA (1728 Ticks)

"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class OrbitProtocol(Protocol):
    """
    Interface for the Orbital Calculator (Jyotisha).
    Determines if an entity should act at a given cosmic moment.
    """

    def should_dance(self, current_tick: int, entity_id: str, kaksha_modulus: int = 16) -> bool:
        """
        Determine if it's time to dance.

        Args:
            current_tick: The absolute cosmic tick count.
            entity_id: Unique string ID of the entity (for Phase Shift).
            kaksha_modulus: The frequency orbit (16=Mantra, 48=Lila, etc).
                            Default is 16 (Every Mantra).

        Returns:
            True if (current_tick + hash(entity_id)) % kaksha_modulus == 0
        """
        ...

    def get_phase_offset(self, entity_id: str, modulus: int = 16) -> int:
        """Get the calculated phase offset for an entity."""
        ...
