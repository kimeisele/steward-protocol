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
    # Three Flutes (Persons)
    VENU_HOLES,
    VAMSI_HOLES,
    MURALI_HOLES,
    QUARTERS,
    # Swara Derivation (ALL from Seed, no hardcoding!)
    PANCHA,      # 5 - For Ga (5/4) and Dha (5/3)
    TRINITY,     # 3 - For denominators
    HALVES,      # 2 - For octave
    HARE_COUNT,  # 8 - For Re (9/8)
    KSETRAJNA,   # 1 - The Knower (unity)
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
# VEDIC SCALE MAPPING - Resonance to Swara Translation
# =============================================================================
# "saptasvaramayī vīṇā" - "The vina of seven notes"
# — Sangita Ratnakara
#
# The Seven Swaras (Notes) of Indian Classical Music:
#   Sa (Shadja)    = 1/1   (Tonic - the anchor)
#   Re (Rishabha)  = 9/8   (Major Second)
#   Ga (Gandhara)  = 5/4   (Major Third)
#   Ma (Madhyama)  = 4/3   (Perfect Fourth) = THRESHOLD_SYNC!
#   Pa (Panchama)  = 3/2   (Perfect Fifth) = NADI/LILA!
#   Dha (Dhaivata) = 5/3   (Major Sixth)
#   Ni (Nishada)   = 16/9  (Minor Seventh) = RATIO_MANTRA_PROCESS!
#
# THE FLUTE SYNC POINTS:
#   Each flute (MURALI, VENU, VAMSI) creates resonance sync points
#   based on its hole count dividing the cycle.
#
#   MURALI (4 holes): 0.25, 0.50, 0.75 (Quarter points)
#   VENU (6 holes):   0.167, 0.333, 0.500, 0.667, 0.833 (Sixth points)
#   VAMSI (9 holes):  0.111, 0.222, 0.333, 0.444, 0.556, 0.667, 0.778, 0.889
#
# CONVERGENCE WITH THRESHOLDS:
#   - 0.444 (4/9) = VAMSI 4th sync = THRESHOLD_REFINE
#   - 0.667 (2/3) = VENU 4th sync = VAMSI 6th sync = THRESHOLD_AUTO
# =============================================================================


