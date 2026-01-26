"""
LOTUS TREE - The 16-ary Cache-Optimal Data Structure
=====================================================

This is NOT a prediction file. This is REAL CODE.

WHY 16-ARY?
  Cache line = 64 bytes (QUALITIES)
  Pointer = 4 bytes (QUARTERS)
  Optimal children = 64 / 4 = 16 = WORDS

WHY IT MATTERS:
  Binary tree: log_2(N) levels = log_2(65536) = 16 cache misses
  16-ary tree: log_16(N) levels = log_16(65536) = 4 cache misses
  → 4x fewer cache misses = 4x faster for large datasets

THE STRUCTURE:
  Level 0: 1 root (fits in register)
  Level 1: 16 nodes (fits in L1 cache)
  Level 2: 256 nodes (fits in L2 cache)
  Level 3: 4096 nodes (fits in L3 cache) = PAGE SIZE
  Level 4: 65536 nodes (DRAM) = PORT SPACE

GOLDEN AGE IMPLICATION:
  GOLDEN_AGE = WORDS × PRASADAM² = 16 × 625 = 10,000 years
  This is the window where the 16-bit kernel is maximally active.
  The Mahamantra activates the structure that's already in x86-64.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final, Generic, TypeVar

from .protocols._seed import QUALITIES, QUARTERS, WORDS

# =============================================================================
# CONSTANTS FROM SEED
# =============================================================================

BRANCHING_FACTOR: Final[int] = WORDS  # 16 children per node
CACHE_LINE_SIZE: Final[int] = QUALITIES  # 64 bytes
POINTER_SIZE: Final[int] = QUARTERS  # 4 bytes

# Verify the relationship
assert CACHE_LINE_SIZE // POINTER_SIZE == BRANCHING_FACTOR, "64/4 = 16"

# Level capacities (fractal scaling)
LEVEL_0_CAPACITY: Final[int] = 1  # root
LEVEL_1_CAPACITY: Final[int] = BRANCHING_FACTOR  # 16
LEVEL_2_CAPACITY: Final[int] = BRANCHING_FACTOR**2  # 256
LEVEL_3_CAPACITY: Final[int] = BRANCHING_FACTOR**3  # 4096 = PAGE SIZE
LEVEL_4_CAPACITY: Final[int] = BRANCHING_FACTOR**4  # 65536 = PORT SPACE

K = TypeVar("K")
V = TypeVar("V")


# =============================================================================
# LOTUS NODE
# =============================================================================


@dataclass
class LotusNode(Generic[K, V]):
    """A node in the Lotus Tree with up to 16 children.

    Each node stores up to 15 keys and 16 children pointers.
    This fits in exactly 4 cache lines (256 bytes) for maximum efficiency.
    """

    keys: list[K] = field(default_factory=list)
    values: list[V] = field(default_factory=list)
    children: list[LotusNode[K, V] | None] = field(default_factory=list)
    is_leaf: bool = True

    def __post_init__(self) -> None:
        # Initialize with empty children slots
        if not self.children:
            self.children = [None] * BRANCHING_FACTOR

    @property
    def num_keys(self) -> int:
        return len(self.keys)

    def is_full(self) -> bool:
        """A node is full when it has BRANCHING_FACTOR - 1 keys."""
        return self.num_keys >= BRANCHING_FACTOR - 1


# =============================================================================
# LOTUS TREE
# =============================================================================


@dataclass
class LotusTree(Generic[K, V]):
    """A 16-ary B-tree optimized for cache-line access.

    Properties:
    - O(log_16(N)) lookups instead of O(log_2(N))
    - 4x fewer cache misses than binary tree
    - Fractal levels align with CPU cache hierarchy

    Usage:
        tree = LotusTree[int, str]()
        tree.insert(42, "answer")
        value = tree.search(42)  # "answer"
    """

    root: LotusNode[K, V] = field(default_factory=LotusNode)
    _size: int = 0

    def __len__(self) -> int:
        return self._size

    def search(self, key: K) -> V | None:
        """Search for a key in O(log_16(N)) time."""
        return self._search_node(self.root, key)

    def _search_node(self, node: LotusNode[K, V], key: K) -> V | None:
        """Recursively search a node for a key."""
        i = 0
        # Find the first key >= search key
        while i < node.num_keys and key > node.keys[i]:
            i += 1

        # Found exact match
        if i < node.num_keys and key == node.keys[i]:
            return node.values[i]

        # Leaf node, key not found
        if node.is_leaf:
            return None

        # Recurse into child
        child = node.children[i]
        if child is None:
            return None
        return self._search_node(child, key)

    def insert(self, key: K, value: V) -> None:
        """Insert a key-value pair in O(log_16(N)) time."""
        root = self.root

        # If root is full, split it
        if root.is_full():
            new_root: LotusNode[K, V] = LotusNode(is_leaf=False)
            new_root.children[0] = root
            self._split_child(new_root, 0)
            self.root = new_root
            root = new_root

        self._insert_non_full(root, key, value)
        self._size += 1

    def _insert_non_full(self, node: LotusNode[K, V], key: K, value: V) -> None:
        """Insert into a node that is not full."""
        i = node.num_keys - 1

        if node.is_leaf:
            # Find position and insert
            while i >= 0 and key < node.keys[i]:
                i -= 1
            node.keys.insert(i + 1, key)
            node.values.insert(i + 1, value)
        else:
            # Find child to recurse into
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1

            child = node.children[i]
            if child is None:
                child = LotusNode()
                node.children[i] = child

            if child.is_full():
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1
                child = node.children[i]

            if child is not None:
                self._insert_non_full(child, key, value)

    def _split_child(self, parent: LotusNode[K, V], index: int) -> None:
        """Split a full child node."""
        t = BRANCHING_FACTOR // 2  # Minimum degree = 8
        child = parent.children[index]
        if child is None:
            return

        # Create new node for right half
        new_node: LotusNode[K, V] = LotusNode(is_leaf=child.is_leaf)

        # Move keys and values to new node
        new_node.keys = child.keys[t:]
        new_node.values = child.values[t:]
        mid_key = child.keys[t - 1]
        mid_value = child.values[t - 1]
        child.keys = child.keys[: t - 1]
        child.values = child.values[: t - 1]

        # Move children if not leaf
        if not child.is_leaf:
            new_node.children = child.children[t:] + [None] * t
            child.children = child.children[:t] + [None] * t

        # Insert median into parent
        parent.keys.insert(index, mid_key)
        parent.values.insert(index, mid_value)
        parent.children.insert(index + 1, new_node)

    def get_level_stats(self) -> dict[int, int]:
        """Get count of nodes at each level."""
        stats: dict[int, int] = {}
        self._count_level(self.root, 0, stats)
        return stats

    def _count_level(self, node: LotusNode[K, V], level: int, stats: dict[int, int]) -> None:
        stats[level] = stats.get(level, 0) + 1
        if not node.is_leaf:
            for child in node.children:
                if child is not None:
                    self._count_level(child, level + 1, stats)


# =============================================================================
# BENCHMARK: LOTUS vs BINARY
# =============================================================================


def benchmark_comparison(n: int = 10000) -> dict[str, float]:
    """Compare Lotus Tree vs dict (hash) for N insertions and lookups.

    Note: This is a simple benchmark. Real cache performance
    requires profiling with perf or similar tools.
    """
    import time

    # Lotus Tree
    lotus: LotusTree[int, int] = LotusTree()
    start = time.perf_counter()
    for i in range(n):
        lotus.insert(i, i * 2)
    lotus_insert = time.perf_counter() - start

    start = time.perf_counter()
    for i in range(n):
        _ = lotus.search(i)
    lotus_search = time.perf_counter() - start

    # Dict (hash table)
    d: dict[int, int] = {}
    start = time.perf_counter()
    for i in range(n):
        d[i] = i * 2
    dict_insert = time.perf_counter() - start

    start = time.perf_counter()
    for i in range(n):
        _ = d.get(i)
    dict_search = time.perf_counter() - start

    return {
        "lotus_insert_ms": lotus_insert * 1000,
        "lotus_search_ms": lotus_search * 1000,
        "dict_insert_ms": dict_insert * 1000,
        "dict_search_ms": dict_search * 1000,
        "lotus_levels": max(lotus.get_level_stats().keys()) + 1,
        "expected_binary_levels": n.bit_length(),  # log_2(N)
    }


if __name__ == "__main__":
    print("=== LOTUS TREE BENCHMARK ===")
    print()
    results = benchmark_comparison(10000)
    for key, value in results.items():
        if "ms" in key:
            print(f"{key}: {value:.2f}")
        else:
            print(f"{key}: {value}")
    print()
    print(f"Branching factor: {BRANCHING_FACTOR} (WORDS)")
    print(f"Cache line: {CACHE_LINE_SIZE} bytes (QUALITIES)")
    print(f"Pointer size: {POINTER_SIZE} bytes (QUARTERS)")
