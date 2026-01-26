"""
LOTUS DNA k-mer INDEX - O(1) k-mer Counting and Lookup
======================================================

THE PROBLEM:
  - Human genome: 3 billion base pairs
  - k-mer counting: need to count all substrings of length k
  - Memory: 8.62 billion 27-mers for Panda genome (512 GB RAM!)
  - Hash collisions waste memory and slow lookups

CURRENT SOLUTIONS:
  - Hash tables: O(1) average but collisions, memory-hungry
  - Bloom filters: probabilistic, false positives
  - BWT/FM-index: complex, slow updates
  - Sparse hashing: complex minimizer schemes

LOTUS SOLUTION:
  DNA has 4 bases: A=00, C=01, G=10, T=11 (2 bits per base)
  2 bases = 4 bits = 1 Lotus level with 16 slots

  8-mer = 16 bits = 4 levels × 4 bits = PERFECT LOTUS STRUCTURE
  16-mer = 32 bits = 8 levels
  32-mer = 64 bits = 16 levels

THE MATHEMATICS:
  DNA_BASES = 4 = QUARTERS (A, C, G, T)
  BITS_PER_BASE = 2
  BASES_PER_LEVEL = 2 (so 4 bits per level)
  SLOTS_PER_LEVEL = 16 = WORDS (all 2-base combinations)

  For 8-mer:
    LEVELS = 8 / 2 = 4 = QUARTERS
    KEY_SPACE = 16^4 = 65536 = WORDS^QUARTERS

  This is NATIVE to the Lotus structure!

WHY THIS IS BETTER:
  1. No hash collisions - each k-mer has unique slot
  2. O(1) exact lookup and counting
  3. Memory-efficient for sparse data (lazy allocation)
  4. Perfect for short k-mers (8-16 bases)
  5. Range queries possible (all k-mers with prefix)
"""

from __future__ import annotations

from typing import Final

from ..protocols._seed import QUARTERS, WORDS

# =============================================================================
# CONSTANTS FROM SEED
# =============================================================================

# DNA bases map to 2 bits
DNA_BASES: Final[dict[str, int]] = {"A": 0b00, "C": 0b01, "G": 0b10, "T": 0b11}
REVERSE_BASES: Final[dict[int, str]] = {0b00: "A", 0b01: "C", 0b10: "G", 0b11: "T"}

BITS_PER_BASE: Final[int] = 2
BASES_PER_LEVEL: Final[int] = 2  # 2 bases = 4 bits per level
BITS_PER_LEVEL: Final[int] = BASES_PER_LEVEL * BITS_PER_BASE  # 4 bits

SLOTS_PER_LEVEL: Final[int] = WORDS  # 16 = 2^4 = all 2-base combinations

# 8-mer = 16 bits = 4 levels = QUARTERS
KMER_8_LEVELS: Final[int] = QUARTERS  # 4
KMER_8_SPACE: Final[int] = SLOTS_PER_LEVEL**KMER_8_LEVELS  # 65536

# Verify the mathematics
assert SLOTS_PER_LEVEL == 1 << BITS_PER_LEVEL, "16 = 2^4"
assert KMER_8_SPACE == 65536, "8-mer space = 65536"
assert KMER_8_SPACE == WORDS**QUARTERS, "8-mer space = WORDS^QUARTERS"
assert len(DNA_BASES) == QUARTERS, "4 DNA bases = QUARTERS"


# =============================================================================
# DNA ENCODING
# =============================================================================


def encode_kmer(kmer: str) -> int:
    """Encode a k-mer string to integer.

    Each base uses 2 bits: A=00, C=01, G=10, T=11
    """
    result = 0
    for base in kmer.upper():
        if base not in DNA_BASES:
            raise ValueError(f"Invalid DNA base: {base}")
        result = (result << BITS_PER_BASE) | DNA_BASES[base]
    return result


def decode_kmer(code: int, k: int) -> str:
    """Decode integer back to k-mer string."""
    bases = []
    for _ in range(k):
        bases.append(REVERSE_BASES[code & 0b11])
        code >>= BITS_PER_BASE
    return "".join(reversed(bases))


def reverse_complement(kmer: str) -> str:
    """Get reverse complement of a k-mer."""
    complement = {"A": "T", "T": "A", "C": "G", "G": "C"}
    return "".join(complement[b] for b in reversed(kmer.upper()))


# =============================================================================
# LOTUS 8-mer INDEX (Flat Array - O(1) Everything)
# =============================================================================


