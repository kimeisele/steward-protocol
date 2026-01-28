"""
LOTUS RADIX[N] - Generische N-Level Struktur (Skaliert beliebig)
================================================================

"ekam evādvitīyam brahma" - "Brahman is one, without a second"
— Chandogya Upanishad 6.2.1

THE PROBLEM:
============

LotusArrayInt:    Fixed 16^4 = 65,536 keys (16-bit)
LotusIPv4Router:  Fixed 16^8 = 4 billion keys (32-bit)

What if we need:
- IPv6?     128-bit = 16^32 keys
- UUIDs?    128-bit = 16^32 keys
- SHA-256?  256-bit = 16^64 keys
- Unknown future requirements?

THE SOLUTION:
=============

LotusRadixN - Generische N-Level Struktur

    N levels × 4 bits per level = N×4 bit keys
    16 entries per level (ALWAYS - Mahamantra aligned)

    LotusRadixN(4)  →  16-bit keys  →  65,536 (like LotusArrayInt)
    LotusRadixN(8)  →  32-bit keys  →  IPv4
    LotusRadixN(32) → 128-bit keys  →  IPv6/UUID
    LotusRadixN(64) → 256-bit keys  →  SHA-256

COMPLEXITY:
===========

    Lookup:  O(N) where N = number of levels (NOT number of keys!)
    Insert:  O(N)
    Memory:  O(K × N) where K = actual keys stored (sparse)

    This is CONSTANT with respect to the total key space!

    IPv6 has 2^128 possible keys, but:
    - Lookup is O(32) = O(1) constant time
    - Memory only grows with actual keys stored

MAHAMANTRA ALIGNMENT:
=====================

    Every level has exactly 16 entries = WORDS
    16 = 2^4 = perfect CPU alignment

    Key decomposition: Split into 4-bit nibbles (0-15)
    Each nibble indexes into 16-slot array

    This IS the Mahamantra structure, just repeated N times.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0xbd0f4898"  # GenesisByte: parampara % 37 == 0

from typing import Any, Final, Generic, Iterator, TypeVar

from ..protocols._seed import WORDS

# =============================================================================
# CONSTANTS
# =============================================================================

SLOTS_PER_LEVEL: Final[int] = WORDS  # 16 (Mahamantra!)
BITS_PER_LEVEL: Final[int] = 4  # log2(16) = 4
NIBBLE_MASK: Final[int] = 0xF  # 4 bits = 0b1111

V = TypeVar("V")


# =============================================================================
# LOTUS RADIX[N] - Generic Implementation
# =============================================================================


class LotusRadixN(Generic[V]):
    """
    Generic N-level radix structure for arbitrary key sizes.

    Type Parameters:
        V: Value type stored at leaf nodes

    Args:
        levels: Number of levels (determines key size = levels × 4 bits)
        default: Default value for missing keys (default: None)

    Examples:
        # 16-bit keys (like LotusArrayInt)
        index_16bit = LotusRadixN[int](levels=4, default=-1)

        # 32-bit keys (like IPv4)
        router_32bit = LotusRadixN[int](levels=8, default=0)

        # 128-bit keys (IPv6/UUID)
        index_128bit = LotusRadixN[str](levels=32, default="")

        # 256-bit keys (SHA-256)
        hash_index = LotusRadixN[bytes](levels=64, default=b"")
    """

    __slots__ = ("_levels", "_root", "_size", "_default", "_max_key")

    def __init__(self, levels: int, default: V | None = None) -> None:
        if levels < 1:
            raise ValueError("levels must be at least 1")
        if levels > 64:
            raise ValueError("levels > 64 not supported (256-bit max)")

        self._levels: int = levels
        self._default: V | None = default
        self._root: list[Any] = [None] * SLOTS_PER_LEVEL
        self._size: int = 0

        # Maximum key value for this structure
        # For levels=4: max_key = 16^4 - 1 = 65535
        # For levels=8: max_key = 16^8 - 1 = 4294967295
        self._max_key: int = (1 << (levels * BITS_PER_LEVEL)) - 1

    @property
    def levels(self) -> int:
        """Number of levels in the structure."""
        return self._levels

    @property
    def key_bits(self) -> int:
        """Number of bits in keys (levels × 4)."""
        return self._levels * BITS_PER_LEVEL

    @property
    def max_key(self) -> int:
        """Maximum key value."""
        return self._max_key

    @property
    def key_space(self) -> int:
        """Total possible keys (16^levels)."""
        return self._max_key + 1

    def _get_nibble(self, key: int, level: int) -> int:
        """Extract 4-bit nibble for given level (0 = top level)."""
        shift = (self._levels - 1 - level) * BITS_PER_LEVEL
        return (key >> shift) & NIBBLE_MASK

    def get(self, key: int) -> V | None:
        """
        O(N) lookup where N = number of levels.

        Returns default value if key not found.
        """
        if key < 0 or key > self._max_key:
            return self._default

        node = self._root
        for level in range(self._levels - 1):
            nibble = self._get_nibble(key, level)
            next_node = node[nibble]
            if next_node is None:
                return self._default
            node = next_node

        # Leaf level
        nibble = self._get_nibble(key, self._levels - 1)
        value = node[nibble]
        return value if value is not None else self._default

    def set(self, key: int, value: V) -> None:
        """
        O(N) insert where N = number of levels.

        Allocates intermediate nodes as needed (sparse).
        """
        if key < 0 or key > self._max_key:
            raise ValueError(f"Key {key} out of range [0, {self._max_key}]")

        node = self._root
        for level in range(self._levels - 1):
            nibble = self._get_nibble(key, level)
            next_node = node[nibble]
            if next_node is None:
                next_node = [None] * SLOTS_PER_LEVEL
                node[nibble] = next_node
            node = next_node

        # Leaf level
        nibble = self._get_nibble(key, self._levels - 1)
        old_value = node[nibble]
        node[nibble] = value

        if old_value is None and value is not None:
            self._size += 1

    def delete(self, key: int) -> bool:
        """
        O(N) delete. Returns True if key existed.

        Note: Does not deallocate empty intermediate nodes (for speed).
        """
        if key < 0 or key > self._max_key:
            return False

        node = self._root
        path: list[tuple[list[Any], int]] = []

        for level in range(self._levels - 1):
            nibble = self._get_nibble(key, level)
            next_node = node[nibble]
            if next_node is None:
                return False
            path.append((node, nibble))
            node = next_node

        # Leaf level
        nibble = self._get_nibble(key, self._levels - 1)
        if node[nibble] is None:
            return False

        node[nibble] = None
        self._size -= 1
        return True

    def __getitem__(self, key: int) -> V | None:
        """O(N) lookup via indexing."""
        return self.get(key)

    def __setitem__(self, key: int, value: V) -> None:
        """O(N) insert via indexing."""
        self.set(key, value)

    def __delitem__(self, key: int) -> None:
        """O(N) delete via indexing."""
        if not self.delete(key):
            raise KeyError(key)

    def __contains__(self, key: int) -> bool:
        """O(N) membership test."""
        return self.get(key) is not None and self.get(key) != self._default

    def __len__(self) -> int:
        """Number of keys stored."""
        return self._size

    def __repr__(self) -> str:
        return f"LotusRadixN(levels={self._levels}, size={self._size}, key_bits={self.key_bits})"

    def prefix_iter(self, prefix: int, prefix_bits: int) -> Iterator[tuple[int, V]]:
        """
        Iterate all keys with given prefix. THIS IS THE KILLER FEATURE.

        Args:
            prefix: The prefix value (upper bits)
            prefix_bits: Number of bits in prefix (must be multiple of 4)

        Yields:
            (key, value) tuples for all keys matching prefix

        Example:
            # Find all IPv4 addresses in 192.168.0.0/16
            prefix = (192 << 24) | (168 << 16)  # 192.168.x.x
            for ip, route in router.prefix_iter(prefix, 16):
                print(f"{ip} -> {route}")

        Complexity: O(P + K) where P = prefix levels, K = matching keys
        Dict equivalent: O(N) must scan ALL keys!
        """
        if prefix_bits % BITS_PER_LEVEL != 0:
            raise ValueError(f"prefix_bits must be multiple of {BITS_PER_LEVEL}")

        prefix_levels = prefix_bits // BITS_PER_LEVEL
        if prefix_levels > self._levels:
            raise ValueError(f"prefix_bits {prefix_bits} > key_bits {self.key_bits}")

        # Navigate to prefix node
        node = self._root
        for level in range(prefix_levels):
            nibble = self._get_nibble(prefix, level)
            next_node = node[nibble]
            if next_node is None:
                return  # No keys with this prefix
            node = next_node

        # Convert positioned prefix to raw nibble accumulator
        # e.g., prefix=0x1200 with prefix_bits=8 in a 16-bit tree:
        # key_prefix = 0x1200 >> (16 - 8) = 0x12
        key_prefix = prefix >> (self.key_bits - prefix_bits)

        # Now recursively yield all keys under this node
        yield from self._iter_subtree(node, key_prefix, prefix_levels)

    def _iter_subtree(self, node: list[Any], key_prefix: int, current_level: int) -> Iterator[tuple[int, V]]:
        """Recursively iterate all keys in subtree."""
        if current_level == self._levels - 1:
            # Leaf level
            for nibble in range(SLOTS_PER_LEVEL):
                value = node[nibble]
                if value is not None:
                    full_key = (key_prefix << BITS_PER_LEVEL) | nibble
                    yield (full_key, value)
        else:
            # Intermediate level
            for nibble in range(SLOTS_PER_LEVEL):
                child = node[nibble]
                if child is not None:
                    new_prefix = (key_prefix << BITS_PER_LEVEL) | nibble
                    yield from self._iter_subtree(child, new_prefix, current_level + 1)

    def count_prefix(self, prefix: int, prefix_bits: int) -> int:
        """Count keys matching prefix. O(P + K) vs Dict's O(N)."""
        return sum(1 for _ in self.prefix_iter(prefix, prefix_bits))


