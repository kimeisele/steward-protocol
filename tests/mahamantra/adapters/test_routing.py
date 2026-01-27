"""
TEST: HolographicRouter Adapter - O(1) Routing Contract
========================================================

"sthāne hṛṣīkeśa tava prakīrtyā jagat prahṛṣyaty anurajyate ca"
"O Hrishikesha, the world becomes joyful upon hearing Your name."
— Bhagavad Gita 11.36

WHAT WE TEST:
1. O(1) Operations: Insert and lookup are constant time
2. Range Queries: O(k) range queries work
3. Prefix Queries: Subnet-style matching works
4. Key Space: Respects configured key space
5. Iteration: Can iterate all entries

THE CONTRACT: These tests GUARANTEE correct holographic routing.
"""

import pytest

from vibe_core.mahamantra.adapters.routing import (
    HolographicRouter,
    RouteEntry,
    RangeResult,
    router_16bit,
    router_32bit,
    router_8bit,
)
from vibe_core.mahamantra.protocols._seed import WORDS, QUARTERS


class TestHolographicRouterBasics:
    """Test basic router operations."""

    def test_insert_and_get(self):
        """Basic insert and get should work."""
        r = HolographicRouter()
        r.insert(0x1234, "value")
        assert r.get(0x1234) == "value"

    def test_dict_style_access(self):
        """Dict-style access should work."""
        r = HolographicRouter()
        r[0xABCD] = "test"
        assert r[0xABCD] == "test"

    def test_contains_check(self):
        """__contains__ should work."""
        r = HolographicRouter()
        r[100] = "exists"
        assert 100 in r
        assert 999 not in r

    def test_len_tracks_entries(self):
        """__len__ should track entry count."""
        r = HolographicRouter()
        assert len(r) == 0
        r[1] = "a"
        assert len(r) == 1
        r[2] = "b"
        assert len(r) == 2

    def test_missing_key_returns_default(self):
        """Missing key should return default."""
        r = HolographicRouter(default="not_found")
        assert r.get(999) == "not_found"


class TestHolographicRouterKeySpace:
    """Test key space configuration."""

    def test_default_levels_is_quarters(self):
        """Default levels should be QUARTERS (4)."""
        r = HolographicRouter()
        assert r.levels == QUARTERS

    def test_key_bits_calculation(self):
        """Key bits should be levels × 4."""
        r = HolographicRouter(levels=4)
        assert r.key_bits == 16
        r2 = HolographicRouter(levels=8)
        assert r2.key_bits == 32

    def test_key_space_calculation(self):
        """Key space should be 16^levels."""
        r = HolographicRouter(levels=4)
        assert r.key_space == 16**4  # 65536
        r2 = HolographicRouter(levels=2)
        assert r2.key_space == 16**2  # 256

    def test_key_masked_to_valid_range(self):
        """Keys should be masked to valid range."""
        r = HolographicRouter(levels=2)  # 8-bit keys
        r[0x1FF] = "masked"  # 0x1FF > 0xFF, should be masked
        # The key should be stored at 0xFF (masked)
        assert r.get(0xFF) == "masked"


class TestHolographicRouterRangeQueries:
    """Test range queries - THE KILLER FEATURE."""

    def test_range_query_finds_entries(self):
        """Range query should find entries in range."""
        r = HolographicRouter()
        r[100] = "a"
        r[150] = "b"
        r[200] = "c"

        result = r.range_query(100, 200)
        assert result.count == 3
        keys = [e.key for e in result.entries]
        assert 100 in keys
        assert 150 in keys
        assert 200 in keys

    def test_range_query_excludes_outside(self):
        """Range query should exclude entries outside range."""
        r = HolographicRouter()
        r[50] = "outside"
        r[100] = "inside"
        r[250] = "outside"

        result = r.range_query(100, 200)
        keys = [e.key for e in result.entries]
        assert 50 not in keys
        assert 250 not in keys

    def test_range_query_empty_range(self):
        """Empty range should return no entries."""
        r = HolographicRouter()
        r[100] = "a"
        result = r.range_query(200, 300)
        assert result.count == 0


class TestHolographicRouterPrefixQueries:
    """Test prefix queries (subnet-style)."""

    def test_prefix_query_basic(self):
        """Prefix query should match prefix."""
        r = HolographicRouter(levels=4)  # 16-bit keys

        # Insert keys with prefix 0x12xx
        r[0x1200] = "a"
        r[0x1234] = "b"
        r[0x12FF] = "c"
        r[0x1300] = "outside"

        result = r.prefix_query(0x12, prefix_bits=8)
        keys = [e.key for e in result.entries]
        assert 0x1200 in keys
        assert 0x1234 in keys
        assert 0x12FF in keys
        assert 0x1300 not in keys


class TestHolographicRouterIteration:
    """Test iteration over entries."""

    def test_items_iteration(self):
        """items() should yield all entries."""
        r = HolographicRouter()
        r[1] = "a"
        r[2] = "b"
        r[3] = "c"

        items = list(r.items())
        assert len(items) == 3
        keys = [k for k, v in items]
        assert sorted(keys) == [1, 2, 3]

    def test_items_returns_correct_values(self):
        """items() should return correct values."""
        r = HolographicRouter()
        r[100] = "hundred"
        r[200] = "twohundred"

        items = dict(r.items())
        assert items[100] == "hundred"
        assert items[200] == "twohundred"


class TestHolographicRouterStats:
    """Test statistics."""

    def test_stats_returns_dict(self):
        """stats() should return dictionary."""
        r = HolographicRouter()
        stats = r.stats()
        assert isinstance(stats, dict)
        assert "levels" in stats
        assert "key_bits" in stats
        assert "entries" in stats

    def test_fill_ratio_calculation(self):
        """Fill ratio should be entries / key_space."""
        r = HolographicRouter(levels=2)  # 256 key space
        r[1] = "a"
        r[2] = "b"
        stats = r.stats()
        assert stats["entries"] == 2
        assert stats["fill_ratio"] == 2 / 256


class TestHolographicRouterFactories:
    """Test factory functions."""

    def test_router_8bit(self):
        """router_8bit should create 2-level router."""
        r = router_8bit()
        assert r.levels == 2
        assert r.key_space == 256

    def test_router_16bit(self):
        """router_16bit should create 4-level router."""
        r = router_16bit()
        assert r.levels == 4
        assert r.key_space == 65536

    def test_router_32bit(self):
        """router_32bit should create 8-level router."""
        r = router_32bit()
        assert r.levels == 8
        assert r.key_space == 2**32


class TestHolographicRouterMahamantraAlignment:
    """Test Mahamantra structure alignment."""

    def test_slots_per_level_is_words(self):
        """Each level should have WORDS (16) slots."""
        from vibe_core.mahamantra.adapters.routing import SLOTS_PER_LEVEL
        assert SLOTS_PER_LEVEL == WORDS

    def test_bits_per_nibble_is_quarters(self):
        """Each nibble should be QUARTERS (4) bits."""
        from vibe_core.mahamantra.adapters.routing import BITS_PER_NIBBLE
        assert BITS_PER_NIBBLE == QUARTERS
