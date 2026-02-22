"""
TESTS: LotusRadixN - Generic N-Level Radix Structure
=====================================================

"ekam evādvitīyam brahma" - "Brahman is one, without a second"

These tests make LotusRadixN ALTAR-WORTHY.
No untested code goes to production.
"""

import pytest
from vibe_core.mahamantra.research.lotus_radix_n import (
    LotusRadixN,
    lotus_16bit,
    lotus_32bit,
    lotus_64bit,
    lotus_128bit,
    SLOTS_PER_LEVEL,
    BITS_PER_LEVEL,
)
from vibe_core.mahamantra.protocols._seed import WORDS


# =============================================================================
# Constants Verification
# =============================================================================


class TestLotusRadixNConstants:
    """Verify constants are Mahamantra-aligned."""

    def test_slots_per_level_is_words(self):
        """SLOTS_PER_LEVEL must equal WORDS (16)."""
        assert SLOTS_PER_LEVEL == WORDS == 16

    def test_bits_per_level_is_four(self):
        """BITS_PER_LEVEL must be 4 (log2(16))."""
        assert BITS_PER_LEVEL == 4

    def test_slots_matches_bits(self):
        """2^BITS_PER_LEVEL must equal SLOTS_PER_LEVEL."""
        assert 2**BITS_PER_LEVEL == SLOTS_PER_LEVEL


# =============================================================================
# Basic Operations
# =============================================================================


class TestLotusRadixNBasics:
    """Test basic CRUD operations."""

    def test_create_empty(self):
        """Can create empty radix tree."""
        tree = LotusRadixN[int](levels=4)
        assert len(tree) == 0

    def test_set_and_get(self):
        """Can set and get a value."""
        tree = LotusRadixN[str](levels=4)
        tree.set(0x1234, "hello")
        assert tree.get(0x1234) == "hello"

    def test_indexing_syntax(self):
        """Can use [] syntax for get/set."""
        tree = LotusRadixN[str](levels=4)
        tree[0x1234] = "hello"
        assert tree[0x1234] == "hello"

    def test_get_missing_returns_default(self):
        """Get missing key returns default."""
        tree = LotusRadixN[int](levels=4, default=-1)
        assert tree.get(0x1234) == -1

    def test_get_missing_returns_none(self):
        """Get missing key returns None if no default."""
        tree = LotusRadixN[str](levels=4)
        assert tree.get(0x1234) is None

    def test_delete_existing(self):
        """Can delete existing key."""
        tree = LotusRadixN[str](levels=4)
        tree.set(0x1234, "hello")
        assert tree.delete(0x1234) is True
        assert tree.get(0x1234) is None

    def test_delete_missing(self):
        """Delete missing key returns False."""
        tree = LotusRadixN[str](levels=4)
        assert tree.delete(0x1234) is False

    def test_contains(self):
        """Can check key membership."""
        tree = LotusRadixN[str](levels=4)
        tree.set(0x1234, "hello")
        assert 0x1234 in tree
        assert 0x5678 not in tree

    def test_len_updates(self):
        """Length updates on insert/delete."""
        tree = LotusRadixN[int](levels=4)
        assert len(tree) == 0
        tree.set(0x1234, 1)
        assert len(tree) == 1
        tree.set(0x5678, 2)
        assert len(tree) == 2
        tree.delete(0x1234)
        assert len(tree) == 1


# =============================================================================
# Key Space Boundaries
# =============================================================================


class TestLotusRadixNBoundaries:
    """Test key space boundaries."""

    def test_max_key_4_levels(self):
        """4 levels = 16-bit = max 65535."""
        tree = LotusRadixN[int](levels=4)
        assert tree.max_key == 0xFFFF
        assert tree.key_bits == 16

    def test_max_key_8_levels(self):
        """8 levels = 32-bit = max 4 billion."""
        tree = LotusRadixN[int](levels=8)
        assert tree.max_key == 0xFFFFFFFF
        assert tree.key_bits == 32

    def test_key_zero(self):
        """Can use key 0."""
        tree = LotusRadixN[str](levels=4)
        tree.set(0, "zero")
        assert tree.get(0) == "zero"

    def test_key_max(self):
        """Can use max key."""
        tree = LotusRadixN[str](levels=4)
        tree.set(0xFFFF, "max")
        assert tree.get(0xFFFF) == "max"

    def test_key_out_of_range_high(self):
        """Key above max raises ValueError."""
        tree = LotusRadixN[int](levels=4)
        with pytest.raises(ValueError):
            tree.set(0x10000, 1)

    def test_key_negative(self):
        """Negative key returns default on get."""
        tree = LotusRadixN[int](levels=4, default=-1)
        assert tree.get(-1) == -1


# =============================================================================
# Prefix Iteration (The Killer Feature)
# =============================================================================


