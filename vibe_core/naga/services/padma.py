"""
PADMA SERVICE - Der Schatzmeister.

Padma - The Lotus Naga who guards treasures in the underworld.

From mythology: Padma (Lotus) represents purity rising from mud,
and the Naga Padma guards wealth and treasures.

Responsibilities:
- In-memory cache with TTL and LRU eviction
- Treasury pattern for memoizing expensive computations
- Cache statistics for Chitragupta monitoring
- Pattern-based key operations

Integration:
- All NAGAs can use for performance optimization
- Chitragupta monitors cache hit rates
"""

import fnmatch
import json
import logging
import sys
import time
from collections import OrderedDict
from datetime import datetime
from threading import Lock
from typing import Callable, Dict, List, Optional

from vibe_core.naga.kulika import (
    NagaCapability,
    NagaLord,
    naga_service,
)
from vibe_core.naga.services.base import NagaBaseService, naga_governed
from vibe_core.protocols.naga import (
    CacheStats,
    NagaStatus,
    NagaType,
    PadmaProtocol,
)

logger = logging.getLogger("PADMA")


@naga_service(
    name="Padma",
    lord=NagaLord.PADMA,
    drift_source=None,  # Pure cache, no drift handling
    priority=80,
    capabilities=[NagaCapability.CACHE],
    protocol_class="vibe_core.protocols.naga.PadmaProtocol",
)
class PadmaService(NagaBaseService, PadmaProtocol):
    """
    Padma - The Treasury Guardian.

    LRU cache with TTL support and statistics tracking.
    Thread-safe for concurrent access.


    OUROBOROS: Inherits NagaBaseService for self-monitoring."""

    def __init__(
        self,
        max_size: int = 10000,
        default_ttl: Optional[float] = None,
    ) -> None:
        """
        Initialize Padma.

        Args:
            max_size: Maximum number of entries (LRU eviction after)
            default_ttl: Default TTL in seconds (None = no expiry)
        """
        super().__init__(service_name="Padma")
        self._max_size = max_size
        self._default_ttl = default_ttl

        # LRU cache using OrderedDict
        self._cache: OrderedDict[str, bytes] = OrderedDict()
        self._expiry: Dict[str, float] = {}  # key -> expiry timestamp
        self._lock = Lock()

        # Statistics
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        self._last_heartbeat = datetime.now()

        logger.info(f"PADMA initialized - Treasury ready (max={max_size})")

    # =========================================================================
    # Basic Cache Operations
    # =========================================================================

    @naga_governed(operation="cache_get")
    def get(self, key: str) -> Optional[bytes]:
        """Get a value from cache."""
        self._last_heartbeat = datetime.now()

        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None

            # Check expiry
            if key in self._expiry and time.time() > self._expiry[key]:
                self._delete_internal(key)
                self._misses += 1
                return None

            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self._hits += 1
            return self._cache[key]

    def get_str(self, key: str) -> Optional[str]:
        """Get a string value from cache."""
        value = self.get(key)
        if value is None:
            return None
        return value.decode("utf-8")

    def get_json(self, key: str) -> Optional[Dict[str, object]]:
        """Get a JSON-deserializable value from cache."""
        value = self.get_str(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return None

    @naga_governed(operation="cache_set")
    def set(self, key: str, value: bytes, ttl: Optional[float] = None) -> None:
        """Store bytes in cache."""
        self._last_heartbeat = datetime.now()
        actual_ttl = ttl if ttl is not None else self._default_ttl

        with self._lock:
            # Evict if at capacity and key is new
            if key not in self._cache and len(self._cache) >= self._max_size:
                self._evict_lru()

            self._cache[key] = value
            self._cache.move_to_end(key)

            if actual_ttl is not None:
                self._expiry[key] = time.time() + actual_ttl
            elif key in self._expiry:
                del self._expiry[key]

    def set_str(self, key: str, value: str, ttl: Optional[float] = None) -> None:
        """Store a string in cache."""
        self.set(key, value.encode("utf-8"), ttl)

    def set_json(self, key: str, value: Dict[str, object], ttl: Optional[float] = None) -> None:
        """Store a JSON-serializable dict in cache."""
        self.set_str(key, json.dumps(value), ttl)

    def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        self._last_heartbeat = datetime.now()

        with self._lock:
            return self._delete_internal(key)

    def _delete_internal(self, key: str) -> bool:
        """Internal delete without lock."""
        if key in self._cache:
            del self._cache[key]
            self._expiry.pop(key, None)
            return True
        return False

    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        self._last_heartbeat = datetime.now()

        with self._lock:
            if key not in self._cache:
                return False
            if key in self._expiry and time.time() > self._expiry[key]:
                self._delete_internal(key)
                return False
            return True

    def clear(self) -> int:
        """Clear all cache entries."""
        self._last_heartbeat = datetime.now()

        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self._expiry.clear()
            return count

    def _evict_lru(self) -> None:
        """Evict least recently used entry (internal, must hold lock)."""
        if self._cache:
            oldest_key = next(iter(self._cache))
            self._delete_internal(oldest_key)
            self._evictions += 1

    # =========================================================================
    # Treasury (Memoization)
    # =========================================================================

    def get_or_compute(
        self,
        key: str,
        compute_fn: Callable[[], bytes],
        ttl: Optional[float] = None,
    ) -> bytes:
        """Get from cache or compute and store."""
        self._last_heartbeat = datetime.now()

        # Try cache first
        value = self.get(key)
        if value is not None:
            return value

        # Compute and store
        computed = compute_fn()
        self.set(key, computed, ttl)
        return computed

    # =========================================================================
    # Bulk Operations
    # =========================================================================

    def get_many(self, keys: List[str]) -> Dict[str, bytes]:
        """Get multiple values at once."""
        result: Dict[str, bytes] = {}
        for key in keys:
            value = self.get(key)
            if value is not None:
                result[key] = value
        return result

    def set_many(self, items: Dict[str, bytes], ttl: Optional[float] = None) -> None:
        """Store multiple values at once."""
        for key, value in items.items():
            self.set(key, value, ttl)

    def delete_many(self, keys: List[str]) -> int:
        """Delete multiple keys."""
        count = 0
        for key in keys:
            if self.delete(key):
                count += 1
        return count

    # =========================================================================
    # Pattern Operations
    # =========================================================================

    def keys(self, pattern: Optional[str] = None) -> List[str]:
        """Get all keys matching pattern."""
        self._last_heartbeat = datetime.now()

        with self._lock:
            # Clean expired first
            now = time.time()
            expired = [k for k, exp in self._expiry.items() if exp < now]
            for k in expired:
                self._delete_internal(k)

            if pattern is None:
                return list(self._cache.keys())

            return [k for k in self._cache.keys() if fnmatch.fnmatch(k, pattern)]

    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        matching = self.keys(pattern)
        return self.delete_many(matching)

    # =========================================================================
    # Statistics
    # =========================================================================

    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        with self._lock:
            total = self._hits + self._misses
            hit_rate = self._hits / total if total > 0 else 0.0

            # Estimate memory (rough)
            memory = sum(len(v) for v in self._cache.values())

            return CacheStats(
                total_entries=len(self._cache),
                hits=self._hits,
                misses=self._misses,
                evictions=self._evictions,
                hit_rate=hit_rate,
                memory_bytes=memory,
            )

    def get_status(self) -> NagaStatus:
        """Get NAGA health status."""
        stats = self.get_stats()
        return NagaStatus(
            naga_type=NagaType.SESHA,  # No PADMA in NagaType
            healthy=True,
            last_heartbeat=self._last_heartbeat,
            events_processed=self._hits + self._misses,
            errors=0,
            message=f"entries={stats.total_entries}, hit_rate={stats.hit_rate:.1%}",
        )
