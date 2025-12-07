"""
Unit tests for EphemeralStorage (OPUS Phase 2).

Tests isolation, lifecycle, and cache behavior.
"""

import time

from vibe_core.playbook.ephemeral_storage import EphemeralStorage


def test_storage_isolates_per_instance():
    """Each EphemeralStorage instance should have isolated state."""
    s1 = EphemeralStorage()
    s2 = EphemeralStorage()

    s1.set("key", "value1")
    s2.set("key", "value2")

    assert s1.get("key") == "value1"
    assert s2.get("key") == "value2"


def test_storage_clears_on_shutdown():
    """Storage should clear all entries on clear()."""
    storage = EphemeralStorage()

    storage.set("key1", "value1")
    storage.set("key2", "value2")
    storage.set("key3", "value3")

    assert len(storage._cache) == 3

    cleared_count = storage.clear()

    assert cleared_count == 3
    assert len(storage._cache) == 0
    assert storage.get("key1") is None


def test_storage_ttl_expiration():
    """Entries should expire after TTL."""
    storage = EphemeralStorage(default_ttl=1)

    storage.set("key", "value", ttl_seconds=1)

    # Should exist immediately
    assert storage.get("key") == "value"

    # Wait for expiration
    time.sleep(1.1)

    # Should be None after expiration
    assert storage.get("key") is None


def test_storage_returns_default_when_missing():
    """Storage should return default value when key doesn't exist."""
    storage = EphemeralStorage()

    result = storage.get("nonexistent", default="fallback")

    assert result == "fallback"


def test_storage_delete():
    """Storage should delete entries."""
    storage = EphemeralStorage()

    storage.set("key", "value")
    assert storage.exists("key")

    deleted = storage.delete("key")
    assert deleted is True
    assert not storage.exists("key")


def test_storage_query_by_tag():
    """Storage should retrieve entries by tag."""
    storage = EphemeralStorage()

    storage.set("key1", "value1", tags=["agent", "status"])
    storage.set("key2", "value2", tags=["agent", "metrics"])
    storage.set("key3", "value3", tags=["circuit"])

    agent_results = storage.query_by_tag("agent")
    assert len(agent_results) == 2
    assert "value1" in agent_results
    assert "value2" in agent_results

    circuit_results = storage.query_by_tag("circuit")
    assert len(circuit_results) == 1
    assert "value3" in circuit_results


def test_storage_get_or_set():
    """Storage should compute and cache values with get_or_set."""
    storage = EphemeralStorage()

    call_count = 0

    def factory():
        nonlocal call_count
        call_count += 1
        return "computed_value"

    # First call: should compute
    result1 = storage.get_or_set("key", factory)
    assert result1 == "computed_value"
    assert call_count == 1

    # Second call: should use cache
    result2 = storage.get_or_set("key", factory)
    assert result2 == "computed_value"
    assert call_count == 1  # Factory not called again


def test_storage_eviction_lru():
    """Storage should evict LRU entries when at capacity."""
    storage = EphemeralStorage(max_entries=5)

    # Fill to capacity
    for i in range(5):
        storage.set(f"key{i}", f"value{i}")

    # Add one more - should trigger eviction
    storage.set("key5", "value5")

    # Should have max_entries
    assert len(storage._cache) <= 5


def test_storage_stats():
    """Storage should track hit/miss statistics."""
    storage = EphemeralStorage()

    storage.set("key", "value")

    # Hit
    storage.get("key")

    # Miss
    storage.get("nonexistent")

    stats = storage.get_stats()

    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["entries"] == 1
