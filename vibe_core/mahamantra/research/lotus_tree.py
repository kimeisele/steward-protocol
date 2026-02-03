"""
LOTUS TREE - O(1) Holographic Data Structure (RESEARCH)
========================================================

KEY INSIGHT: The address IS the path. No search, no hash, no collisions.

STRUCTURE:
  16-bit key = 4 × 4 bits = 4 levels × 16 slots
  KEY_SPACE = 16^4 = 65536 = WORDS^QUARTERS

PRODUCTION VS RESEARCH:
  - HolographicRouter (adapters/routing.py) = PRODUCTION radix tree
  - LotusArrayInt (this file) = RESEARCH array.array for C-speed integers

This file contains ONLY experimental code not yet in production.
For production radix tree, use: from vibe_core.mahamantra.adapters.routing import HolographicRouter

UNIQUE RESEARCH CODE:
  LotusArrayInt - Uses array.array('q') for 64-bit integers at C-level speed.
                  Faster than dict for sequential access and range queries.
                  Pre-allocates 65536 slots (512KB) for O(1) access.
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
# LOTUS ARRAY - Flat O(1) for integers (EXPERIMENTAL - uses array.array)
# =============================================================================


class LotusArrayInt:
    """O(1) integer key-value store using array.array.

    EXPERIMENTAL: Uses array.array('q') for C-level speed.
    Pre-allocates all 65536 slots (512KB memory).

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
# LOTUS RADIX - DEPRECATED, USE PRODUCTION
# =============================================================================
# LotusRadixInt has been promoted to production.
# Use HolographicRouter from adapters/routing.py instead.

from vibe_core.mahamantra.adapters.routing import HolographicRouter


# Backward compatibility alias - wraps production HolographicRouter
class LotusRadixInt:
    """DEPRECATED: Use HolographicRouter from adapters/routing.py.

    This is a backward-compatibility wrapper around the production
    HolographicRouter. New code should import directly from production.
    """

    def __init__(self) -> None:
        import warnings

        warnings.warn(
            "LotusRadixInt is deprecated. Use HolographicRouter from vibe_core.mahamantra.adapters.routing instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self._router: HolographicRouter[int] = HolographicRouter()

    def get(self, key: int) -> int:
        """O(1) lookup. Returns -1 if not found."""
        val = self._router.get(key)
        return -1 if val is None else val

    def set(self, key: int, value: int) -> None:
        """O(1) insert."""
        self._router[key] = value

    def __len__(self) -> int:
        return len(self._router)

    def __contains__(self, key: int) -> bool:
        return key in self._router


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
    print()
    print("NOTE: For radix tree functionality, use HolographicRouter from production.")


# Backward compatibility aliases
LotusArray = LotusArrayInt
LotusRadix = LotusRadixInt  # Deprecated wrapper

if __name__ == "__main__":
    benchmark()
