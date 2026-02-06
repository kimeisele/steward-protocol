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

PRODUCTION USE:
===============

    - CLI routing backbone (Balarama Pattern)
    - Command prefix matching O(P + K)
    - Vibrational seed → handler mapping
    - Future: IPv6/UUID indexing
"""

from __future__ import annotations

from typing import Any, Final, Generic, Iterator, TypeVar

from vibe_core.mahamantra.protocols._seed import HARE_COUNT, KSETRAJNA, QUALITIES, QUARTERS, WORDS

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0xbd0f4898"  # GenesisByte: parampara % 37 == 0

# =============================================================================
# CONSTANTS
# =============================================================================

SLOTS_PER_LEVEL: Final[int] = WORDS  # 16 (Mahamantra!)
BITS_PER_LEVEL: Final[int] = QUARTERS  # log2(16) = 4
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
        if levels < KSETRAJNA:
            raise ValueError("levels must be at least 1")
        if levels > QUALITIES:
            raise ValueError("levels > 64 not supported (256-bit max)")

        self._levels: int = levels
        self._default: V | None = default
        self._root: list[object] = [None] * SLOTS_PER_LEVEL
        self._size: int = 0

        # Maximum key value for this structure
        # For levels=4: max_key = 16^4 - 1 = 65535
        # For levels=8: max_key = 16^8 - 1 = 4294967295
        self._max_key: int = (KSETRAJNA << (levels * BITS_PER_LEVEL)) - KSETRAJNA

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
        return self._max_key + KSETRAJNA

    def _get_nibble(self, key: int, level: int) -> int:
        """Extract 4-bit nibble for given level (0 = top level)."""
        shift = (self._levels - KSETRAJNA - level) * BITS_PER_LEVEL
        return (key >> shift) & NIBBLE_MASK

    def get(self, key: int) -> V | None:
        """
        O(N) lookup where N = number of levels.

        Returns default value if key not found.
        """
        if key < 0 or key > self._max_key:
            return self._default

        node = self._root
        for level in range(self._levels - KSETRAJNA):
            nibble = self._get_nibble(key, level)
            next_node = node[nibble]
            if next_node is None:
                return self._default
            node = next_node

        # Leaf level
        nibble = self._get_nibble(key, self._levels - KSETRAJNA)
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
        for level in range(self._levels - KSETRAJNA):
            nibble = self._get_nibble(key, level)
            next_node = node[nibble]
            if next_node is None:
                next_node = [None] * SLOTS_PER_LEVEL
                node[nibble] = next_node
            node = next_node

        # Leaf level
        nibble = self._get_nibble(key, self._levels - KSETRAJNA)
        old_value = node[nibble]
        node[nibble] = value

        if old_value is None and value is not None:
            self._size += KSETRAJNA

    def delete(self, key: int) -> bool:
        """
        O(N) delete. Returns True if key existed.

        Note: Does not deallocate empty intermediate nodes (for speed).
        """
        if key < 0 or key > self._max_key:
            return False

        node = self._root
        path: list[tuple[list[object], int]] = []

        for level in range(self._levels - KSETRAJNA):
            nibble = self._get_nibble(key, level)
            next_node = node[nibble]
            if next_node is None:
                return False
            path.append((node, nibble))
            node = next_node

        # Leaf level
        nibble = self._get_nibble(key, self._levels - KSETRAJNA)
        if node[nibble] is None:
            return False

        node[nibble] = None
        self._size -= KSETRAJNA
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

    def _iter_subtree(self, node: list[object], key_prefix: int, current_level: int) -> Iterator[tuple[int, V]]:
        """Recursively iterate all keys in subtree."""
        if current_level == self._levels - KSETRAJNA:
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
                    yield from self._iter_subtree(child, new_prefix, current_level + KSETRAJNA)

    def count_prefix(self, prefix: int, prefix_bits: int) -> int:
        """Count keys matching prefix. O(P + K) vs Dict's O(N)."""
        return sum(KSETRAJNA for _ in self.prefix_iter(prefix, prefix_bits))


# =============================================================================
# SPECIALIZED FACTORIES
# =============================================================================


def lotus_16bit(default: V | None = None) -> LotusRadixN[V]:
    """Create 16-bit key structure (65,536 keys, like LotusArrayInt)."""
    return LotusRadixN[V](levels=QUARTERS, default=default)


def lotus_32bit(default: V | None = None) -> LotusRadixN[V]:
    """Create 32-bit key structure (4 billion keys, IPv4)."""
    return LotusRadixN[V](levels=HARE_COUNT, default=default)


def lotus_64bit(default: V | None = None) -> LotusRadixN[V]:
    """Create 64-bit key structure (uint64 keys)."""
    return LotusRadixN[V](levels=WORDS, default=default)


def lotus_128bit(default: V | None = None) -> LotusRadixN[V]:
    """Create 128-bit key structure (IPv6, UUID)."""
    return LotusRadixN[V](levels=32, default=default)


def lotus_256bit(default: V | None = None) -> LotusRadixN[V]:
    """Create 256-bit key structure (SHA-256 hashes)."""
    return LotusRadixN[V](levels=QUALITIES, default=default)
