"""
TESTS: LotusBio - O(1) DNA k-mer Indexing
=========================================

"bījaṁ māṁ sarva-bhūtānāṁ viddhi pārtha sanātanam"
"Know that I am the eternal seed of all existences."
— Bhagavad Gita 7.10

These tests make LotusBio ALTAR-WORTHY.
"""

import pytest

from vibe_core.mahamantra.adapters.bio import (
    LotusBio,
    KmerResult,
    IndexStats,
    encode_kmer,
    decode_kmer,
    create_kmer_index,
    BASE_A,
    BASE_C,
    BASE_G,
    BASE_T,
    BITS_PER_BASE,
    BASES_PER_BYTE,
    DEFAULT_K,
)
from vibe_core.mahamantra.protocols._seed import QUARTERS, HALVES, HARE_COUNT


# =============================================================================
# CONSTANTS TESTS
# =============================================================================


class TestBioConstants:
    """Test constants are derived from seed."""

    def test_bits_per_base_is_halves(self):
        """BITS_PER_BASE must equal HALVES (2)."""
        assert BITS_PER_BASE == HALVES == 2

    def test_bases_per_byte_is_quarters(self):
        """BASES_PER_BYTE must equal QUARTERS (4)."""
        assert BASES_PER_BYTE == QUARTERS == 4

    def test_default_k_is_hare_count(self):
        """DEFAULT_K must equal HARE_COUNT (8)."""
        assert DEFAULT_K == HARE_COUNT == 8

    def test_base_encodings(self):
        """Base encodings are 2-bit values 0-3."""
        assert BASE_A == 0b00
        assert BASE_C == 0b01
        assert BASE_G == 0b10
        assert BASE_T == 0b11


# =============================================================================
# ENCODING FUNCTION TESTS
# =============================================================================


class TestEncodeKmer:
    """Test encode_kmer function."""

    def test_encode_single_base(self):
        """Single bases encode correctly."""
        assert encode_kmer("A") == 0b00
        assert encode_kmer("C") == 0b01
        assert encode_kmer("G") == 0b10
        assert encode_kmer("T") == 0b11

    def test_encode_two_bases(self):
        """Two bases encode correctly."""
        # AA = 00 00 = 0
        assert encode_kmer("AA") == 0b0000
        # AC = 00 01 = 1
        assert encode_kmer("AC") == 0b0001
        # GT = 10 11 = 11
        assert encode_kmer("GT") == 0b1011

    def test_encode_8mer(self):
        """8-mer encodes to 16-bit value."""
        kmer = "ACGTACGT"
        key = encode_kmer(kmer)
        # Each base is 2 bits, 8 bases = 16 bits
        assert 0 <= key < 2 ** 16

    def test_encode_lowercase(self):
        """Lowercase bases work."""
        assert encode_kmer("acgt") == encode_kmer("ACGT")

    def test_encode_uracil(self):
        """Uracil (U) encodes same as Thymine (T)."""
        assert encode_kmer("U") == encode_kmer("T")
        assert encode_kmer("ACGU") == encode_kmer("ACGT")

    def test_encode_invalid_base(self):
        """Invalid base returns -1."""
        assert encode_kmer("ACGN") == -1
        assert encode_kmer("ACGX") == -1


class TestDecodeKmer:
    """Test decode_kmer function."""

    def test_decode_single_base(self):
        """Single bases decode correctly."""
        assert decode_kmer(0b00, 1) == "A"
        assert decode_kmer(0b01, 1) == "C"
        assert decode_kmer(0b10, 1) == "G"
        assert decode_kmer(0b11, 1) == "T"

    def test_decode_8mer(self):
        """8-mer decodes correctly."""
        kmer = "ACGTACGT"
        key = encode_kmer(kmer)
        assert decode_kmer(key, 8) == kmer

    def test_roundtrip(self):
        """Encode/decode roundtrip works."""
        kmers = ["AAAAAAAA", "TTTTTTTT", "ACGTACGT", "GATTACA"]
        for kmer in kmers:
            key = encode_kmer(kmer)
            decoded = decode_kmer(key, len(kmer))
            assert decoded == kmer.upper()


