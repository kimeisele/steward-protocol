"""
TESTS: fractal.py - Fractal Hierarchy Levels
=============================================

"yathā nadīnāṁ bahavo 'mbu-vegāḥ"

REAL TESTS for:
1. FractalLevel enum
2. DIMENSIONS constant
3. MAHAMANTRA_COUNTS constant
4. FRACTAL_BASE constant
"""

import pytest
from vibe_core.mahamantra.substrate.fractal import (
    FractalLevel,
    DIMENSIONS,
    MAHAMANTRA_COUNTS,
    FRACTAL_BASE,
)


# =============================================================================
# FractalLevel Enum Tests
# =============================================================================


class TestFractalLevel:
    """Test FractalLevel enum."""

    def test_fractal_level_has_6_levels(self):
        """FractalLevel has 6 levels."""
        assert len(FractalLevel) == 6

    def test_varna_is_0(self):
        """VARNA is 0 (smallest)."""
        assert FractalLevel.VARNA.value == 0

    def test_aksara_is_1(self):
        """AKSARA is 1."""
        assert FractalLevel.AKSARA.value == 1

    def test_pada_is_2(self):
        """PADA is 2."""
        assert FractalLevel.PADA.value == 2

    def test_vakya_is_3(self):
        """VAKYA is 3."""
        assert FractalLevel.VAKYA.value == 3

    def test_mala_is_4(self):
        """MALA is 4."""
        assert FractalLevel.MALA.value == 4

    def test_sadhana_is_5(self):
        """SADHANA is 5 (largest)."""
        assert FractalLevel.SADHANA.value == 5

    def test_fractal_level_is_int_enum(self):
        """FractalLevel is IntEnum."""
        from enum import IntEnum
        assert issubclass(FractalLevel, IntEnum)

    def test_fractal_levels_sequential(self):
        """FractalLevel values are sequential 0-5."""
        values = [level.value for level in FractalLevel]
        assert values == [0, 1, 2, 3, 4, 5]


# =============================================================================
# DIMENSIONS Tests
# =============================================================================


class TestDimensions:
    """Test DIMENSIONS constant."""

    def test_dimensions_exists(self):
        """DIMENSIONS exists."""
        assert DIMENSIONS is not None

    def test_dimensions_is_dict(self):
        """DIMENSIONS is a dict."""
        assert isinstance(DIMENSIONS, dict)

    def test_dimensions_has_all_levels(self):
        """DIMENSIONS has all FractalLevel keys."""
        for level in FractalLevel:
            assert level in DIMENSIONS

    def test_varna_dimension_is_50(self):
        """VARNA dimension is 50 (Sanskrit alphabet)."""
        assert DIMENSIONS[FractalLevel.VARNA] == 50

    def test_aksara_dimension_is_6(self):
        """AKSARA dimension is 6 (unique syllables)."""
        assert DIMENSIONS[FractalLevel.AKSARA] == 6

    def test_pada_dimension_is_3(self):
        """PADA dimension is 3 (Hare, Krishna, Rama)."""
        assert DIMENSIONS[FractalLevel.PADA] == 3

    def test_vakya_dimension_is_16(self):
        """VAKYA dimension is 16 (words per mantra)."""
        assert DIMENSIONS[FractalLevel.VAKYA] == 16

    def test_mala_dimension_is_108(self):
        """MALA dimension is 108 (mantras per round)."""
        assert DIMENSIONS[FractalLevel.MALA] == 108

    def test_sadhana_dimension_is_16(self):
        """SADHANA dimension is 16 (rounds minimum)."""
        assert DIMENSIONS[FractalLevel.SADHANA] == 16


# =============================================================================
# MAHAMANTRA_COUNTS Tests
# =============================================================================


class TestMahamantraCounts:
    """Test MAHAMANTRA_COUNTS constant."""

    def test_mahamantra_counts_exists(self):
        """MAHAMANTRA_COUNTS exists."""
        assert MAHAMANTRA_COUNTS is not None

    def test_mahamantra_counts_is_dict(self):
        """MAHAMANTRA_COUNTS is a dict."""
        assert isinstance(MAHAMANTRA_COUNTS, dict)

    def test_pada_count_is_16(self):
        """PADA count is 16 (words)."""
        assert MAHAMANTRA_COUNTS[FractalLevel.PADA] == 16

    def test_aksara_count_is_32(self):
        """AKSARA count is 32 (~2 per word)."""
        assert MAHAMANTRA_COUNTS[FractalLevel.AKSARA] == 32

    def test_varna_count_is_64(self):
        """VARNA count is 64 (~2 per syllable)."""
        assert MAHAMANTRA_COUNTS[FractalLevel.VARNA] == 64


# =============================================================================
# FRACTAL_BASE Tests
# =============================================================================


class TestFractalBase:
    """Test FRACTAL_BASE constant."""

    def test_fractal_base_is_37(self):
        """FRACTAL_BASE is 37 (PARAMPARA)."""
        assert FRACTAL_BASE == 37

    def test_fractal_base_is_int(self):
        """FRACTAL_BASE is int."""
        assert isinstance(FRACTAL_BASE, int)

    def test_fractal_base_is_prime(self):
        """FRACTAL_BASE (37) is prime."""
        def is_prime(n):
            if n < 2:
                return False
            for i in range(2, int(n**0.5) + 1):
                if n % i == 0:
                    return False
            return True
        assert is_prime(FRACTAL_BASE)


# =============================================================================
# Integration Tests
# =============================================================================


class TestFractalIntegration:
    """Integration tests for fractal module."""

    def test_dimensions_values_positive(self):
        """All DIMENSIONS values are positive."""
        for level, dim in DIMENSIONS.items():
            assert dim > 0, f"{level.name} dimension should be positive"

    def test_fractal_hierarchy_order(self):
        """Fractal hierarchy follows proper order."""
        # VARNA < AKSARA < PADA < VAKYA < MALA < SADHANA
        assert FractalLevel.VARNA < FractalLevel.AKSARA
        assert FractalLevel.AKSARA < FractalLevel.PADA
        assert FractalLevel.PADA < FractalLevel.VAKYA
        assert FractalLevel.VAKYA < FractalLevel.MALA
        assert FractalLevel.MALA < FractalLevel.SADHANA

    def test_mahamantra_counts_consistent(self):
        """MAHAMANTRA_COUNTS shows proper scaling."""
        # PADA (16) -> AKSARA (32) -> VARNA (64)
        # Each level roughly doubles
        assert MAHAMANTRA_COUNTS[FractalLevel.AKSARA] == 2 * MAHAMANTRA_COUNTS[FractalLevel.PADA]
        assert MAHAMANTRA_COUNTS[FractalLevel.VARNA] == 2 * MAHAMANTRA_COUNTS[FractalLevel.AKSARA]


# =============================================================================
# Module Exports Tests
# =============================================================================


class TestModuleExports:
    """Test module exports."""

    def test_all_exports(self):
        """All expected items are in __all__."""
        from vibe_core.mahamantra.substrate import fractal
        assert "FractalLevel" in fractal.__all__
        assert "DIMENSIONS" in fractal.__all__
        assert "MAHAMANTRA_COUNTS" in fractal.__all__
        assert "FRACTAL_BASE" in fractal.__all__
