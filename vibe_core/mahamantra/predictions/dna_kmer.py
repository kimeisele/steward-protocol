"""
LOTUS DNA k-mer INDEX - O(1) k-mer Counting (OPTIMIZED)
=======================================================

KEY INSIGHT: Rolling hash - encode once, shift for each new base.

PERFORMANCE:
  Counting: Uses rolling hash, NOT per-kmer encoding
  Prefix query: O(4^suffix) - scans only matching range
  Memory: 256 KB fixed for 8-mers (65536 × 4 bytes)

STRUCTURE:
  DNA = 4 bases = QUARTERS (A=0, C=1, G=2, T=3)
  2 bits per base, 8-mer = 16 bits = 65536 space = WORDS^QUARTERS
"""

from __future__ import annotations

import array
from typing import Final

from ..protocols._seed import QUARTERS, WORDS

# =============================================================================
# CONSTANTS
# =============================================================================

KMER_8_SPACE: Final[int] = 65536  # 16^4 = WORDS^QUARTERS

# Base encoding: A=0, C=1, G=2, T=3 (2 bits each)
_BASE_TO_INT: Final[list[int]] = [
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,  # 0-15
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,  # 16-31
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,  # 32-47
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,  # 48-63
    -1,
    0,
    -1,
    1,
    -1,
    -1,
    -1,
    2,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,  # 64-79: A=65, C=67, G=71
    -1,
    -1,
    -1,
    -1,
    3,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,  # 80-95: T=84
    -1,
    0,
    -1,
    1,
    -1,
    -1,
    -1,
    2,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,  # 96-111: a=97, c=99, g=103
    -1,
    -1,
    -1,
    -1,
    3,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,
    -1,  # 112-127: t=116
]

_INT_TO_BASE: Final[str] = "ACGT"
_MASK_16: Final[int] = 0xFFFF  # 16 bits


# =============================================================================
# LOTUS 8-mer INDEX (OPTIMIZED)
# =============================================================================


class Lotus8merIndex:
    """O(1) 8-mer counter using rolling hash.

    Uses array.array for C-level speed.
    Rolling hash: O(1) per base instead of O(8) per k-mer.
    """

    __slots__ = ("_counts", "_total")

    def __init__(self) -> None:
        self._counts: array.array[int] = array.array("I", [0] * KMER_8_SPACE)
        self._total: int = 0

    def count_sequence(self, sequence: str | bytes) -> int:
        """Count all 8-mers using rolling hash. O(n) total, O(1) per base."""
        if isinstance(sequence, str):
            seq = sequence.encode("ascii")
        else:
            seq = sequence

        counts = self._counts
        n = len(seq)
        if n < 8:
            return 0

        # Initial encoding of first 8 bases
        code = 0
        for i in range(8):
            b = _BASE_TO_INT[seq[i]]
            if b < 0:
                return self._count_with_invalid(seq)
            code = (code << 2) | b

        counts[code] += 1
        counted = 1

        # Rolling hash for remaining bases
        for i in range(8, n):
            b = _BASE_TO_INT[seq[i]]
            if b < 0:
                return self._count_with_invalid(seq)
            code = ((code << 2) | b) & _MASK_16
            counts[code] += 1
            counted += 1

        self._total += counted
        return counted

    def _count_with_invalid(self, seq: bytes) -> int:
        """Fallback for sequences with invalid bases (N, etc.)."""
        counts = self._counts
        n = len(seq)
        counted = 0
        i = 0

        while i <= n - 8:
            # Try to encode 8 bases
            code = 0
            valid = True
            for j in range(8):
                b = _BASE_TO_INT[seq[i + j]]
                if b < 0:
                    valid = False
                    i = i + j + 1  # Skip past invalid base
                    break
                code = (code << 2) | b

            if valid:
                counts[code] += 1
                counted += 1
                i += 1

        self._total += counted
        return counted

    def get_count(self, code: int) -> int:
        """Get count by numeric code. O(1)."""
        return self._counts[code]

    def get_count_str(self, kmer: str) -> int:
        """Get count by string. O(8) for encoding."""
        code = 0
        for c in kmer:
            code = (code << 2) | _BASE_TO_INT[ord(c)]
        return self._counts[code]

    @property
    def total(self) -> int:
        return self._total

    @property
    def unique(self) -> int:
        return sum(1 for c in self._counts if c > 0)

    def prefix_sum(self, prefix_code: int, prefix_len: int) -> int:
        """Sum counts for all k-mers with given prefix. O(4^suffix)."""
        suffix_bits = (8 - prefix_len) * 2
        suffix_count = 1 << suffix_bits
        base_code = prefix_code << suffix_bits

        total = 0
        counts = self._counts
        for i in range(suffix_count):
            total += counts[base_code + i]
        return total


# =============================================================================
# BENCHMARK
# =============================================================================


def benchmark(seq_length: int = 100000) -> None:
    """Benchmark optimized Lotus vs dict."""
    import random
    import time

    random.seed(42)
    sequence = "".join(random.choice("ACGT") for _ in range(seq_length))
    seq_bytes = sequence.encode("ascii")

    print(f"=== DNA k-mer BENCHMARK ({seq_length:,} bp) ===\n")

    # --- Lotus (optimized) ---
    lotus = Lotus8merIndex()
    start = time.perf_counter()
    lotus.count_sequence(seq_bytes)
    lotus_time = (time.perf_counter() - start) * 1000

    # --- Dict ---
    d: dict[str, int] = {}
    start = time.perf_counter()
    for i in range(len(sequence) - 7):
        kmer = sequence[i : i + 8]
        d[kmer] = d.get(kmer, 0) + 1
    dict_time = (time.perf_counter() - start) * 1000

    print("COUNTING 8-mers:")
    print(f"  Lotus: {lotus_time:.2f} ms ({lotus.unique:,} unique)")
    print(f"  Dict:  {dict_time:.2f} ms ({len(d):,} unique)")

    speedup = dict_time / lotus_time
    print(f"  → Lotus is {speedup:.1f}x {'FASTER' if speedup > 1 else 'slower'}")
    print()

    # --- Prefix query (Lotus advantage) ---
    # Find all k-mers starting with "ACGT"
    prefix = "ACGT"
    prefix_code = 0
    for c in prefix:
        prefix_code = (prefix_code << 2) | _BASE_TO_INT[ord(c)]

    start = time.perf_counter()
    lotus_sum = lotus.prefix_sum(prefix_code, len(prefix))
    lotus_prefix_time = (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    dict_sum = sum(v for k, v in d.items() if k.startswith(prefix))
    dict_prefix_time = (time.perf_counter() - start) * 1000

    print(f"PREFIX QUERY ('{prefix}*'):")
    print(f"  Lotus: {lotus_prefix_time:.3f} ms (sum={lotus_sum})")
    print(f"  Dict:  {dict_prefix_time:.3f} ms (sum={dict_sum})")

    prefix_speedup = dict_prefix_time / lotus_prefix_time
    print(f"  → Lotus is {prefix_speedup:.1f}x {'FASTER' if prefix_speedup > 1 else 'slower'}")


# Keep old names for compatibility
LotusKmerRadix = Lotus8merIndex

if __name__ == "__main__":
    benchmark()
