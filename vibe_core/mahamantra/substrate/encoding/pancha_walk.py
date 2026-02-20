"""
PANCHA WALK - Element Walk through Sanskrit Phonemes
=====================================================

"pañca-mahā-bhūta" - The Five Great Elements

FOUR DIMENSIONS — all derived from axioms (= QUARTERS = catur-vyūha):

    Dim 1 (Sthāna):    COORD_ELEMENT   — PANCHA (5) articulation → element
    Dim 2 (Varga):     COORD_VARGA     — TRINITY (3) sound classes
    Dim 3 (Prayatna):  COORD_SUB       — intra-section quality:
        Sparsha:  column = (c - WORDS) % PANCHA   → catur-vyūha + nasal (5)
        Svara:    duration type = c // PANCHA      → QUARTERS (4): short/long/compound/special
        Shesha:   class = (c - 41) // QUARTERS     → HALVES (2): antastha/ūṣman
    Dim 4 (Harmonic):  COORD_HARMONIC  — H-orbit (×SEVEN mod 49):
        Where each phoneme GOES under absorption = dissolution path

UNIQUENESS (tested on 4127 Gita words):
    3D (element+varga+sub):     99.97% (4126 unique, 3 phoneme collisions)
    4D (+harmonic):             100.00% (4127 unique, 49/49 phoneme bijection)
"""

from __future__ import annotations

from enum import IntEnum
from typing import Final, Sequence

from vibe_core.mahamantra.protocols._seed import (
    HALVES,
    HARE_COUNT,
    PANCHA,
    PRASADAM,
    QUARTERS,
    SEVEN,
    WORDS,
)
from vibe_core.mahamantra.substrate.rama_grid import (
    SPARSHA_GRID,
    VARNAMALA_TOTAL,
)

# =============================================================================
# THE FIVE ELEMENTS (derived from SPARSHA_GRID row→element mapping)
# =============================================================================


class Element(IntEnum):
    """The Pancha Mahabhuta - 5 Great Elements."""

    AKASHA = 0  # Space/Ether - kantha (throat)
    VAYU = 1  # Air - talu (palate)
    AGNI = 2  # Fire - murdha (roof of mouth)
    JALA = 3  # Water - danta (teeth)
    PRITHVI = 4  # Earth - oshtha (lips)


assert len(Element) == PANCHA

# Element names for display
ELEMENT_NAMES: Final[tuple[str, ...]] = ("akasha", "vayu", "agni", "jala", "prithvi")

# Element symbols (for compact notation, unique per element)
ELEMENT_SYMBOLS: Final[str] = "SVFWE"

# =============================================================================
# COORDINATE → ELEMENT MAP (derived from SPARSHA_GRID + phonetic science)
# =============================================================================

# Vowel articulation points (Sanskrit phonetic tradition):
#   a/ā  → kantha  → AKASHA      (coords 0, 5)
#   i/ī  → talu    → VAYU        (coords 1, 6)
#   u/ū  → oshtha  → PRITHVI     (coords 2, 7)
#   ṛ/ṝ  → murdha  → AGNI        (coords 3, 8)
#   ḷ/ḹ  → danta   → JALA        (coords 4, 9)
#   e/ai → talu    → VAYU        (coords 10, 11)
#   o/au → oshtha  → PRITHVI     (coords 12, 13)
#   ṁ    → nasal   → AKASHA      (coord 14)
#   ḥ    → visarga → AKASHA      (coord 15)

_VOWEL_ELEMENTS: Final[tuple[Element, ...]] = (
    Element.AKASHA,  # 0: a
    Element.VAYU,  # 1: i
    Element.PRITHVI,  # 2: u
    Element.AGNI,  # 3: ṛ
    Element.JALA,  # 4: ḷ
    Element.AKASHA,  # 5: ā
    Element.VAYU,  # 6: ī
    Element.PRITHVI,  # 7: ū
    Element.AGNI,  # 8: ṝ
    Element.JALA,  # 9: ḹ
    Element.VAYU,  # 10: e
    Element.VAYU,  # 11: ai
    Element.PRITHVI,  # 12: o
    Element.PRITHVI,  # 13: au
    Element.AKASHA,  # 14: ṁ
    Element.AKASHA,  # 15: ḥ
)