# =============================================================================
# RESULT TYPE TESTS
# =============================================================================


class TestKmerResult:
    """Test KmerResult dataclass."""

    def test_create_kmer_result(self):
        """Can create KmerResult."""
        result = KmerResult(
            kmer="ACGTACGT",
            key=12345,
            count=5,
            positions=(0, 10, 20),
        )
        assert result.kmer == "ACGTACGT"
        assert result.count == 5
        assert len(result.positions) == 3


class TestIndexStats:
    """Test IndexStats dataclass."""

    def test_create_index_stats(self):
        """Can create IndexStats."""
        stats = IndexStats(
            k=8,
            key_space=65536,
            unique_kmers=100,
            total_indexed=500,
            sequence_length=507,
        )
        assert stats.k == 8
        assert stats.key_space == 65536


# =============================================================================
# LOTUS BIO INIT TESTS
# =============================================================================


class TestLotusBioInit:
    """Test LotusBio initialization."""

    def test_default_k(self):
        """Default k is 8."""
        bio = LotusBio()
        assert bio.k == 8

    def test_custom_k(self):
        """Can create with custom k."""
        bio = LotusBio(k=6)
        assert bio.k == 6

    def test_k_too_large_raises(self):
        """k > 16 raises ValueError."""
        with pytest.raises(ValueError):
            LotusBio(k=17)

    def test_key_space(self):
        """key_space is 4^k."""
        bio = LotusBio(k=8)
        assert bio.key_space == 4 ** 8 == 65536

        bio = LotusBio(k=4)
        assert bio.key_space == 4 ** 4 == 256


# =============================================================================
# INDEXING TESTS
# =============================================================================


class TestLotusBioIndexing:
    """Test indexing methods."""

    @pytest.fixture
    def bio(self) -> LotusBio:
        """Create 8-mer index."""
        return LotusBio(k=8)

    def test_index_single_kmer(self, bio: LotusBio):
        """Can index single k-mer."""
        result = bio.index_kmer("ACGTACGT", position=0)
        assert result is True
        assert bio.count("ACGTACGT") == 1

    def test_index_wrong_length_fails(self, bio: LotusBio):
        """Wrong length k-mer returns False."""
        result = bio.index_kmer("ACGT", position=0)  # 4-mer, not 8-mer
        assert result is False

    def test_index_invalid_base_fails(self, bio: LotusBio):
        """Invalid base returns False."""
        result = bio.index_kmer("ACGTACGN", position=0)  # N is invalid
        assert result is False

    def test_index_sequence(self, bio: LotusBio):
        """Can index entire sequence."""
        sequence = "ACGTACGTACGTACGT"  # 16 bases = 9 8-mers
        indexed = bio.index_sequence(sequence)
        assert indexed == 9

    def test_index_tracks_positions(self, bio: LotusBio):
        """index_sequence tracks positions."""
        sequence = "ACGTACGTACGTACGT"
        bio.index_sequence(sequence)

        # First k-mer appears at positions 0 and 8
        positions = bio.find("ACGTACGT")
        assert 0 in positions
        assert 8 in positions


# =============================================================================
# QUERYING TESTS
# =============================================================================


class TestLotusBioQuerying:
    """Test query methods."""

    @pytest.fixture
    def indexed_bio(self) -> LotusBio:
        """Create and index a sequence."""
        bio = LotusBio(k=8)
        bio.index_sequence("ACGTACGTAAAAAAAA")
        return bio

    def test_count_existing(self, indexed_bio: LotusBio):
        """count() returns correct count."""
        assert indexed_bio.count("ACGTACGT") == 1
        assert indexed_bio.count("AAAAAAAA") == 1

    def test_count_not_found(self, indexed_bio: LotusBio):
        """count() returns 0 for not found."""
        assert indexed_bio.count("TTTTTTTT") == 0

    def test_count_wrong_length(self, indexed_bio: LotusBio):
        """count() returns 0 for wrong length."""
        assert indexed_bio.count("ACGT") == 0

    def test_find_positions(self, indexed_bio: LotusBio):
        """find() returns positions."""
        positions = indexed_bio.find("ACGTACGT")
        assert isinstance(positions, tuple)

    def test_find_not_found(self, indexed_bio: LotusBio):
        """find() returns empty tuple for not found."""
        positions = indexed_bio.find("TTTTTTTT")
        assert positions == ()

    def test_query_returns_kmer_result(self, indexed_bio: LotusBio):
        """query() returns KmerResult."""
        result = indexed_bio.query("ACGTACGT")
        assert isinstance(result, KmerResult)
        assert result.kmer == "ACGTACGT"
        assert result.count > 0

    def test_contains(self, indexed_bio: LotusBio):
        """__contains__ works."""
        assert "ACGTACGT" in indexed_bio
        assert "TTTTTTTT" not in indexed_bio

    def test_getitem(self, indexed_bio: LotusBio):
        """__getitem__ returns count."""
        assert indexed_bio["ACGTACGT"] == 1
        assert indexed_bio["TTTTTTTT"] == 0


