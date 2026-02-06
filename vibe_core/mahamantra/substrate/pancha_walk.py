"""
PANCHA WALK - Element Walk through Sanskrit Phonemes
=====================================================

"pañca-mahā-bhūta" - The Five Great Elements

Every phoneme is produced at one of PANCHA (5) articulation points.
Each articulation point IS an element (Pancha Mahabhuta).
This mapping is from SPARSHA_GRID (Sanskrit phonetic science).

A word's phoneme sequence = a walk through the 5 elements.

WHAT IS DERIVED (from SPARSHA_GRID + phonetic tradition):
    - COORD_ELEMENT: 49 entries, each phoneme → its element
    - COORD_VARGA: 49 entries, partition into WORDS + PRASADAM + HARE_COUNT

WHAT IS NOT HERE (not yet derived from the Mantra):
    - Quality/prayatna dimension for vowels and remaining consonants
    - Anything claiming 100% uniqueness from walk alone (it's 80.7%)

The RAMA coordinate itself IS the unique identifier (0 collisions).
The element walk captures WHERE, not the full identity.
"""

from __future__ import annotations

from enum import IntEnum
from typing import Final, Sequence

from vibe_core.mahamantra.protocols._seed import (
    HARE_COUNT,
    PANCHA,
    PRASADAM,
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
    "element_walk",
    "walk_signature",
    "element_histogram",
    "dominant_element",
    "walk_direction",
    "element_transitions",
    "walk_distance",
]