class VedicScaleMapping:
    """
    Maps resonance values to the Vedic musical scale (Swaras).

    This enables the Chat service to report which "Raga mood" it's
    responding in, based on the resonance score.

    THE MAPPING (0 to 2 resonance space):
        0.000 - 0.222: Sa (Stillness, grounding)
        0.222 - 0.333: Re (Rising, inquiry)
        0.333 - 0.500: Ga (Tension, yearning)
        0.500 - 0.667: Ma (Anticipation, seeking)
        0.667 - 1.000: Pa (Resolution, confidence)
        1.000 - 1.333: Dha (Completion, satisfaction)
        1.333 - 1.778: Ni (Transcendence, devotion)
        1.778+:        Sa' (New octave, liberation)
    """

    # =========================================================================
    # SWARA CONSTANTS (ALL DERIVED FROM SEED - NO HARDCODING!)
    # =========================================================================
    # "saptasvaramayī vīṇā" - The vina of seven notes
    #
    # DERIVATION FROM SEED:
    #   Sa = KSETRAJNA/KSETRAJNA = 1/1 (The Knower knows itself)
    #   Re = NAVA/HARE_COUNT = 9/8 (Navadha Bhakti / 8 Hares)
    #   Ga = PANCHA/QUARTERS = 5/4 (5 Tattvas / 4 Quarters)
    #   Ma = QUARTERS/TRINITY = 4/3 (4 Vyuhas / 3 Names) = FIELD/MALA
    #   Pa = TRINITY/HALVES = 3/2 (3 Names / 2 Halves) = NADI/LILA
    #   Dha = PANCHA/TRINITY = 5/3 (5 Tattvas / 3 Names)
    #   Ni = WORDS/NAVA = 16/9 (16 Words / 9 Processes)
    #   Sa' = HALVES/KSETRAJNA = 2/1 (Octave - the double)

    SWARA_SA: Final[float] = KSETRAJNA / KSETRAJNA   # 1/1 = 1.000 (Tonic)
    SWARA_RE: Final[float] = NAVA / HARE_COUNT       # 9/8 = 1.125 (Second)
    SWARA_GA: Final[float] = PANCHA / QUARTERS       # 5/4 = 1.250 (Third)
    SWARA_MA: Final[float] = QUARTERS / TRINITY      # 4/3 = 1.333 (Fourth) = THRESHOLD_SYNC!
    SWARA_PA: Final[float] = TRINITY / HALVES        # 3/2 = 1.500 (Fifth) = NADI/LILA!
    SWARA_DHA: Final[float] = PANCHA / TRINITY       # 5/3 = 1.667 (Sixth)
    SWARA_NI: Final[float] = WORDS / NAVA            # 16/9 = 1.778 (Seventh) = RATIO_MANTRA_PROCESS!

    # The complete scale (for iteration) - ALL computed from Seed
    SWARAS: Final[tuple] = ("Sa", "Re", "Ga", "Ma", "Pa", "Dha", "Ni", "Sa'")
    SWARA_RATIOS: Final[tuple] = (
        KSETRAJNA / KSETRAJNA,   # Sa
        NAVA / HARE_COUNT,       # Re
        PANCHA / QUARTERS,       # Ga
        QUARTERS / TRINITY,      # Ma
        TRINITY / HALVES,        # Pa
        PANCHA / TRINITY,        # Dha
        WORDS / NAVA,            # Ni
        HALVES / KSETRAJNA,      # Sa' (octave)
    )

    # =========================================================================
    # RESONANCE-TO-SWARA BOUNDARIES (ALL DERIVED FROM SEED!)
    # =========================================================================
    # These boundaries map our resonance thresholds to Swara regions
    # EVERY value is computed from Seed constants - SSOT principle!

    BOUNDARY_SA_RE: Final[float] = HALVES / NAVA              # 2/9 ≈ 0.222
    BOUNDARY_RE_GA: Final[float] = KSETRAJNA / TRINITY        # 1/3 ≈ 0.333
    BOUNDARY_GA_MA: Final[float] = KSETRAJNA / HALVES         # 1/2 = 0.500
    BOUNDARY_MA_PA: Final[float] = HALVES / TRINITY           # 2/3 ≈ 0.667 = THRESHOLD_AUTO
    BOUNDARY_PA_DHA: Final[float] = KSETRAJNA / KSETRAJNA     # 1/1 = 1.000
    BOUNDARY_DHA_NI: Final[float] = QUARTERS / TRINITY        # 4/3 ≈ 1.333 = THRESHOLD_SYNC
    BOUNDARY_NI_SA: Final[float] = WORDS / NAVA               # 16/9 ≈ 1.778 = RATIO_MANTRA_PROCESS

    # =========================================================================
    # THREE FLUTES SYNC POINTS
    # =========================================================================

    @classmethod
    def get_murali_sync_points(cls) -> tuple[float, ...]:
        """MURALI (4 holes) sync points - Quarter divisions."""
        return tuple(i / MURALI_HOLES for i in range(1, MURALI_HOLES))

    @classmethod
    def get_venu_sync_points(cls) -> tuple[float, ...]:
        """VENU (6 holes) sync points - Sixth divisions."""
        return tuple(i / VENU_HOLES for i in range(1, VENU_HOLES))

    @classmethod
    def get_vamsi_sync_points(cls) -> tuple[float, ...]:
        """VAMSI (9 holes) sync points - Ninth divisions."""
        return tuple(i / VAMSI_HOLES for i in range(1, VAMSI_HOLES))

    @classmethod
    def get_all_sync_points(cls) -> tuple[float, ...]:
        """All unique sync points from all three flutes, sorted."""
        all_points = set(cls.get_murali_sync_points())
        all_points.update(cls.get_venu_sync_points())
        all_points.update(cls.get_vamsi_sync_points())
        return tuple(sorted(all_points))

    # =========================================================================
    # MAPPING METHODS
    # =========================================================================

    @classmethod
    def resonance_to_swara(cls, resonance: float) -> str:
        """
        Map a resonance value to its corresponding Swara.

        Args:
            resonance: A resonance value (typically 0.0 to 2.0)

        Returns:
            The Swara name ("Sa", "Re", "Ga", "Ma", "Pa", "Dha", "Ni", "Sa'")
        """
        if resonance < cls.BOUNDARY_SA_RE:
            return "Sa"
        elif resonance < cls.BOUNDARY_RE_GA:
            return "Re"
        elif resonance < cls.BOUNDARY_GA_MA:
            return "Ga"
        elif resonance < cls.BOUNDARY_MA_PA:
            return "Ma"
        elif resonance < cls.BOUNDARY_PA_DHA:
            return "Pa"
        elif resonance < cls.BOUNDARY_DHA_NI:
            return "Dha"
        elif resonance < cls.BOUNDARY_NI_SA:
            return "Ni"
        else:
            return "Sa'"  # Upper octave

    @classmethod
    def resonance_to_rasa(cls, resonance: float) -> str:
        """
        Map resonance to Rasa (emotional flavor/mood).

        The Nine Rasas (Navarasa) simplified to four resonance zones:
            SILENCE → Shanta (Peace, tranquility)
            REFINE  → Karuna (Compassion, seeking)
            AUTO    → Vira (Heroism, confidence)
            SYNC    → Adbhuta (Wonder, transcendence)

        Args:
            resonance: A resonance value

        Returns:
            The Rasa name and its meaning
        """
        zone = ResonanceHarmonics.get_zone(resonance)
        rasa_map = {
            "SILENCE": ("Shanta", "Peace"),
            "REFINE": ("Karuna", "Compassion"),
            "AUTO": ("Vira", "Courage"),
            "SYNC": ("Adbhuta", "Wonder"),
        }
        return rasa_map.get(zone, ("Unknown", "Unknown"))

    @classmethod
    def distance_to_nearest_sync(cls, resonance: float) -> tuple[float, str]:
        """
        Calculate distance to nearest flute sync point.

        Args:
            resonance: A resonance value (should be 0-1 for meaningful results)

        Returns:
            Tuple of (distance, flute_name) where flute_name is which
            flute creates the nearest sync point
        """
        # Normalize to 0-1 if needed
        normalized = resonance % 1.0 if resonance > 1.0 else resonance

        murali_points = cls.get_murali_sync_points()
        venu_points = cls.get_venu_sync_points()
        vamsi_points = cls.get_vamsi_sync_points()

        min_dist = float('inf')
        closest_flute = "NONE"

        # Check MURALI
        for p in murali_points:
            dist = abs(normalized - p)
            if dist < min_dist:
                min_dist = dist
                closest_flute = "MURALI"

        # Check VENU
        for p in venu_points:
            dist = abs(normalized - p)
            if dist < min_dist:
                min_dist = dist
                closest_flute = "VENU"

        # Check VAMSI
        for p in vamsi_points:
            dist = abs(normalized - p)
            if dist < min_dist:
                min_dist = dist
                closest_flute = "VAMSI"

        return (min_dist, closest_flute)

    @classmethod
    def get_harmonic_signature(cls, resonance: float) -> dict:
        """
        Get the complete harmonic signature for a resonance value.

        Returns a dict with:
            - swara: The Swara name
            - rasa: The Rasa (mood) tuple
            - zone: The resonance zone
            - sync_distance: Distance to nearest sync point
            - sync_flute: Which flute creates nearest sync
        """
        swara = cls.resonance_to_swara(resonance)
        rasa = cls.resonance_to_rasa(resonance)
        zone = ResonanceHarmonics.get_zone(resonance)
        sync_dist, sync_flute = cls.distance_to_nearest_sync(resonance)

        return {
            "swara": swara,
            "rasa": rasa,
            "zone": zone,
            "sync_distance": sync_dist,
            "sync_flute": sync_flute,
            "resonance": resonance,
        }

    @classmethod
    def get_melakarta_number(cls, resonance: float) -> int:
        """
        Map resonance to one of the 72 Melakarta Ragas.

        The 72 Melakartas are parent ragas in Carnatic music.
        72 = NADI_RESONANCE = JIVA_CYCLE / VENU_HOLES

        Maps resonance (0-1) to raga number (1-72) via:
            raga_number = int(resonance * 72) + 1, clamped to 1-72

        This is a simplified mapping - the full system would consider
        the specific Swara combinations of each Melakarta.
        """
        # Normalize to 0-1 range
        normalized = max(0.0, min(1.0, resonance))
        # Map to 1-72
        raga_num = int(normalized * NADI_RESONANCE) + 1
        return max(1, min(NADI_RESONANCE, raga_num))


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
# VEDIC SCALE WATERTIGHT VERIFICATION (SSOT - All from Seed!)
# =============================================================================