class TestLotusRadixNPrefix:
    """Test prefix iteration - O(P+K) instead of O(N)."""

    def test_prefix_iter_finds_matching(self):
        """prefix_iter finds all keys with prefix."""
        tree = LotusRadixN[str](levels=4)
        # Insert keys in 0x12xx range (high nibble 1, second nibble 2)
        tree.set(0x1200, "a")
        tree.set(0x1234, "b")
        tree.set(0x12FF, "c")
        # Insert keys in other ranges
        tree.set(0x1300, "d")
        tree.set(0x0000, "e")

        # Find all 0x12xx keys (prefix 0x12 = 8 bits)
        # Note: prefix_iter expects the prefix in the HIGH bits
        results = list(tree.prefix_iter(0x1200, 8))
        keys = set(k for k, v in results)

        # All 0x12xx keys should be found
        assert len(keys) == 3
        assert 0x1200 in keys
        assert 0x1234 in keys
        assert 0x12FF in keys

    def test_prefix_iter_empty_prefix(self):
        """prefix_iter with no matching prefix yields nothing."""
        tree = LotusRadixN[str](levels=4)
        tree.set(0x1234, "a")

        results = list(tree.prefix_iter(0x5600, 8))
        assert len(results) == 0

    def test_prefix_bits_must_be_multiple_of_4(self):
        """prefix_bits must be multiple of BITS_PER_LEVEL."""
        tree = LotusRadixN[int](levels=4)
        with pytest.raises(ValueError):
            list(tree.prefix_iter(0x1200, 7))


# =============================================================================
# Factory Functions
# =============================================================================


class TestLotusFactories:
    """Test convenience factory functions."""

    def test_lotus_16bit(self):
        """lotus_16bit creates 4-level tree."""
        tree = lotus_16bit(default=-1)
        assert tree.levels == 4
        assert tree.key_bits == 16

    def test_lotus_32bit(self):
        """lotus_32bit creates 8-level tree."""
        tree = lotus_32bit()
        assert tree.levels == 8
        assert tree.key_bits == 32

    def test_lotus_64bit(self):
        """lotus_64bit creates 16-level tree."""
        tree = lotus_64bit()
        assert tree.levels == 16
        assert tree.key_bits == 64

    def test_lotus_128bit(self):
        """lotus_128bit creates 32-level tree."""
        tree = lotus_128bit()
        assert tree.levels == 32
        assert tree.key_bits == 128


# =============================================================================
# Validation Constraints
# =============================================================================


class TestLotusRadixNValidation:
    """Test input validation."""

    def test_levels_minimum(self):
        """levels must be at least 1."""
        with pytest.raises(ValueError):
            LotusRadixN[int](levels=0)

    def test_levels_maximum(self):
        """levels must be at most 64."""
        with pytest.raises(ValueError):
            LotusRadixN[int](levels=65)

    def test_levels_64_allowed(self):
        """levels=64 (256-bit) is allowed."""
        tree = LotusRadixN[int](levels=64)
        assert tree.key_bits == 256


# =============================================================================
# Sparse Allocation
# =============================================================================


class TestLotusRadixNSparse:
    """Test sparse allocation behavior."""

    def test_sparse_allocation(self):
        """Only allocates nodes for paths used."""
        tree = LotusRadixN[int](levels=4)
        # Insert just one key
        tree.set(0x1234, 1)
        # Tree should have minimal nodes, not full 16^4
        # This is implicit - we just verify it works
        assert tree.get(0x1234) == 1
        assert len(tree) == 1

    def test_many_keys_same_prefix(self):
        """Many keys with same prefix share nodes."""
        tree = LotusRadixN[int](levels=4)
        # Insert 256 keys in 0x12xx range
        for i in range(256):
            tree.set(0x1200 + i, i)
        assert len(tree) == 256
        # Verify all accessible
        for i in range(256):
            assert tree.get(0x1200 + i) == i


# =============================================================================
# Idempotency (GAD Compliance)
# =============================================================================


class TestLotusRadixNIdempotent:
    """Test idempotent behavior for GAD compliance."""

    def test_same_key_same_result(self):
        """Same key always returns same result."""
        tree = LotusRadixN[int](levels=4)
        tree.set(42, 137)
        assert tree.get(42) == tree.get(42) == tree.get(42) == 137

    def test_overwrite_updates_value(self):
        """Setting same key updates value."""
        tree = LotusRadixN[str](levels=4)
        tree.set(42, "first")
        tree.set(42, "second")
        assert tree.get(42) == "second"
        assert len(tree) == 1  # Still just one key


# =============================================================================
# Repr
# =============================================================================


class TestLotusRadixNRepr:
    """Test string representation."""

    def test_repr(self):
        """repr shows useful info."""
        tree = LotusRadixN[int](levels=4)
        tree.set(1, 1)
        tree.set(2, 2)
        r = repr(tree)
        assert "LotusRadixN" in r
        assert "levels=4" in r
        assert "size=2" in r
        assert "key_bits=16" in r
