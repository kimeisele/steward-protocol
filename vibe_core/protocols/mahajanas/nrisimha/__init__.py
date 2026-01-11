"""
NRISIMHA - The 4th Avatara (Cache State)
========================================

POSITION: 12 (MOKSHA Quarter HEAD, CACHE_STATE OpCode)

Lord Nrisimha - The Half-Man Half-Lion.
Appeared from a pillar to protect Prahlada.
Neither man nor animal, neither inside nor outside.

DERIVED FROM MAHAMANTRA:
    Position 12 -> guardian=NRISIMHA, opcode=CACHE_STATE, quarter=MOKSHA
    All properties derived from truth table. No manual wiring.

HEAD POSITION:
    This is a HEAD (Avatara) position, not a WORKER (Mahajana).
    HEADs are at positions 0, 4, 8, 12 (first of each quarter).
    They initiate action; Workers execute.

DOMAIN:
- State Caching (CACHE_STATE)
- Protection of State
- Transformation (neither this nor that)
- Liberation through Protection

"ugram viram maha-vishnum jvalantam sarvato mukham
nrisimham bhishanam bhadram mrityur mrityum namamy aham"

"I bow to Lord Nrisimha who is ferocious and heroic,
the great Vishnu, blazing in all directions, terrifying yet auspicious,
the death of death itself."

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import (
    ClassVar,
    Dict,
    List,
    Optional,
    Protocol,
    TypedDict,
    Union,
    runtime_checkable,
)

from vibe_core.mahamantra import HeadProtocol, Avatara, MantraOpCode


# =============================================================================
# NRISIMHA PROTOCOL BASE - Derives from MantraPosition 12
# =============================================================================

class NrisimhaProtocolBase(HeadProtocol):
    """
    Nrisimha protocol ownership - DERIVED from Mahamantra position 12.

    NO MANUAL WIRING:
        _position_index = 12 is the ONLY configuration.
        Everything else derived from truth table.

    DERIVED PROPERTIES:
        guardian()  -> Avatara.NRISIMHA
        opcode()    -> MantraOpCode.CACHE_STATE
        quarter()   -> Quarter.MOKSHA
        is_head()   -> True (HEAD position)
        parampara_vector() -> 481 (% 37 == 0)
    """
    _position_index: ClassVar[int] = 12  # THE ONLY CONFIGURATION


# NO MANUAL WIRING - Everything derived from mahamantra[12]


# =============================================================================
# WATERTIGHT STATE TYPES (No Any!)
# =============================================================================

class CacheLevel(str, Enum):
    """Levels of cache protection."""
    HOT = "hot"               # Frequently accessed, in memory
    WARM = "warm"             # Moderately accessed
    COLD = "cold"             # Rarely accessed, may be evicted
    PROTECTED = "protected"   # Never evict (Prahlada protection)
    EVICTED = "evicted"       # Removed from cache


# Cache value types - WATERTIGHT
CacheValue = Union[str, int, float, bool, bytes, Dict[str, str], List[str]]


class CacheResult(TypedDict, total=False):
    """
    Result of cache operation.
    WATERTIGHT - no Any!
    """
    success: bool
    cache_key: str
    cache_level: str          # CacheLevel value
    hit: bool                 # Cache hit or miss
    size_bytes: int
    timestamp: str            # ISO timestamp
    ttl_seconds: int          # Time to live
    error_message: str


class CacheState(TypedDict, total=False):
    """
    State of cache.
    WATERTIGHT - no Any!
    """
    total_entries: int
    hot_entries: int
    protected_entries: int
    total_size_bytes: int
    max_size_bytes: int
    hit_rate: float           # 0.0-1.0
    total_hits: int
    total_misses: int
    last_access: str          # ISO timestamp
    health: str               # "pristine", "healthy", "degraded"


# =============================================================================
# NRISIMHA PROTOCOL
# =============================================================================


@runtime_checkable
class NrisimhaProtocol(Protocol):
    """
    The State Cache Protocol - Nrisimha's domain.

    DERIVED: Position 12 -> NRISIMHA, CACHE_STATE, MOKSHA
    WATERTIGHT - no Any types!

    As Nrisimha protects Prahlada (memory),
    this protocol caches and protects state.
    """

    @classmethod
    def position_index(cls) -> int:
        """Position 12 in the Mahamantra."""
        ...

    def cache(self, key: str, value: CacheValue, ttl_seconds: int = 3600) -> CacheResult:
        """CACHE_STATE: Cache a value with TTL."""
        ...

    def get(self, key: str) -> Optional[CacheValue]:
        """Get cached value. Returns None on miss."""
        ...

    def protect(self, key: str) -> CacheResult:
        """Protect a cache entry (never evict - Prahlada protection)."""
        ...

    def unprotect(self, key: str) -> CacheResult:
        """Remove protection from a cache entry."""
        ...

    def evict(self, key: str) -> bool:
        """Evict a cache entry. Returns False if protected."""
        ...

    def get_level(self, key: str) -> CacheLevel:
        """Get cache level of an entry."""
        ...

    def warm_up(self, keys: List[str]) -> int:
        """Warm up cache entries. Returns count warmed."""
        ...

    def clear(self, include_protected: bool = False) -> int:
        """Clear cache. Returns count cleared."""
        ...

    def get_state(self) -> CacheState:
        """Get cache state. WATERTIGHT."""
        ...


# =============================================================================
# NULL NRISIMHA (For testing)
# =============================================================================


class NullNrisimha(NrisimhaProtocolBase):
    """
    The Dormant Protector.
    No real caching (for testing without state).

    Inherits from NrisimhaProtocolBase -> position 12 -> NRISIMHA.
    """

    def cache(self, key: str, value: CacheValue, ttl_seconds: int = 3600) -> CacheResult:
        return CacheResult(
            success=True,
            cache_key=key,
            cache_level=CacheLevel.HOT.value,
            hit=False,  # It's a write
            size_bytes=0,
            timestamp=datetime.now().isoformat(),
            ttl_seconds=ttl_seconds,
        )

    def get(self, key: str) -> Optional[CacheValue]:
        return None  # Always miss in null mode

    def protect(self, key: str) -> CacheResult:
        return CacheResult(
            success=True,
            cache_key=key,
            cache_level=CacheLevel.PROTECTED.value,
            hit=False,
            timestamp=datetime.now().isoformat(),
        )

    def unprotect(self, key: str) -> CacheResult:
        return CacheResult(
            success=True,
            cache_key=key,
            cache_level=CacheLevel.WARM.value,
            hit=False,
            timestamp=datetime.now().isoformat(),
        )

    def evict(self, key: str) -> bool:
        return True  # Always succeeds in null mode

    def get_level(self, key: str) -> CacheLevel:
        return CacheLevel.EVICTED

    def warm_up(self, keys: List[str]) -> int:
        return 0

    def clear(self, include_protected: bool = False) -> int:
        return 0

    def get_state(self) -> CacheState:
        return CacheState(
            total_entries=0,
            hot_entries=0,
            protected_entries=0,
            total_size_bytes=0,
            max_size_bytes=0,
            hit_rate=1.0,  # No misses if no requests
            total_hits=0,
            total_misses=0,
            health="pristine",
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Protocol Base (HeadProtocol derivative) - THE ONLY SOURCE
    "NrisimhaProtocolBase",
    # State Types (WATERTIGHT)
    "CacheLevel",
    "CacheValue",
    "CacheResult",
    "CacheState",
    # Protocol
    "NrisimhaProtocol",
    # Implementations
    "NullNrisimha",
]
