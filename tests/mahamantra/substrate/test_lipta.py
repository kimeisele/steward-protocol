"""
TESTS: lipta.py - High-Resolution Degree to Lipta Conversion
=============================================================

"liptāḥ kalāḥ" - The minutes of arc.

REAL TESTS for:
1. degree_to_lipta conversion
2. lipta_to_degree conversion
3. Circularity (360 -> 0)
4. The 799-trap (floating point precision)
5. Negative degree handling
"""

import pytest
from vibe_core.mahamantra.substrate.lipta import (
    degree_to_lipta,
    lipta_to_degree,
    get_lipta_name,
)
from vibe_core.mahamantra.protocols._seed import COSMIC_FRAME


class TestLiptaConstants:
    """Test that Lipta constants are correctly set."""

    def test_cosmic_frame_is_21600(self):
        """COSMIC_FRAME = 360 * 60 = 21600 Lipta."""
        assert COSMIC_FRAME == 21600
        assert COSMIC_FRAME == 360 * 60

    def test_get_lipta_name(self):
        """get_lipta_name returns 'Lipta'."""
        assert get_lipta_name() == "Lipta"


class TestDegreeToLipta:
    """Test degree_to_lipta conversion."""

    def test_zero_degrees(self):
        """0 degrees = 0 Lipta."""
        assert degree_to_lipta(0.0) == 0

    def test_one_degree(self):
        """1 degree = 60 Lipta."""
        assert degree_to_lipta(1.0) == 60

    def test_half_degree(self):
        """0.5 degrees = 30 Lipta."""
        assert degree_to_lipta(0.5) == 30

    def test_90_degrees(self):
        """90 degrees = 5400 Lipta."""
        assert degree_to_lipta(90.0) == 5400

    def test_180_degrees(self):
        """180 degrees = 10800 Lipta."""
        assert degree_to_lipta(180.0) == 10800

    def test_360_degrees_wraps_to_zero(self):
        """360 degrees wraps to 0 (circularity)."""
        assert degree_to_lipta(360.0) == 0

    def test_720_degrees_wraps_to_zero(self):
        """720 degrees (2 full rotations) wraps to 0."""
        assert degree_to_lipta(720.0) == 0

    def test_361_degrees_wraps_to_60(self):
        """361 degrees wraps to 60 Lipta (1 degree)."""
        assert degree_to_lipta(361.0) == 60

    def test_negative_degree_wraps_correctly(self):
        """Negative degrees wrap correctly (Python % handles this)."""
        # -1 degree = 359 degrees = 21540 Lipta
        result = degree_to_lipta(-1.0)
        assert result == COSMIC_FRAME - 60  # 21540

    def test_negative_0_1_degree(self):
        """Test -0.1 degree wraps to near 360."""
        # -0.1 degrees = 359.9 degrees = round(359.9 * 60) = 21594 Lipta
        result = degree_to_lipta(-0.1)
        expected = COSMIC_FRAME - 6  # 21600 - 6 = 21594
        assert result == expected


class TestThe799Trap:
    """Test the floating point precision trap (13.333... * 60 = 799.999...)."""

    def test_13_333_degrees(self):
        """13.333... degrees should give exactly 800 Lipta, not 799."""
        # This is the 799-trap: 13.333... * 60 = 799.999...
        # Without round(), int() would give 799
        degrees = 40.0 / 3.0  # 13.333...
        result = degree_to_lipta(degrees)
        assert result == 800, f"799-trap! Got {result} instead of 800"

    def test_one_third_degree(self):
        """1/3 degree should give 20 Lipta."""
        # 1/3 * 60 = 19.999... -> should round to 20
        degrees = 1.0 / 3.0
        result = degree_to_lipta(degrees)
        assert result == 20

    def test_two_thirds_degree(self):
        """2/3 degree should give 40 Lipta."""
        # 2/3 * 60 = 39.999... -> should round to 40
        degrees = 2.0 / 3.0
        result = degree_to_lipta(degrees)
        assert result == 40

    def test_precision_stability(self):
        """Multiple conversions should be stable."""
        for i in range(1, 100):
            degrees = i / 7.0  # Repeating decimal
            lipta = degree_to_lipta(degrees)
            # Must be in valid range
            assert 0 <= lipta < COSMIC_FRAME


class TestLiptaToDegree:
    """Test lipta_to_degree conversion."""

    def test_zero_lipta(self):
        """0 Lipta = 0.0 degrees."""
        assert lipta_to_degree(0) == 0.0

    def test_60_lipta(self):
        """60 Lipta = 1.0 degree."""
        assert lipta_to_degree(60) == 1.0

    def test_30_lipta(self):
        """30 Lipta = 0.5 degrees."""
        assert lipta_to_degree(30) == 0.5

    def test_5400_lipta(self):
        """5400 Lipta = 90.0 degrees."""
        assert lipta_to_degree(5400) == 90.0

    def test_cosmic_frame_wraps_to_zero(self):
        """COSMIC_FRAME Lipta wraps to 0.0 degrees."""
        assert lipta_to_degree(COSMIC_FRAME) == 0.0

    def test_negative_lipta_wraps(self):
        """Negative Lipta wraps correctly."""
        # -60 Lipta = 21540 Lipta = 359 degrees
        result = lipta_to_degree(-60)
        assert result == 359.0


class TestRoundTrip:
    """Test degree -> lipta -> degree round trips."""

    def test_whole_degrees_round_trip(self):
        """Whole degrees round-trip perfectly."""
        for deg in range(0, 360):
            lipta = degree_to_lipta(float(deg))
            back = lipta_to_degree(lipta)
            assert back == float(deg), f"Round trip failed for {deg}"

    def test_half_degrees_round_trip(self):
        """Half degrees round-trip perfectly."""
        for deg in range(0, 720):
            half_deg = deg / 2.0
            lipta = degree_to_lipta(half_deg)
            back = lipta_to_degree(lipta)
            expected = half_deg % 360.0
            assert abs(back - expected) < 0.0001, f"Round trip failed for {half_deg}"


class TestEdgeCases:
    """Test edge cases."""

    def test_very_small_positive(self):
        """Very small positive degree."""
        result = degree_to_lipta(0.001)
        # 0.001 * 60 = 0.06 -> rounds to 0
        assert result == 0

    def test_threshold_for_one_lipta(self):
        """Minimum degree for 1 Lipta."""
        # 1/60 = 0.01666... degrees per Lipta
        # Need >= 0.5/60 = 0.00833... to round up to 1
        result = degree_to_lipta(0.009)  # Just above threshold
        assert result == 1

    def test_just_below_threshold(self):
        """Just below threshold stays at 0."""
        result = degree_to_lipta(0.008)  # Just below threshold
        assert result == 0

    def test_max_lipta_value(self):
        """Maximum valid Lipta is COSMIC_FRAME - 1."""
        # 359.99... degrees
        result = degree_to_lipta(359.99)
        assert result == COSMIC_FRAME - 1  # 21599