class Lotus8merIndex:
    """O(1) index for 8-mers (65536 possible k-mers).

    Uses flat array where k-mer encoding = index.
    Perfect for counting k-mers in sequences.

    Memory: 65536 × 4 bytes = 256 KB (fixed, small)

    Usage:
        index = Lotus8merIndex()
        index.count_sequence("ACGTACGTACGTACGT")
        print(index.get_count("ACGTACGT"))
    """

    __slots__ = ("_counts", "_total")

    def __init__(self) -> None:
        self._counts: list[int] = [0] * KMER_8_SPACE
        self._total: int = 0

    def add(self, kmer: str) -> None:
        """Add a single 8-mer to the index. O(1)."""
        if len(kmer) != 8:
            raise ValueError(f"Expected 8-mer, got {len(kmer)}-mer")
        code = encode_kmer(kmer)
        self._counts[code] += 1
        self._total += 1

    def get_count(self, kmer: str) -> int:
        """Get count of a specific 8-mer. O(1)."""
        if len(kmer) != 8:
            raise ValueError(f"Expected 8-mer, got {len(kmer)}-mer")
        code = encode_kmer(kmer)
        return self._counts[code]

    def count_sequence(self, sequence: str) -> int:
        """Count all 8-mers in a DNA sequence. O(n)."""
        sequence = sequence.upper()
        count = 0
        for i in range(len(sequence) - 7):
            kmer = sequence[i : i + 8]
            try:
                self.add(kmer)
                count += 1
            except ValueError:
                pass  # Skip invalid bases (N, etc.)
        return count

    @property
    def total_kmers(self) -> int:
        """Total number of k-mers counted."""
        return self._total

    @property
    def unique_kmers(self) -> int:
        """Number of unique k-mers observed."""
        return sum(1 for c in self._counts if c > 0)

    def get_top_kmers(self, n: int = 10) -> list[tuple[str, int]]:
        """Get the n most frequent k-mers."""
        indexed = [(decode_kmer(i, 8), c) for i, c in enumerate(self._counts) if c > 0]
        indexed.sort(key=lambda x: x[1], reverse=True)
        return indexed[:n]

    def get_kmers_with_prefix(self, prefix: str) -> list[tuple[str, int]]:
        """Get all 8-mers starting with given prefix. O(16^(8-len(prefix)))."""
        if len(prefix) > 8:
            raise ValueError("Prefix too long")

        result = []
        prefix_code = encode_kmer(prefix) << (BITS_PER_BASE * (8 - len(prefix)))
        suffix_bits = BITS_PER_BASE * (8 - len(prefix))
        suffix_count = 1 << suffix_bits

        for suffix in range(suffix_count):
            code = prefix_code | suffix
            if self._counts[code] > 0:
                result.append((decode_kmer(code, 8), self._counts[code]))

        return result


# =============================================================================
# LOTUS k-mer RADIX (Sparse, Any k)
# =============================================================================


class LotusKmerRadix:
    """Sparse k-mer index for any k using radix structure.

    Uses 4-bit levels (2 bases per level) with lazy allocation.
    Memory scales with number of unique k-mers, not k-mer space.

    For k=16: 32 bits = 8 levels
    For k=32: 64 bits = 16 levels

    Usage:
        index = LotusKmerRadix(k=16)
        index.count_sequence("ACGT" * 100)
    """

    __slots__ = ("_k", "_levels", "_root", "_total", "_unique")

    def __init__(self, k: int) -> None:
        if k % BASES_PER_LEVEL != 0:
            raise ValueError(f"k must be multiple of {BASES_PER_LEVEL}")
        self._k = k
        self._levels = k // BASES_PER_LEVEL
        self._root: list = [None] * SLOTS_PER_LEVEL
        self._total = 0
        self._unique = 0

    @staticmethod
    def _extract_nibble(code: int, level: int, total_levels: int) -> int:
        """Extract 4-bit nibble at given level."""
        shift = (total_levels - 1 - level) * BITS_PER_LEVEL
        return (code >> shift) & 0xF

    def add(self, kmer: str) -> None:
        """Add a k-mer to the index. O(k/2) = O(1) constant."""
        if len(kmer) != self._k:
            raise ValueError(f"Expected {self._k}-mer, got {len(kmer)}-mer")

        code = encode_kmer(kmer)
        node = self._root

        # Traverse/create levels
        for level in range(self._levels - 1):
            nibble = self._extract_nibble(code, level, self._levels)
            if node[nibble] is None:
                node[nibble] = [None] * SLOTS_PER_LEVEL
            node = node[nibble]

        # Final level: store count
        nibble = self._extract_nibble(code, self._levels - 1, self._levels)
        if node[nibble] is None:
            node[nibble] = 0
            self._unique += 1
        node[nibble] += 1
        self._total += 1

    def get_count(self, kmer: str) -> int:
        """Get count of a k-mer. O(k/2) = O(1) constant."""
        if len(kmer) != self._k:
            raise ValueError(f"Expected {self._k}-mer, got {len(kmer)}-mer")

        code = encode_kmer(kmer)
        node = self._root

        for level in range(self._levels - 1):
            nibble = self._extract_nibble(code, level, self._levels)
            if node[nibble] is None:
                return 0
            node = node[nibble]

        nibble = self._extract_nibble(code, self._levels - 1, self._levels)
        return node[nibble] if node[nibble] is not None else 0

    def count_sequence(self, sequence: str) -> int:
        """Count all k-mers in a sequence."""
        sequence = sequence.upper()
        count = 0
        for i in range(len(sequence) - self._k + 1):
            kmer = sequence[i : i + self._k]
            try:
                self.add(kmer)
                count += 1
            except ValueError:
                pass
        return count

    @property
    def total_kmers(self) -> int:
        return self._total

    @property
    def unique_kmers(self) -> int:
        return self._unique

    @property
    def k(self) -> int:
        return self._k


