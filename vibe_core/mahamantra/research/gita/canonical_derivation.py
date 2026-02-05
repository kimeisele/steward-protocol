"""
GITA CANONICAL DERIVATION - The Research Frontier
==================================================

PROBLEM STATEMENT:
==================
The 18 Gita chapters have specific verse counts:
    (47, 72, 43, 42, 29, 47, 30, 28, 34, 42, 55, 20, 35, 27, 20, 24, 28, 78)

These are currently HARDCODED. We need them DERIVED from EPOCH_KEY (1972).

WHY THIS MATTERS:
=================
Without canonical derivation:
- 18 chapters = flat list (no hierarchy)
- No routing information
- Split brain between 18 chapters and 16 guardians
- Gita cannot serve as PROTOCOL layer

With canonical derivation:
- 18 chapters become COMPUTED structure
- Routing values emerge from mathematics
- Gita becomes true parent hierarchy
- Guardians align within chapter structure

KEY DISCOVERY:
==============
1972 = 4 x 17 x 29

Where:
- 4  = QUARTERS
- 17 = POSITION_SUM_KRISHNA (THE ONLY PRIME POSITION SUM!)
- 29 = CHAPTER 5 VERSE COUNT (Karma Sannyasa!)

The EPOCH_KEY factorization CONTAINS a chapter verse count.
This cannot be coincidence.

ADDITIONAL OBSERVATIONS:
========================
1972 mod 18 = 10  -> Chapter 10 (Vibhuti - Divine Manifestations)
1972 mod 27 = 1   -> KSETRAJNA (Observer arrived)
1977 mod 37 = 16  -> WORDS (Message complete)

digit_sum(1972) = 1+9+7+2 = 19 = FLUTE_HOLES_SUM

VERSE COUNT PATTERNS:
=====================
Ch 2:  72 = NADI_RESONANCE
Ch 14: 27 = NAKSHATRAS
Ch 16: 24 = KSHETRA
Ch 18: 78 = NADI_RESONANCE + SHARANAGATI = 72 + 6

Duplicates:
- 47 appears in Ch 1, Ch 6
- 42 appears in Ch 4, Ch 10
- 20 appears in Ch 12, Ch 15
- 28 appears in Ch 8, Ch 17

RESEARCH DIRECTION:
===================
Find function f(EPOCH_KEY, chapter_index) that generates verse counts.

Possible approaches:
1. Modular arithmetic chains from 1972
2. Factor decomposition patterns
3. Cumulative sum relationships
4. Resonance with gita_resonance_index.json attractors
5. Triangular/figurate number relationships

"satyam param dhimahi" - We meditate on the supreme truth.
"""

__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x545fe2f1"

from typing import Dict, Final, Tuple

from vibe_core.mahamantra.protocols._seed import (
    EPOCH_KEY,
    FLUTE_HOLES_SUM,
    GITA_CHAPTERS,
    KSETRAJNA,
    KSHETRA,
    NADI_RESONANCE,
    NAKSHATRAS,
    PARAMPARA,
    POSITION_SUM_KRISHNA,
    QUARTERS,
    SHARANAGATI,
    WORDS,
)

# =============================================================================
# THE CANONICAL DATA (Currently hardcoded - to be derived)
# =============================================================================

CHAPTER_VERSES: Final[Tuple[int, ...]] = (47, 72, 43, 42, 29, 47, 30, 28, 34, 42, 55, 20, 35, 27, 20, 24, 28, 78)
assert len(CHAPTER_VERSES) == GITA_CHAPTERS
assert sum(CHAPTER_VERSES) == 700  # SEVEN x 100

# =============================================================================
# EPOCH_KEY ANALYSIS
# =============================================================================

# Prime factorization
EPOCH_FACTOR_1: Final[int] = QUARTERS  # 4
EPOCH_FACTOR_2: Final[int] = POSITION_SUM_KRISHNA  # 17 (PRIME!)
EPOCH_FACTOR_3: Final[int] = 29  # Chapter 5 verse count!

assert EPOCH_KEY == EPOCH_FACTOR_1 * EPOCH_FACTOR_2 * EPOCH_FACTOR_3, (
    f"1972 = 4 x 17 x 29, got {EPOCH_FACTOR_1 * EPOCH_FACTOR_2 * EPOCH_FACTOR_3}"
)

