"""
NRISIMHA SERVICE - Wraps Legacy narasimha.py
=============================================

POSITION: 12 (HEAD - MOKSHA Quarter)

This is a THIN WRAPPER that connects the legacy NarasimhaProtocol
to the Mahajana framework. NO DUPLICATION - just delegation.

WRAPPED: vibe_core.narasimha.NarasimhaProtocol
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "nrisimha"
__position__ = 12
__genesis__ = "0x0176ec06"  # GenesisByte: parampara % 37 == 0

from datetime import datetime
from typing import Dict, List, Optional

from vibe_core.protocols.mahajanas.nrisimha import (
    NrisimhaProtocolBase,
    CacheLevel,
    CacheValue,
    CacheResult,
    CacheState,
)

# Import from canonical location (narasimha.py moved to nrisimha/types/)
from vibe_core.protocols.mahajanas.nrisimha.types.narasimha import NarasimhaProtocol as LegacyNarasimha


class NrisimhaService(NrisimhaProtocolBase):
    """
    NRISIMHA Service - Security/State Protection.

    WRAPS the legacy NarasimhaProtocol (hypervisor kill-switch).
    Adds state caching on top of security monitoring.

    This is Prahlada's protector - guards system state.
    """

    def __init__(self) -> None:
        """Initialize with legacy hypervisor."""
        self._hypervisor = LegacyNarasimha()
        self._cache: Dict[str, CacheValue] = {}
        self._cache_meta: Dict[str, Dict[str, any]] = {}
        self._stats = {
            "hits": 0,
            "misses": 0,
        }

    # =========================================================================
    # CACHE PROTOCOL (Position 12 - CACHE_STATE)
    # =========================================================================

    def cache(self, key: str, value: CacheValue, ttl_seconds: int = 3600) -> CacheResult:
        """Cache a value with protection."""
        self._cache[key] = value
        self._cache_meta[key] = {
            "level": CacheLevel.HOT,
            "timestamp": datetime.now().isoformat(),
            "ttl": ttl_seconds,
            "protected": False,
        }
        return CacheResult(
            success=True,
            cache_key=key,
            cache_level=CacheLevel.HOT.value,
            hit=False,
            size_bytes=len(str(value)),
            timestamp=datetime.now().isoformat(),
            ttl_seconds=ttl_seconds,
        )

    def get(self, key: str) -> Optional[CacheValue]:
        """Get cached value. Nrisimha protects."""
        if key in self._cache:
            self._stats["hits"] += 1
            return self._cache[key]
        self._stats["misses"] += 1
        return None

    def protect(self, key: str) -> CacheResult:
        """Protect a cache entry - Prahlada's shield."""
        if key in self._cache_meta:
            self._cache_meta[key]["protected"] = True
            self._cache_meta[key]["level"] = CacheLevel.PROTECTED
        return CacheResult(
            success=True,
            cache_key=key,
            cache_level=CacheLevel.PROTECTED.value,
            hit=key in self._cache,
            timestamp=datetime.now().isoformat(),
        )

    def unprotect(self, key: str) -> CacheResult:
        """Remove protection from a cache entry."""
        if key in self._cache_meta:
            self._cache_meta[key]["protected"] = False
            self._cache_meta[key]["level"] = CacheLevel.WARM
        return CacheResult(
            success=True,
            cache_key=key,
            cache_level=CacheLevel.WARM.value,
            hit=key in self._cache,
            timestamp=datetime.now().isoformat(),
        )

    def evict(self, key: str) -> bool:
        """Evict a cache entry. Protected entries cannot be evicted."""
        if key in self._cache_meta and self._cache_meta[key].get("protected"):
            return False  # Nrisimha protects!
        if key in self._cache:
            del self._cache[key]
            if key in self._cache_meta:
                del self._cache_meta[key]
            return True
        return False

    def get_level(self, key: str) -> CacheLevel:
        """Get cache level of an entry."""
        if key in self._cache_meta:
            return self._cache_meta[key].get("level", CacheLevel.COLD)
        return CacheLevel.EVICTED

    def warm_up(self, keys: List[str]) -> int:
        """Warm up cache entries."""
        count = 0
        for key in keys:
            if key in self._cache_meta:
                if self._cache_meta[key]["level"] == CacheLevel.COLD:
                    self._cache_meta[key]["level"] = CacheLevel.WARM
                    count += 1
        return count

    def clear(self, include_protected: bool = False) -> int:
        """Clear cache. Protected entries survive unless forced."""
        if include_protected:
            count = len(self._cache)
            self._cache.clear()
            self._cache_meta.clear()
            return count

        # Preserve protected entries
        to_remove = [k for k, m in self._cache_meta.items() if not m.get("protected")]
        for key in to_remove:
            self._cache.pop(key, None)
            self._cache_meta.pop(key, None)
        return len(to_remove)

    def get_state(self) -> CacheState:
        """Get cache state."""
        total = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / total if total > 0 else 1.0

        protected = sum(1 for m in self._cache_meta.values() if m.get("protected"))

        return CacheState(
            total_entries=len(self._cache),
            hot_entries=sum(1 for m in self._cache_meta.values() if m.get("level") == CacheLevel.HOT),
            protected_entries=protected,
            total_size_bytes=sum(len(str(v)) for v in self._cache.values()),
            max_size_bytes=1024 * 1024 * 100,  # 100MB default
            hit_rate=hit_rate,
            total_hits=self._stats["hits"],
            total_misses=self._stats["misses"],
            health="pristine" if hit_rate > 0.8 else "healthy",
        )

    # =========================================================================
    # HYPERVISOR ACCESS (Legacy NarasimhaProtocol)
    # =========================================================================

    @property
    def hypervisor(self) -> LegacyNarasimha:
        """Access the legacy hypervisor kill-switch."""
        return self._hypervisor

    @property
    def is_activated(self) -> bool:
        """Check if Narasimha has been activated."""
        return self._hypervisor.activated


__all__ = ["NrisimhaService"]
