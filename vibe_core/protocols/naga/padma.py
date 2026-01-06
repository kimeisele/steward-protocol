"""
PADMA Protocol - Der Schatzmeister (Cache Protocol)

Padma (Lotus) - Guardian of the Treasury.
From mythology: The Naga Padma guards treasures in the underworld.

Responsibilities:
- In-memory cache with TTL
- LRU eviction policy
- Treasury for expensive computations
- Cache warming and invalidation
- Statistics and monitoring

Integration:
- Does NOT register as CorrectionHandler (pure cache)
- All NAGAs can use for performance optimization
- Chitragupta monitors cache performance
"""

from dataclasses import dataclass
from typing import Callable, Dict, Generic, List, Optional, Protocol, TypeVar, runtime_checkable

from vibe_core.protocols.naga.types import NagaStatus, NagaType

CacheValue = TypeVar("CacheValue")


@dataclass
class CacheEntry(Generic[CacheValue]):
    """A cached value with metadata."""

    key: str
    value: CacheValue
    created_at: float
    expires_at: Optional[float] = None
    hits: int = 0


@dataclass
class CacheStats:
    """Cache statistics."""

    total_entries: int
    hits: int
    misses: int
    evictions: int
    hit_rate: float
    memory_bytes: int = 0


@runtime_checkable
class PadmaProtocol(Protocol):
    """
    Padma - Der Schatzmeister. Guardian of the Treasury.

    Usage:
        padma = ServiceRegistry.get(PadmaProtocol)
        padma.set("key", expensive_value, ttl=300)
        value = padma.get("key")

    Note: Cache stores bytes/str/int/float/dict/list - serializable types.
    """

    # === Basic Cache Operations ===

    def get(self, key: str) -> Optional[bytes]:
        """Get a value from cache."""
        ...

    def get_str(self, key: str) -> Optional[str]:
        """Get a string value from cache."""
        ...

    def get_json(self, key: str) -> Optional[Dict[str, object]]:
        """Get a JSON-deserializable value from cache."""
        ...

    def set(self, key: str, value: bytes, ttl: Optional[float] = None) -> None:
        """Store bytes in cache."""
        ...

    def set_str(self, key: str, value: str, ttl: Optional[float] = None) -> None:
        """Store a string in cache."""
        ...

    def set_json(self, key: str, value: Dict[str, object], ttl: Optional[float] = None) -> None:
        """Store a JSON-serializable dict in cache."""
        ...

    def delete(self, key: str) -> bool:
        """Delete a value from cache."""
        ...

    def exists(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        ...

    def clear(self) -> int:
        """Clear all cache entries."""
        ...

    # === Treasury (Memoization) ===

    def get_or_compute(
        self,
        key: str,
        compute_fn: Callable[[], bytes],
        ttl: Optional[float] = None,
    ) -> bytes:
        """Get from cache or compute and store (Treasury pattern)."""
        ...

    # === Bulk Operations ===

    def get_many(self, keys: List[str]) -> Dict[str, bytes]:
        """Get multiple values at once."""
        ...

    def set_many(self, items: Dict[str, bytes], ttl: Optional[float] = None) -> None:
        """Store multiple values at once."""
        ...

    def delete_many(self, keys: List[str]) -> int:
        """Delete multiple keys."""
        ...

    # === Pattern Operations ===

    def keys(self, pattern: Optional[str] = None) -> List[str]:
        """Get all keys matching pattern."""
        ...

    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        ...

    # === Statistics ===

    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        ...

    def get_status(self) -> NagaStatus:
        """Get NAGA health status."""
        ...


# =============================================================================
# NULL IMPLEMENTATION (Arjuna Pattern)
# =============================================================================


class NullPadma:
    """No-op Padma for when cache is unavailable."""

    def get(self, key: str) -> Optional[bytes]:
        return None

    def get_str(self, key: str) -> Optional[str]:
        return None

    def get_json(self, key: str) -> Optional[Dict[str, object]]:
        return None

    def set(self, key: str, value: bytes, ttl: Optional[float] = None) -> None:
        pass

    def set_str(self, key: str, value: str, ttl: Optional[float] = None) -> None:
        pass

    def set_json(self, key: str, value: Dict[str, object], ttl: Optional[float] = None) -> None:
        pass

    def delete(self, key: str) -> bool:
        return False

    def exists(self, key: str) -> bool:
        return False

    def clear(self) -> int:
        return 0

    def get_or_compute(self, key: str, compute_fn: Callable[[], bytes], ttl: Optional[float] = None) -> bytes:
        return compute_fn()

    def get_many(self, keys: List[str]) -> Dict[str, bytes]:
        return {}

    def set_many(self, items: Dict[str, bytes], ttl: Optional[float] = None) -> None:
        pass

    def delete_many(self, keys: List[str]) -> int:
        return 0

    def keys(self, pattern: Optional[str] = None) -> List[str]:
        return []

    def delete_pattern(self, pattern: str) -> int:
        return 0

    def get_stats(self) -> CacheStats:
        return CacheStats(total_entries=0, hits=0, misses=0, evictions=0, hit_rate=0.0)

    def get_status(self) -> NagaStatus:
        return NagaStatus(naga_type=NagaType.SESHA, healthy=False, message="Cache not available")
