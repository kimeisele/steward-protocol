"""
OFFERING PROTOCOL - The Interface of Grace
==========================================

"patram pushpam phalam toyam" (BG 9.26)

Defines the interface for submitting offerings and receiving grace.
This is separate from the mechanical execution of the algorithm.
"""

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass
class Offering:
    """
    A unified offering object.

    Contains the seed (Intent) and the qualifiers (Tulasi).
    """

    seed: int
    has_tulasi: bool = False
    devotion_level: int = 0  # 0-100


@runtime_checkable
class GraceProtocol(Protocol):
    """
    Protocol for entities that can dispense Grace.

    Grace modifies the 'mod_space' and 'feedback' of the algorithm.
    """

    def purify_offering(self, seed: int, has_tulasi: bool) -> int:
        """Transform input seed based on offering quality."""
        ...

    def expand_field(self, current_mod: int, has_tulasi: bool) -> int:
        """Expand the modulus space (e.g. 137 -> 1096)."""
        ...

    def modulate_feedback(self, feedback: int, has_tulasi: bool) -> int:
        """Modulate the feedback loop accumulator."""
        ...
