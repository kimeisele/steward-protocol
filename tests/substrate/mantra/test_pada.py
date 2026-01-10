"""
Tests for PADA - The Word Unit
===============================
"""

import pytest
from vibe_core.protocols.substrate.mantra.pada import (
    PadaType,
    Pada,
    PADA_HARE,
    PADA_KRISHNA,
    PADA_RAMA,
    PADA_BY_TYPE,
    MAHAMANTRA_SEQUENCE,
    get_pada,
    mahamantra_to_string,
    count_padas,
)


class TestPadaType:
    """Test the PadaType enum."""

    def test_three_types(self):
        """There are 3 types + VOID."""
        assert PadaType.HARE.value == 0
        assert PadaType.KRISHNA.value == 1
        assert PadaType.RAMA.value == 2
        assert PadaType.VOID.value == 3


class TestPadaStructure:
    """Test the Pada dataclass."""

    def test_hare_triple_encoding(self):
        """HARE has correct triple encoding."""
        assert PADA_HARE.devanagari == "हरे"
        assert PADA_HARE.iast == "hare"
        assert PADA_HARE.roman == "hare"

    def test_krishna_triple_encoding(self):
        """KRISHNA has correct triple encoding."""
        assert PADA_KRISHNA.devanagari == "कृष्ण"
        assert PADA_KRISHNA.iast == "kṛṣṇa"
        assert PADA_KRISHNA.roman == "krishna"

    def test_rama_triple_encoding(self):
        """RAMA has correct triple encoding."""
        assert PADA_RAMA.devanagari == "राम"
        assert PADA_RAMA.iast == "rāma"
        assert PADA_RAMA.roman == "raama"

    def test_pada_str_returns_iast(self):
        """str() returns IAST."""
        assert str(PADA_HARE) == "hare"
        assert str(PADA_KRISHNA) == "kṛṣṇa"

    def test_pada_has_meaning(self):
        """Each pada has philosophical meaning."""
        assert len(PADA_HARE.meaning) > 0
        assert len(PADA_KRISHNA.meaning) > 0
        assert len(PADA_RAMA.meaning) > 0


class TestMahamantraSequence:
    """Test the 16-word Mahamantra sequence."""

    def test_sequence_has_16_words(self):
        """Mahamantra has 16 words."""
        assert len(MAHAMANTRA_SEQUENCE) == 16

    def test_sequence_starts_with_hare(self):
        """Mahamantra starts with HARE."""
        assert MAHAMANTRA_SEQUENCE[0].pada_type == PadaType.HARE

    def test_sequence_ends_with_hare(self):
        """Mahamantra ends with HARE."""
        assert MAHAMANTRA_SEQUENCE[15].pada_type == PadaType.HARE

    def test_quarter_1(self):
        """Quarter 1: Hare Krishna Hare Krishna."""
        q1 = MAHAMANTRA_SEQUENCE[0:4]
        types = [p.pada_type for p in q1]
        assert types == [PadaType.HARE, PadaType.KRISHNA, PadaType.HARE, PadaType.KRISHNA]

    def test_quarter_2(self):
        """Quarter 2: Krishna Krishna Hare Hare."""
        q2 = MAHAMANTRA_SEQUENCE[4:8]
        types = [p.pada_type for p in q2]
        assert types == [PadaType.KRISHNA, PadaType.KRISHNA, PadaType.HARE, PadaType.HARE]

    def test_quarter_3(self):
        """Quarter 3: Hare Rama Hare Rama."""
        q3 = MAHAMANTRA_SEQUENCE[8:12]
        types = [p.pada_type for p in q3]
        assert types == [PadaType.HARE, PadaType.RAMA, PadaType.HARE, PadaType.RAMA]

    def test_quarter_4(self):
        """Quarter 4: Rama Rama Hare Hare."""
        q4 = MAHAMANTRA_SEQUENCE[12:16]
        types = [p.pada_type for p in q4]
        assert types == [PadaType.RAMA, PadaType.RAMA, PadaType.HARE, PadaType.HARE]


class TestPadaCounts:
    """Test counting of padas."""

    def test_hare_count(self):
        """HARE appears 8 times."""
        counts = count_padas()
        assert counts["hare"] == 8

    def test_krishna_count(self):
        """KRISHNA appears 4 times."""
        counts = count_padas()
        assert counts["krishna"] == 4

    def test_rama_count(self):
        """RAMA appears 4 times."""
        counts = count_padas()
        assert counts["rama"] == 4

    def test_total_is_16(self):
        """Total is 16 words."""
        counts = count_padas()
        assert sum(counts.values()) == 16


class TestMahamantraToString:
    """Test string output of full Mahamantra."""

    def test_devanagari_output(self):
        """Devanagari output is correct."""
        result = mahamantra_to_string("devanagari")
        assert "हरे" in result
        assert "कृष्ण" in result
        assert "राम" in result

    def test_iast_output(self):
        """IAST output has diacritics."""
        result = mahamantra_to_string("iast")
        assert "kṛṣṇa" in result
        assert "rāma" in result

    def test_roman_output(self):
        """Roman output is readable."""
        result = mahamantra_to_string("roman")
        assert "krishna" in result
        assert "raama" in result

    def test_invalid_encoding_raises(self):
        """Invalid encoding raises ValueError."""
        with pytest.raises(ValueError):
            mahamantra_to_string("invalid")
