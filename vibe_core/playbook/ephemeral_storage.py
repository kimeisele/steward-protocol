"""
Ephemeral Storage - Session-based Cache for Query Responses.

NEURO-SYMBOLIC ARCHITECTURE:
- Caches query responses with TTL
- Enables circuits to store/retrieve computed results
- No external dependencies (in-memory + optional disk backup)

USAGE:
    from vibe_core.playbook.ephemeral_storage import EphemeralStorage

    storage = EphemeralStorage()

    # Store with TTL
    storage.set("status_summary", {"agents": 8, "status": "running"}, ttl_seconds=300)

    # Retrieve (returns None if expired)
    result = storage.get("status_summary")

    # Query by tag
    results = storage.query_by_tag("status")
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0xd177108f"  # GenesisByte: parampara % 37 == 0

import hashlib
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("EPHEMERAL_STORAGE")


@dataclass
class CacheEntry:
    """Single cache entry with metadata."""

    key: str
    value: Any
    created_at: float
    ttl_seconds: int
    tags: List[str] = field(default_factory=list)
    access_count: int = 0
    last_accessed: float = 0.0

    def is_expired(self) -> bool:
        """Check if entry has expired."""
        return time.time() > (self.created_at + self.ttl_seconds)

    def age_seconds(self) -> float:
        """Get age in seconds."""
        return time.time() - self.created_at

    def remaining_ttl(self) -> float:
        """Get remaining TTL in seconds."""
        return max(0, (self.created_at + self.ttl_seconds) - time.time())


class EphemeralStorage:
    """
    Session-based in-memory cache with optional disk persistence.

    Features:
    - TTL-based expiration
    - Tag-based retrieval
    - Automatic cleanup
    - Cache hit/miss tracking
    - Optional disk backup for crash recovery

    Philosophy:
    - Fast in-memory access for active session
    - No dependencies (stdlib only)
    - Deterministic behavior (same input = same cached output)
    """

    def __init__(
        self,
        kernel=None,
        backup_dir: Optional[Path] = None,
        max_entries: int = 1000,
        default_ttl: int = 300,
    ):
        """
        Initialize ephemeral storage.

        Args:
            kernel: Optional kernel reference for sandbox path
            backup_dir: Optional disk backup directory
            max_entries: Maximum cache entries before cleanup
            default_ttl: Default TTL in seconds (5 min)
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._kernel = kernel
        self._backup_dir = backup_dir
        self._max_entries = max_entries
        self._default_ttl = default_ttl

        # Statistics
        self._hits = 0
        self._misses = 0
        self._evictions = 0

        logger.info(f"EphemeralStorage initialized (max={max_entries}, default_ttl={default_ttl}s)")

    # =========================================================================
    # CORE OPERATIONS
    # =========================================================================

    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """
        Store a value with TTL.

        Args:
            key: Cache key
            value: Value to store (must be JSON-serializable)
            ttl_seconds: Time-to-live in seconds (default: 300)
            tags: Optional tags for grouped retrieval

        Returns:
            The cache key
        """
        if ttl_seconds is None:
            ttl_seconds = self._default_ttl

        # Enforce max entries
        if len(self._cache) >= self._max_entries:
            self._evict_expired()
            if len(self._cache) >= self._max_entries:
                self._evict_lru(count=max(1, self._max_entries // 10))

        entry = CacheEntry(
            key=key,
            value=value,
            created_at=time.time(),
            ttl_seconds=ttl_seconds,
            tags=tags or [],
            access_count=0,
            last_accessed=time.time(),
        )

        self._cache[key] = entry
        logger.debug(f"Cache SET: {key} (ttl={ttl_seconds}s, tags={tags})")

        return key

    def get(self, key: str, default: Any = None) -> Optional[Any]:
        """
        Retrieve a value if not expired.

        Args:
            key: Cache key
            default: Value to return if not found or expired

        Returns:
            Cached value or default
        """
        entry = self._cache.get(key)

        if entry is None:
            self._misses += 1
            logger.debug(f"Cache MISS: {key}")
            return default

        if entry.is_expired():
            self._misses += 1
            del self._cache[key]
            logger.debug(f"Cache EXPIRED: {key}")
            return default

        # Update access stats
        entry.access_count += 1
        entry.last_accessed = time.time()
        self._hits += 1

        logger.debug(f"Cache HIT: {key} (age={entry.age_seconds():.1f}s)")
        return entry.value

    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        entry = self._cache.get(key)
        if entry is None:
            return False
        if entry.is_expired():
            del self._cache[key]
            return False
        return True

    def delete(self, key: str) -> bool:
        """Delete a cache entry."""
        if key in self._cache:
            del self._cache[key]
            logger.debug(f"Cache DELETE: {key}")
            return True
        return False

    def clear(self) -> int:
        """Clear all cache entries. Returns count of cleared entries."""
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"Cache CLEARED: {count} entries")
        return count

    # =========================================================================
    # TAG-BASED OPERATIONS
    # =========================================================================

    def query_by_tag(self, tag: str) -> List[Any]:
        """
        Find all non-expired values with given tag.

        Args:
            tag: Tag to search for

        Returns:
            List of values with the tag
        """
        results = []
        expired_keys = []

        for key, entry in self._cache.items():
            if entry.is_expired():
                expired_keys.append(key)
                continue
            if tag in entry.tags:
                results.append(entry.value)

        # Cleanup expired
        for key in expired_keys:
            del self._cache[key]

        return results

    def get_keys_by_tag(self, tag: str) -> List[str]:
        """Get all keys with given tag."""
        return [key for key, entry in self._cache.items() if tag in entry.tags and not entry.is_expired()]

    # =========================================================================
    # CACHE MANAGEMENT
    # =========================================================================

    def _evict_expired(self) -> int:
        """Remove all expired entries. Returns count evicted."""
        expired = [k for k, v in self._cache.items() if v.is_expired()]
        for key in expired:
            del self._cache[key]
        self._evictions += len(expired)
        if expired:
            logger.debug(f"Evicted {len(expired)} expired entries")
        return len(expired)

    def _evict_lru(self, count: int = 100) -> int:
        """Remove least-recently-used entries. Returns count evicted."""
        if not self._cache:
            return 0

        # Sort by last_accessed (oldest first)
        sorted_keys = sorted(self._cache.keys(), key=lambda k: self._cache[k].last_accessed)

        evict_keys = sorted_keys[:count]
        for key in evict_keys:
            del self._cache[key]

        self._evictions += len(evict_keys)
        logger.debug(f"Evicted {len(evict_keys)} LRU entries")
        return len(evict_keys)

    def cleanup(self) -> int:
        """Run cleanup (evict expired). Returns count evicted."""
        return self._evict_expired()

    # =========================================================================
    # STATISTICS
    # =========================================================================

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0.0

        return {
            "entries": len(self._cache),
            "max_entries": self._max_entries,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(hit_rate, 2),
            "evictions": self._evictions,
        }

    def get_entry_info(self, key: str) -> Optional[Dict[str, Any]]:
        """Get metadata about a cache entry."""
        entry = self._cache.get(key)
        if entry is None:
            return None

        return {
            "key": entry.key,
            "created_at": datetime.fromtimestamp(entry.created_at).isoformat(),
            "ttl_seconds": entry.ttl_seconds,
            "age_seconds": round(entry.age_seconds(), 1),
            "remaining_ttl": round(entry.remaining_ttl(), 1),
            "is_expired": entry.is_expired(),
            "access_count": entry.access_count,
            "tags": entry.tags,
        }

    # =========================================================================
    # CONVENIENCE METHODS
    # =========================================================================

    def get_or_set(
        self,
        key: str,
        factory: callable,
        ttl_seconds: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> Any:
        """
        Get from cache or compute and store.

        Args:
            key: Cache key
            factory: Callable to produce value if not cached
            ttl_seconds: TTL for new entry
            tags: Tags for new entry

        Returns:
            Cached or computed value
        """
        value = self.get(key)
        if value is not None:
            return value

        # Compute and store
        value = factory()
        self.set(key, value, ttl_seconds=ttl_seconds, tags=tags)
        return value

    @staticmethod
    def make_cache_key(*parts) -> str:
        """
        Create a deterministic cache key from parts.

        Args:
            *parts: String parts to hash together

        Returns:
            Hex digest cache key
        """
        combined = "|".join(str(p) for p in parts)
        return hashlib.sha256(combined.encode()).hexdigest()[:16]


# =============================================================================
# DEPRECATED: Global singleton pattern removed (OPUS Refactor Phase 2)
# Use dependency injection instead - get EphemeralStorage from kernel.envoy
# =============================================================================