assert len(_VOWEL_ELEMENTS) == WORDS

# Sparsha elements: row index = element index (from SPARSHA_GRID)
_SPARSHA_ELEMENT_NAMES: Final[tuple[str, ...]] = tuple(row.element for row in SPARSHA_GRID)
assert _SPARSHA_ELEMENT_NAMES == ELEMENT_NAMES

# Remaining consonants (41-48): ya/ra/la/va/śa/ṣa/sa/ha
_REMAINING_ELEMENTS: Final[tuple[Element, ...]] = (
    Element.VAYU,  # 41: ya (talu)
    Element.AGNI,  # 42: ra (murdha)
    Element.JALA,  # 43: la (danta)
    Element.PRITHVI,  # 44: va (oshtha)
    Element.VAYU,  # 45: śa (talu)
    Element.AGNI,  # 46: ṣa (murdha)
    Element.JALA,  # 47: sa (danta)
    Element.AKASHA,  # 48: ha (kantha)
)


def _build_element_map() -> tuple[Element, ...]:
    """Build the complete RAMA coordinate → Element mapping."""
    result: list[Element] = []
    result.extend(_VOWEL_ELEMENTS)
    for row_idx in range(PANCHA):
        for _col_idx in range(PANCHA):
            result.append(Element(row_idx))
    result.extend(_REMAINING_ELEMENTS)
    assert len(result) == VARNAMALA_TOTAL
    return tuple(result)


COORD_ELEMENT: Final[tuple[Element, ...]] = _build_element_map()
assert len(COORD_ELEMENT) == VARNAMALA_TOTAL


# =============================================================================
# VARGA PARTITION (derived: WORDS + PRASADAM + HARE_COUNT = VARNAMALA)
# =============================================================================


def _build_varga_map() -> tuple[int, ...]:
    """Partition coords into 3 sound classes (svara/sparsha/shesha)."""
    result: list[int] = []
    result.extend([0] * WORDS)  # 16 svara (vowels)
    result.extend([1] * PRASADAM)  # 25 sparsha (stops)
    result.extend([2] * HARE_COUNT)  # 8 remaining
    assert len(result) == VARNAMALA_TOTAL
    return tuple(result)


COORD_VARGA: Final[tuple[int, ...]] = _build_varga_map()


# =============================================================================
# PRAYATNA / SUB-INDEX (derived intra-section quality)
# =============================================================================
# Each varga has its own quality dimension, ALL derived from coordinate structure:
#
#   Sparsha (25): column = (c - WORDS) % PANCHA
#     Col 0: unvoiced       (ka, ca, ṭa, ta, pa)      = Vāsudeva
#     Col 1: unvoiced-asp   (kha, cha, ṭha, tha, pha)  = Saṅkarṣaṇa
#     Col 2: voiced         (ga, ja, ḍa, da, ba)       = Pradyumna
#     Col 3: voiced-asp     (gha, jha, ḍha, dha, bha)  = Aniruddha
#     Col 4: nasal          (ṅa, ña, ṇa, na, ma)       = +1 = PANCHA
#
#   Svara (16): duration type = c // PANCHA (for simple), then compound/special
#     0: short   (a, i, u, ṛ, ḷ)     — coords 0-4
#     1: long    (ā, ī, ū, ṝ, ḹ)     — coords 5-9
#     2: compound (e, ai, o, au)       — coords 10-13 = QUARTERS
#     3: special  (ṁ, ḥ)              — coords 14-15 = HALVES
#
#   Shesha (8): class = (c - WORDS - PRASADAM) // QUARTERS
#     0: antastha   (ya, ra, la, va)   — semivowels = QUARTERS
#     1: ūṣman      (śa, ṣa, sa, ha)  — sibilants  = QUARTERS


