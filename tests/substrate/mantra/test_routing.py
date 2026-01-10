"""
Tests for ROUTING - Fractal Connections
========================================
"""

import pytest
from vibe_core.protocols.substrate.mantra.routing import (
    FractalLevel,
    FractalRoute,
    DIMENSIONS,
    MAHAMANTRA_COUNTS,
    route_pada_to_aksaras,
    route_index_to_pada,
    route_index_to_type,
    iter_mahamantra,
    get_fractal_path,
    QUARTER_1,
    QUARTER_2,
    QUARTER_3,
    QUARTER_4,
    QUARTERS,
    get_quarter,
    get_padas_in_quarter,
)
from vibe_core.protocols.substrate.mantra.pada import PadaType, PADA_HARE


class TestFractalLevel:
    """Test the FractalLevel enum."""

    def test_six_levels(self):
        """There are 6 fractal levels."""
        assert len(FractalLevel) == 6

    def test_level_order(self):
        """Levels are ordered from smallest to largest."""
        assert FractalLevel.VARNA < FractalLevel.AKSARA
        assert FractalLevel.AKSARA < FractalLevel.PADA
        assert FractalLevel.PADA < FractalLevel.VAKYA
        assert FractalLevel.VAKYA < FractalLevel.MALA
        assert FractalLevel.MALA < FractalLevel.SADHANA


class TestDimensions:
    """Test fractal dimensions."""

    def test_vakya_is_16(self):
        """A mantra (vakya) has 16 words."""
        assert DIMENSIONS[FractalLevel.VAKYA] == 16

    def test_mala_is_108(self):
        """A mala has 108 mantras."""
        assert DIMENSIONS[FractalLevel.MALA] == 108

    def test_sadhana_is_16(self):
        """A sadhana (session) has 16 rounds."""
        assert DIMENSIONS[FractalLevel.SADHANA] == 16


class TestRouteToAksaras:
    """Test routing from pada to aksaras."""

    def test_hare_has_two_aksaras(self):
        """HARE routes to 2 aksaras."""
        aksaras = route_pada_to_aksaras(PADA_HARE)
        assert len(aksaras) == 2
        assert aksaras[0].iast == "ha"
        assert aksaras[1].iast == "re"


class TestRouteIndexToPada:
    """Test routing from index to pada."""

    def test_index_0_is_hare(self):
        """Index 0 is HARE."""
        pada = route_index_to_pada(0)
        assert pada.pada_type == PadaType.HARE

    def test_index_1_is_krishna(self):
        """Index 1 is KRISHNA."""
        pada = route_index_to_pada(1)
        assert pada.pada_type == PadaType.KRISHNA

    def test_index_9_is_rama(self):
        """Index 9 is RAMA."""
        pada = route_index_to_pada(9)
        assert pada.pada_type == PadaType.RAMA

    def test_invalid_index_raises(self):
        """Invalid index raises IndexError."""
        with pytest.raises(IndexError):
            route_index_to_pada(16)
        with pytest.raises(IndexError):
            route_index_to_pada(-1)


class TestIterMahamantra:
    """Test iteration through the Mahamantra."""

    def test_iter_pada_level(self):
        """Iterate at pada level gives 16 items."""
        padas = list(iter_mahamantra(FractalLevel.PADA))
        assert len(padas) == 16

    def test_iter_aksara_level(self):
        """Iterate at aksara level gives ~32 items."""
        aksaras = list(iter_mahamantra(FractalLevel.AKSARA))
        assert len(aksaras) == 32  # 16 words * 2 syllables each


class TestFractalPath:
    """Test fractal path generation."""

    def test_path_has_three_levels(self):
        """Path from vakya to aksara has 3 levels."""
        path = get_fractal_path(0, 0)
        assert len(path) == 3
        assert path[0].level == FractalLevel.VAKYA
        assert path[1].level == FractalLevel.PADA
        assert path[2].level == FractalLevel.AKSARA


class TestQuarters:
    """Test quarter routing."""

    def test_four_quarters(self):
        """There are 4 quarters."""
        assert len(QUARTERS) == 4

    def test_each_quarter_has_4_indices(self):
        """Each quarter has 4 word indices."""
        assert len(QUARTER_1) == 4
        assert len(QUARTER_2) == 4
        assert len(QUARTER_3) == 4
        assert len(QUARTER_4) == 4

    def test_quarter_1_indices(self):
        """Quarter 1 is indices 0-3."""
        assert QUARTER_1 == (0, 1, 2, 3)

    def test_get_quarter_function(self):
        """get_quarter returns correct quarter."""
        assert get_quarter(0) == 0
        assert get_quarter(3) == 0
        assert get_quarter(4) == 1
        assert get_quarter(8) == 2
        assert get_quarter(12) == 3

    def test_get_padas_in_quarter(self):
        """get_padas_in_quarter returns 4 padas."""
        padas = get_padas_in_quarter(0)
        assert len(padas) == 4
        # Quarter 1: Hare Krishna Hare Krishna
        types = [p.pada_type for p in padas]
        assert types == [PadaType.HARE, PadaType.KRISHNA, PadaType.HARE, PadaType.KRISHNA]

    def test_invalid_quarter_raises(self):
        """Invalid quarter raises IndexError."""
        with pytest.raises(IndexError):
            get_padas_in_quarter(4)