# =============================================================================
# STATS TESTS
# =============================================================================


class TestLotusBioStats:
    """Test stats and reset."""

    def test_stats_empty(self):
        """stats() on empty index."""
        bio = LotusBio(k=8)
        stats = bio.stats()

        assert isinstance(stats, IndexStats)
        assert stats.k == 8
        assert stats.unique_kmers == 0
        assert stats.total_indexed == 0

    def test_stats_after_indexing(self):
        """stats() after indexing."""
        bio = LotusBio(k=8)
        bio.index_sequence("ACGTACGTACGTACGT")

        stats = bio.stats()
        assert stats.total_indexed > 0
        assert stats.sequence_length == 16

    def test_reset(self):
        """reset() clears index."""
        bio = LotusBio(k=8)
        bio.index_sequence("ACGTACGT")
        assert bio.count("ACGTACGT") > 0

        bio.reset()
        assert bio.count("ACGTACGT") == 0
        assert bio.unique_kmers == 0


# =============================================================================
# FACTORY FUNCTION TESTS
# =============================================================================


class TestCreateKmerIndex:
    """Test factory function."""

    def test_create_default(self):
        """create_kmer_index() creates default index."""
        bio = create_kmer_index()
        assert isinstance(bio, LotusBio)
        assert bio.k == 8

    def test_create_custom_k(self):
        """create_kmer_index() accepts k."""
        bio = create_kmer_index(k=6)
        assert bio.k == 6


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


class TestLotusBioIntegration:
    """Integration tests for LotusBio."""

    def test_realistic_sequence(self):
        """Index and query realistic DNA."""
        bio = LotusBio(k=8)

        # A simple gene-like sequence
        sequence = "ATGACGTACGTACGTACGTACGTACGTTAA"
        bio.index_sequence(sequence)

        # Should be able to find repeated patterns
        stats = bio.stats()
        assert stats.total_indexed == len(sequence) - 8 + 1

    def test_repeated_kmers(self):
        """Correctly counts repeated k-mers."""
        bio = LotusBio(k=4)

        # ACGT repeated multiple times
        sequence = "ACGTACGTACGTACGT"
        bio.index_sequence(sequence)

        # ACGT should appear multiple times
        assert bio.count("ACGT") > 1

    def test_complementary_strands(self):
        """Can index forward and reverse complement."""
        bio = LotusBio(k=4)

        forward = "ACGT"
        reverse = "ACGT"  # ACGT is self-complementary

        bio.index_kmer(forward, 0)
        bio.index_kmer(reverse, 0)

        # Both indexed
        assert bio.count("ACGT") == 2

    def test_unique_kmers_property(self):
        """unique_kmers tracks distinct k-mers."""
        bio = LotusBio(k=4)

        # Index same k-mer multiple times
        bio.index_kmer("ACGT", 0)
        bio.index_kmer("ACGT", 4)
        bio.index_kmer("AAAA", 8)

        # Only 2 unique k-mers
        assert bio.unique_kmers == 2

    def test_various_k_values(self):
        """Works with various k values."""
        for k in [4, 6, 8, 10, 12]:
            bio = LotusBio(k=k)
            kmer = "A" * k
            bio.index_kmer(kmer, 0)
            assert bio.count(kmer) == 1
