"""
LORD NRISIMHADEVA - The State Protector (MOKSHA HEAD)
=====================================================

"Lord Nrisimhadeva appeared to protect Prahlada Maharaja,
a pure devotee who was being persecuted by his demon father.
The Lord appeared in a form never seen before - half-man,
half-lion - to circumvent Hiranyakashipu's boons."
- Srimad Bhagavatam 7.8

SHAKTI: Rakshana-shakti (The Protection Potency)
OPCODE: CACHE_STATE (Position 12 - HEAD of Q4 MOKSHA)
VYUHA: ANIRUDDHA (Moksha Cycle)

STORY (SB 7.8-10):
Hiranyakashipu had boons that made him nearly immortal:
- Not killed by man or beast (Nrisimha is neither)
- Not inside or outside (on the threshold)
- Not day or night (at twilight)
- Not by weapon (by nails)
- Not on land, air, or water (on His lap)

The Lord appeared at the exact moment to protect His devotee.

ARCHITECTURAL MEANING:

Nrisimha = State Protector/Cache Manager

He does NOT create or execute. He PROTECTS:
1. CACHES state (preserves for liberation)
2. PROTECTS devotees (guards critical data)
3. DESTROYS demons (purges corrupt state)
4. TRANSCENDS limitations (circumvents constraints)

RELATION TO OTHER ROLES:

| Role       | Analogy                    | Function                  |
|------------|----------------------------|---------------------------|
| KRISHNA    | The Supreme Protector      | Ultimate shelter          |
| VISHNU     | The Maintainer             | Sustains all              |
| NRISIMHA   | The Guardian               | Active protection         |
| BALI       | The Surrendered            | Optimizes through surrender |
| SHUKA      | The Visionary              | Yields insights           |
| YAMARAJA   | The Judge                  | Final reset/judgment      |

PROTOCOL LEVEL:

Nrisimha operates at Level 0 (AVATARA/EXECUTIVE).
He is the HEAD of the MOKSHA cycle (Q4).
His workers are: BALI, SHUKA, YAMARAJA

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "shambhu"
__position__ = 3
__genesis__ = "0x41128d37"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Final, List, Optional, Protocol, TypedDict, runtime_checkable

from vibe_core.protocols.avataras import (
    Avatara,
    AvatarType,
    BaseAvatara,
    MilkingResult,
    MilkingRole,
    MilkingSetup,
    Shakti,
)


# =============================================================================
# STATE TYPES (What Nrisimha protects)
# =============================================================================


class CacheEntry(TypedDict, total=False):
    """
    A cached state entry.
    WATERTIGHT - no Any!
    """

    key: str  # Cache key
    value: str  # Cached value (serialized)
    size_bytes: int
    created_at: str  # ISO timestamp
    expires_at: str  # ISO timestamp or empty for permanent
    protected: bool  # Is this entry protected?
    lineage_hash: int  # Parampara verification


class CacheResult(TypedDict, total=False):
    """
    Result of a cache operation.
    WATERTIGHT - no Any!
    """

    success: bool
    key: str
    value: str
    hit: bool  # Was it a cache hit?
    protected: bool
    lineage_verified: bool
    error_message: str


class ProtectionRequest(TypedDict, total=False):
    """
    Request to protect an entity.
    WATERTIGHT - no Any!
    """

    entity_id: str  # What to protect
    entity_type: str  # "state", "process", "resource"
    threat: str  # What threatens it
    duration_seconds: int  # How long (0 = permanent)
    lineage_hash: int


class ProtectionResult(TypedDict, total=False):
    """
    Result of protection.
    WATERTIGHT - no Any!
    """

    success: bool
    entity_id: str
    protected_at: str  # ISO timestamp
    protection_level: str  # "standard", "elevated", "absolute"
    expires_at: str  # ISO timestamp or empty
    lineage_verified: bool
    error_message: str


class PurgeRequest(TypedDict, total=False):
    """
    Request to purge corrupt state.
    WATERTIGHT - no Any!
    """

    target_id: str  # What to purge
    reason: str  # Why purging
    force: bool  # Force purge even if protected?
    lineage_hash: int


class PurgeResult(TypedDict, total=False):
    """
    Result of purge operation.
    WATERTIGHT - no Any!
    """

    success: bool
    target_id: str
    purged_at: str  # ISO timestamp
    bytes_freed: int
    lineage_verified: bool
    error_message: str


# =============================================================================
# STANDARD MILKING SETUPS (Protection Operations)
# =============================================================================

MILKING_PROTECTION: Final[MilkingSetup] = MilkingSetup(
    kalb=MilkingRole(
        identity="prahlada_devotee",
        role_type="kalb",
        description="Stimulates with devotion/need for protection",
    ),
    melker=MilkingRole(
        identity="nrisimha",
        role_type="melker",
        description="Provides divine protection",
    ),
    topf=MilkingRole(
        identity="protection_shield",
        role_type="topf",
        description="Protected domain",
    ),
    resource="protection",
    source="divine_power",
)

MILKING_CACHE: Final[MilkingSetup] = MilkingSetup(
    kalb=MilkingRole(
        identity="bali",
        role_type="kalb",
        description="Stimulates with surrendered state",
    ),
    melker=MilkingRole(
        identity="nrisimha",
        role_type="melker",
        description="Caches surrendered state",
    ),
    topf=MilkingRole(
        identity="moksha_store",
        role_type="topf",
        description="Liberation cache",
    ),
    resource="cached_state",
    source="surrendered_state",
)

MILKING_PURGE: Final[MilkingSetup] = MilkingSetup(
    kalb=MilkingRole(
        identity="yamaraja",
        role_type="kalb",
        description="Stimulates with judgment of corruption",
    ),
    melker=MilkingRole(
        identity="nrisimha",
        role_type="melker",
        description="Destroys corrupt state",
    ),
    topf=MilkingRole(
        identity="void",
        role_type="topf",
        description="Purged into non-existence",
    ),
    resource="freed_space",
    source="corrupt_state",
)


# =============================================================================
# NRISIMHA PROTOCOL
# =============================================================================


@runtime_checkable
class NrisimhaProtocol(Protocol):
    """
    The State Protector Protocol.

    Any system that caches state and provides protection
    MUST implement this.

    Nrisimha is the PERSON responsible - not abstract "caching".
    """

    def cache_state(self, entry: CacheEntry) -> CacheResult:
        """
        Cache a state entry.

        This is CACHE_STATE opcode implementation.
        The HEAD of MOKSHA cycle preserves state.
        """
        ...

    def get_cached(self, key: str) -> CacheResult:
        """
        Retrieve a cached state entry.

        Nrisimha guards the cache.
        """
        ...

    def protect(self, request: ProtectionRequest) -> ProtectionResult:
        """
        Protect an entity from threats.

        Like Nrisimha protecting Prahlada:
        - Receive the plea
        - Assess the threat
        - Apply protection
        - Maintain vigilance
        """
        ...

    def purge(self, request: PurgeRequest) -> PurgeResult:
        """
        Purge corrupt state.

        Like Nrisimha destroying Hiranyakashipu:
        - Identify the corruption
        - Verify authority to purge
        - Execute destruction
        - Free the resources
        """
        ...

    def is_protected(self, entity_id: str) -> bool:
        """Check if an entity is under Nrisimha's protection."""
        ...

    def list_protected(self) -> List[str]:
        """List all protected entity IDs."""
        ...

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        ...


