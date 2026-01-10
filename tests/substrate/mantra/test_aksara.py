"""
Tests for AKSARA - The Syllable Unit
=====================================
"""

import pytest
from vibe_core.protocols.substrate.mantra.aksara import (
    Aksara,
    AKSARA_HA,
    AKSARA_RE,
    AKSARA_KRI,
    AKSARA_SHNA,
    AKSARA_RAA,
    AKSARA_MA,
    MAHAMANTRA_AKSARAS,
    HARE_AKSARAS,
    KRISHNA_AKSARAS,
    RAMA_AKSARAS,
    join_aksaras,
    get_aksara_count,
)


class TestAksaraStructure:
    """Test the Aksara dataclass."""

    def test_aksara_has_triple_encoding(self):
        """Each aksara has devanagari, iast, and roman."""
        assert AKSARA_HA.devanagari == "ह"
        assert AKSARA_HA.iast == "ha"
        assert AKSARA_HA.roman == "ha"

    def test_aksara_str_returns_iast(self):
        """str() returns IAST."""
        assert str(AKSARA_HA) == "ha"


class TestMahamantraAksaras:
    """Test the 6 unique syllables in the Mahamantra."""

    def test_six_unique_syllables(self):
        """There are 6 unique syllables."""
        assert len(MAHAMANTRA_AKSARAS) == 6

    def test_hare_syllables(self):
        """HARE = ha + re."""
        assert len(HARE_AKSARAS) == 2
        assert HARE_AKSARAS[0].iast == "ha"
        assert HARE_AKSARAS[1].iast == "re"

    def test_krishna_syllables(self):
        """KRISHNA = kṛ + ṣṇa."""
        assert len(KRISHNA_AKSARAS) == 2
        assert KRISHNA_AKSARAS[0].iast == "kṛ"
        assert KRISHNA_AKSARAS[1].iast == "ṣṇa"

    def test_rama_syllables(self):
        """RAMA = rā + ma."""
        assert len(RAMA_AKSARAS) == 2
        assert RAMA_AKSARAS[0].iast == "rā"
        assert RAMA_AKSARAS[1].iast == "ma"


class TestJoinAksaras:
    """Test syllable joining."""

    def test_join_hare_devanagari(self):
        """Join HARE syllables to Devanagari."""
        result = join_aksaras(HARE_AKSARAS, "devanagari")
        assert result == "हरे"

    def test_join_hare_iast(self):
        """Join HARE syllables to IAST."""
        result = join_aksaras(HARE_AKSARAS, "iast")
        assert result == "hare"

    def test_join_krishna_iast(self):
        """Join KRISHNA syllables to IAST."""
        result = join_aksaras(KRISHNA_AKSARAS, "iast")
        assert result == "kṛṣṇa"

    def test_join_rama_devanagari(self):
        """Join RAMA syllables to Devanagari."""
        result = join_aksaras(RAMA_AKSARAS, "devanagari")
        assert result == "राम"

    def test_invalid_encoding_raises(self):
        """Invalid encoding raises ValueError."""
        with pytest.raises(ValueError):
            join_aksaras(HARE_AKSARAS, "invalid")


class TestSyllableCounting:
    """Test syllable counting."""

    def test_hare_has_two_syllables(self):
        """HARE has 2 syllables."""
        assert get_aksara_count("hare") == 2

    def test_krishna_has_two_syllables(self):
        """KRISHNA has 2 syllables."""
        assert get_aksara_count("kṛṣṇa") == 2

    def test_rama_has_two_syllables(self):
        """RAMA has 2 syllables."""
        assert get_aksara_count("rāma") == 2
