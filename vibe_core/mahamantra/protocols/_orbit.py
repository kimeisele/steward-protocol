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

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x3f31a22c"  # GenesisByte: parampara % 37 == 0

from typing import Protocol, runtime_checkable

from vibe_core.mahamantra.protocols._seed import WORDS


@runtime_checkable
class OrbitProtocol(Protocol):
    """
    Interface for the Orbital Calculator (Jyotisha).
    Determines if an entity should act at a given cosmic moment.
    """

    def should_dance(self, current_tick: int, entity_id: str, kaksha_modulus: int = WORDS) -> bool:
        """
        Determine if it's time to dance.

        Args:
            current_tick: The absolute cosmic tick count.
            entity_id: Unique string ID of the entity (for Phase Shift).
            kaksha_modulus: The frequency orbit (16=Mantra, 48=Lila, etc).
                            Default is WORDS (Every Mantra).

        Returns:
            True if (current_tick + hash(entity_id)) % kaksha_modulus == 0
        """
        ...

    def get_phase_offset(self, entity_id: str, modulus: int = WORDS) -> int:
        """Get the calculated phase offset for an entity."""
        ...