# The 29 connection
KARMA_SANNYASA_CHAPTER: Final[int] = 5
assert CHAPTER_VERSES[KARMA_SANNYASA_CHAPTER - 1] == EPOCH_FACTOR_3, (
    "29 appears in 1972 factorization AND is Chapter 5 verse count"
)

# Modular signatures
EPOCH_MOD_18: Final[int] = EPOCH_KEY % GITA_CHAPTERS  # 10 = Vibhuti
EPOCH_MOD_27: Final[int] = EPOCH_KEY % NAKSHATRAS  # 1 = KSETRAJNA
EPOCH_DIGIT_SUM: Final[int] = sum(int(d) for d in str(EPOCH_KEY))  # 19

assert EPOCH_DIGIT_SUM == FLUTE_HOLES_SUM, "digit_sum(1972) = 19"

# =============================================================================
# KNOWN VERSE-CONSTANT MATCHES
# =============================================================================

KNOWN_MATCHES: Final[Dict[int, str]] = {
    2: f"72 = NADI_RESONANCE ({NADI_RESONANCE})",
    14: f"27 = NAKSHATRAS ({NAKSHATRAS})",
    16: f"24 = KSHETRA ({KSHETRA})",
    18: f"78 = NADI + SHARANAGATI ({NADI_RESONANCE + SHARANAGATI})",
}

# Verify known matches
assert CHAPTER_VERSES[1] == NADI_RESONANCE  # Ch 2
assert CHAPTER_VERSES[13] == NAKSHATRAS  # Ch 14
assert CHAPTER_VERSES[15] == KSHETRA  # Ch 16
assert CHAPTER_VERSES[17] == NADI_RESONANCE + SHARANAGATI  # Ch 18

# =============================================================================
# RESEARCH INTERFACE
# =============================================================================


def analyze_chapter(chapter: int) -> Dict:
    """Analyze a single chapter for derivation patterns."""
    if not 1 <= chapter <= GITA_CHAPTERS:
        raise ValueError(f"Chapter must be 1-18, got {chapter}")

    idx = chapter - 1
    verses = CHAPTER_VERSES[idx]

    return {
        "chapter": chapter,
        "verses": verses,
        "verses_mod_17": verses % POSITION_SUM_KRISHNA,
        "verses_mod_37": verses % PARAMPARA,
        "verses_mod_16": verses % WORDS,
        "epoch_mod_verses": EPOCH_KEY % verses if verses > 0 else 0,
        "known_match": KNOWN_MATCHES.get(chapter),
    }


def search_derivation() -> None:
    """
    RESEARCH FUNCTION: Search for derivation patterns.

    This is the frontier. The goal is to find f(1972, n) -> verse_count[n].
    """
    print("=" * 60)
    print("GITA CANONICAL DERIVATION RESEARCH")
    print("=" * 60)
    print(f"\nEPOCH_KEY = {EPOCH_KEY} = {EPOCH_FACTOR_1} x {EPOCH_FACTOR_2} x {EPOCH_FACTOR_3}")
    print(f"Note: {EPOCH_FACTOR_3} = Chapter 5 verse count (Karma Sannyasa)")
    print(f"\n1972 mod 18 = {EPOCH_MOD_18} (Chapter {EPOCH_MOD_18} = Vibhuti)")
    print(f"digit_sum(1972) = {EPOCH_DIGIT_SUM} = FLUTE_HOLES_SUM")

    print("\n" + "-" * 60)
    print("CHAPTER ANALYSIS:")
    print("-" * 60)

    for ch in range(1, GITA_CHAPTERS + 1):
        data = analyze_chapter(ch)
        match_str = f" <- {data['known_match']}" if data["known_match"] else ""
        print(
            f"Ch {ch:2d}: {data['verses']:2d} verses | "
            f"mod17={data['verses_mod_17']:2d} | "
            f"mod37={data['verses_mod_37']:2d} | "
            f"mod16={data['verses_mod_16']:2d}{match_str}"
        )


if __name__ == "__main__":
    search_derivation()
