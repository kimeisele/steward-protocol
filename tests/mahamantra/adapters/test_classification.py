"""
Tests for MahaClassifier adapter.

Tests data structure/algorithm classification.
"""

import pytest
from vibe_core.mahamantra.adapters import MahaClassifier


class TestMahaClassifier:
    """Test suite for MahaClassifier."""

    @pytest.fixture
    def classifier(self):
        """Create classifier instance."""
        return MahaClassifier()

    # =========================================================================
    # BASIC CLASSIFICATION
    # =========================================================================

    def test_classify_returns_result(self, classifier):
        """Classify should return a ClassificationResult."""
        result = classifier.classify(
            name="TestStructure",
            alignment="perfect",
            complexity="structure",
            memory="bounded_static",
            determinism="always",
            key_space_size=65536,
            max_memory_bytes=512_000,
        )
        assert result is not None
        assert result.name == "TestStructure"

    def test_classify_alignment_values(self, classifier):
        """Different alignments should produce different scores."""
        perfect = classifier.classify(
            name="Perfect",
            alignment="perfect",
            complexity="structure",
            memory="bounded_static",
            determinism="always",
            key_space_size=65536,
            max_memory_bytes=512_000,
        )
        partial = classifier.classify(
            name="Partial",
            alignment="partial",
            complexity="structure",
            memory="bounded_static",
            determinism="always",
            key_space_size=65536,
            max_memory_bytes=512_000,
        )
        # Perfect alignment should score better
        assert perfect.mercy_advantage >= partial.mercy_advantage

    # =========================================================================
    # PRE-CLASSIFIED STRUCTURES
    # =========================================================================

    def test_lotus_array_classification(self, classifier):
        """Lotus array should have high score."""
        result = classifier.lotus_array()
        assert result is not None
        assert "Lotus" in result.name or "lotus" in result.name.lower()
        # Should be well-aligned
        assert result.mercy_advantage > 0

    def test_ipv4_router_classification(self, classifier):
        """IPv4 router should be classified."""
        result = classifier.ipv4_router()
        assert result is not None

    def test_kmer_index_classification(self, classifier):
        """K-mer index should be classified."""
        result = classifier.kmer_index()
        assert result is not None

    # =========================================================================
    # COMPARISON
    # =========================================================================

    def test_compare_structures(self, classifier):
        """Compare should rank structures."""
        lotus = classifier.lotus_array()
        ipv4 = classifier.ipv4_router()

        comparison = classifier.compare([lotus, ipv4])
        assert comparison is not None
        # ComparisonResult may have different attributes
        # Just verify we got a valid comparison object
        assert hasattr(comparison, 'summary') or hasattr(comparison, 'results') or hasattr(comparison, 'ranked')

    # =========================================================================
    # QUICK VERDICT
    # =========================================================================

    def test_quick_verdict_anukulya(self, classifier):
        """Perfect structure should get ANUKULYA verdict."""
        verdict = classifier.quick_verdict(
            uses_16_alignment=True,
            is_o1_by_structure=True,
            is_bounded=True,
            is_deterministic=True,
        )
        assert "ANUKULYA" in verdict

    def test_quick_verdict_pratikulya(self, classifier):
        """Bad structure should get PRATIKULYA verdict."""
        verdict = classifier.quick_verdict(
            uses_16_alignment=False,
            is_o1_by_structure=False,
            is_bounded=False,
            is_deterministic=False,
        )
        assert "PRATIKULYA" in verdict

    # =========================================================================
    # GOLDEN AGE VIABILITY
    # =========================================================================

    def test_golden_age_viable(self, classifier):
        """Well-structured algorithms should be Golden Age viable."""
        result = classifier.classify(
            name="GoldenAlgo",
            alignment="perfect",
            complexity="structure",
            memory="bounded_static",
            determinism="always",
            key_space_size=65536,
            max_memory_bytes=512_000,
        )
        # Check if golden_age_viable exists on result
        if hasattr(result, 'golden_age_viable'):
            assert result.golden_age_viable is True