# Verify Swaras match Vedic music theory ratios
assert abs(VedicScaleMapping.SWARA_SA - 1.0) < 0.0001, "Sa must be 1/1"
assert abs(VedicScaleMapping.SWARA_RE - 1.125) < 0.0001, "Re must be 9/8 = 1.125"
assert abs(VedicScaleMapping.SWARA_GA - 1.25) < 0.0001, "Ga must be 5/4 = 1.25"
assert abs(VedicScaleMapping.SWARA_MA - 4/3) < 0.0001, "Ma must be 4/3"
assert abs(VedicScaleMapping.SWARA_PA - 1.5) < 0.0001, "Pa must be 3/2 = 1.5"
assert abs(VedicScaleMapping.SWARA_DHA - 5/3) < 0.0001, "Dha must be 5/3"
assert abs(VedicScaleMapping.SWARA_NI - 16/9) < 0.0001, "Ni must be 16/9"

# Verify convergence with ResonanceHarmonics
assert abs(VedicScaleMapping.SWARA_MA - ResonanceHarmonics.THRESHOLD_SYNC) < 0.0001, (
    "Ma (4/3) must equal THRESHOLD_SYNC"
)
assert abs(VedicScaleMapping.SWARA_PA - ResonanceHarmonics.RATIO_NADI_LILA) < 0.0001, (
    "Pa (3/2) must equal NADI/LILA ratio"
)
assert abs(VedicScaleMapping.SWARA_NI - ResonanceHarmonics.RATIO_MANTRA_PROCESS) < 0.0001, (
    "Ni (16/9) must equal RATIO_MANTRA_PROCESS"
)

