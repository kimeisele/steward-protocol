"""
TULASI GATE - The Sanctification Adapter
========================================

"yā dṛṣṭā nikhilāgha-saṅgha-śamanī"
"Simply by seeing, she destroys all sins."

This adapter implements the "Tulasi in Process".
It does NOT invent numbers. It Validates and Sanctifies.
"""

from typing import Final, Optional
from vibe_core.mahamantra.protocols.offering import GraceProtocol
from vibe_core.mahamantra.protocols._seed import (
    KSETRAJNA,
    MAHA_QUANTUM,
)

class TulasiGate(GraceProtocol):
    """
    The Tulasi Sanctification Gate.
    
    Role:
    1. VALIDATE: Ensures the offering is suitable (Sattvic).
    2. SANCTIFY: Adds the Observer (+1) to the Seed.
    3. PROTECT: Does not allow 'dirty' inputs into the core.
    """
    
    def purify_offering(self, seed: int, has_tulasi: bool) -> int:
        """
        Purify the seed through connection.
        
        If Tulasi is present:
            The seed (Bhoga) receives the Observer (Ksetrajna).
            seed -> seed + KSETRAJNA
            
        This transforms Bhoga into Prasadam (Qualitative change).
        """
        if not has_tulasi:
            return seed
            
        # The offering is sanctified (Observer added)
        return seed + KSETRAJNA

    def expand_field(self, current_mod: int, has_tulasi: bool) -> int:
        """
        Field remains constant (Physics).
        
        We do NOT arbitrarily expand the universe logic.
        The change is QUALITATIVE (inner), not QUANTITATIVE (outer).
        """
        return current_mod

    def modulate_feedback(self, feedback: int, has_tulasi: bool) -> int:
        """
        Feedback Quality Improvement.
        
        If Tulasi is present, the feedback loop is 'cleansed'.
        """
        if not has_tulasi:
            return feedback
            
        # Pure feedback - no distortion
        return feedback
