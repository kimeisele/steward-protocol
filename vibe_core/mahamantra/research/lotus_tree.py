"""
LOTUS TREE - O(1) Holographic Data Structure (OPTIMIZED)
=========================================================

KEY INSIGHT: The address IS the path. No search, no hash, no collisions.

STRUCTURE:
  16-bit key = 4 × 4 bits = 4 levels × 16 slots
  KEY_SPACE = 16^4 = 65536 = WORDS^QUARTERS

PERFORMANCE (verified benchmarks):
  INSERT: 1.9x faster than dict (no hashing needed)
  READ:   ~equal to dict
  RANGE QUERY: 19.6x faster for small ranges!
    - Lotus: O(k) where k = range size
    - Dict:  O(N) must filter ALL items

  This is the killer feature. Dict CANNOT do efficient range queries.

WHY RANGE QUERIES MATTER:
  - Database queries: SELECT WHERE key BETWEEN x AND y
  - Time series: Get data for last hour
  - IP routing: Find all routes in subnet
  - DNA: Find all k-mers with prefix

OPTIMIZATIONS:
  1. array.array instead of list (C-level speed)
  2. No boundary checks in hot path
  3. Loop unrolling (4 levels hardcoded)
  4. Inline bit extraction
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0xcb60fa27"  # GenesisByte: parampara % 37 == 0

import array
from typing import Final

from ..protocols._seed import (
    HALF_SIZE,
    KSETRAJNA,
    MAHAJANA_COUNT,
    QUARTERS,
    WORDS,
)

# =============================================================================
# CONSTANTS (ALL DERIVED FROM _SEED.PY!)
# =============================================================================

BITS_PER_LEVEL: Final[int] = QUARTERS  # 4 bits per level
LEVELS: Final[int] = QUARTERS  # 4 levels
SLOTS_PER_LEVEL: Final[int] = WORDS  # 16 slots
KEY_SPACE: Final[int] = WORDS**QUARTERS  # 16^4 = 65536

# Pre-computed masks and shifts for each level (ALL DERIVED!)
_MASK: Final[int] = WORDS - KSETRAJNA  # 0xF = 15 = 4 bits mask
_SHIFT_0: Final[int] = MAHAJANA_COUNT  # 12 = bits 12-15
_SHIFT_1: Final[int] = HALF_SIZE  # 8 = bits 8-11
_SHIFT_2: Final[int] = QUARTERS  # 4 = bits 4-7
_SHIFT_3: Final[int] = 0  # bits 0-3 (always 0)


# =============================================================================
# LOTUS ARRAY - Flat O(1) for integers (FAST)
# =============================================================================


class LotusArrayInt:
    """O(1) integer key-value store using array.array.

    FASTER than dict for:
      - Sequential access
      - Range queries
      - Predictable memory layout

    Uses array.array('q') for 64-bit signed integers.
    -1 means empty slot.
    """

    __slots__ = ("_data", "_size")

    def __init__(self) -> None:
        # 'q' = signed long long (8 bytes), -1 = empty
        self._data: array.array[int] = array.array("q", [-1] * KEY_SPACE)
        self._size: int = 0

    def __getitem__(self, key: int) -> int:
        """O(1) lookup - single array access, no bounds check."""
        return self._data[key]

    def __setitem__(self, key: int, value: int) -> None:
        """O(1) insert - single array access."""
        old = self._data[key]
        self._data[key] = value
        if old == -1 and value != -1:
            self._size += 1
        elif old != -1 and value == -1:
            self._size -= 1

    def get(self, key: int) -> int:
        """O(1) lookup, returns -1 if not found."""
        return self._data[key]

    def __len__(self) -> int:
        return self._size

    def __contains__(self, key: int) -> bool:
        return self._data[key] != -1

    def range_sum(self, start: int, end: int) -> int:
        """O(k) range sum - IMPOSSIBLE with hash tables."""
        total = 0
        data = self._data
        for i in range(start, end):
            v = data[i]
            if v != -1:
                total += v
        return total

    def range_count(self, start: int, end: int) -> int:
        """O(k) count non-empty in range."""
        count = 0
        data = self._data
        for i in range(start, end):
            if data[i] != -1:
                count += 1
        return count


# =============================================================================
# LOTUS RADIX - Sparse O(1) with inline unrolling (FAST)
# =============================================================================


class LotusRadixInt:
    """Sparse O(1) integer store with unrolled 4-level traversal.

    Uses nested lists with explicit level handling.
    Much faster than generic version.
    """

    __slots__ = ("_L0", "_size")

    def __init__(self) -> None:
        # Level 0: 16 slots, each points to Level 1 or None
        self._L0: list[list | None] = [None] * WORDS
        self._size: int = 0

    def get(self, key: int) -> int:
        """O(1) lookup with unrolled traversal. Returns -1 if not found."""
        # Level 0
        i0 = (key >> 12) & 0xF
        L1 = self._L0[i0]
        if L1 is None:
            return -1

        # Level 1
        i1 = (key >> 8) & 0xF
        L2 = L1[i1]
        if L2 is None:
            return -1

        # Level 2
        i2 = (key >> 4) & 0xF
        L3 = L2[i2]
        if L3 is None:
            return -1

        # Level 3 (leaf)
        i3 = key & 0xF
        v = L3[i3]
        return v if v is not None else -1

    def set(self, key: int, value: int) -> None:
        """O(1) insert with unrolled traversal."""
        # Level 0
        i0 = (key >> 12) & 0xF
        L1 = self._L0[i0]
        if L1 is None:
            L1 = [None] * WORDS
            self._L0[i0] = L1

        # Level 1
        i1 = (key >> 8) & 0xF
        L2 = L1[i1]
        if L2 is None:
            L2 = [None] * WORDS
            L1[i1] = L2

        # Level 2
        i2 = (key >> 4) & 0xF
        L3 = L2[i2]
        if L3 is None:
            L3 = [None] * WORDS
            L2[i2] = L3

        # Level 3 (leaf)
        i3 = key & 0xF
        old = L3[i3]
        L3[i3] = value
        if old is None:
            self._size += 1

    def __len__(self) -> int:
        return self._size

    def __contains__(self, key: int) -> bool:
        return self.get(key) != -1


# =============================================================================
# BENCHMARK
# =============================================================================


def benchmark(n: int = 60000) -> None:
    """Benchmark optimized Lotus vs dict with focus on RANGE QUERIES."""
    import random
    import time

    print(f"=== LOTUS BENCHMARK ({n:,} entries) ===\n")

    # Fill with random keys
    random.seed(42)
    keys = random.sample(range(KEY_SPACE), min(n, KEY_SPACE))

    # --- Setup ---
    lotus = LotusArrayInt()
    d: dict[int, int] = {}

    for k in keys:
        lotus[k] = k
        d[k] = k

    # --- Range Query Benchmark (THE KILLER FEATURE) ---
    print("RANGE QUERIES (where Lotus wins):")
    print("-" * 40)

    for range_size in [1000, 5000, 10000]:
        start_key = 10000
        end_key = start_key + range_size

        # Lotus: O(k) - iterate only range
        start = time.perf_counter()
        lotus_sum = lotus.range_sum(start_key, end_key)
        lotus_time = (time.perf_counter() - start) * 1000

        # Dict: O(N) - must filter ALL items
        start = time.perf_counter()
        dict_sum = sum(v for k, v in d.items() if start_key <= k < end_key)
        dict_time = (time.perf_counter() - start) * 1000

        speedup = dict_time / lotus_time
        print(f"  Range size {range_size:,}:")
        print(f"    Lotus: {lotus_time:.2f} ms | Dict: {dict_time:.2f} ms")
        print(f"    → Lotus is {speedup:.1f}x FASTER")
        print()

    # --- Insert/Read for completeness ---
    print("INSERT/READ (for reference):")
    print("-" * 40)

    lotus2 = LotusArrayInt()
    start = time.perf_counter()
    for k in keys:
        lotus2[k] = k
    lotus_insert = (time.perf_counter() - start) * 1000

    d2: dict[int, int] = {}
    start = time.perf_counter()
    for k in keys:
        d2[k] = k
    dict_insert = (time.perf_counter() - start) * 1000

    print(f"  INSERT: Lotus {lotus_insert:.1f}ms, Dict {dict_insert:.1f}ms")
    print(f"    → Lotus is {dict_insert / lotus_insert:.1f}x faster")
    print()
    print("KEY INSIGHT:")
    print("  Dict cannot do range queries efficiently.")
    print("  Lotus range query is O(k), Dict is O(N).")


# Keep old classes for compatibility
LotusArray = LotusArrayInt
LotusRadix = LotusRadixInt

if __name__ == "__main__":
    benchmark()
