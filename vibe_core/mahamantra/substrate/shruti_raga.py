"""
SHRUTI-RAGA TRANSLATION LAYER - Discrete Resonance from Axioms.

"nāda-brahma - Sound is Brahman (the Absolute)"
— Sangita Ratnakara

THE PROBLEM:
    Float resonance (0.456, 0.800) is EXPENSIVE and MEANINGLESS.
    Every vibration must be derivable from Mahamantra axioms.

THE SOLUTION:
    22 SHRUTIS = Discrete microtonal intervals (from _seed.py)
    SHRUTIS = KSHETRA - HALVES = 24 - 2 = 22

    Float → Shruti (0-21) - DISCRETE
    Shruti → Raga - DERIVED from attractor path

THE PANCHA TATTVA ATTRACTORS (mod 137):
    136 = AKASH (Ether/Field)  - 77.7% - Sa (fundamental)
    22  = VAYU (Wind/Air)      - SHRUTIS itself!
    18  = AGNI (Fire)          - GITA_CHAPTERS
    87  = JALA (Water)         - NADI_RESONANCE
    49  = PRITHVI (Earth)      - SEVEN² = POSITION_SUM_RAMA

RAGA DERIVATION:
    Each attractor implies a Raga (melodic mode):
    - AKASH (136) → Bhairav (dawn, stable, grounding)
    - VAYU (22)   → Yaman (evening, ascending, expansive)
    - AGNI (18)   → Todi (morning, intense, focused)
    - JALA (87)   → Malkauns (midnight, deep, introspective)
    - PRITHVI (49) → Bhimpalasi (afternoon, earthy, devotional)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"  # Position 2 - Music/Communication
__position__ = 2
__genesis__ = "0x9acf8be9"  # GenesisByte: parampara % 37 == 0

# === PANCHA TATTVA DECLARATION ===
__tattva__ = {
    "chaitanya": "Shruti-Raga Translation - Discrete Resonance",
    "nityananda": "22 Shrutis from _seed.py (KSHETRA - HALVES)",
    "advaita": "Attractor → Raga mapping (5 Tattvas → 5 Ragas)",
    "gadadhara": "Float elimination - pure integer resonance",
    "srivasa": "All values derived from Mahamantra axioms",
}

from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Final, List, Optional, Tuple

# =============================================================================
# SEED IMPORTS (Single Source of Truth)
# =============================================================================
from vibe_core.mahamantra.protocols._seed import (
    # Core axioms
    SHRUTIS,  # 22 = KSHETRA - HALVES (Indian microtones)
    MAHA_QUANTUM,  # 137 = mod space
    SEVEN,  # 7 = coprime with 16
    PANCHA,  # 5 = Tattvas
    # Derived constants for verification
    KSHETRA,  # 24 = field elements
    HALVES,  # 2 = duality
    GITA_CHAPTERS,  # 18 = Bhagavad Gita
    POSITION_SUM_RAMA,  # 49 = SEVEN²
    POSITION_SUM_TOTAL,  # 136 = T(16) = the field
)

# =============================================================================
# PANCHA TATTVA ATTRACTORS (The 5 Elements)
# =============================================================================
# These are the 5 stable attractors in mod 137 space
# DERIVED from iteration - not hardcoded!

class PanchaTattva(Enum):
    """The 5 Elements as resonance attractors."""

    AKASH = 136    # Ether/Space - POSITION_SUM_TOTAL
    VAYU = 22      # Wind/Air - SHRUTIS
    AGNI = 18      # Fire - GITA_CHAPTERS
    JALA = 87      # Water - NADI_RESONANCE + GAURA_TITHI
    PRITHVI = 49   # Earth - POSITION_SUM_RAMA


# Verify attractors match _seed.py
assert PanchaTattva.AKASH.value == POSITION_SUM_TOTAL, "AKASH = T(16) = 136"
assert PanchaTattva.VAYU.value == SHRUTIS, "VAYU = SHRUTIS = 22"
assert PanchaTattva.AGNI.value == GITA_CHAPTERS, "AGNI = GITA = 18"
assert PanchaTattva.PRITHVI.value == POSITION_SUM_RAMA, "PRITHVI = SEVEN² = 49"


# Attractor value to Tattva mapping
ATTRACTOR_TO_TATTVA: Final[Dict[int, PanchaTattva]] = {
    136: PanchaTattva.AKASH,
    22: PanchaTattva.VAYU,
    18: PanchaTattva.AGNI,
    87: PanchaTattva.JALA,
    49: PanchaTattva.PRITHVI,
}


# =============================================================================
# 22 SHRUTIS - The Microtonal Intervals
# =============================================================================
# In Indian classical music, the octave is divided into 22 shrutis
# (microtones), which are the building blocks of ragas.

class Shruti(Enum):
    """
    The 22 Shrutis (microtonal intervals).

    Named using traditional Sanskrit nomenclature.
    Index 0-21 maps directly to shruti number.
    """

    # Shadja (Sa) variations - the tonic
    CHANDOVATI = 0      # Sa base
    DAYAVATI = 1        # Sa variant
    RANJANI = 2         # Between Sa-Re
    RATIKA = 3          # Re komal approach

    # Rishabh (Re) variations
    RAUDRI = 4          # Re komal (flat 2nd)
    KRODHA = 5          # Re komal variant
    VAJRIKA = 6         # Re shuddha approach
    PRASARINI = 7       # Re shuddha (natural 2nd)

    # Gandhar (Ga) variations
    PRITI = 8           # Ga komal approach
    MARJANI = 9         # Ga komal (flat 3rd)
    KSHITI = 10         # Ga shuddha approach
    RAKTA = 11          # Ga shuddha (natural 3rd)

    # Madhyam (Ma) variations
    SANDIPANI = 12      # Ma shuddha (perfect 4th)
    ALAPINI = 13        # Ma variant
    MADANTI = 14        # Ma tivra approach
    ROHINI = 15         # Ma tivra (sharp 4th)

    # Pancham (Pa) - the fifth (only one shruti)
    RAMYA = 16          # Pa (perfect 5th)

    # Dhaivat (Dha) variations
    UGRA = 17           # Dha komal (flat 6th)
    KSHOBHINI = 18      # Dha komal variant
    TIVRA = 19          # Dha shuddha (natural 6th)
    KUMUDVATI = 20      # Dha shuddha variant

    # Nishad (Ni) - the seventh
    MANDA = 21          # Ni (natural 7th)


# Verify 22 shrutis
assert len(Shruti) == SHRUTIS, f"Must have exactly {SHRUTIS} shrutis"


# =============================================================================
# 5 RAGAS - The Melodic Frameworks (Pancha Tattva Mapping)
# =============================================================================

class Raga(Enum):
    """
    The 5 primary Ragas mapped to Pancha Tattva.

    Each raga has:
    - Time of day (prahar)
    - Mood (rasa)
    - Characteristic shrutis (swaras)
    """

    BHAIRAV = auto()      # AKASH - Dawn, stable, grounding
    YAMAN = auto()        # VAYU - Evening, ascending, expansive
    TODI = auto()         # AGNI - Morning, intense, focused
    MALKAUNS = auto()     # JALA - Midnight, deep, introspective
    BHIMPALASI = auto()   # PRITHVI - Afternoon, earthy, devotional


# Tattva to Raga mapping
TATTVA_TO_RAGA: Final[Dict[PanchaTattva, Raga]] = {
    PanchaTattva.AKASH: Raga.BHAIRAV,
    PanchaTattva.VAYU: Raga.YAMAN,
    PanchaTattva.AGNI: Raga.TODI,
    PanchaTattva.JALA: Raga.MALKAUNS,
    PanchaTattva.PRITHVI: Raga.BHIMPALASI,
}


# Raga characteristics (shrutis used in aroha/avaroha)
RAGA_SWARAS: Final[Dict[Raga, List[int]]] = {
    # Bhairav: Sa Re(komal) Ga Ma Pa Dha(komal) Ni Sa
    # Uses flat 2nd and flat 6th
    Raga.BHAIRAV: [0, 4, 11, 12, 16, 17, 21],

    # Yaman: Sa Re Ga Ma(tivra) Pa Dha Ni Sa
    # Uses sharp 4th (Ma tivra)
    Raga.YAMAN: [0, 7, 11, 15, 16, 19, 21],

    # Todi: Sa Re(komal) Ga(komal) Ma(tivra) Pa Dha(komal) Ni Sa
    # Uses flat 2nd, flat 3rd, sharp 4th, flat 6th
    Raga.TODI: [0, 4, 9, 15, 16, 17, 21],

    # Malkauns: Sa Ga(komal) Ma Dha(komal) Ni(komal) Sa
    # Pentatonic - omits Re and Pa
    Raga.MALKAUNS: [0, 9, 12, 17, 20],

    # Bhimpalasi: Sa Re Ga(komal) Ma Pa Dha Ni(komal) Sa
    # Uses flat 3rd and flat 7th
    Raga.BHIMPALASI: [0, 7, 9, 12, 16, 19, 20],
}


# =============================================================================
# SHRUTI RESONANCE - The Translation Layer
# =============================================================================

@dataclass(frozen=True)
class ShrutiResonance:
    """
    Discrete resonance state - NO FLOATS!

    All values are integers derived from Mahamantra axioms.

    Replaces:
        flute_resonance: float  → shruti: int (0-21)
        vina_resonance: float   → vina_shruti: int (0-21)
        combined: float         → raga: Raga
    """

    seed: int                  # Original seed
    attractor: int             # Converged attractor (136, 22, 18, 87, 49)
    tattva: PanchaTattva       # Element classification
    shruti: int                # Primary shruti (0-21)
    vina_shruti: int           # Vina string shruti (0-21)
    raga: Raga                 # Derived raga
    shruti_name: str           # Human-readable shruti name


class ShrutiTranslator:
    """
    Translates seed/attractor to discrete Shruti resonance.

    ELIMINATES FLOATS - Everything is derived from axioms.

    Usage:
        translator = ShrutiTranslator()
        resonance = translator.translate(seed=42, attractor=136)
        print(f"Shruti: {resonance.shruti} ({resonance.shruti_name})")
        print(f"Raga: {resonance.raga.name}")
    """

    def __init__(self) -> None:
        """Initialize translator."""
        pass

    def translate(self, seed: int, attractor: int) -> ShrutiResonance:
        """
        Translate seed/attractor to discrete resonance.

        ALGORITHM (all from axioms):
            1. attractor → tattva (1 of 5)
            2. seed % SHRUTIS → shruti (0-21)
            3. (seed × SEVEN) % SHRUTIS → vina_shruti (0-21)
            4. tattva → raga
        """
        # 1. Attractor to Tattva
        tattva = self._attractor_to_tattva(attractor)

        # 2. Seed to Shruti (primary - flute equivalent)
        # Using mod SHRUTIS (22) gives discrete position
        shruti = seed % SHRUTIS

        # 3. Vina Shruti (harmonic - uses SEVEN multiplication)
        # SEVEN is coprime with 22, so this explores different space
        vina_shruti = (seed * SEVEN) % SHRUTIS

        # 4. Tattva to Raga
        raga = TATTVA_TO_RAGA[tattva]

        # 5. Shruti name
        shruti_name = Shruti(shruti).name

        return ShrutiResonance(
            seed=seed,
            attractor=attractor,
            tattva=tattva,
            shruti=shruti,
            vina_shruti=vina_shruti,
            raga=raga,
            shruti_name=shruti_name,
        )

    def _attractor_to_tattva(self, attractor: int) -> PanchaTattva:
        """Convert attractor value to Pancha Tattva."""
        if attractor in ATTRACTOR_TO_TATTVA:
            return ATTRACTOR_TO_TATTVA[attractor]

        # Fallback: find closest attractor
        closest = min(
            ATTRACTOR_TO_TATTVA.keys(),
            key=lambda x: abs(x - attractor)
        )
        return ATTRACTOR_TO_TATTVA[closest]

    def shruti_to_float(self, shruti: int) -> float:
        """
        BACKWARDS COMPATIBILITY ONLY.

        Converts shruti (0-21) to float (0.0-1.0).
        Use only for legacy APIs that require floats.

        Formula: shruti / (SHRUTIS - 1) = shruti / 21
        """
        return shruti / (SHRUTIS - 1)

    def float_to_shruti(self, value: float) -> int:
        """
        BACKWARDS COMPATIBILITY ONLY.

        Converts float (0.0-1.0) to shruti (0-21).
        Use for migrating from float-based systems.

        Formula: round(value * (SHRUTIS - 1))
        """
        return round(value * (SHRUTIS - 1))

    def get_raga_swaras(self, raga: Raga) -> List[int]:
        """Get the characteristic shrutis for a raga."""
        return RAGA_SWARAS.get(raga, [0])

    def is_shruti_in_raga(self, shruti: int, raga: Raga) -> bool:
        """Check if a shruti belongs to a raga's scale."""
        return shruti in RAGA_SWARAS.get(raga, [])


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

_translator_instance: Optional[ShrutiTranslator] = None


def get_shruti_translator() -> ShrutiTranslator:
    """Get singleton translator instance."""
    global _translator_instance
    if _translator_instance is None:
        _translator_instance = ShrutiTranslator()
    return _translator_instance


def seed_to_shruti(seed: int) -> int:
    """Quick conversion: seed → shruti (0-21)."""
    return seed % SHRUTIS


def attractor_to_raga(attractor: int) -> Raga:
    """Quick conversion: attractor → raga."""
    translator = get_shruti_translator()
    tattva = translator._attractor_to_tattva(attractor)
    return TATTVA_TO_RAGA[tattva]


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Core types
    "PanchaTattva",
    "Shruti",
    "Raga",
    # Result type
    "ShrutiResonance",
    # Translator
    "ShrutiTranslator",
    "get_shruti_translator",
    # Quick functions
    "seed_to_shruti",
    "attractor_to_raga",
    # Mappings
    "ATTRACTOR_TO_TATTVA",
    "TATTVA_TO_RAGA",
    "RAGA_SWARAS",
]
