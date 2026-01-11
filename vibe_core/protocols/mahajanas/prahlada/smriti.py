"""
SMRITI - Long-term Memory Protocol (Cache)
==========================================

OWNER: PRAHLADA (The Resilient One)
POSITION: 9 (KARMA Quarter)
OPCODE: EXEC_SERVICE

Smriti (Sanskrit: 'Memory', 'Remembrance') is long-term storage.
Like a cache - persistent, larger capacity, slower access.

SHASTRA BASIS:
    Smriti vs Chitta:
    - Chitta = working memory (volatile, fast, small)
    - Smriti = long-term memory (persistent, slow, large)

    In Vedic literature:
    - Shruti = "that which is heard" (Vedas - direct revelation)
    - Smriti = "that which is remembered" (derivative texts)

    Prahlada's smriti of Vishnu was so strong that even
    Hiranyakashipu's torture could not erase it.

CACHE STRATEGIES:
    - LRU: Least Recently Used eviction
    - LFU: Least Frequently Used eviction
    - TTL: Time-based expiration
    - FIFO: First In First Out

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

import hashlib
import json
import time
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Callable, Dict, Final, Iterator, List, Optional, Protocol, Tuple, runtime_checkable

from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode

from vibe_core.protocols.mahajanas.prahlada import (
    MemoryValue,
    MemoryEntry,
    MemoryState,
    AttackType,
    SurvivalResult,
)


# =============================================================================
# OWNERSHIP DECLARATION
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.PRAHLADA
LOTUS_POSITION: Final[int] = 9
LOTUS_QUARTER: Final[str] = "karma"

OWNED_OPCODES: Final[List[MantraOpCode]] = [
    MantraOpCode.EXEC_SERVICE,
]


# =============================================================================
# CACHE STRATEGY
# =============================================================================

class CacheStrategy(str, Enum):
    """Eviction strategies for the cache."""
    LRU = "lru"       # Least Recently Used
    LFU = "lfu"       # Least Frequently Used
    TTL = "ttl"       # Time-based only
    FIFO = "fifo"     # First In First Out


# =============================================================================
# SMRITI ENTRY
# =============================================================================

@dataclass
class SmritiEntry:
    """A long-term memory entry."""
    key: str
    value: MemoryValue
    value_type: str
    value_hash: str
    created_at: datetime
    expires_at: Optional[datetime]
    access_count: int = 0
    last_accessed: Optional[datetime] = None

    @classmethod
    def create(cls, key: str, value: MemoryValue, ttl_seconds: Optional[int] = None) -> "SmritiEntry":
        """Create a new entry."""
        now = datetime.now()
        value_type = type(value).__name__ if value is not None else "NoneType"

        if value is None:
            value_hash = hashlib.sha256(b"None").hexdigest()[:16]
        elif isinstance(value, bytes):
            value_hash = hashlib.sha256(value).hexdigest()[:16]
        else:
            value_hash = hashlib.sha256(str(value).encode()).hexdigest()[:16]

        expires_at = None
        if ttl_seconds and ttl_seconds > 0:
            expires_at = now + timedelta(seconds=ttl_seconds)

        return cls(
            key=key,
            value=value,
            value_type=value_type,
            value_hash=value_hash,
            created_at=now,
            expires_at=expires_at,
        )

    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def touch(self) -> None:
        """Update access metadata."""
        self.access_count += 1
        self.last_accessed = datetime.now()

    def to_memory_entry(self) -> MemoryEntry:
        """Convert to MemoryEntry for observability."""
        return MemoryEntry(
            key=self.key,
            value_type=self.value_type,
            value_repr=repr(self.value)[:100],
            value_hash=self.value_hash,
            stored_at=self.created_at.isoformat(),
            expires_at=self.expires_at.isoformat() if self.expires_at else "",
            access_count=self.access_count,
            last_accessed=self.last_accessed.isoformat() if self.last_accessed else "",
        )

    def size_bytes(self) -> int:
        """Estimate size in bytes."""
        base = 200
        if self.value is None:
            return base
        if isinstance(self.value, bytes):
            return base + len(self.value)
        if isinstance(self.value, str):
            return base + len(self.value.encode())
        return base + 8


# =============================================================================
# SMRITI PROTOCOL
# =============================================================================

@runtime_checkable
class SmritiProtocol(Protocol):
    """
    The Long-term Memory Protocol - Prahlada's Cache.

    OWNER: Mahajana.PRAHLADA

    This is PERSISTENT, LARGE memory:
    - Multiple eviction strategies
    - TTL support
    - Larger capacity than Chitta
    """

    @property
    def owner(self) -> Mahajana:
        """Always returns Mahajana.PRAHLADA."""
        ...

    @property
    def strategy(self) -> CacheStrategy:
        """Current cache strategy."""
        ...

    @property
    def capacity(self) -> int:
        """Maximum entries."""
        ...

    @property
    def size(self) -> int:
        """Current entries."""
        ...

    def store(self, key: str, value: MemoryValue, ttl_seconds: Optional[int] = None) -> bool:
        """Store a value."""
        ...

    def retrieve(self, key: str) -> Optional[MemoryValue]:
        """Retrieve a value."""
        ...

    def delete(self, key: str) -> bool:
        """Delete a value."""
        ...

    def exists(self, key: str) -> bool:
        """Check if key exists."""
        ...

    def clear(self) -> int:
        """Clear all entries."""
        ...

    def keys(self) -> List[str]:
        """Get all keys."""
        ...

    def get_state(self) -> MemoryState:
        """Get memory state."""
        ...


# =============================================================================
# SMRITI IMPLEMENTATION
# =============================================================================

class Smriti:
    """
    Prahlada's Long-term Memory - The Cache.

    OWNER: Mahajana.PRAHLADA

    Features:
    - Multiple eviction strategies (LRU, LFU, TTL, FIFO)
    - Large capacity
    - Persistent patterns
    """

    def __init__(
        self,
        capacity: int = 10000,
        strategy: CacheStrategy = CacheStrategy.LRU,
        default_ttl_seconds: Optional[int] = None,
    ) -> None:
        """Initialize long-term memory."""
        self._capacity = capacity
        self._strategy = strategy
        self._default_ttl = default_ttl_seconds
        self._storage: Dict[str, SmritiEntry] = {}
        self._access_order: List[str] = []  # For LRU/FIFO
        self._stats = {"hits": 0, "misses": 0}

    @property
    def owner(self) -> Mahajana:
        return Mahajana.PRAHLADA

    @property
    def strategy(self) -> CacheStrategy:
        return self._strategy

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def size(self) -> int:
        return len(self._storage)

    def store(self, key: str, value: MemoryValue, ttl_seconds: Optional[int] = None) -> bool:
        """Store a value in long-term memory."""
        # Use default TTL if not specified
        if ttl_seconds is None:
            ttl_seconds = self._default_ttl

        # Evict if at capacity
        while len(self._storage) >= self._capacity:
            self._evict()

        # Create and store entry
        entry = SmritiEntry.create(key, value, ttl_seconds)
        self._storage[key] = entry

        # Update access order
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)

        return True

    def retrieve(self, key: str) -> Optional[MemoryValue]:
        """Retrieve a value from long-term memory."""
        entry = self._storage.get(key)
        if entry is None:
            self._stats["misses"] += 1
            return None

        # Check expiration
        if entry.is_expired():
            del self._storage[key]
            if key in self._access_order:
                self._access_order.remove(key)
            self._stats["misses"] += 1
            return None

        # Update access metadata
        entry.touch()
        self._stats["hits"] += 1

        # Update access order for LRU
        if self._strategy == CacheStrategy.LRU:
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)

        return entry.value

    def delete(self, key: str) -> bool:
        """Delete a value."""
        if key in self._storage:
            del self._storage[key]
            if key in self._access_order:
                self._access_order.remove(key)
            return True
        return False

    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        entry = self._storage.get(key)
        if entry is None:
            return False
        if entry.is_expired():
            del self._storage[key]
            return False
        return True

    def clear(self) -> int:
        """Clear all entries."""
        count = len(self._storage)
        self._storage.clear()
        self._access_order.clear()
        return count

    def keys(self) -> List[str]:
        """Get all valid keys."""
        # Remove expired while iterating
        valid_keys: List[str] = []
        for key in list(self._storage.keys()):
            entry = self._storage[key]
            if entry.is_expired():
                del self._storage[key]
            else:
                valid_keys.append(key)
        return valid_keys

    def _evict(self) -> None:
        """Evict one entry based on strategy."""
        if not self._storage:
            return

        if self._strategy == CacheStrategy.LRU:
            # Evict least recently used
            if self._access_order:
                key = self._access_order.pop(0)
                self._storage.pop(key, None)

        elif self._strategy == CacheStrategy.LFU:
            # Evict least frequently used
            min_count = float('inf')
            min_key = None
            for key, entry in self._storage.items():
                if entry.access_count < min_count:
                    min_count = entry.access_count
                    min_key = key
            if min_key:
                del self._storage[min_key]
                if min_key in self._access_order:
                    self._access_order.remove(min_key)

        elif self._strategy == CacheStrategy.FIFO:
            # Evict first in
            if self._access_order:
                key = self._access_order.pop(0)
                self._storage.pop(key, None)

        elif self._strategy == CacheStrategy.TTL:
            # Evict oldest (by creation time)
            oldest_key = None
            oldest_time = datetime.now()
            for key, entry in self._storage.items():
                if entry.created_at < oldest_time:
                    oldest_time = entry.created_at
                    oldest_key = key
            if oldest_key:
                del self._storage[oldest_key]
                if oldest_key in self._access_order:
                    self._access_order.remove(oldest_key)

    def get_state(self) -> MemoryState:
        """Get memory state for observability."""
        entries = {k: e.to_memory_entry() for k, e in self._storage.items() if not e.is_expired()}
        total_size = sum(e.size_bytes() for e in self._storage.values())

        timestamps = [e.created_at for e in self._storage.values()]
        oldest = min(timestamps).isoformat() if timestamps else ""
        newest = max(timestamps).isoformat() if timestamps else ""

        hit_rate = self._stats["hits"] / max(1, self._stats["hits"] + self._stats["misses"])
        health = "healthy" if hit_rate > 0.5 else "degraded" if hit_rate > 0.2 else "critical"

        return MemoryState(
            entries=entries,
            total_count=len(self._storage),
            total_size_bytes=total_size,
            oldest_entry=oldest,
            newest_entry=newest,
            health=health,
        )


# =============================================================================
# NULL SMRITI
# =============================================================================

class NullSmriti:
    """Null long-term memory - no persistence."""

    @property
    def owner(self) -> Mahajana:
        return Mahajana.PRAHLADA

    @property
    def strategy(self) -> CacheStrategy:
        return CacheStrategy.LRU

    @property
    def capacity(self) -> int:
        return 0

    @property
    def size(self) -> int:
        return 0

    def store(self, key: str, value: MemoryValue, ttl_seconds: Optional[int] = None) -> bool:
        return True

    def retrieve(self, key: str) -> Optional[MemoryValue]:
        return None

    def delete(self, key: str) -> bool:
        return False

    def exists(self, key: str) -> bool:
        return False

    def clear(self) -> int:
        return 0

    def keys(self) -> List[str]:
        return []

    def get_state(self) -> MemoryState:
        return MemoryState(entries={}, total_count=0, total_size_bytes=0, health="pristine")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "OWNER", "LOTUS_POSITION", "LOTUS_QUARTER", "OWNED_OPCODES",
    "CacheStrategy",
    "SmritiEntry",
    "SmritiProtocol",
    "Smriti",
    "NullSmriti",
]