def _build_sub_map() -> tuple[int, ...]:
    """Build the intra-section quality index for each coordinate."""
    result: list[int] = []

    # Svara: duration type
    for c in range(WORDS):
        if c < PANCHA * HALVES:  # 0-9: simple vowels
            result.append(c // PANCHA)  # 0=short, 1=long
        elif c < PANCHA * HALVES + QUARTERS:  # 10-13: compounds
            result.append(HALVES)  # 2
        else:  # 14-15: specials
            result.append(HALVES + 1)  # 3
    assert len(result) == WORDS

    # Sparsha: column index
    for c in range(WORDS, WORDS + PRASADAM):
        result.append((c - WORDS) % PANCHA)
    assert len(result) == WORDS + PRASADAM

    # Shesha: antastha (0) vs ūṣman (1)
    for c in range(WORDS + PRASADAM, WORDS + PRASADAM + HARE_COUNT):
        result.append((c - WORDS - PRASADAM) // QUARTERS)
    assert len(result) == VARNAMALA_TOTAL

    return tuple(result)


COORD_SUB: Final[tuple[int, ...]] = _build_sub_map()

# Verify sub-index ranges per varga
assert max(COORD_SUB[:WORDS]) == HALVES + 1  # QUARTERS sub-types for vowels
assert max(COORD_SUB[WORDS : WORDS + PRASADAM]) == PANCHA - 1  # PANCHA columns for sparsha
assert max(COORD_SUB[WORDS + PRASADAM :]) == 1  # HALVES for shesha


# =============================================================================
# HARMONIC / H-ORBIT (derived from SEVEN axiom)
# =============================================================================
# The H-operation (×SEVEN mod VARNAMALA) maps each phoneme to its
# dissolution path — where it goes under absorption (pralaya).
#
# This is the 4th dimension: not WHERE a phoneme is, but WHERE IT GOES.
# 3D (element, varga, sub) = kṣetra (the field, 46/49 unique phonemes)
# 4D + harmonic           = kṣetra + kṣetrajña (49/49 = BIJECTION)
#
# 3 phoneme-level collision pairs in 3D, ALL resolved by H-orbit:
#   ṁ(14)/ḥ(15):  H→0 / H→7   (direct absorption vs via ū)
#   e(10)/ai(11): H→21 / H→28  (ca-varga vs ṭa-varga)
#   o(12)/au(13): H→35 / H→42  (na vs ra)


COORD_HARMONIC: Final[tuple[int, ...]] = tuple((c * SEVEN) % VARNAMALA_TOTAL for c in range(VARNAMALA_TOTAL))

# Verify: 3D + harmonic is a BIJECTION on the 49 phonemes
_4d_keys = {(COORD_ELEMENT[c], COORD_VARGA[c], COORD_SUB[c], COORD_HARMONIC[c]) for c in range(VARNAMALA_TOTAL)}
assert len(_4d_keys) == VARNAMALA_TOTAL, "4D must be bijective on VARNAMALA"


# =============================================================================
# SHRUTI / NAKSHATRA PARTITION (R-operation: quadratic residues mod 49)
# =============================================================================
# R(v) = v² mod VARNAMALA. The set of residues = SHRUTIS (22 microtones).
# The complement = NAKSHATRAS (27 lunar mansions).
# Together: 22 + 27 = 49 = VARNAMALA.

_R_RESIDUES: frozenset[int] = frozenset((c * c) % VARNAMALA_TOTAL for c in range(VARNAMALA_TOTAL))

IS_SHRUTI: Final[tuple[bool, ...]] = tuple(c in _R_RESIDUES for c in range(VARNAMALA_TOTAL))

_shruti_count = sum(IS_SHRUTI)
_nakshatra_count = VARNAMALA_TOTAL - _shruti_count
assert _shruti_count == 22, f"SHRUTIS must be 22, got {_shruti_count}"
assert _nakshatra_count == 27, f"NAKSHATRAS must be 27, got {_nakshatra_count}"


# =============================================================================
# DERIVED SIGNATURE (all 3 spatial dimensions + harmonic)
# =============================================================================


def derived_signature(coords: Sequence[int]) -> str:
    """
    3D phoneme signature: element + varga + sub-index per phoneme.

    4126/4127 Gita words unique (99.97%).
    3 phoneme-level collisions (ṁ/ḥ, e/ai, o/au).
    Use full_signature() for 100% with harmonic dimension.
    """
    return "".join(f"{COORD_ELEMENT[c]}{COORD_VARGA[c]}{COORD_SUB[c]}" for c in coords)


def full_signature(coords: Sequence[int]) -> str:
    """
    4D phoneme signature: element + varga + sub + harmonic.

    Includes H-orbit (×SEVEN mod 49) as 4th dimension.
    4127/4127 Gita words unique (100.00%). 49/49 phoneme bijection.
    """
    return "".join(f"{COORD_ELEMENT[c]}{COORD_VARGA[c]}{COORD_SUB[c]}{COORD_HARMONIC[c]:02d}" for c in coords)


# =============================================================================
# ELEMENT WALK
# =============================================================================


def element_walk(coords: Sequence[int]) -> tuple[Element, ...]:
    """Convert RAMA coordinate sequence to element walk."""
    return tuple(COORD_ELEMENT[c] for c in coords)


def walk_signature(coords: Sequence[int]) -> str:
    """Compact string: S=Space, V=Vayu, F=Fire, W=Water, E=Earth."""
    return "".join(ELEMENT_SYMBOLS[COORD_ELEMENT[c]] for c in coords)


def element_histogram(coords: Sequence[int]) -> tuple[int, ...]:
    """Count per element: (akasha, vayu, agni, jala, prithvi)."""
    counts = [0] * PANCHA
    for c in coords:
        counts[COORD_ELEMENT[c]] += 1
    return tuple(counts)


def dominant_element(coords: Sequence[int]) -> Element:
    """Most frequent element in a word's walk."""
    counts = element_histogram(coords)
    return Element(counts.index(max(counts)))


def walk_direction(coords: Sequence[int]) -> int:
    """Net direction: positive = ascending (earth→space), negative = descending."""
    walk = element_walk(coords)
    if len(walk) < 2:
        return 0
    return sum(walk[i].value - walk[i + 1].value for i in range(len(walk) - 1))


def element_transitions(coords: Sequence[int]) -> tuple[tuple[Element, Element], ...]:
    """All element-to-element transitions in a walk."""
    walk = element_walk(coords)
    return tuple((walk[i], walk[i + 1]) for i in range(len(walk) - 1))


def walk_distance(coords_a: Sequence[int], coords_b: Sequence[int]) -> float:
    """Element-histogram distance, normalized to [0, 1]."""
    ha = element_histogram(coords_a)
    hb = element_histogram(coords_b)
    total_a = sum(ha) or 1
    total_b = sum(hb) or 1
    dist = sum(abs(ha[i] / total_a - hb[i] / total_b) for i in range(PANCHA))
    return dist / 2.0


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "Element",
    "ELEMENT_NAMES",
    "ELEMENT_SYMBOLS",
    "COORD_ELEMENT",
    "COORD_VARGA",
    "COORD_SUB",
    "COORD_HARMONIC",
    "IS_SHRUTI",
    "derived_signature",
    "full_signature",
    "element_walk",
    "walk_signature",
    "element_histogram",
    "dominant_element",
    "walk_direction",
    "element_transitions",
    "walk_distance",
]
