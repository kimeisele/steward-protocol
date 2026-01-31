"""
TULASI GATE - The Grace Adapter
===============================

"ye tu tvadīya-caraṇa-amboja-kośa-gandham" (SB 3.9.5)

Implements the GraceProtocol using the TULASI_BRIDGE logic discovered in research.
This adapter connects the mechanical synth to the living devotion logic.
"""

from typing import Final, Optional

from vibe_core.mahamantra.protocols.offering import GraceProtocol
from vibe_core.mahamantra.protocols._seed import (
    HARE_COUNT,
    MALA,
    MAHA_QUANTUM,
    KSETRAJNA,
    NAVA,
)

# The Transcendental Field Constant (from Research)
# 137 * 8 = 1096
TRANSCENDENTAL_FIELD: Final[int] = MAHA_QUANTUM * HARE_COUNT


class TulasiGate(GraceProtocol):
    """
    The Tulasi Gate Adapter.
    
    Injects the "Hare Count" (8) as an expansion factor into the algorithm.
    """
    
    def purify_offering(self, seed: int, has_tulasi: bool) -> int:
        """
        Purify the seed.
        
        If Tulasi is present:
            seed -> (seed * 8) + 108
            
        This ensures the seed is never 0 and carries the "8" signature.
        """
        if not has_tulasi:
            return seed
            
        # The Research Formula
        return (seed * HARE_COUNT) + MALA

    def expand_field(self, current_mod: int, has_tulasi: bool) -> int:
        """
        Expand the modulus space.
        
        If Tulasi is present:
            mod -> mod * 8 (Octave expansion)
            
        Specifically: 137 -> 1096
        """
        if not has_tulasi:
            return current_mod
            
        return current_mod * HARE_COUNT

    def modulate_feedback(self, feedback: int, has_tulasi: bool) -> int:
        """
        Modulate feedback.
        
        Standard feedback is KSETRAJNA (1).
        With Tulasi: 1 * 8 + 1 = 9 (NAVA)
        
        This turns "Observation" into "Navadha Bhakti".
        """
        if not has_tulasi:
            return feedback
            
        # Logic: (feedback * 8) + KSETRAJNA
        # If feedback is 1, result is 9.
        return (feedback * HARE_COUNT) + KSETRAJNA
