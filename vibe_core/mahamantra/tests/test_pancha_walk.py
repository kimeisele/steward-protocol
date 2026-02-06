"""
Tests for PANCHA Walk - Articulation-Based Semantic Engine.

Verifies element mapping, walk signatures, and semantic fingerprinting.
"""

import pytest

from vibe_core.mahamantra.protocols._seed import PANCHA, PRASADAM, WORDS
from vibe_core.mahamantra.substrate.pancha_walk import (
    COORD_ELEMENT,
    ELEMENT_NAMES,
    ELEMENT_SYMBOLS,
    Element,
    dominant_element,
    element_histogram,
    element_transitions,
    element_walk,
    semantic_fingerprint,
    walk_direction,
    walk_distance,
    walk_signature,
)
from vibe_core.mahamantra.substrate.rama_grid import SPARSHA_GRID, VARNAMALA_TOTAL
from vibe_core.mahamantra.substrate.varnamala_codec import encode


class TestElementMap:
    """COORD_ELEMENT must cover all 49 RAMA coordinates."""

    def test_complete_coverage(self):
        assert len(COORD_ELEMENT) == VARNAMALA_TOTAL

    def test_all_elements_present(self):
        """Every element must appear at least once."""
        present = set(COORD_ELEMENT)
        assert present == set(Element)

    def test_sparsha_rows_match_grid(self):
        """Sparsha consonant elements must match SPARSHA_GRID."""
        for row_idx, row in enumerate(SPARSHA_GRID):
            for col_idx in range(PANCHA):
                coord = WORDS + row_idx * PANCHA + col_idx
                assert COORD_ELEMENT[coord] == Element(row_idx), (
                    f"coord {coord}: expected {Element(row_idx).name}, got {COORD_ELEMENT[coord].name} (row {row.name})"
                )

    def test_vowel_a_is_akasha(self):
        """'a' (coord 0) = throat = AKASHA."""
        assert COORD_ELEMENT[0] == Element.AKASHA

    def test_vowel_i_is_vayu(self):
        """'i' (coord 1) = palate = VAYU."""
        assert COORD_ELEMENT[1] == Element.VAYU

    def test_vowel_u_is_prithvi(self):
        """'u' (coord 2) = lips = PRITHVI."""
        assert COORD_ELEMENT[2] == Element.PRITHVI

    def test_ha_is_akasha(self):
        """'ha' (coord 48) = throat = AKASHA."""
        assert COORD_ELEMENT[48] == Element.AKASHA

    def test_element_enum_is_pancha(self):
        assert len(Element) == PANCHA

    def test_symbols_length(self):
        assert len(ELEMENT_SYMBOLS) == PANCHA

    def test_symbols_unique(self):
        assert len(set(ELEMENT_SYMBOLS)) == PANCHA


class TestElementWalk:
    """element_walk() and walk_signature() correctness."""

    def test_dharma_walk(self):
        """dharma = dha(jala) + r(agni) + ma(prithvi)."""
        walk = element_walk(encode("dharma"))
        assert walk == (Element.JALA, Element.AGNI, Element.PRITHVI)

    def test_walk_signature_matches(self):
        """Signature string must match walk elements."""
        coords = encode("dharma")
        walk = element_walk(coords)
        sig = walk_signature(coords)
        assert len(sig) == len(walk)
        for i, el in enumerate(walk):
            assert sig[i] == ELEMENT_SYMBOLS[el]

    def test_empty_coords(self):
        assert element_walk(()) == ()
        assert walk_signature(()) == ""


class TestHistogram:
    """element_histogram() correctness."""

    def test_histogram_sums_to_length(self):
        coords = encode("bhagavad")
        hist = element_histogram(coords)
        assert sum(hist) == len(coords)

    def test_histogram_length(self):
        hist = element_histogram(encode("yoga"))
        assert len(hist) == PANCHA


class TestDominantElement:
    """dominant_element() picks the most frequent."""

    def test_krsna_fire_dominant(self):
        """kṛṣṇa has 3 agni phonemes (ṛ, ṣ, ṇ) = AGNI dominant."""
        assert dominant_element(encode("kṛṣṇa")) == Element.AGNI


class TestDirection:
    """walk_direction() captures ascending/descending patterns."""

    def test_ascending_positive(self):
        """bhakti ascends (earth → space → water → air)."""
        assert walk_direction(encode("bhakti")) > 0

    def test_single_phoneme_neutral(self):
        assert walk_direction(encode("a")) == 0


class TestTransitions:
    """element_transitions() pairs."""

    def test_transition_count(self):
        coords = encode("dharma")
        trans = element_transitions(coords)
        assert len(trans) == len(coords) - 1

    def test_transition_types(self):
        trans = element_transitions(encode("dharma"))
        assert all(isinstance(t, tuple) and len(t) == 2 for t in trans)
        assert all(isinstance(t[0], Element) and isinstance(t[1], Element) for t in trans)


class TestDistance:
    """walk_distance() between words."""

    def test_self_distance_zero(self):
        coords = encode("dharma")
        assert walk_distance(coords, coords) == pytest.approx(0.0)

    def test_distance_symmetric(self):
        a = encode("dharma")
        b = encode("bhakti")
        assert walk_distance(a, b) == pytest.approx(walk_distance(b, a))

    def test_distance_bounded(self):
        a = encode("dharma")
        b = encode("yoga")
        d = walk_distance(a, b)
        assert 0.0 <= d <= 1.0


class TestSemanticFingerprint:
    """Combined walk + HKR fingerprint."""

    def test_fingerprint_format(self):
        fp = semantic_fingerprint(encode("dharma"), hkr_cycles=1)
        parts = fp.split("|")
        assert len(parts) == 2
        # Walk part: only SVFWE characters
        assert all(c in ELEMENT_SYMBOLS for c in parts[0])
        # HKR part: only H/K/R characters
        assert all(c in "HKR" for c in parts[1])

    def test_fingerprint_different_words(self):
        fp1 = semantic_fingerprint(encode("dharma"))
        fp2 = semantic_fingerprint(encode("bhakti"))
        assert fp1 != fp2

    def test_multi_cycle_more_unique(self):
        """More HKR cycles should produce longer fingerprints."""
        fp1 = semantic_fingerprint(encode("dharma"), hkr_cycles=1)
        fp3 = semantic_fingerprint(encode("dharma"), hkr_cycles=3)
        assert len(fp3) > len(fp1)


class TestArchitecturalIdentities:
    """Verifiable mathematical properties."""

    def test_sparsha_element_order(self):
        """SPARSHA_GRID elements must follow PANCHA Mahabhuta order."""
        expected = ("akasha", "vayu", "agni", "jala", "prithvi")
        actual = tuple(row.element for row in SPARSHA_GRID)
        assert actual == expected

    def test_remaining_consonants_cover_all_elements(self):
        """Antastha + Ushman (coords 41-48) must touch all 5 elements."""
        remaining_elements = set(COORD_ELEMENT[c] for c in range(41, 49))
        assert remaining_elements == set(Element)

    def test_vowels_cover_all_elements(self):
        """Vowels (coords 0-15) must touch all 5 elements."""
        vowel_elements = set(COORD_ELEMENT[c] for c in range(WORDS))
        assert vowel_elements == set(Element)
