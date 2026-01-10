"""
Tests for VARNA - The Smallest Unit of Sound
=============================================
"""

import pytest
from vibe_core.protocols.substrate.mantra.varna import (
    VarnaType,
    Varna,
    SVARA,
    MATRA,
    VIRAMA,
    VYANJANA,
    KAVARGA,
    CAVARGA,
    TAVARGA,
    TAVARGA2,
    PAVARGA,
    ANTAHSTHA,
    USHMAN,
    get_varna_by_devanagari,
    get_varna_by_iast,
)


class TestVarnaStructure:
    """Test the Varna dataclass."""

    def test_varna_has_triple_encoding(self):
        """Each varna has devanagari, iast, and roman."""
        v = Varna("क", "k", "k", VarnaType.VYANJANA, 1)
        assert v.devanagari == "क"
        assert v.iast == "k"
        assert v.roman == "k"

    def test_varna_str_returns_iast(self):
        """str() returns IAST."""
        v = Varna("क", "k", "k", VarnaType.VYANJANA, 1)
        assert str(v) == "k"


class TestSvara:
    """Test vowels (svara)."""

    def test_svara_count(self):
        """There are 14 svaras (including anusvara/visarga)."""
        assert len(SVARA) == 14

    def test_basic_vowels(self):
        """Basic vowels are correct."""
        # First vowel: अ (a)
        assert SVARA[0].devanagari == "अ"
        assert SVARA[0].iast == "a"

        # Long a: आ (ā)
        assert SVARA[1].devanagari == "आ"
        assert SVARA[1].iast == "ā"

    def test_vocalic_r(self):
        """Vocalic ṛ is present (used in kṛṣṇa)."""
        ri = SVARA[6]
        assert ri.devanagari == "ऋ"
        assert ri.iast == "ṛ"


class TestVyanjana:
    """Test consonants (vyanjana)."""

    def test_total_consonants(self):
        """There are 33 consonants."""
        assert len(VYANJANA) == 33

    def test_vargas(self):
        """Each varga has 5 consonants."""
        assert len(KAVARGA) == 5   # ka-varga
        assert len(CAVARGA) == 5   # ca-varga
        assert len(TAVARGA) == 5   # ṭa-varga (retroflex)
        assert len(TAVARGA2) == 5  # ta-varga (dental)
        assert len(PAVARGA) == 5   # pa-varga

    def test_semi_vowels(self):
        """There are 4 semi-vowels (antahstha)."""
        assert len(ANTAHSTHA) == 4
        # y, r, l, v
        iasts = [v.iast for v in ANTAHSTHA]
        assert "y" in iasts
        assert "r" in iasts
        assert "l" in iasts
        assert "v" in iasts

    def test_sibilants(self):
        """There are 4 ushman (3 sibilants + 1 aspirate)."""
        assert len(USHMAN) == 4
        # ś, ṣ, s, h
        iasts = [v.iast for v in USHMAN]
        assert "ś" in iasts
        assert "ṣ" in iasts
        assert "s" in iasts
        assert "h" in iasts

    def test_ha_for_hare(self):
        """'h' (ह) is available for 'hare'."""
        h = get_varna_by_iast("h")
        assert h is not None
        assert h.devanagari == "ह"


class TestMatra:
    """Test vowel marks (matra)."""

    def test_matra_count(self):
        """There are 12 matras."""
        assert len(MATRA) == 12

    def test_e_matra_for_hare(self):
        """'e' matra (े) is available for 'hare'."""
        e_matra = None
        for m in MATRA:
            if m.iast == "e":
                e_matra = m
                break
        assert e_matra is not None
        assert e_matra.devanagari == "े"


class TestVirama:
    """Test the vowel killer."""

    def test_virama_exists(self):
        """Virama exists."""
        assert VIRAMA is not None
        assert VIRAMA.devanagari == "्"
        assert VIRAMA.varna_type == VarnaType.VIRAMA


class TestLookup:
    """Test lookup functions."""

    def test_get_by_devanagari(self):
        """Can find varna by Devanagari."""
        v = get_varna_by_devanagari("क")
        assert v is not None
        assert v.iast == "k"

    def test_get_by_iast(self):
        """Can find varna by IAST."""
        v = get_varna_by_iast("k")
        assert v is not None
        assert v.devanagari == "क"

    def test_not_found_returns_none(self):
        """Unknown character returns None."""
        assert get_varna_by_devanagari("X") is None
        assert get_varna_by_iast("zzz") is None
