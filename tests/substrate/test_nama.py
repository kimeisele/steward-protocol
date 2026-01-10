"""
Tests for NAMA - The Holy Name (Triple Encoding)
=================================================

"These three words, namely Hare, Krishna and Rama,
are the transcendental seeds of the maha-mantra."
- Srila Prabhupada
"""

import pytest
from vibe_core.protocols.substrate.nama import (
    DEVANAGARI,
    IAST,
    ROMAN,
    MAHAMANTRA_DEVANAGARI,
    MAHAMANTRA_IAST,
    MAHAMANTRA_ROMAN,
    to_devanagari,
    to_iast,
    to_roman,
    encode_sequence,
    get_triple,
)


class TestEncodingTables:
    """Test the encoding lookup tables."""

    def test_devanagari_has_four_entries(self):
        """Devanagari table has HARE, KRISHNA, RAMA, VOID."""
        assert len(DEVANAGARI) == 4

    def test_iast_has_four_entries(self):
        """IAST table has four entries."""
        assert len(IAST) == 4

    def test_roman_has_four_entries(self):
        """Roman table has four entries."""
        assert len(ROMAN) == 4

    def test_hare_encodings(self):
        """HARE (index 0) has correct encodings."""
        assert DEVANAGARI[0] == "हरे"
        assert IAST[0] == "hare"
        assert ROMAN[0] == "Hare"

    def test_krishna_encodings(self):
        """KRISHNA (index 1) has correct encodings."""
        assert DEVANAGARI[1] == "कृष्ण"
        assert IAST[1] == "kṛṣṇa"
        assert ROMAN[1] == "Krishna"

    def test_rama_encodings(self):
        """RAMA (index 2) has correct encodings."""
        assert DEVANAGARI[2] == "राम"
        assert IAST[2] == "rāma"
        assert ROMAN[2] == "Rama"

    def test_void_encodings(self):
        """VOID (index 3) represents Maya/error."""
        assert DEVANAGARI[3] == "शून्य"
        assert IAST[3] == "śūnya"
        assert ROMAN[3] == "Void"


class TestEncodingFunctions:
    """Test the encoding conversion functions."""

    def test_to_devanagari(self):
        """to_devanagari converts values correctly."""
        assert to_devanagari(0) == "हरे"
        assert to_devanagari(1) == "कृष्ण"
        assert to_devanagari(2) == "राम"

    def test_to_iast(self):
        """to_iast converts with diacritics."""
        assert to_iast(0) == "hare"
        assert to_iast(1) == "kṛṣṇa"
        assert to_iast(2) == "rāma"

    def test_to_roman(self):
        """to_roman converts to Western form."""
        assert to_roman(0) == "Hare"
        assert to_roman(1) == "Krishna"
        assert to_roman(2) == "Rama"

    def test_invalid_value_returns_void(self):
        """Invalid values return VOID encoding."""
        assert to_devanagari(99) == "शून्य"
        assert to_iast(-1) == "śūnya"
        assert to_roman(100) == "Void"

    def test_get_triple(self):
        """get_triple returns all three encodings."""
        deva, iast, roman = get_triple(1)  # KRISHNA
        assert deva == "कृष्ण"
        assert iast == "kṛṣṇa"
        assert roman == "Krishna"


class TestSequenceEncoding:
    """Test encoding of sequences."""

    def test_encode_first_quarter(self):
        """Encode first quarter: HARE KRISHNA HARE KRISHNA."""
        seq = [0, 1, 0, 1]  # H K H K
        assert encode_sequence(seq, "devanagari") == "हरे कृष्ण हरे कृष्ण"
        assert encode_sequence(seq, "iast") == "hare kṛṣṇa hare kṛṣṇa"
        assert encode_sequence(seq, "roman") == "Hare Krishna Hare Krishna"

    def test_encode_full_mahamantra(self):
        """Encode full 16-word Mahamantra."""
        # H K H K K K H H H R H R R R H H
        seq = [0, 1, 0, 1, 1, 1, 0, 0, 0, 2, 0, 2, 2, 2, 0, 0]

        result_iast = encode_sequence(seq, "iast")
        expected = "hare kṛṣṇa hare kṛṣṇa kṛṣṇa kṛṣṇa hare hare hare rāma hare rāma rāma rāma hare hare"
        assert result_iast == expected

    def test_encode_with_custom_separator(self):
        """Custom separator works."""
        seq = [0, 1, 2]
        result = encode_sequence(seq, "roman", separator="-")
        assert result == "Hare-Krishna-Rama"

    def test_invalid_encoding_raises(self):
        """Invalid encoding name raises ValueError."""
        with pytest.raises(ValueError):
            encode_sequence([0, 1], "invalid_encoding")


class TestMahamantraConstants:
    """Test the complete Mahamantra constants."""

    def test_mahamantra_devanagari_format(self):
        """Devanagari Mahamantra has correct format."""
        assert "हरे कृष्ण" in MAHAMANTRA_DEVANAGARI
        assert "हरे राम" in MAHAMANTRA_DEVANAGARI
        assert "।" in MAHAMANTRA_DEVANAGARI  # Danda
        assert "॥" in MAHAMANTRA_DEVANAGARI  # Double danda

    def test_mahamantra_iast_format(self):
        """IAST Mahamantra has diacritics."""
        assert "kṛṣṇa" in MAHAMANTRA_IAST
        assert "rāma" in MAHAMANTRA_IAST
        assert "|" in MAHAMANTRA_IAST  # Separator

    def test_mahamantra_roman_format(self):
        """Roman Mahamantra is readable."""
        assert "Krishna" in MAHAMANTRA_ROMAN
        assert "Rama" in MAHAMANTRA_ROMAN
        assert "|" in MAHAMANTRA_ROMAN


class TestDiacritics:
    """Test correct Sanskrit diacritics (IAST)."""

    def test_krishna_has_retroflex_s(self):
        """Krishna has retroflex ṣ (ष)."""
        assert "ṣ" in IAST[1]  # kṛṣṇa

    def test_krishna_has_vocalic_r(self):
        """Krishna has vocalic ṛ (ऋ)."""
        assert "ṛ" in IAST[1]  # kṛṣṇa

    def test_rama_has_long_a(self):
        """Rama has long ā (आ)."""
        assert "ā" in IAST[2]  # rāma

    def test_void_has_palatal_s(self):
        """Shunya has palatal ś (श)."""
        assert "ś" in IAST[3]  # śūnya


class TestPhilosophy:
    """Test philosophical properties."""

    def test_three_transcendental_seeds(self):
        """
        'These three words, namely Hare, Krishna and Rama,
        are the transcendental seeds of the maha-mantra.'
        """
        # Only indices 0, 1, 2 are transcendental (not VOID)
        transcendental = [ROMAN[0], ROMAN[1], ROMAN[2]]
        assert transcendental == ["Hare", "Krishna", "Rama"]

    def test_hare_addresses_energy(self):
        """
        'The word Hara is the form of addressing the energy of the Lord'
        Hare is vocative of Hara.
        """
        assert IAST[0] == "hare"  # Vocative form

    def test_krishna_rama_address_lord(self):
        """
        'The words Krishna and Rama are forms of addressing the Lord Himself'
        """
        assert IAST[1] == "kṛṣṇa"
        assert IAST[2] == "rāma"
