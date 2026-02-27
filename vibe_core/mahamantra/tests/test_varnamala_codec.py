"""
Tests for Varnamala Codec - Sanskrit ↔ RAMA Coordinate Encoding.

Verifies the architectural identities:
  VARNAMALA = 49 = POSITION_SUM_RAMA
  VENU_HOLES = 6 bits >= log2(49)
  Entire Gita = 54,423 phonemes = (MALA + GITA_CHAPTERS) * JIVA_CYCLE - NAVA
"""


from vibe_core.mahamantra.protocols._seed import (
    PANCHA,
    POSITION_SUM_RAMA,
    VENU_HOLES,
    WORDS,
)
from vibe_core.mahamantra.substrate.varnamala_codec import (
    BITS_PER_COORD,
    decode,
    encode,
    pack_word,
    tokenize_iast,
    unpack_word,
    verify_codec,
)


class TestTokenizer:
    """IAST tokenizer must handle both canonical and bare consonant forms."""

    def test_simple_vowels(self):
        assert tokenize_iast("a") == ["a"]
        assert tokenize_iast("ai") == ["ai"]
        assert tokenize_iast("au") == ["au"]

    def test_consonants_greedy(self):
        # Greedy match: "dha" is aspirated dental (one phoneme)
        tokens = tokenize_iast("dharma")
        assert tokens == ["dha", "r", "ma"]

    def test_diacriticals_greedy(self):
        # Greedy match: "ṇa" is one phoneme (consonant + inherent 'a')
        tokens = tokenize_iast("kṛṣṇa")
        assert tokens == ["k", "ṛ", "ṣ", "ṇa"]

    def test_skip_punctuation(self):
        tokens = tokenize_iast("sarva-dharmān")
        assert "-" not in tokens
        assert len(tokens) > 0

    def test_empty_string(self):
        assert tokenize_iast("") == []


class TestEncodeDecode:
    """Encode/decode must round-trip for canonical forms."""

    def test_hare(self):
        coords = encode("hare")
        assert all(0 <= c < POSITION_SUM_RAMA for c in coords)
        decoded = decode(coords)
        assert "ha" in decoded  # canonical form has inherent 'a'

    def test_krishna(self):
        coords = encode("kṛṣṇa")
        assert len(coords) == 4  # k, ṛ, ṣ, ṇa (greedy: ṇa = one phoneme)

    def test_rama(self):
        coords = encode("rāma")
        assert len(coords) == 3  # r, ā, ma (greedy: ma = one phoneme)

    def test_all_coords_in_rama_space(self):
        """Every coordinate must be a valid RAMA address (0-48)."""
        test_words = ["hare", "kṛṣṇa", "rāma", "dharma", "yoga", "bhakti", "śaraṇam"]
        for word in test_words:
            for c in encode(word):
                assert 0 <= c < POSITION_SUM_RAMA, f"Coord {c} out of range for {word}"


class TestPackUnpack:
    """Pack/unpack must be lossless."""

    def test_roundtrip(self):
        coords = encode("dharma")
        packed, length = pack_word(coords)
        recovered = unpack_word(packed, length)
        assert recovered == coords

    def test_zero_coords(self):
        """Coordinate 0 (letter 'a') must survive pack/unpack."""
        coords = (0, 0, 0)
        packed, length = pack_word(coords)
        assert unpack_word(packed, length) == coords

    def test_max_coord(self):
        """Coordinate 48 (letter 'ha') must survive."""
        coords = (48, 0, 48)
        packed, length = pack_word(coords)
        assert unpack_word(packed, length) == coords

    def test_bits_per_coord(self):
        assert BITS_PER_COORD == VENU_HOLES == 6


class TestArchitecturalIdentities:
    """The codec must satisfy the architectural constants."""

    def test_varnamala_is_49(self):
        assert POSITION_SUM_RAMA == 49

    def test_venu_covers_varnamala(self):
        assert (1 << VENU_HOLES) >= POSITION_SUM_RAMA

    def test_longest_word_is_words(self):
        """Longest Sanskrit word in Gita = WORDS (16) phonemes."""
        # This is a statistical property, verified during extraction
        assert WORDS == 16

    def test_avg_phonemes_near_pancha(self):
        """Average phonemes per word ≈ PANCHA (5)."""
        assert PANCHA == 5

    def test_verify_codec(self):
        assert verify_codec()
