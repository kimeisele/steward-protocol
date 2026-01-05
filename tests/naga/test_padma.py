"""
Tests for PadmaService - The Treasury Guardian.

Verifies:
- Basic cache get/set operations
- TTL expiration
- LRU eviction
- String and JSON convenience methods
- Pattern operations
- Bulk operations
- Memoization (get_or_compute)
- Statistics tracking
"""

import time

import pytest

from vibe_core.naga.services.padma import PadmaService


@pytest.fixture
def padma():
    """Create a PadmaService with small size for testing."""
    return PadmaService(max_size=10, default_ttl=None)


@pytest.fixture
def padma_with_ttl():
    """Create a PadmaService with default TTL."""
    return PadmaService(max_size=100, default_ttl=0.1)  # 100ms TTL


class TestPadmaBasics:
    """Basic initialization tests."""

    def test_initialization(self, padma):
        """Test service initializes correctly."""
        assert padma is not None
        assert padma._max_size == 10

    def test_get_status(self, padma):
        """Test get_status returns valid status."""
        status = padma.get_status()
        assert status is not None
        assert "entries=" in status.message
        assert "hit_rate=" in status.message


class TestBasicOperations:
    """Basic get/set tests."""

    def test_set_and_get(self, padma):
        """Test basic set and get."""
        padma.set("key1", b"value1")
        result = padma.get("key1")
        assert result == b"value1"

    def test_get_nonexistent_returns_none(self, padma):
        """Test getting non-existent key returns None."""
        result = padma.get("nonexistent")
        assert result is None

    def test_delete(self, padma):
        """Test deleting a key."""
        padma.set("to_delete", b"value")
        assert padma.get("to_delete") == b"value"

        success = padma.delete("to_delete")
        assert success is True
        assert padma.get("to_delete") is None

    def test_delete_nonexistent(self, padma):
        """Test deleting non-existent key returns False."""
        result = padma.delete("never_existed")
        assert result is False

    def test_exists(self, padma):
        """Test exists check."""
        padma.set("exists_key", b"value")
        assert padma.exists("exists_key") is True
        assert padma.exists("not_exists") is False

    def test_clear(self, padma):
        """Test clearing all entries."""
        padma.set("a", b"1")
        padma.set("b", b"2")
        padma.set("c", b"3")

        count = padma.clear()
        assert count == 3
        assert padma.get("a") is None
        assert padma.get("b") is None
        assert padma.get("c") is None


class TestStringAndJSON:
    """String and JSON convenience method tests."""

    def test_set_str_and_get_str(self, padma):
        """Test string convenience methods."""
        padma.set_str("str_key", "hello world")
        result = padma.get_str("str_key")
        assert result == "hello world"

    def test_set_json_and_get_json(self, padma):
        """Test JSON convenience methods."""
        data = {"name": "Padma", "count": 42, "active": True}
        padma.set_json("json_key", data)
        result = padma.get_json("json_key")
        assert result == data

    def test_get_str_nonexistent(self, padma):
        """Test get_str on non-existent key."""
        result = padma.get_str("not_there")
        assert result is None

    def test_get_json_nonexistent(self, padma):
        """Test get_json on non-existent key."""
        result = padma.get_json("not_there")
        assert result is None

    def test_get_json_invalid_json(self, padma):
        """Test get_json on non-JSON value."""
        padma.set_str("not_json", "this is not json")
        result = padma.get_json("not_json")
        assert result is None


class TestTTL:
    """TTL expiration tests."""

    def test_entry_expires_after_ttl(self, padma):
        """Test that entries expire after TTL."""
        padma.set("expires", b"value", ttl=0.05)  # 50ms TTL
        assert padma.get("expires") == b"value"

        time.sleep(0.06)  # Wait for expiry
        assert padma.get("expires") is None

    def test_default_ttl_applied(self, padma_with_ttl):
        """Test that default TTL is applied."""
        padma_with_ttl.set("default_ttl", b"value")
        assert padma_with_ttl.get("default_ttl") == b"value"

        time.sleep(0.15)  # Wait for 100ms default TTL
        assert padma_with_ttl.get("default_ttl") is None

    def test_explicit_ttl_overrides_default(self, padma_with_ttl):
        """Test that explicit TTL overrides default."""
        padma_with_ttl.set("long_ttl", b"value", ttl=1.0)  # 1 second
        time.sleep(0.15)  # Past default TTL
        assert padma_with_ttl.get("long_ttl") == b"value"  # Still there

    def test_exists_respects_ttl(self, padma):
        """Test that exists() checks TTL."""
        padma.set("check_exists", b"value", ttl=0.05)
        assert padma.exists("check_exists") is True

        time.sleep(0.06)
        assert padma.exists("check_exists") is False


