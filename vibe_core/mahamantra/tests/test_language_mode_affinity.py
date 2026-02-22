"""
Tests for substrate/language/mode_affinity.py — WordNet graph-distance classification.

Only tests what is DERIVED from protocol, not invented.
"""

import pytest

from vibe_core.mahamantra.substrate.language.mode_affinity import (
    classify_by_graph,
    mode_anchor_phrases,
)
from vibe_core.mahamantra.substrate.seed import HolyName


# =============================================================================
# mode_anchor_phrases: protocol-derived anchor phrases
# =============================================================================


class TestModeAnchorPhrases:
    """mode_anchor_phrases builds anchors from trinity functions."""

    def test_returns_dict(self):
        anchors = mode_anchor_phrases()
        assert isinstance(anchors, dict)

    def test_three_modes(self):
        anchors = mode_anchor_phrases()
        assert set(anchors.keys()) == {"DHARMA", "GENESIS", "KARMA"}

    def test_dharma_contains_hare(self):
        anchors = mode_anchor_phrases()
        assert "hare" in anchors["DHARMA"].lower()

    def test_genesis_contains_krishna(self):
        anchors = mode_anchor_phrases()
        assert "krishna" in anchors["GENESIS"].lower()

    def test_karma_contains_rama(self):
        anchors = mode_anchor_phrases()
        assert "rama" in anchors["KARMA"].lower()

    def test_all_values_are_strings(self):
        for mode, phrase in mode_anchor_phrases().items():
            assert isinstance(phrase, str)
            assert len(phrase) > 0

    def test_cached(self):
        a = mode_anchor_phrases()
        b = mode_anchor_phrases()
        assert a is b  # lru_cache


# =============================================================================
# classify_by_graph: WordNet semantic classification
# =============================================================================


class TestClassifyByGraph:
    """classify_by_graph classifies words by graph distance to anchors."""

    def test_returns_string_or_none(self):
        result = classify_by_graph("test")
        assert result is None or isinstance(result, str)

    def test_valid_mode_if_classified(self):
        result = classify_by_graph("devotion")
        if result is not None:
            assert result in ("DHARMA", "GENESIS", "KARMA")

    def test_empty_input(self):
        result = classify_by_graph("")
        # Empty string may return None (no semantic content)
        assert result is None or result in ("DHARMA", "GENESIS", "KARMA")

    def test_custom_anchors(self):
        custom = {"A": "love", "B": "war", "C": "peace"}
        result = classify_by_graph("devotion", anchors=custom)
        if result is not None:
            assert result in ("A", "B", "C")

    def test_deterministic(self):
        a = classify_by_graph("dharma")
        b = classify_by_graph("dharma")
        assert a == b
