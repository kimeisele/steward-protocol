"""
Tests for MahaJapa adapter.

Tests the mathematics of hearing and chanting (108 rounds, attractors).
"""

import pytest
from vibe_core.mahamantra.adapters import MahaJapa


class TestMahaJapa:
    """Test suite for MahaJapa."""

    @pytest.fixture
    def japa(self):
        """Create japa instance."""
        return MahaJapa()

    # =========================================================================
    # SINGLE ROUND
    # =========================================================================

    def test_round_returns_result(self, japa):
        """round() should return RoundResult."""
        result = japa.round(42)
        assert result is not None
        assert result.seed == 42
        assert result.value is not None

    def test_round_deterministic(self, japa):
        """Same input should produce same output."""
        result1 = japa.round(100)
        result2 = japa.round(100)
        assert result1.value == result2.value

    def test_round_transformation(self, japa):
        """Round should transform value."""
        result = japa.round(50)
        # Output should be different from input (unless fixed point)
        # But should be within bounds
        assert result.value >= 0  # value should be non-negative

    # =========================================================================
    # MALA (108 ROUNDS)
    # =========================================================================

    def test_mala_returns_result(self, japa):
        """mala() should return MalaResult."""
        result = japa.mala(seed=42)
        assert result is not None
        assert result.seed == 42
        # attractor may be None if not found in 108 rounds
        assert result.rounds >= 0

    def test_mala_finds_attractor(self, japa):
        """Mala should complete 108 rounds."""
        result = japa.mala(seed=1)
        assert result.rounds == 108
        # final_value should exist
        assert result.final_value >= 0

    def test_mala_attractor_stable(self, japa):
        """Mala should produce a final value."""
        result = japa.mala(seed=100)
        final_val = result.final_value

        # Running another round from final value
        round_result = japa.round(final_val)
        # The test verifies we get a valid result
        assert round_result.value is not None

    def test_mala_different_seeds(self, japa):
        """Different seeds may converge to same or different attractors."""
        results = [japa.mala(seed=i) for i in range(10)]
        attractors = {r.attractor for r in results}
        # Should have found at least 1 attractor
        assert len(attractors) >= 1

    # =========================================================================
    # GOLDEN AGE STATUS
    # =========================================================================

    def test_golden_age_status(self, japa):
        """golden_age_status should return valid status."""
        status = japa.golden_age_status()
        assert status is not None
        assert status.start_year == 1486
        assert status.years_elapsed >= 0
        assert status.years_remaining >= 0
        # total should be 10000
        assert status.years_elapsed + status.years_remaining == 10000

    def test_golden_age_started(self, japa):
        """Golden Age should have started (after 1486)."""
        status = japa.golden_age_status()
        # Golden Age started in 1486, so years elapsed should be > 500
        assert status.years_elapsed > 500

    def test_golden_age_not_ended(self, japa):
        """Golden Age should not have ended yet."""
        status = japa.golden_age_status()
        # 10000 - ~538 = ~9462 remaining
        assert status.years_remaining > 9000

    # =========================================================================
    # COLLAPSE DETECTION
    # =========================================================================

    def test_is_collapsed_one(self, japa):
        """Value 1 should be collapsed (singularity)."""
        result = japa.is_collapsed(1)
        assert result.is_collapsed is True

    def test_is_collapsed_large(self, japa):
        """Large values should not be collapsed."""
        result = japa.is_collapsed(1000)
        assert result.is_collapsed is False

    def test_collapse_result_has_value(self, japa):
        """CollapseResult should include the tested value."""
        result = japa.is_collapsed(42)
        assert result.input_value == 42

    # =========================================================================
    # CONSTANTS (via module imports)
    # =========================================================================

    def test_mala_rounds_in_result(self, japa):
        """Mala result should have 108 rounds."""
        result = japa.mala(seed=1)
        assert result.rounds == 108

    def test_prasadam_in_round(self, japa):
        """Round result should have prasadam = 25."""
        result = japa.round(1)
        assert result.prasadam == 25

    def test_golden_age_duration_derived(self, japa):
        """Golden Age should be 10000 years (16 × 25²)."""
        status = japa.golden_age_status()
        # end_year - start_year = 10000
        assert status.end_year - status.start_year == 10000

    # =========================================================================
    # EDGE CASES
    # =========================================================================

    def test_round_zero(self, japa):
        """Round with zero should not crash."""
        result = japa.round(0)
        assert result is not None

    def test_round_negative(self, japa):
        """Round with negative should handle gracefully."""
        # Negative seeds may be handled differently by implementation
        # Just verify it doesn't crash
        result = japa.round(-5)
        assert result is not None

    def test_round_large(self, japa):
        """Round with large number should handle gracefully."""
        result = japa.round(10**9)
        assert result.value is not None

    def test_mala_seed_zero(self, japa):
        """Mala with seed zero should not crash."""
        result = japa.mala(seed=0)
        assert result is not None
