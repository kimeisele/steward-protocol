"""
TEST: COSMIC_FRAME Resolution & Boundary Checks
================================================

This test ensures that the Lipta conversion logic handles the
"799-trap", circularity, and negative angles correctly.
"""

import pytest
from vibe_core.mahamantra.protocols import COSMIC_FRAME, NAKSHATRA_UNIT, TITHI_UNIT, PADA_UNIT, QUARTER_UNIT
from vibe_core.mahamantra.substrate.lipta import degree_to_lipta, lipta_to_degree


class TestResolutionIntegrity:
    """Verify constants and their relationships."""

    def test_constants_import(self):
        """Constants must be importable from the protocol package."""
        assert COSMIC_FRAME == 21600
        assert NAKSHATRA_UNIT == 800
        assert TITHI_UNIT == 720
        assert PADA_UNIT == 200
        assert QUARTER_UNIT == 5400

    def test_substrate_alignment(self):
        """Substrate/seed.py must use the SAME constants (via import)."""
        from vibe_core.mahamantra.substrate.seed import COSMIC_FRAME as S_CF, NAKSHATRA_UNIT as S_NU

        assert S_CF == COSMIC_FRAME
        assert S_NU == NAKSHATRA_UNIT


class TestLiptaConversion:
    """Verify the hardened rounding and boundary logic."""

    @pytest.mark.parametrize(
        "degrees,expected_lipta",
        [
            (0.0, 0),
            (360.0, 0),
            (720.0, 0),
            # The 799-trap: 13.333... * 60 should be EXACTLY 800
            (13.333333333333334, 800),
            (13.333333333, 800),
            # The Tithi: 12.0 * 60 = 720
            (12.0, 720),
            # The Pada: 3.333... * 60 = 200
            (3.3333333333, 200),
            # Negative angles (should wrap correctly)
            (-0.1, 21594),  # -6 minutes
            (-360.0, 0),
            (-360.1, 21594),
        ],
    )
    def test_degree_to_lipta_boundaries(self, degrees, expected_lipta):
        """Verify boundary conversion logic."""
        assert degree_to_lipta(degrees) == expected_lipta

    def test_round_trip(self):
        """Verify that conversion back to degrees works (within reason)."""
        original_degree = 13.333333333333334
        lipta = degree_to_lipta(original_degree)
        back_to_degree = lipta_to_degree(lipta)
        # 800 / 60 = 13.333...
        assert back_to_degree == pytest.approx(original_degree, rel=1e-5)

    def test_symmetry(self):
        """Verify that 0 and 360 are treated identically."""
        assert degree_to_lipta(0.0) == degree_to_lipta(360.0) == 0
