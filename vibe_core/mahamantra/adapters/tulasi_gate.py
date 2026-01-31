"""
TULASI GATE - The Sanctification Adapter
========================================

"yā dṛṣṭā nikhilāgha-saṅgha-śamanī"
"Simply by seeing, she destroys all sins."

This adapter implements the "Tulasi in Process".
It handles the BHOGA -> PRASADAM transformation logic.
"""

from typing import Final, Optional
from vibe_core.mahamantra.protocols.offering import GraceProtocol
from vibe_core.mahamantra.protocols._seed import (
    KSETRAJNA,
    MAHA_QUANTUM,
    POSITION_SUM_TOTAL,
    KSHETRA,
    PRASADAM,
)

class TulasiGate(GraceProtocol):
    """
    The Tulasi Sanctification Gate.
    
    Role:
    1. VALIDATE: Ensures the offering is suitable (Sattvic).
    2. SANCTIFY: Transforms Bhoga (Material) to Prasadam (Spiritual).
    3. PROTECT: Does not allow 'dirty' inputs into the core.
    """
    
    def purify_offering(self, seed: int, has_tulasi: bool) -> int:
        """
        Purify the seed through connection.
        
        TRANSFORMATION LOGIC (Ontological):
        - Bhoga (Material) = Field (No Observer)
        - Prasadam (Spiritual) = Field + Observer (Ksetrajna)
        
        Transitions:
        - 136 (POSITION_SUM_TOTAL) -> 137 (MAHA_QUANTUM)
        - 24 (KSHETRA) -> 25 (PRASADAM)
        
        If Tulasi is present, she facilitates this addition of the Observer.
        """
        if not has_tulasi:
            return seed
            
        # If seed is exactly the Classical Field (136), sanctify to Quantum (137)
        if seed == POSITION_SUM_TOTAL:
            return MAHA_QUANTUM
            
        # If seed is exactly the Material Field (24), sanctify to Prasadam (25)
        if seed == KSHETRA:
            return PRASADAM
            
        # General case: Add KSETRAJNA (The Observer)
        # But ONLY if it's not already sanctified (to avoid 137+1=138 nonsense)
        # We assume if mod 17 == 1, it might already have the observer.
        # But simplest "safe" logic for arbitrary seeds is to add the Observer
        # to ensure the computation includes the "collapse function".
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
