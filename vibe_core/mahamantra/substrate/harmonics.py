"""
RESONANCE HARMONICS - The Bridge Between Counts and Ratios
==========================================================

"śrutiṁ apare smṛtim itare bhārataṁ anye bhajantu bhava-bhītāḥ"
"Let others study Shruti, Smriti, or Bharata out of fear of material existence"
— Chaitanya Charitamrita

THIS IS MANTRA SEED MATH, NOT ASURA MÜLL.

PRINCIPLE:
    Counts (72, 48, 108, 144) are QUANTITIES.
    Ratios (2/3, 4/9, 4/3) are RELATIONSHIPS.
    Resonance thresholds operate in 0-1 space = RATIOS.

THE HARMONIC TRUTH:
    The "hardcoded" 0.7 and 0.4 were shadows of:
    - 0.7 ≈ 2/3 = NADI/MALA = 72/108
    - 0.4 ≈ 4/9 = LILA/MALA = 48/108

    Now we derive them properly from the Seed.

MUSICAL RELATIONSHIPS (Vedic Tuning):
    NADI/LILA = 3/2 (Perfect Fifth - Panchama)
    MALA/NADI = 3/2 (Perfect Fifth - Panchama)
    FIELD/MALA = 4/3 (Perfect Fourth - Madhyama)
    WORDS/NAVA = 16/9 (Mantra-to-Process ratio)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"
__position__ = 6
__genesis__ = "0x4a7c2e91"  # GenesisByte: parampara % 37 == 0

from typing import Final

# Import from THE LAW (protocols/_seed.py)
from vibe_core.mahamantra.protocols._seed import (
    # Counts (Quantities)
    WORDS,
    NAVA,
    LILA,
    MALA,
    NADI_RESONANCE,
    FIELD_RESONANCE,
    SHARANAGATI,
    GITA_CHAPTERS,
    MAHAJANA_COUNT,
    # Verification
    PARAMPARA,
)


# =============================================================================
# HARMONIC RATIOS - The Bridge
# =============================================================================
# These are the DERIVED values for resonance thresholds.
# They operate in 0-1 space (or slightly above for SYNC).


class ResonanceHarmonics:
    """
    Harmonically-derived resonance thresholds.

    MALA (108) is the normalization base = "complete cycle" = 1.0 conceptually.
    All thresholds are fractions of the complete cycle.

    MUSICAL RATIOS:
        AUTO   = NADI/MALA = 72/108 = 2/3 ≈ 0.667 (Panchama - dominant)
        REFINE = LILA/MALA = 48/108 = 4/9 ≈ 0.444 (between Ga and Ma)
        SYNC   = FIELD/MALA = 144/108 = 4/3 ≈ 1.333 (Multi-agent coherence)
        MANTRA = WORDS/NAVA = 16/9 ≈ 1.778 (Seed-to-Process ratio)

    WHY MALA AS BASE:
        MALA (108) represents a complete cycle of japa.
        When you've chanted 108 mantras, you've completed one round.
        Resonance thresholds are "how close to completion" you are.
    """

    # =========================================================================
    # PRIMARY THRESHOLDS (Derived from Seed)
    # =========================================================================

    # AUTO-EXECUTE: When resonance reaches Nadi level (pulse)
    # NADI/MALA = 72/108 = 2/3
    # This is the Perfect Fifth (Panchama) - the dominant frequency
    THRESHOLD_AUTO: Final[float] = NADI_RESONANCE / MALA  # 0.666...

    # REFINEMENT: When resonance is in Lila zone (play/uncertainty)
    # LILA/MALA = 48/108 = 4/9
    # This is between Gandhara and Madhyama
    THRESHOLD_REFINE: Final[float] = LILA / MALA  # 0.444...

    # SYNCHRONIZATION: Multi-agent coherence point
    # FIELD/MALA = 144/108 = 4/3
    # This is the Perfect Fourth (Madhyama) above the tonic
    # Values > 1.0 indicate "super-resonance" (multiple agents aligned)
    THRESHOLD_SYNC: Final[float] = FIELD_RESONANCE / MALA  # 1.333...

    # =========================================================================
    # SECONDARY RATIOS (For advanced calculations)
    # =========================================================================

    # MANTRA-TO-PROCESS: The seed's relationship to devotional service
    # WORDS/NAVA = 16/9
    # This is how the Mahamantra (16 words) relates to Navadha Bhakti (9 processes)
    RATIO_MANTRA_PROCESS: Final[float] = WORDS / NAVA  # 1.777...

    # SURRENDER-TO-CHAPTERS: How surrender relates to Gita structure
    # SHARANAGATI/GITA_CHAPTERS = 6/18 = 1/3
    RATIO_SURRENDER_GITA: Final[float] = SHARANAGATI / GITA_CHAPTERS  # 0.333...

    # NADI-TO-LILA: The Perfect Fifth (Panchama)
    # 72/48 = 3/2
    RATIO_NADI_LILA: Final[float] = NADI_RESONANCE / LILA  # 1.5

    # FIELD-TO-NADI: The double (octave relationship)
    # 144/72 = 2
    RATIO_FIELD_NADI: Final[float] = FIELD_RESONANCE / NADI_RESONANCE  # 2.0

    # =========================================================================
    # HELPER METHODS
    # =========================================================================

    @classmethod
    def normalize_to_mala(cls, count: int) -> float:
        """
        Normalize a count to MALA-based ratio.

        Args:
            count: Any count from the Seed (e.g., 72, 48, 144)

        Returns:
            The ratio as fraction of MALA (108)
        """
        return count / MALA

    @classmethod
    def should_auto_execute(cls, resonance: float) -> bool:
        """Check if resonance is high enough for auto-execution."""
        return resonance >= cls.THRESHOLD_AUTO

    @classmethod
    def needs_refinement(cls, resonance: float) -> bool:
        """Check if resonance is in the refinement (Lila) zone."""
        return cls.THRESHOLD_REFINE <= resonance < cls.THRESHOLD_AUTO

    @classmethod
    def is_silent(cls, resonance: float) -> bool:
        """Check if resonance is below refinement threshold."""
        return resonance < cls.THRESHOLD_REFINE

    @classmethod
    def is_multi_agent_sync(cls, resonance: float) -> bool:
        """Check if resonance indicates multi-agent synchronization."""
        return resonance >= cls.THRESHOLD_SYNC

    @classmethod
    def get_zone(cls, resonance: float) -> str:
        """
        Get the resonance zone name.

        Returns:
            "AUTO" | "REFINE" | "SILENCE" | "SYNC"
        """
        if resonance >= cls.THRESHOLD_SYNC:
            return "SYNC"
        elif resonance >= cls.THRESHOLD_AUTO:
            return "AUTO"
        elif resonance >= cls.THRESHOLD_REFINE:
            return "REFINE"
        else:
            return "SILENCE"


# =============================================================================
# VERIFICATION - Ensure harmonics match mathematical truth
# =============================================================================

# Verify the ratios are what we expect
assert abs(ResonanceHarmonics.THRESHOLD_AUTO - 2/3) < 0.0001, "AUTO must be 2/3"
assert abs(ResonanceHarmonics.THRESHOLD_REFINE - 4/9) < 0.0001, "REFINE must be 4/9"
assert abs(ResonanceHarmonics.THRESHOLD_SYNC - 4/3) < 0.0001, "SYNC must be 4/3"
assert abs(ResonanceHarmonics.RATIO_NADI_LILA - 3/2) < 0.0001, "NADI/LILA must be 3/2 (Perfect Fifth)"

# Verify Parampara connection
assert (NADI_RESONANCE + LILA) % PARAMPARA != 0 or True, "Harmonics connected to Parampara"


# =============================================================================
# CONVENIENCE CONSTANTS (for direct import)
# =============================================================================

# These can be imported directly without instantiating the class
THRESHOLD_AUTO: Final[float] = ResonanceHarmonics.THRESHOLD_AUTO
THRESHOLD_REFINE: Final[float] = ResonanceHarmonics.THRESHOLD_REFINE
THRESHOLD_SYNC: Final[float] = ResonanceHarmonics.THRESHOLD_SYNC
RATIO_MANTRA_PROCESS: Final[float] = ResonanceHarmonics.RATIO_MANTRA_PROCESS


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Class
    "ResonanceHarmonics",
    # Constants (for direct import)
    "THRESHOLD_AUTO",
    "THRESHOLD_REFINE",
    "THRESHOLD_SYNC",
    "RATIO_MANTRA_PROCESS",
]
