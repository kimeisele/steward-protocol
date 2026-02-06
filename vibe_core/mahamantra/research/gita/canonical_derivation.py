"""
GITA CANONICAL DERIVATION - SOLVED
===================================

THE EPOCH EQUATION (The Master Key):
====================================

    1972 = GENESIS × NAVA + EPOCH_ADDITIVE
    1972 = 203 × 9 + 145
    145  = POSITION_SUM_TOTAL + NAVA = 136 + 9
    145  = PANCHA × Ch5_verses = 5 × 29 (Peace Formula!)

Where:
- GENESIS = sum(Ch 1-4) = 203 verses (The Foundation)
- NAVA = 9 (The Nine Processes of Devotion)
- EPOCH_ADDITIVE = 145 = POSITION_SUM_TOTAL + NAVA

This is NOT coincidence. The publication year ENCODES the Gita structure.

THE CANONICAL TOPOLOGY:
=======================

1. THE FIELD (Ch 1-16) = 594 verses = 18 × 33 = GITA_CHAPTERS × 33
   - Also: 594 = 9 × 66 = NAVA × 66
   - Also: 594 = 6 × 99 = SHARANAGATI × 99
   - The 16 Guardians' domain

2. THE FRUIT (Ch 17-18) = 106 verses
   - Beyond the Guardians' domain
   - The Transcendental Result

3. MOKSHA = FRUIT (Perfect Symmetry)
   - Moksha Quarter (Ch 13-16) = 106 verses
   - Fruit (Ch 17-18) = 106 verses
   - The effort equals the reward

QUARTER SUMS (Computed):
========================
- Genesis (Ch 1-4):   203 verses  <- IN THE EPOCH EQUATION!
- Dharma (Ch 5-8):    134 verses
- Karma (Ch 9-12):    151 verses
- Moksha (Ch 13-16):  106 verses  <- EQUALS FRUIT!
- Fruit (Ch 17-18):   106 verses  <- BEYOND GUARDIANS

SPLIT BRAIN RESOLVED:
=====================
- 16 Guardians handle Ch 1-16 (THE FIELD = 594 = 18 × 33)
- Ch 17-18 are THE FRUIT (Transcendental, beyond process)
- No conflict: 16 manages process, 18 includes result

FACTORIZATION (Secondary Discovery):
====================================
1972 = 4 × 17 × 29

Where:
- 4 = QUARTERS
- 17 = POSITION_SUM_KRISHNA (prime!)
- 29 = Chapter 5 verse count (Karma Sannyasa - the bridge)

"suhṛdaṁ sarva-bhūtānām" - He is the best friend of all beings (BG 5.29)
The Peace Formula chapter's verse count is IN the Epoch factorization.

"satyam param dhimahi" - We meditate on the supreme truth.
"""

__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x545fe2f1"

from typing import Dict, Final

from vibe_core.mahamantra.protocols._seed import (
    EPOCH_KEY,
    FLUTE_HOLES_SUM,
    GITA_CHAPTERS,
    KSETRAJNA,
    KSHETRA,
    NADI_RESONANCE,
    NAKSHATRAS,
    NAVA,
    PARAMPARA,
    POSITION_SUM_KRISHNA,
    POSITION_SUM_TOTAL,
    QUARTERS,
    SHARANAGATI,
    WORDS,
)
from vibe_core.mahamantra.protocols.seed._topology import CHAPTER_VERSES

# =============================================================================
# THE CANONICAL TOPOLOGY (SOLVED!)
# =============================================================================

# Quarter sums
GENESIS_SUM: Final[int] = sum(CHAPTER_VERSES[0:4])   # Ch 1-4: 203
DHARMA_SUM: Final[int] = sum(CHAPTER_VERSES[4:8])    # Ch 5-8: 134
KARMA_SUM: Final[int] = sum(CHAPTER_VERSES[8:12])    # Ch 9-12: 151
MOKSHA_SUM: Final[int] = sum(CHAPTER_VERSES[12:16])  # Ch 13-16: 106
FRUIT_SUM: Final[int] = sum(CHAPTER_VERSES[16:18])   # Ch 17-18: 106

# The Field (16 Guardians' domain)
FIELD_SUM: Final[int] = sum(CHAPTER_VERSES[0:16])    # Ch 1-16: 594

# =============================================================================
# THE EPOCH EQUATION (The Master Key)
# =============================================================================
# 1972 = GENESIS × NAVA + EPOCH_ADDITIVE
# 1972 = 203 × 9 + 145
# 145  = POSITION_SUM_TOTAL + NAVA = 136 + 9

EPOCH_ADDITIVE: Final[int] = POSITION_SUM_TOTAL + NAVA  # 145

assert EPOCH_KEY == GENESIS_SUM * NAVA + EPOCH_ADDITIVE, (
    f"THE EPOCH EQUATION: 1972 = {GENESIS_SUM} × {NAVA} + {EPOCH_ADDITIVE}"
)

# =============================================================================
# THE FIELD = GITA_CHAPTERS × 33 = NAVA × 66 (The Guardian Domain)
# =============================================================================
# 594 = 18 × 33 = GITA_CHAPTERS × 33
# 594 = 9 × 66 = NAVA × 66

FIELD_FACTOR: Final[int] = FIELD_SUM // GITA_CHAPTERS  # 33

assert FIELD_SUM == GITA_CHAPTERS * FIELD_FACTOR, (
    f"THE FIELD: {FIELD_SUM} = {GITA_CHAPTERS} × {FIELD_FACTOR}"
)
assert FIELD_SUM % GITA_CHAPTERS == 0, "Field must be divisible by GITA_CHAPTERS"
assert FIELD_SUM % NAVA == 0, "Field must be divisible by NAVA"
assert FIELD_SUM % SHARANAGATI == 0, "Field must be divisible by SHARANAGATI"

# =============================================================================
# MOKSHA = FRUIT (Perfect Symmetry)
# =============================================================================
# The effort (Moksha Quarter) equals the result (Fruit)

assert MOKSHA_SUM == FRUIT_SUM, f"SYMMETRY: Moksha ({MOKSHA_SUM}) = Fruit ({FRUIT_SUM})"

# =============================================================================
# EPOCH_KEY FACTORIZATION
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
