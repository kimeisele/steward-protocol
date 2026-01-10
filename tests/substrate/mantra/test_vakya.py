"""
Tests for VAKYA - The Mantra Level
==================================
"""

import pytest
from vibe_core.protocols.substrate.mantra.vakya import (
    QuarterType,
    Quarter,
    Vakya,
    QUARTER_1,
    QUARTER_2,
    QUARTER_3,
    QUARTER_4,
    QUARTERS,
    MAHAMANTRA,
    create_vakya,
    iter_vakya_quarters,
    iter_vakya_padas,
)
from vibe_core.protocols.substrate.mantra.pada import PadaType


class TestQuarterType:
    """Test the QuarterType enum."""

    def test_four_quarter_types(self):
        """There are 4 quarter types."""
        assert QuarterType.KRISHNA_ADDRESS == 0
        assert QuarterType.KRISHNA_GLORIFY == 1
        assert QuarterType.RAMA_ADDRESS == 2
        assert QuarterType.RAMA_GLORIFY == 3


class TestQuarter:
    """Test the Quarter dataclass."""

    def test_quarter_has_4_padas(self):
        """Each quarter has 4 words."""
        assert len(QUARTER_1) == 4
        assert len(QUARTER_2) == 4
        assert len(QUARTER_3) == 4
        assert len(QUARTER_4) == 4

    def test_quarter_1_pattern(self):
        """Q1: Hare Krishna Hare Krishna."""
        types = [p.pada_type for p in QUARTER_1.padas]
        assert types == [PadaType.HARE, PadaType.KRISHNA, PadaType.HARE, PadaType.KRISHNA]

    def test_quarter_2_pattern(self):
        """Q2: Krishna Krishna Hare Hare."""
        types = [p.pada_type for p in QUARTER_2.padas]
        assert types == [PadaType.KRISHNA, PadaType.KRISHNA, PadaType.HARE, PadaType.HARE]

    def test_quarter_3_pattern(self):
        """Q3: Hare Rama Hare Rama."""
        types = [p.pada_type for p in QUARTER_3.padas]
        assert types == [PadaType.HARE, PadaType.RAMA, PadaType.HARE, PadaType.RAMA]

    def test_quarter_4_pattern(self):
        """Q4: Rama Rama Hare Hare."""
        types = [p.pada_type for p in QUARTER_4.padas]
        assert types == [PadaType.RAMA, PadaType.RAMA, PadaType.HARE, PadaType.HARE]

    def test_quarter_triple_encoding(self):
        """Quarter has triple encoding."""
        q = QUARTER_1
        assert "हरे" in q.devanagari
        assert "hare" in q.iast
        assert "hare" in q.roman

    def test_quarter_aksaras(self):
        """Quarter has 8 aksaras (4 words × 2 syllables)."""
        assert len(QUARTER_1.aksaras) == 8

    def test_quarter_iterable(self):
        """Quarter is iterable."""
        padas = list(QUARTER_1)
        assert len(padas) == 4


class TestVakya:
    """Test the Vakya (Mantra) dataclass."""

    def test_vakya_has_4_quarters(self):
        """Vakya has 4 quarters."""
        assert len(MAHAMANTRA.quarters) == 4

    def test_vakya_has_16_padas(self):
        """Vakya has 16 words."""
        assert len(MAHAMANTRA.padas) == 16
        assert MAHAMANTRA.word_count == 16

    def test_vakya_has_32_aksaras(self):
        """Vakya has 32 syllables."""
        assert len(MAHAMANTRA.aksaras) == 32
        assert MAHAMANTRA.syllable_count == 32

    def test_vakya_triple_encoding(self):
        """Vakya has complete triple encoding."""
        # Devanagari
        dev = MAHAMANTRA.devanagari
        assert "हरे" in dev
        assert "कृष्ण" in dev
        assert "राम" in dev

        # IAST
        iast = MAHAMANTRA.iast
        assert "hare" in iast
        assert "kṛṣṇa" in iast
        assert "rāma" in iast

        # Roman
        roman = MAHAMANTRA.roman
        assert "hare" in roman
        assert "krishna" in roman
        assert "raama" in roman

    def test_vakya_get_quarter(self):
        """Can get quarter by index."""
        assert MAHAMANTRA.get_quarter(0) == QUARTER_1
        assert MAHAMANTRA.get_quarter(3) == QUARTER_4

    def test_vakya_get_quarter_invalid(self):
        """Invalid quarter raises IndexError."""
        with pytest.raises(IndexError):
            MAHAMANTRA.get_quarter(4)

    def test_vakya_get_pada(self):
        """Can get pada by index."""
        assert MAHAMANTRA.get_pada(0).pada_type == PadaType.HARE
        assert MAHAMANTRA.get_pada(1).pada_type == PadaType.KRISHNA
        assert MAHAMANTRA.get_pada(15).pada_type == PadaType.HARE

    def test_vakya_get_pada_invalid(self):
        """Invalid pada index raises IndexError."""
        with pytest.raises(IndexError):
            MAHAMANTRA.get_pada(16)

    def test_vakya_iterable(self):
        """Vakya is iterable over padas."""
        padas = list(MAHAMANTRA)
        assert len(padas) == 16

    def test_vakya_length(self):
        """len(vakya) returns 16."""
        assert len(MAHAMANTRA) == 16

    def test_vakya_str_returns_iast(self):
        """str(vakya) returns IAST."""
        s = str(MAHAMANTRA)
        assert "hare" in s
        assert "kṛṣṇa" in s


class TestCreateVakya:
    """Test vakya creation."""

    def test_create_with_count(self):
        """Can create vakya with specific count."""
        v = create_vakya(42)
        assert v.count == 42

    def test_default_count_is_1(self):
        """Default count is 1."""
        v = create_vakya()
        assert v.count == 1


class TestIterators:
    """Test iteration functions."""

    def test_iter_quarters(self):
        """iter_vakya_quarters yields 4 quarters."""
        quarters = list(iter_vakya_quarters())
        assert len(quarters) == 4

    def test_iter_padas(self):
        """iter_vakya_padas yields 16 padas."""
        padas = list(iter_vakya_padas())
        assert len(padas) == 16
