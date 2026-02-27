"""
TULASI GATE - The Sanctification Adapter
========================================

"yā dṛṣṭā nikhilāgha-saṅgha-śamanī"
"Simply by seeing, she destroys all sins."

This adapter implements the "Tulasi in Process".
It handles the BHOGA -> PRASADAM transformation logic.
"""

__all__ = ["TulasiGate"]

from vibe_core.mahamantra.protocols._seed import (
    HARE_COUNT,
    KSETRAJNA,
    KSHETRA,
    MAHA_QUANTUM,
    POSITION_SUM_TOTAL,
    PRASADAM,
)
from vibe_core.mahamantra.protocols.offering import GraceProtocol


class TulasiGate(GraceProtocol):
    """
    The Tulasi Sanctification Gate.

    Role:
    1. VALIDATE: Ensures the offering is suitable (Sattvic).
    2. SANCTIFY: Transforms Bhoga (Material) to Prasadam (Spiritual).
    3. EXPAND: Opens the Transcendental Field (1096) via Grace.
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
        return seed + KSETRAJNA

    def expand_field(self, current_mod: int, has_tulasi: bool) -> int:
        """
        Expand the Field to the Transcendental Plane.

        If Tulasi is present (Grace):
            Field = Field * HARE_COUNT (8)
            Example: 137 * 8 = 1096

        This breaks the "Stubborn Loop" of the finite field (137)
        by accessing the infinite expansion of the Name (8 Shaktis).
        """
        if not has_tulasi:
            return current_mod

        return current_mod * HARE_COUNT

    def modulate_feedback(self, feedback: int, has_tulasi: bool) -> int:
        """
        Feedback Quality Improvement.

        If Tulasi is present, the feedback loop is 'cleansed'.
        """
        if not has_tulasi:
            return feedback

        # Pure feedback - no distortion
        return feedback
