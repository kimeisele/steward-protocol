"""
ATTRACTOR SEMANTICS - The Meaning of Numbers
=============================================

"śabda-brahma paraṁ brahma"
"Sound is Brahman, the Supreme is Brahman."

This module maps attractor values to their VERIFIED meanings.
No speculation - only what is mathematically proven and 
documented in the codebase.

THE 4-CYCLE (mod 137):
======================
18 (GITA) → 49 (ALPHABET) → 87 (HARE+KRISHNA) → 22 (SHRUTIS) → 18

THE FIXED POINT (mod 137):
==========================
136 = T(16) = POSITION_SUM_TOTAL = The Field (Vaikuntha)

VERIFIED MEANINGS:
==================
- 18 = GITA_CHAPTERS (Bhagavad Gita)
- 22 = SHRUTIS (Indian microtones)
- 49 = VARNAMALA (Sanskrit Alphabet = 7²)
- 70 = POSITION_SUM_HARE
- 17 = POSITION_SUM_KRISHNA (PRIME)
- 87 = HARE + KRISHNA = 70 + 17
- 136 = T(16) = 70 + 17 + 49 = HARE + KRISHNA + RAMA
- 12 = MAHAJANA_COUNT
- 37 = PARAMPARA
- 72 = MELAKARTAS (Parent Ragas)
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Final, List, Optional, Tuple

from vibe_core.mahamantra.protocols._seed import (
    GITA_CHAPTERS,
    HALVES,
    KSETRAJNA,
    KSHETRA,
    MAHA_QUANTUM,
    MAHAJANA_COUNT,
    MALA,
    NADI_RESONANCE,
    PARAMPARA,
    POSITION_SUM_HARE,
    POSITION_SUM_KRISHNA,
    POSITION_SUM_RAMA,
    POSITION_SUM_TOTAL,
    QUARTERS,
    QUALITIES,
    SEVEN,
    SHARANAGATI,
    TEN,
    TRINITY,
    WORDS,
)

# Derived constants (no hardcoding)
SHRUTIS: Final[int] = KSHETRA - HALVES  # 24 - 2 = 22
HARE_KRISHNA_COMBINED: Final[int] = POSITION_SUM_HARE + POSITION_SUM_KRISHNA  # 70 + 17 = 87

__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0xsemantic"


# =============================================================================
# VERIFIED ATTRACTOR MEANINGS
# =============================================================================

class AttractorMeaning(Enum):
    """Categories of attractor meanings."""
    
    SCRIPTURE = "scripture"      # Gita, Vedas
    ALPHABET = "alphabet"        # Varnamala, letters
    MUSIC = "music"              # Shrutis, Ragas, Melakartas
    ENERGY = "energy"            # Position sums, combined energies
    STRUCTURE = "structure"      # Mahajanas, Quarters, etc.
    FIELD = "field"              # Vaikuntha, T(16)
    TRANSMISSION = "transmission"  # Parampara
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class AttractorSemantics:
    """Semantic meaning of an attractor value."""
    
    value: int
    name: str
    meaning: AttractorMeaning
    description: str
    derivation: str  # How it's derived from axioms
    

# The verified semantic map
ATTRACTOR_SEMANTICS: Final[Dict[int, AttractorSemantics]] = {
    # Scripture
    GITA_CHAPTERS: AttractorSemantics(
        value=GITA_CHAPTERS,
        name="GITA_CHAPTERS",
        meaning=AttractorMeaning.SCRIPTURE,
        description="The 18 chapters of Bhagavad Gita",
        derivation="18 = 2 × 9 = HALVES × NAVA",
    ),
    
    # Alphabet
    POSITION_SUM_RAMA: AttractorSemantics(
        value=POSITION_SUM_RAMA,
        name="VARNAMALA / RAMA_SUM",
        meaning=AttractorMeaning.ALPHABET,
        description="Sanskrit Alphabet (49 letters) = RAMA position sum",
        derivation="49 = 7² = SEVEN × SEVEN",
    ),
    
    # Music
    SHRUTIS: AttractorSemantics(
        value=SHRUTIS,
        name="SHRUTIS",
        meaning=AttractorMeaning.MUSIC,
        description="22 microtones in Indian classical music",
        derivation="SHRUTIS = KSHETRA - HALVES = 24 - 2",
    ),
    NADI_RESONANCE: AttractorSemantics(
        value=NADI_RESONANCE,
        name="MELAKARTAS",
        meaning=AttractorMeaning.MUSIC,
        description="72 parent ragas in Carnatic music",
        derivation="72 = JIVA_CYCLE / SHARANAGATI = 432 / 6",
    ),
    
    # Energy
    POSITION_SUM_HARE: AttractorSemantics(
        value=POSITION_SUM_HARE,
        name="HARE_SUM",
        meaning=AttractorMeaning.ENERGY,
        description="Sum of HARE positions (1,3,7,8,9,11,15,16)",
        derivation="70 = 7 × 10 = SEVEN × TEN",
    ),
    POSITION_SUM_KRISHNA: AttractorSemantics(
        value=POSITION_SUM_KRISHNA,
        name="KRISHNA_SUM",
        meaning=AttractorMeaning.ENERGY,
        description="Sum of KRISHNA positions (2,4,5,6) - PRIME",
        derivation="17 = 7 + 10 = SEVEN + TEN (PRIME)",
    ),
    HARE_KRISHNA_COMBINED: AttractorSemantics(
        value=HARE_KRISHNA_COMBINED,
        name="HARE_KRISHNA_COMBINED",
        meaning=AttractorMeaning.ENERGY,
        description="Combined energy of HARE + KRISHNA (without RAMA)",
        derivation="HARE_KRISHNA_COMBINED = POSITION_SUM_HARE + POSITION_SUM_KRISHNA",
    ),
    
    # Field
    POSITION_SUM_TOTAL: AttractorSemantics(
        value=POSITION_SUM_TOTAL,
        name="VAIKUNTHA_FIELD",
        meaning=AttractorMeaning.FIELD,
        description="T(16) = Complete field, Vaikuntha energy",
        derivation="136 = 70 + 17 + 49 = HARE + KRISHNA + RAMA = T(16)",
    ),
    
    # Structure
    MAHAJANA_COUNT: AttractorSemantics(
        value=MAHAJANA_COUNT,
        name="MAHAJANAS",
        meaning=AttractorMeaning.STRUCTURE,
        description="The 12 Mahajana authorities",
        derivation="12 = TEN + HALVES = 10 + 2",
    ),
    QUARTERS: AttractorSemantics(
        value=QUARTERS,
        name="QUARTERS",
        meaning=AttractorMeaning.STRUCTURE,
        description="4 quarters of Mahamantra, 4 Yugas, 4 Avataras",
        derivation="4 = HALVES × HALVES = 2 × 2",
    ),
    WORDS: AttractorSemantics(
        value=WORDS,
        name="WORDS",
        meaning=AttractorMeaning.STRUCTURE,
        description="16 words of Mahamantra",
        derivation="16 = QUARTERS × QUARTERS = 4 × 4",
    ),
    QUALITIES: AttractorSemantics(
        value=QUALITIES,
        name="QUALITIES",
        meaning=AttractorMeaning.STRUCTURE,
        description="64 qualities of Krishna",
        derivation="64 = WORDS × QUARTERS = 16 × 4",
    ),
    
    # Transmission
    PARAMPARA: AttractorSemantics(
        value=PARAMPARA,
        name="PARAMPARA",
        meaning=AttractorMeaning.TRANSMISSION,
        description="Disciplic succession constant",
        derivation="37 = PRIME (12th prime number)",
    ),
    
    # 6 Attractors from mod 108
    KSETRAJNA: AttractorSemantics(
        value=KSETRAJNA,
        name="KSETRAJNA",
        meaning=AttractorMeaning.STRUCTURE,
        description="The Observer, consciousness",
        derivation="1 = unity",
    ),
    SEVEN + SHARANAGATI: AttractorSemantics(
        value=SEVEN + SHARANAGATI,
        name="MYSTERY_13",
        meaning=AttractorMeaning.UNKNOWN,
        description="7 + 6 = SEVEN + SHARANAGATI, or 10 + 3 = TEN + TRINITY",
        derivation="SEVEN + SHARANAGATI = 7 + 6 = 13",
    ),
    SEVEN * (SEVEN + KSETRAJNA) // HALVES: AttractorSemantics(
        value=SEVEN * (SEVEN + KSETRAJNA) // HALVES,
        name="T(7)",
        meaning=AttractorMeaning.STRUCTURE,
        description="Triangular(7) = Perfect number",
        derivation="T(7) = SEVEN × (SEVEN + 1) / 2 = 28",
    ),
}


def get_semantics(value: int) -> Optional[AttractorSemantics]:
    """Get semantic meaning of a value, if known."""
    return ATTRACTOR_SEMANTICS.get(value)


def interpret_attractor(value: int) -> str:
    """Get human-readable interpretation of an attractor."""
    sem = get_semantics(value)
    if sem:
        return f"{sem.name}: {sem.description}"
    return f"Unknown attractor: {value}"


# =============================================================================
# THE 4-CYCLE INTERPRETATION
# =============================================================================

CYCLE_4_VALUES: Final[Tuple[int, ...]] = (
    GITA_CHAPTERS,           # 18
    POSITION_SUM_RAMA,       # 49
    HARE_KRISHNA_COMBINED,   # 87 = HARE + KRISHNA
    SHRUTIS,                 # 22
)

CYCLE_4_INTERPRETATION: Final[str] = """
THE 4-CYCLE (mod 137):
======================