# =============================================================================
# NRISIMHA IMPLEMENTATION
# =============================================================================


class Nrisimha(BaseAvatara):
    """
    Lord Nrisimhadeva - The State Protector.

    SHAKTI: Rakshana (Protection)
    HEAD: MOKSHA cycle (ANIRUDDHA)
    WORKERS: Bali, Shuka, Yamaraja

    He caches state, protects devotees, purges demons.
    Without Nrisimha, no protection. Without protection, no moksha.

    ANTI-MAYAVAD: This is not abstract "cache layer".
    NRISIMHA (the Person) protects. He is the Supreme Guardian.
    """

    AVATARA_NAME = "Nrisimha"
    AVATARA_SHAKTI = Shakti.RAKSHANA
    AVATARA_TYPE = AvatarType.LILA  # Nrisimha is a Lila avatara
    DOMAIN = "State Protection/Caching"
    DESCRIPTION = "The State Protector - caches state, protects devotees, purges demons"

    def __init__(self) -> None:
        super().__init__()
        self._cache: Dict[str, CacheEntry] = {}
        self._protected: Dict[str, ProtectionResult] = {}
        self._purge_log: Dict[str, PurgeResult] = {}
        self._cache_hits = 0
        self._cache_misses = 0

    # =========================================================================
    # CACHE OPERATIONS
    # =========================================================================

    def cache_state(self, entry: CacheEntry) -> CacheResult:
        """
        Cache a state entry.

        CACHE_STATE opcode implementation.
        """
        if not self._empowered:
            return CacheResult(
                success=False,
                key=entry.get("key", ""),
                value="",
                hit=False,
                protected=False,
                lineage_verified=False,
                error_message="Nrisimha not empowered - no valid parampara",
            )

        key = entry.get("key", "")
        if not key:
            return CacheResult(
                success=False,
                key="",
                value="",
                hit=False,
                protected=False,
                lineage_verified=False,
                error_message="Empty cache key",
            )

        # Verify lineage
        lineage_hash = entry.get("lineage_hash", 0)
        lineage_ok = self.verify_parampara(lineage_hash)

        # Store in cache
        self._cache[key] = entry

        return CacheResult(
            success=True,
            key=key,
            value=entry.get("value", ""),
            hit=False,  # This was a write
            protected=entry.get("protected", False),
            lineage_verified=lineage_ok,
            error_message="",
        )

    def get_cached(self, key: str) -> CacheResult:
        """Retrieve a cached state entry."""
        entry = self._cache.get(key)

        if entry:
            self._cache_hits += 1
            return CacheResult(
                success=True,
                key=key,
                value=entry.get("value", ""),
                hit=True,
                protected=entry.get("protected", False),
                lineage_verified=True,
                error_message="",
            )
        else:
            self._cache_misses += 1
            return CacheResult(
                success=False,
                key=key,
                value="",
                hit=False,
                protected=False,
                lineage_verified=False,
                error_message="Cache miss",
            )

    def protect(self, request: ProtectionRequest) -> ProtectionResult:
        """Protect an entity from threats."""
        if not self._empowered:
            return ProtectionResult(
                success=False,
                entity_id=request.get("entity_id", ""),
                protected_at="",
                protection_level="none",
                expires_at="",
                lineage_verified=False,
                error_message="Nrisimha not empowered",
            )

        lineage_hash = request.get("lineage_hash", 0)
        lineage_ok = self.verify_parampara(lineage_hash)

        entity_id = request.get("entity_id", "")
        duration = request.get("duration_seconds", 0)

        now = datetime.now()
        expires = ""
        if duration > 0:
            from datetime import timedelta

            expires = (now + timedelta(seconds=duration)).isoformat()

        result = ProtectionResult(
            success=True,
            entity_id=entity_id,
            protected_at=now.isoformat(),
            protection_level="elevated" if lineage_ok else "standard",
            expires_at=expires,
            lineage_verified=lineage_ok,
            error_message="",
        )

        self._protected[entity_id] = result
        return result

    def purge(self, request: PurgeRequest) -> PurgeResult:
        """Purge corrupt state."""
        if not self._empowered:
            return PurgeResult(
                success=False,
                target_id=request.get("target_id", ""),
                purged_at="",
                bytes_freed=0,
                lineage_verified=False,
                error_message="Nrisimha not empowered",
            )

        target_id = request.get("target_id", "")
        lineage_hash = request.get("lineage_hash", 0)
        lineage_ok = self.verify_parampara(lineage_hash)
        force = request.get("force", False)

        # Check if target is protected
        if target_id in self._protected and not force:
            return PurgeResult(
                success=False,
                target_id=target_id,
                purged_at="",
                bytes_freed=0,
                lineage_verified=lineage_ok,
                error_message="Target is protected - use force=True to override",
            )

        # Perform purge
        bytes_freed = 0
        if target_id in self._cache:
            entry = self._cache.pop(target_id)
            bytes_freed = entry.get("size_bytes", 0)

        if target_id in self._protected:
            del self._protected[target_id]

        result = PurgeResult(
            success=True,
            target_id=target_id,
            purged_at=datetime.now().isoformat(),
            bytes_freed=bytes_freed,
            lineage_verified=lineage_ok,
            error_message="",
        )

        purge_id = f"purge_{len(self._purge_log)}"
        self._purge_log[purge_id] = result
        return result

    def is_protected(self, entity_id: str) -> bool:
        """Check if an entity is under protection."""
        return entity_id in self._protected

    def list_protected(self) -> List[str]:
        """List all protected entity IDs."""
        return list(self._protected.keys())

    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            "entries": len(self._cache),
            "protected": len(self._protected),
            "hits": self._cache_hits,
            "misses": self._cache_misses,
            "purges": len(self._purge_log),
        }

    # =========================================================================
    # MILKING PROTOCOL
    # =========================================================================

    def _do_milk(self, setup: MilkingSetup) -> MilkingResult:
        """Execute protection operation according to setup."""
        return MilkingResult(
            resource=setup.resource,
            amount=1.0,
            quality=1.0,  # Nrisimha's protection is absolute
            source_id=setup.source,
            operator_id=self.AVATARA_NAME,
            timestamp=datetime.now().isoformat(),
            lineage_verified=self._empowered,
        )


# =============================================================================
# NULL NRISIMHA (For Testing)
# =============================================================================


class NullNrisimha(Nrisimha):
    """The Unmanifested Protector. No caching (for testing)."""

    def __init__(self) -> None:
        super().__init__()
        self._empowered = True  # Always empowered for null

    def cache_state(self, entry: CacheEntry) -> CacheResult:
        return CacheResult(
            success=True,
            key=entry.get("key", ""),
            value=entry.get("value", ""),
            hit=False,
            protected=True,
            lineage_verified=True,
            error_message="",
        )

    def protect(self, request: ProtectionRequest) -> ProtectionResult:
        return ProtectionResult(
            success=True,
            entity_id=request.get("entity_id", ""),
            protected_at=datetime.now().isoformat(),
            protection_level="absolute",
            expires_at="",
            lineage_verified=True,
            error_message="",
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Types
    "CacheEntry",
    "CacheResult",
    "ProtectionRequest",
    "ProtectionResult",
    "PurgeRequest",
    "PurgeResult",
    # Milking setups
    "MILKING_PROTECTION",
    "MILKING_CACHE",
    "MILKING_PURGE",
    # Protocol
    "NrisimhaProtocol",
    # Implementation
    "Nrisimha",
    "NullNrisimha",
]