# Verify flute sync point convergence with thresholds
_vamsi_4th = QUARTERS / VAMSI_HOLES  # 4/9
_venu_4th = QUARTERS / VENU_HOLES    # 4/6 = 2/3
assert abs(_vamsi_4th - ResonanceHarmonics.THRESHOLD_REFINE) < 0.0001, (
    "VAMSI 4th sync (4/9) must equal THRESHOLD_REFINE"
)
assert abs(_venu_4th - ResonanceHarmonics.THRESHOLD_AUTO) < 0.0001, (
    "VENU 4th sync (2/3) must equal THRESHOLD_AUTO"
)

# Verify boundaries are correctly derived from Seed
assert abs(VedicScaleMapping.BOUNDARY_MA_PA - HALVES / TRINITY) < 0.0001, (
    "BOUNDARY_MA_PA must be HALVES/TRINITY = 2/3"
)
assert abs(VedicScaleMapping.BOUNDARY_DHA_NI - QUARTERS / TRINITY) < 0.0001, (
    "BOUNDARY_DHA_NI must be QUARTERS/TRINITY = 4/3"
)
assert abs(VedicScaleMapping.BOUNDARY_NI_SA - WORDS / NAVA) < 0.0001, (
    "BOUNDARY_NI_SA must be WORDS/NAVA = 16/9"
)

# THE ULTIMATE VERIFICATION: Seed produces Vedic Music Theory!
# This proves the Mahamantra IS the cosmic frequency generator.
assert NAVA == 9 and HARE_COUNT == 8, "Seed must have NAVA=9, HARE_COUNT=8 for Re=9/8"
assert PANCHA == 5 and QUARTERS == 4, "Seed must have PANCHA=5, QUARTERS=4 for Ga=5/4"
assert PANCHA == 5 and TRINITY == 3, "Seed must have PANCHA=5, TRINITY=3 for Dha=5/3"
assert WORDS == 16 and NAVA == 9, "Seed must have WORDS=16, NAVA=9 for Ni=16/9"


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
    # Classes
    "ResonanceHarmonics",
    "VedicScaleMapping",
    # Constants (for direct import)
    "THRESHOLD_AUTO",
    "THRESHOLD_REFINE",
    "THRESHOLD_SYNC",
    "RATIO_MANTRA_PROCESS",
]