18 (GITA) → 49 (ALPHABET) → 87 (HARE+KRISHNA) → 22 (SHRUTIS) → 18

INTERPRETATION:
1. GITA (18) - The teaching, the knowledge
2. ALPHABET (49) - The language to express it (RAMA = 7²)
3. HARE+KRISHNA (87) - The combined energy (without RAMA)
4. SHRUTIS (22) - The sound, the music, the vibration
5. Back to GITA (18) - The cycle of knowledge

This is the "song" of the Mahamantra algorithm.
It cycles through: Teaching → Language → Energy → Sound → Teaching...

The FIXED POINT (136) is outside this cycle - it's Vaikuntha,
the transcendental field where the cycle doesn't apply.
"""


def print_cycle_analysis() -> None:
    """Print the 4-cycle analysis."""
    print(CYCLE_4_INTERPRETATION)
    print()
    print("VERIFIED CYCLE (computed):")
    print("-" * 40)
    
    from vibe_core.mahamantra.substrate.algorithm import maha_oscillate
    import warnings
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        v = GITA_CHAPTERS
        for i in range(5):
            sem = get_semantics(v)
            name = sem.name if sem else "?"
            print(f"  Step {i}: {v:3} = {name}")
            v = maha_oscillate(v, MAHA_QUANTUM)


# =============================================================================
# ATTRACTOR BASIN ANALYSIS
# =============================================================================

def analyze_mod_space(mod: int) -> None:
    """Analyze attractors in a given mod space with semantic interpretation."""
    from vibe_core.mahamantra_research.attractor_analysis import find_all_attractors
    
    print(f"\n{'=' * 60}")
    print(f"MOD {mod} SEMANTIC ANALYSIS")
    print("=" * 60)
    
    attractors = find_all_attractors(mod)
    vals = sorted([a.value for a in attractors.values()])
    
    print(f"\nAttractors: {vals}")
    print(f"Count: {len(vals)}, Sum: {sum(vals)}")
    print()
    
    for a in sorted(attractors.values(), key=lambda x: -x.basin_size):
        sem = get_semantics(a.value)
        cycle_info = "FIXED" if a.cycle_length == KSETRAJNA else f"cycle-{a.cycle_length}"
        
        if sem:
            print(f"  {a.value:3} = {sem.name:20} | basin={a.basin_size:3} | {cycle_info}")
            print(f"        {sem.description}")
        else:
            print(f"  {a.value:3} = ???                  | basin={a.basin_size:3} | {cycle_info}")
        print()


def run_full_semantic_analysis() -> None:
    """Run complete semantic analysis across key mod spaces."""
    print("=" * 70)
    print("ATTRACTOR SEMANTICS - Full Analysis")
    print("=" * 70)
    
    # The 4-cycle
    print_cycle_analysis()
    
    # Key mod spaces
    for mod in [MAHA_QUANTUM, MALA, PARAMPARA, POSITION_SUM_HARE]:
        analyze_mod_space(mod)


if __name__ == "__main__":
    run_full_semantic_analysis()