# =============================================================================
# BENCHMARK
# =============================================================================


def benchmark_kmer(seq_length: int = 100000) -> dict[str, float]:
    """Benchmark Lotus k-mer index vs dict."""
    import random
    import time

    # Generate random DNA sequence
    bases = "ACGT"
    sequence = "".join(random.choice(bases) for _ in range(seq_length))

    results: dict[str, float] = {}

    # Lotus 8-mer Index
    lotus8 = Lotus8merIndex()
    start = time.perf_counter()
    lotus8.count_sequence(sequence)
    results["lotus8_count_ms"] = (time.perf_counter() - start) * 1000
    results["lotus8_unique"] = lotus8.unique_kmers
    results["lotus8_total"] = lotus8.total_kmers

    # Lotus 16-mer Radix
    lotus16 = LotusKmerRadix(k=16)
    start = time.perf_counter()
    lotus16.count_sequence(sequence)
    results["lotus16_count_ms"] = (time.perf_counter() - start) * 1000
    results["lotus16_unique"] = lotus16.unique_kmers

    # Dict-based counter
    dict_counts: dict[str, int] = {}
    start = time.perf_counter()
    for i in range(len(sequence) - 7):
        kmer = sequence[i : i + 8]
        dict_counts[kmer] = dict_counts.get(kmer, 0) + 1
    results["dict8_count_ms"] = (time.perf_counter() - start) * 1000
    results["dict8_unique"] = len(dict_counts)

    # Lookup benchmark
    test_kmers = [sequence[i : i + 8] for i in range(0, 10000, 10)]

    start = time.perf_counter()
    for kmer in test_kmers:
        _ = lotus8.get_count(kmer)
    results["lotus8_lookup_ms"] = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    for kmer in test_kmers:
        _ = dict_counts.get(kmer, 0)
    results["dict8_lookup_ms"] = (time.perf_counter() - start) * 1000

    return results


# =============================================================================
# DEMO
# =============================================================================

if __name__ == "__main__":
    print("=== LOTUS DNA k-mer INDEX ===")
    print()
    print(f"DNA bases: {QUARTERS} = QUARTERS (A, C, G, T)")
    print(f"Bits per base: {BITS_PER_BASE}")
    print(f"Bases per level: {BASES_PER_LEVEL}")
    print(f"Slots per level: {SLOTS_PER_LEVEL} = WORDS")
    print()
    print(f"8-mer: {8 * BITS_PER_BASE} bits = {KMER_8_LEVELS} levels = QUARTERS")
    print(f"8-mer space: {KMER_8_SPACE} = WORDS^QUARTERS")
    print()

    # Demo
    index = Lotus8merIndex()

    # Count k-mers in a sequence
    test_seq = "ACGTACGTAAACCCGGGTTTACGTACGTACGT"
    print(f"Sequence: {test_seq}")
    print(f"Length: {len(test_seq)}")
    print()

    n_counted = index.count_sequence(test_seq)
    print(f"8-mers counted: {n_counted}")
    print(f"Unique 8-mers: {index.unique_kmers}")
    print()

    # Top k-mers
    print("Top 5 k-mers:")
    for kmer, count in index.get_top_kmers(5):
        print(f"  {kmer}: {count}")
    print()

    # Prefix query
    print("K-mers starting with 'ACGT':")
    for kmer, count in index.get_kmers_with_prefix("ACGT"):
        print(f"  {kmer}: {count}")
    print()

    # Benchmark
    print("=== BENCHMARK (100,000 bp sequence) ===")
    results = benchmark_kmer(100000)
    print()
    print("Counting all 8-mers:")
    print(f"  Lotus: {results['lotus8_count_ms']:.2f} ms ({results['lotus8_unique']} unique)")
    print(f"  Dict:  {results['dict8_count_ms']:.2f} ms ({results['dict8_unique']} unique)")
    print()
    print("Counting all 16-mers:")
    print(f"  Lotus Radix: {results['lotus16_count_ms']:.2f} ms ({results['lotus16_unique']} unique)")
    print()
    print("Lookup (1000 queries):")
    print(f"  Lotus: {results['lotus8_lookup_ms']:.2f} ms")
    print(f"  Dict:  {results['dict8_lookup_ms']:.2f} ms")
