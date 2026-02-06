"""
Tests for PANCHA Walk - Element Walk through Sanskrit Phonemes.

Only tests what is DERIVED, not invented.
"""

import pytest

from vibe_core.mahamantra.protocols._seed import HARE_COUNT, PANCHA, PRASADAM, WORDS
from vibe_core.mahamantra.substrate.pancha_walk import (
    COORD_ELEMENT,
    COORD_VARGA,
    ELEMENT_NAMES,
    ELEMENT_SYMBOLS,
    Element,
    dominant_element,
    element_histogram,
    element_transitions,
    element_walk,
    walk_direction,
    walk_distance,
    walk_signature,
)
from vibe_core.mahamantra.substrate.rama_grid import SPARSHA_GRID, VARNAMALA_TOTAL
from vibe_core.mahamantra.substrate.varnamala_codec import encode


class TestElementMap:
    """COORD_ELEMENT: derived from SPARSHA_GRID + phonetic science."""

    def test_complete_coverage(self):
        assert len(COORD_ELEMENT) == VARNAMALA_TOTAL

    def test_all_elements_present(self):
        present = set(COORD_ELEMENT)
        assert present == set(Element)

    def test_sparsha_rows_match_grid(self):
        """Sparsha consonant elements must match SPARSHA_GRID rows."""
        for row_idx, row in enumerate(SPARSHA_GRID):
            for col_idx in range(PANCHA):
                coord = WORDS + row_idx * PANCHA + col_idx
                assert COORD_ELEMENT[coord] == Element(row_idx)

    def test_vowel_a_is_akasha(self):
        assert COORD_ELEMENT[0] == Element.AKASHA

    def test_vowel_i_is_vayu(self):
        assert COORD_ELEMENT[1] == Element.VAYU

    def test_vowel_u_is_prithvi(self):
        assert COORD_ELEMENT[2] == Element.PRITHVI

    def test_ha_is_akasha(self):
        assert COORD_ELEMENT[48] == Element.AKASHA

    def test_element_enum_is_pancha(self):
        assert len(Element) == PANCHA

    def test_symbols_unique(self):
        assert len(set(ELEMENT_SYMBOLS)) == PANCHA


class TestVargaPartition:
    """COORD_VARGA: derived from WORDS + PRASADAM + HARE_COUNT."""

    def test_svara_count(self):
        assert sum(1 for v in COORD_VARGA if v == 0) == WORDS

    def test_sparsha_count(self):
        assert sum(1 for v in COORD_VARGA if v == 1) == PRASADAM

    def test_remaining_count(self):
        assert sum(1 for v in COORD_VARGA if v == 2) == HARE_COUNT

    def test_total(self):
        assert len(COORD_VARGA) == VARNAMALA_TOTAL


class TestElementWalk:
    """element_walk() and walk_signature()."""

    def test_dharma_walk(self):
        walk = element_walk(encode("dharma"))
        assert walk == (Element.JALA, Element.AGNI, Element.PRITHVI)

    def test_walk_signature_matches(self):
        coords = encode("dharma")
        walk = element_walk(coords)
        sig = walk_signature(coords)
        assert len(sig) == len(walk)

    def test_empty_coords(self):
        assert element_walk(()) == ()
        assert walk_signature(()) == ""


class TestHistogram:
    def test_histogram_sums_to_length(self):
        coords = encode("bhagavad")
        assert sum(element_histogram(coords)) == len(coords)

    def test_histogram_length(self):
        assert len(element_histogram(encode("yoga"))) == PANCHA


class TestDominantElement:
    def test_krsna_fire_dominant(self):
        assert dominant_element(encode("kṛṣṇa")) == Element.AGNI


class TestDirection:
    def test_ascending_positive(self):
        assert walk_direction(encode("bhakti")) > 0

    def test_single_phoneme_neutral(self):
        assert walk_direction(encode("a")) == 0


class TestTransitions:
    def test_transition_count(self):
        coords = encode("dharma")
        assert len(element_transitions(coords)) == len(coords) - 1


class TestDistance:
    def test_self_distance_zero(self):
        coords = encode("dharma")
        assert walk_distance(coords, coords) == pytest.approx(0.0)

    def test_distance_symmetric(self):
        a, b = encode("dharma"), encode("bhakti")
        assert walk_distance(a, b) == pytest.approx(walk_distance(b, a))

    def test_distance_bounded(self):
        d = walk_distance(encode("dharma"), encode("yoga"))
        assert 0.0 <= d <= 1.0


class TestArchitecturalIdentities:
    def test_sparsha_element_order(self):
        expected = ("akasha", "vayu", "agni", "jala", "prithvi")
        assert tuple(row.element for row in SPARSHA_GRID) == expected

    def test_remaining_cover_all_elements(self):
        assert set(COORD_ELEMENT[c] for c in range(41, 49)) == set(Element)

    def test_vowels_cover_all_elements(self):
        assert set(COORD_ELEMENT[c] for c in range(WORDS)) == set(Element)
