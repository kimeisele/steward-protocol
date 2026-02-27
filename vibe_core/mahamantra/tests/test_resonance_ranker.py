"""
RESONANCE RANKER — Multi-Dimensional Scoring Tests
====================================================

Tests the 7-dimension resonance ranking system:
- Weight integrity (sum = 1.0)
- COSMIC_FRAME-scaled weights
- RankedWord structure
- rank_words / resonate API
"""

import pytest

from vibe_core.mahamantra.substrate.encoding.resonance_ranker import (
    RankedWord,
    rank_words,
    resonate,
    resonate_coords,
)


# ============================================================================
# Weight Integrity
# ============================================================================


class TestWeights:
    """All 7 dimension weights must sum to 1.0."""

    def test_weights_sum_to_one(self):
        from vibe_core.mahamantra.substrate.encoding.resonance_ranker import (
            W_ELEMENT,
            W_HARMONIC,
            W_SHRUTI,
            W_VARGA,
            W_ATTRACTOR,
            W_HKR,
            W_PHONEME_ATTRACTOR,
        )

        total = W_ELEMENT + W_HARMONIC + W_SHRUTI + W_VARGA + W_ATTRACTOR + W_HKR + W_PHONEME_ATTRACTOR
        assert abs(total - 1.0) < 1e-6, f"Weights sum to {total}, expected 1.0"

    def test_cosmic_frame_weights_sum(self):
        from vibe_core.mahamantra.substrate.encoding.resonance_ranker import (
            W_ELEMENT_CF,
            W_HARMONIC_CF,
            W_SHRUTI_CF,
            W_VARGA_CF,
            W_ATTRACTOR_CF,
            W_HKR_CF,
            W_PHONEME_ATTRACTOR_CF,
        )

        total_cf = W_ELEMENT_CF + W_HARMONIC_CF + W_SHRUTI_CF + W_VARGA_CF + W_ATTRACTOR_CF + W_HKR_CF + W_PHONEME_ATTRACTOR_CF
        assert total_cf == 21600, f"CF weights sum to {total_cf}, expected 21600 (COSMIC_FRAME)"

    def test_float_derived_from_integer(self):
        """Float weights are CF / COSMIC_FRAME."""
        from vibe_core.mahamantra.substrate.encoding.resonance_ranker import (
            W_ELEMENT, W_ELEMENT_CF,
            W_HARMONIC, W_HARMONIC_CF,
        )

        assert abs(W_ELEMENT - W_ELEMENT_CF / 21600) < 1e-10
        assert abs(W_HARMONIC - W_HARMONIC_CF / 21600) < 1e-10

    def test_weight_ordering(self):
        """Element has highest weight, attractor has lowest."""
        from vibe_core.mahamantra.substrate.encoding.resonance_ranker import (
            W_ELEMENT, W_HARMONIC, W_SHRUTI, W_VARGA, W_ATTRACTOR,
        )

        assert W_ELEMENT > W_HARMONIC > W_SHRUTI > W_VARGA > W_ATTRACTOR


# ============================================================================
# RankedWord Structure
# ============================================================================


class TestRankedWord:
    """RankedWord must expose all 7 scores + total."""

    def test_score_breakdown_keys(self):
        """score_breakdown() returns all 7 dimensions + total."""
        # Use resonate_coords to get actual RankedWords
        results = resonate_coords([0, 7, 14, 21], top_n=1)
        if len(results) > 0:
            rw = results[0]
            breakdown = rw.score_breakdown()
            assert "total" in breakdown
            assert "element" in breakdown
            assert "harmonic" in breakdown
            assert isinstance(breakdown["total"], float)

    def test_total_score_positive(self):
        results = resonate_coords([0, 7, 14, 21], top_n=3)
        for rw in results:
            assert rw.total_score >= 0


# ============================================================================
# Ranking API
# ============================================================================


class TestRankingAPI:
    """High-level ranking functions."""

    def test_resonate_coords_returns_list(self):
        results = resonate_coords([0, 7, 14], top_n=5)
        assert isinstance(results, list)
        assert len(results) <= 5

    def test_resonate_coords_sorted_descending(self):
        results = resonate_coords([0, 7, 14, 21, 28], top_n=10)
        if len(results) > 1:
            scores = [r.total_score for r in results]
            assert scores == sorted(scores, reverse=True)

    def test_rank_words_with_coords(self):
        results = rank_words([0, 7, 14, 21], top_n=3)
        assert isinstance(results, list)
        assert len(results) <= 3

    def test_resonate_text(self):
        """resonate() accepts text input."""
        results = resonate("krishna", top_n=3)
        assert isinstance(results, list)
        assert len(results) <= 3

    def test_deterministic(self):
        """Same input → same output (no randomness)."""
        r1 = resonate_coords([0, 7, 14], top_n=5)
        r2 = resonate_coords([0, 7, 14], top_n=5)
        assert len(r1) == len(r2)
        for a, b in zip(r1, r2):
            assert abs(a.total_score - b.total_score) < 1e-10