# =============================================================================
# SPECIALIZED FACTORIES
# =============================================================================


def lotus_16bit(default: V | None = None) -> LotusRadixN[V]:
    """Create 16-bit key structure (65,536 keys, like LotusArrayInt)."""
    return LotusRadixN[V](levels=4, default=default)


def lotus_32bit(default: V | None = None) -> LotusRadixN[V]:
    """Create 32-bit key structure (4 billion keys, IPv4)."""
    return LotusRadixN[V](levels=8, default=default)


def lotus_64bit(default: V | None = None) -> LotusRadixN[V]:
    """Create 64-bit key structure (uint64 keys)."""
    return LotusRadixN[V](levels=16, default=default)


def lotus_128bit(default: V | None = None) -> LotusRadixN[V]:
    """Create 128-bit key structure (IPv6, UUID)."""
    return LotusRadixN[V](levels=32, default=default)


def lotus_256bit(default: V | None = None) -> LotusRadixN[V]:
    """Create 256-bit key structure (SHA-256 hashes)."""
    return LotusRadixN[V](levels=64, default=default)


# =============================================================================
# BENCHMARK
# =============================================================================


def benchmark() -> None:
    """Benchmark LotusRadixN against dict and specialized implementations."""
    import random
    import time

    print("=" * 70)
    print("LOTUS RADIX[N] BENCHMARK")
    print("Generische N-Level Struktur - Skaliert beliebig")
    print("=" * 70)
    print()

    # Test different key sizes
    configs = [
        (4, 60000, "16-bit (like LotusArrayInt)"),
        (8, 100000, "32-bit (like IPv4)"),
        (16, 100000, "64-bit (uint64)"),
    ]

    for levels, n_keys, description in configs:
        print(f"\n### {description} - {levels} levels ###")
        print(f"Key space: 16^{levels} = {16**levels:,}")
        print(f"Testing with {n_keys:,} random keys")
        print("-" * 50)

        max_key = (1 << (levels * 4)) - 1
        random.seed(42)
        keys = [random.randint(0, min(max_key, 10**9)) for _ in range(n_keys)]

        # --- LotusRadixN ---
        lotus = LotusRadixN[int](levels=levels, default=-1)

        start = time.perf_counter()
        for k in keys:
            lotus[k] = k
        lotus_insert = (time.perf_counter() - start) * 1000

        start = time.perf_counter()
        lotus_sum = sum(lotus[k] for k in keys)
        lotus_read = (time.perf_counter() - start) * 1000

        # --- Dict ---
        d: dict[int, int] = {}

        start = time.perf_counter()
        for k in keys:
            d[k] = k
        dict_insert = (time.perf_counter() - start) * 1000

        start = time.perf_counter()
        dict_sum = sum(d[k] for k in keys)
        dict_read = (time.perf_counter() - start) * 1000

        # Results
        print(f"INSERT: Lotus {lotus_insert:.1f}ms, Dict {dict_insert:.1f}ms")
        insert_ratio = dict_insert / lotus_insert if lotus_insert > 0 else 0
        print(f"  → {'Lotus' if insert_ratio > 1 else 'Dict'} is {max(insert_ratio, 1 / insert_ratio):.1f}x faster")

        print(f"READ:   Lotus {lotus_read:.1f}ms, Dict {dict_read:.1f}ms")
        read_ratio = dict_read / lotus_read if lotus_read > 0 else 0
        print(f"  → {'Lotus' if read_ratio > 1 else 'Dict'} is {max(read_ratio, 1 / read_ratio):.1f}x faster")

        print(f"Memory: Lotus stores {len(lotus):,} keys")

    # PREFIX QUERY BENCHMARK (THE KILLER FEATURE)
    print()
    print("=" * 70)
    print("PREFIX QUERIES (where LotusRadixN WINS)")
    print("=" * 70)

    # Use 32-bit keys (like IPv4)
    levels = 8
    n_keys = 100000
    max_key = (1 << 32) - 1

    random.seed(42)

    # Create keys with common prefixes (like IP subnets)
    # Simulate 192.168.x.x (prefix = 192.168.0.0, prefix_bits = 16)
    base_prefix = (192 << 24) | (168 << 16)
    keys_in_prefix = [base_prefix | random.randint(0, 65535) for _ in range(10000)]
    other_keys = [random.randint(0, max_key) for _ in range(n_keys - 10000)]
    all_keys = keys_in_prefix + other_keys
    random.shuffle(all_keys)

    # Build structures
    lotus = LotusRadixN[int](levels=8, default=-1)
    d: dict[int, int] = {}

    for k in all_keys:
        lotus[k] = k
        d[k] = k

    print(f"\nTest: Find all keys with prefix 192.168.x.x ({len(keys_in_prefix):,} keys)")
    print(f"Total keys: {len(all_keys):,}")
    print("-" * 50)

    # LotusRadixN: O(P + K) where P = prefix levels, K = matching keys
    start = time.perf_counter()
    lotus_count = lotus.count_prefix(base_prefix, 16)
    lotus_prefix_time = (time.perf_counter() - start) * 1000

    # Dict: O(N) must scan ALL keys
    start = time.perf_counter()
    dict_count = sum(1 for k in d if (k >> 16) == (base_prefix >> 16))
    dict_prefix_time = (time.perf_counter() - start) * 1000

    print(f"LotusRadixN: {lotus_prefix_time:.2f}ms (found {lotus_count:,} keys)")
    print(f"Dict:        {dict_prefix_time:.2f}ms (found {dict_count:,} keys)")
    speedup = dict_prefix_time / lotus_prefix_time if lotus_prefix_time > 0 else 0
    print(f"→ LotusRadixN is {speedup:.1f}x FASTER for prefix queries!")

    # Summary
    print()
    print("=" * 70)
    print("KEY INSIGHT:")
    print("=" * 70)
    print("""
LotusRadixN provides:

1. ARBITRARY KEY SIZES
   - 16-bit, 32-bit, 64-bit, 128-bit, 256-bit
   - All with same O(N) complexity where N = levels

2. MAHAMANTRA ALIGNMENT
   - Every level has exactly 16 entries
   - 16 = WORDS = Mahamantra alignment

3. SPARSE ALLOCATION
   - Only allocates nodes that are used
   - Memory grows with actual keys, not key space

4. DETERMINISTIC
   - Same input → same output
   - No hashing, no collisions, no randomization

TRADE-OFF:
- Dict may be faster for small key counts (< 10,000)
- LotusRadixN wins for:
  - Large key spaces (IPv6, SHA-256)
  - Prefix-based operations (routing, search)
  - Deterministic requirements
  - Memory predictability
""")


if __name__ == "__main__":
    benchmark()