class TestLRU:
    """LRU eviction tests."""

    def test_lru_eviction_at_capacity(self, padma):
        """Test LRU eviction when at capacity."""
        # Fill cache to capacity (10)
        for i in range(10):
            padma.set(f"key{i}", f"value{i}".encode())

        # All should exist
        for i in range(10):
            assert padma.exists(f"key{i}")

        # Add one more - should evict oldest (key0)
        padma.set("key10", b"value10")

        assert padma.get("key0") is None  # Evicted
        assert padma.get("key10") == b"value10"  # New entry exists

    def test_access_updates_lru_order(self, padma):
        """Test that accessing an entry updates LRU order."""
        # Fill cache
        for i in range(10):
            padma.set(f"key{i}", f"value{i}".encode())

        # Access key0 to make it recently used
        padma.get("key0")

        # Add new entry - should evict key1 (now oldest) instead of key0
        padma.set("key10", b"value10")

        assert padma.get("key0") == b"value0"  # Still exists (was accessed)
        assert padma.get("key1") is None  # Evicted

    def test_eviction_count_tracked(self, padma):
        """Test that evictions are counted."""
        # Fill and overflow
        for i in range(15):
            padma.set(f"key{i}", f"value{i}".encode())

        stats = padma.get_stats()
        assert stats.evictions == 5  # 5 entries evicted


class TestMemoization:
    """Memoization (get_or_compute) tests."""

    def test_get_or_compute_caches_result(self, padma):
        """Test that get_or_compute caches the computed value."""
        call_count = [0]

        def compute():
            call_count[0] += 1
            return b"computed_value"

        result1 = padma.get_or_compute("memo_key", compute)
        result2 = padma.get_or_compute("memo_key", compute)

        assert result1 == b"computed_value"
        assert result2 == b"computed_value"
        assert call_count[0] == 1  # Only called once

    def test_get_or_compute_with_ttl(self, padma):
        """Test get_or_compute with TTL."""
        call_count = [0]

        def compute():
            call_count[0] += 1
            return b"value"

        result1 = padma.get_or_compute("ttl_memo", compute, ttl=0.05)
        assert call_count[0] == 1

        time.sleep(0.06)  # Wait for expiry

        result2 = padma.get_or_compute("ttl_memo", compute, ttl=0.05)
        assert call_count[0] == 2  # Called again after expiry


class TestBulkOperations:
    """Bulk operation tests."""

    def test_get_many(self, padma):
        """Test getting multiple values."""
        padma.set("a", b"1")
        padma.set("b", b"2")
        padma.set("c", b"3")

        result = padma.get_many(["a", "b", "c", "d"])  # d doesn't exist
        assert result == {"a": b"1", "b": b"2", "c": b"3"}

    def test_set_many(self, padma):
        """Test setting multiple values."""
        items = {"x": b"10", "y": b"20", "z": b"30"}
        padma.set_many(items)

        assert padma.get("x") == b"10"
        assert padma.get("y") == b"20"
        assert padma.get("z") == b"30"

    def test_delete_many(self, padma):
        """Test deleting multiple keys."""
        padma.set("d1", b"1")
        padma.set("d2", b"2")
        padma.set("d3", b"3")

        count = padma.delete_many(["d1", "d2", "d4"])  # d4 doesn't exist
        assert count == 2

        assert padma.get("d1") is None
        assert padma.get("d2") is None
        assert padma.get("d3") == b"3"  # Not deleted


class TestPatternOperations:
    """Pattern-based operation tests."""

    def test_keys_all(self, padma):
        """Test getting all keys."""
        padma.set("key1", b"v1")
        padma.set("key2", b"v2")
        padma.set("other", b"v3")

        keys = padma.keys()
        assert set(keys) == {"key1", "key2", "other"}

    def test_keys_with_pattern(self, padma):
        """Test getting keys matching pattern."""
        padma.set("user:1", b"alice")
        padma.set("user:2", b"bob")
        padma.set("session:abc", b"data")

        keys = padma.keys("user:*")
        assert set(keys) == {"user:1", "user:2"}

    def test_delete_pattern(self, padma):
        """Test deleting keys by pattern."""
        padma.set("cache:a", b"1")
        padma.set("cache:b", b"2")
        padma.set("other", b"3")

        count = padma.delete_pattern("cache:*")
        assert count == 2

        assert padma.get("cache:a") is None
        assert padma.get("cache:b") is None
        assert padma.get("other") == b"3"


class TestStatistics:
    """Statistics tracking tests."""

    def test_hits_and_misses_tracked(self, padma):
        """Test that hits and misses are tracked."""
        padma.set("exists", b"value")

        padma.get("exists")  # Hit
        padma.get("exists")  # Hit
        padma.get("missing")  # Miss
        padma.get("missing")  # Miss
        padma.get("missing")  # Miss

        stats = padma.get_stats()
        assert stats.hits == 2
        assert stats.misses == 3

    def test_hit_rate_calculated(self, padma):
        """Test hit rate calculation."""
        padma.set("key", b"value")

        padma.get("key")  # Hit
        padma.get("key")  # Hit
        padma.get("key")  # Hit
        padma.get("key")  # Hit
        padma.get("miss")  # Miss

        stats = padma.get_stats()
        assert stats.hit_rate == 0.8  # 4 hits / 5 total = 80%

    def test_memory_bytes_estimated(self, padma):
        """Test memory usage estimation."""
        padma.set("key1", b"x" * 100)
        padma.set("key2", b"y" * 200)

        stats = padma.get_stats()
        assert stats.memory_bytes == 300


class TestHeartbeat:
    """Heartbeat update tests."""

    def test_heartbeat_updates_on_operations(self, padma):
        """Test that heartbeat updates on operations."""
        initial = padma._last_heartbeat

        time.sleep(0.01)
        padma.set("key", b"value")

        assert padma._last_heartbeat > initial

        time.sleep(0.01)
        padma.get("key")

        assert padma._last_heartbeat > initial
