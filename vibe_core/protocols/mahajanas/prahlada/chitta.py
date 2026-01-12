"""
CHITTA - Working Memory Protocol (RAM)
======================================

OWNER: PRAHLADA (The Resilient One)
POSITION: 9 (KARMA Quarter)
OPCODE: EXEC_SERVICE (Memory operations via service execution)

Chitta (Sanskrit: 'Mind-stuff', 'Consciousness') is the working memory.
Like RAM - fast, volatile, limited capacity.

SHASTRA BASIS:
    Chitta is one of the four aspects of the antahkarana (inner instrument):
    - Manas (mind) - processes sense data
    - Buddhi (intellect) - discriminates
    - Ahamkara (ego) - identifies
    - CHITTA (memory) - stores impressions (samskaras)

    Prahlada's chitta was always fixed on Vishnu, even under torture.
    This is the model: memory that SURVIVES attacks through devotion.

MEMORY MODEL:
    - Working memory (RAM) - fast, limited, volatile
    - LRU eviction when capacity reached
    - TTL support for automatic expiration
    - Integrity checking via hashes
    - Attack survival through redundancy

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

import hashlib
import time
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, Final, List, Optional, Protocol, Tuple, runtime_checkable

from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode

# Import types from parent module
from vibe_core.protocols.mahajanas.prahlada import (
    MemoryValue,
    MemoryEntry,
    MemoryState,
    AttackType,
    SurvivalResult,
    PrahladaProtocol,
)


# =============================================================================
# OWNERSHIP DECLARATION - Prahlada OWNS this protocol
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.PRAHLADA
LOTUS_POSITION: Final[int] = 9  # KARMA Quarter, Worker 1
LOTUS_QUARTER: Final[str] = "karma"

OWNED_OPCODES: Final[List[MantraOpCode]] = [
    MantraOpCode.EXTEND_CAP,  # Memory operations
]


# =============================================================================
# CHITTA CONFIGURATION
# =============================================================================

@dataclass(frozen=True)
class ChittaConfig:
    """Configuration for Chitta working memory."""
    max_entries: int = 1000           # Maximum entries before LRU eviction
    default_ttl_seconds: int = 3600   # 1 hour default TTL
    redundancy_copies: int = 2        # Copies for attack survival
    integrity_check_interval: int = 60  # Seconds between integrity checks


# =============================================================================
# INTERNAL STORAGE ENTRY
# =============================================================================

@dataclass
class ChittaEntry:
    """Internal storage for a memory entry."""
    key: str
    value: MemoryValue
    value_type: str
    value_hash: str
    stored_at: datetime
    expires_at: Optional[datetime]
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    # Redundancy for attack survival
    backup_value: Optional[MemoryValue] = None
    backup_hash: Optional[str] = None

    @classmethod
    def create(
        cls,
        key: str,
        value: MemoryValue,
        ttl_seconds: Optional[int] = None,
    ) -> "ChittaEntry":
        """Create a new entry with computed hash."""
        now = datetime.now()
        value_type = type(value).__name__ if value is not None else "NoneType"
        value_hash = cls._compute_hash(value)

        expires_at = None
        if ttl_seconds is not None and ttl_seconds > 0:
            expires_at = now + timedelta(seconds=ttl_seconds)

        return cls(
            key=key,
            value=value,
            value_type=value_type,
            value_hash=value_hash,
            stored_at=now,
            expires_at=expires_at,
            access_count=0,
            last_accessed=None,
            backup_value=value,  # Redundant copy
            backup_hash=value_hash,
        )

    @staticmethod
    def _compute_hash(value: MemoryValue) -> str:
        """Compute SHA-256 hash of value."""
        if value is None:
            return hashlib.sha256(b"None").hexdigest()[:16]
        if isinstance(value, bytes):
            return hashlib.sha256(value).hexdigest()[:16]
        return hashlib.sha256(str(value).encode()).hexdigest()[:16]

    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def is_corrupted(self) -> bool:
        """Check if value hash doesn't match."""
        current_hash = self._compute_hash(self.value)
        return current_hash != self.value_hash

    def touch(self) -> None:
        """Update access metadata."""
        self.access_count += 1
        self.last_accessed = datetime.now()

    def heal(self) -> bool:
        """Attempt to heal from backup."""
        if self.backup_hash is None or self.backup_value is None:
            return False
        # Restore from backup
        self.value = self.backup_value
        self.value_hash = self.backup_hash
        return not self.is_corrupted()

    def to_memory_entry(self) -> MemoryEntry:
        """Convert to MemoryEntry TypedDict for observability."""
        return MemoryEntry(
            key=self.key,
            value_type=self.value_type,
            value_repr=repr(self.value)[:100],  # Truncate for safety
            value_hash=self.value_hash,
            stored_at=self.stored_at.isoformat(),
            expires_at=self.expires_at.isoformat() if self.expires_at else "",
            access_count=self.access_count,
            last_accessed=self.last_accessed.isoformat() if self.last_accessed else "",
        )

    def size_bytes(self) -> int:
        """Estimate memory size in bytes."""
        base = 200  # Overhead for metadata
        if self.value is None:
            return base
        if isinstance(self.value, bytes):
            return base + len(self.value)
        if isinstance(self.value, str):
            return base + len(self.value.encode())
        return base + 8  # Primitive types


# =============================================================================
# CHITTA PROTOCOL - Working Memory Interface
# =============================================================================

@runtime_checkable
class ChittaProtocol(Protocol):
    """
    The Working Memory Protocol - Prahlada's RAM.

    OWNER: Mahajana.PRAHLADA

    This is FAST, VOLATILE memory:
    - O(1) access time (dict-based)
    - LRU eviction when full
    - TTL-based expiration
    - Attack survival through redundancy

    ANTI-MAYAVAD:
    - No Any types
    - Prahlada OWNS this memory
    - Memory survives through devotion
    """

    @property
    def owner(self) -> Mahajana:
        """Always returns Mahajana.PRAHLADA."""
        ...

    @property
    def capacity(self) -> int:
        """Maximum number of entries."""
        ...

    @property
    def size(self) -> int:
        """Current number of entries."""
        ...

    # =========================================================================
    # Memory Operations
    # =========================================================================

    def remember(
        self,
        key: str,
        value: MemoryValue,
        ttl_seconds: Optional[int] = None,
    ) -> bool:
        """
        Store a value in working memory.
        WATERTIGHT: value is MemoryValue union, not Any.
        """
        ...

    def recall(self, key: str) -> Optional[MemoryValue]:
        """
        Recall a value from working memory.
        Returns None if not found, expired, or corrupted.
        """
        ...

    def forget(self, key: str) -> bool:
        """
        Remove a value from working memory.
        Returns True if key existed and was removed.
        """
        ...

    def has_memory(self, key: str) -> bool:
        """Check if key exists and is not expired."""
        ...

    def clear(self) -> int:
        """Clear all entries. Returns count of cleared entries."""
        ...

    # =========================================================================
    # Resilience Operations (Prahlada's Domain)
    # =========================================================================

    def survive(self, attack_type: AttackType, severity: float = 1.0) -> SurvivalResult:
        """
        Survive an attack on memory.
        Prahlada ALWAYS survives - the question is damage mitigation.
        """
        ...

    def heal(self) -> Tuple[int, int]:
        """
        Heal corrupted entries from backups.
        Returns (healed_count, failed_count).
        """
        ...

    def check_integrity(self) -> List[str]:
        """
        Check integrity of all entries.
        Returns list of corrupted keys.
        """
        ...

    # =========================================================================
    # Observability
    # =========================================================================

    def get_state(self) -> MemoryState:
        """Get complete memory state for observability."""
        ...

    def get_entry(self, key: str) -> Optional[MemoryEntry]:
        """Get metadata for a specific entry."""
        ...


# =============================================================================
# CHITTA IMPLEMENTATION - Working Memory
# =============================================================================

class Chitta:
    """
    Prahlada's Working Memory - The RAM of the system.

    OWNER: Mahajana.PRAHLADA

    Like Prahlada's consciousness that remained fixed on Vishnu
    even under Hiranyakashipu's torture, this memory survives attacks.

    Features:
    - LRU eviction (Least Recently Used)
    - TTL expiration (Time To Live)
    - Integrity checking (hash verification)
    - Attack survival (backup copies)
    """

    def __init__(self, config: Optional[ChittaConfig] = None) -> None:
        """Initialize working memory."""
        self._config = config or ChittaConfig()
        # OrderedDict for LRU ordering
        self._storage: OrderedDict[str, ChittaEntry] = OrderedDict()
        self._attack_log: List[SurvivalResult] = []

    @property
    def owner(self) -> Mahajana:
        return Mahajana.PRAHLADA

    @property
    def capacity(self) -> int:
        return self._config.max_entries

    @property
    def size(self) -> int:
        return len(self._storage)

    # =========================================================================
    # Memory Operations
    # =========================================================================

    def remember(
        self,
        key: str,
        value: MemoryValue,
        ttl_seconds: Optional[int] = None,
    ) -> bool:
        """Store a value in working memory."""
        # Use default TTL if not specified
        if ttl_seconds is None:
            ttl_seconds = self._config.default_ttl_seconds

        # Evict if at capacity (LRU)
        while len(self._storage) >= self._config.max_entries:
            self._evict_lru()

        # Create and store entry
        entry = ChittaEntry.create(key, value, ttl_seconds)
        self._storage[key] = entry

        # Move to end (most recently used)
        self._storage.move_to_end(key)
        return True

    def recall(self, key: str) -> Optional[MemoryValue]:
        """Recall a value from working memory."""
        entry = self._storage.get(key)
        if entry is None:
            return None

        # Check expiration
        if entry.is_expired():
            del self._storage[key]
            return None

        # Check corruption
        if entry.is_corrupted():
            # Attempt auto-heal
            if entry.heal():
                entry.touch()
                self._storage.move_to_end(key)
                return entry.value
            else:
                del self._storage[key]
                return None

        # Success - update access metadata
        entry.touch()
        self._storage.move_to_end(key)
        return entry.value

    def forget(self, key: str) -> bool:
        """Remove a value from working memory."""
        if key in self._storage:
            del self._storage[key]
            return True
        return False

    def has_memory(self, key: str) -> bool:
        """Check if key exists and is valid."""
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
        return count

    def _evict_lru(self) -> None:
        """Evict least recently used entry."""
        if self._storage:
            # First item in OrderedDict is LRU
            self._storage.popitem(last=False)

    # =========================================================================
    # Resilience Operations (Prahlada's Domain)
    # =========================================================================

    def survive(self, attack_type: AttackType, severity: float = 1.0) -> SurvivalResult:
        """
        Survive an attack on memory.

        Prahlada ALWAYS survives - the question is damage mitigation.
        Different attack types affect memory differently:

        - MEMORY_OVERFLOW: Evict entries to free space
        - DATA_CORRUPTION: Heal from backups
        - CACHE_POISON: Clear and rebuild
        - DOS: Rate limit operations
        - TIMEOUT: Expire stale entries
        - ENTROPY_SPIKE: Validate all hashes
        """
        entries_lost = 0
        entries_recovered = 0
        start_time = time.time()

        if attack_type == AttackType.MEMORY_OVERFLOW:
            # Evict to survive
            target_evict = int(len(self._storage) * severity * 0.5)
            for _ in range(target_evict):
                if self._storage:
                    self._evict_lru()
                    entries_lost += 1

        elif attack_type == AttackType.DATA_CORRUPTION:
            # Simulate corruption based on severity
            corrupted_count = int(len(self._storage) * severity * 0.3)
            keys = list(self._storage.keys())[:corrupted_count]
            for key in keys:
                entry = self._storage[key]
                # Corrupt the value
                entry.value = None
                entry.value_hash = "corrupted"

            # Now heal
            healed, failed = self.heal()
            entries_recovered = healed
            entries_lost = failed

        elif attack_type == AttackType.CACHE_POISON:
            # Validate all entries
            corrupted = self.check_integrity()
            for key in corrupted:
                entry = self._storage.get(key)
                if entry and not entry.heal():
                    del self._storage[key]
                    entries_lost += 1
                else:
                    entries_recovered += 1

        elif attack_type == AttackType.TIMEOUT:
            # Force expire old entries
            now = datetime.now()
            cutoff = now - timedelta(seconds=int(self._config.default_ttl_seconds * severity))
            for key in list(self._storage.keys()):
                entry = self._storage[key]
                if entry.stored_at < cutoff:
                    del self._storage[key]
                    entries_lost += 1

        elif attack_type == AttackType.ENTROPY_SPIKE:
            # Validate all hashes
            corrupted = self.check_integrity()
            entries_lost = len(corrupted)
            healed, _ = self.heal()
            entries_recovered = healed

        elif attack_type == AttackType.DOS:
            # Just log it - Prahlada survives
            pass

        elapsed_ms = int((time.time() - start_time) * 1000)

        result = SurvivalResult(
            survived=True,  # Prahlada ALWAYS survives
            attack_type=attack_type.value,
            damage_mitigated=1.0 - (entries_lost / max(1, len(self._storage) + entries_lost)),
            recovery_time_ms=elapsed_ms,
            entries_lost=entries_lost,
            entries_recovered=entries_recovered,
            message=f"Prahlada survived {attack_type.value} through devotion",
        )

        self._attack_log.append(result)
        return result

    def heal(self) -> Tuple[int, int]:
        """Heal corrupted entries from backups."""
        healed = 0
        failed = 0

        for key in list(self._storage.keys()):
            entry = self._storage[key]
            if entry.is_corrupted():
                if entry.heal():
                    healed += 1
                else:
                    del self._storage[key]
                    failed += 1

        return (healed, failed)

    def check_integrity(self) -> List[str]:
        """Check integrity of all entries."""
        corrupted: List[str] = []
        for key, entry in self._storage.items():
            if entry.is_corrupted() or entry.is_expired():
                corrupted.append(key)
        return corrupted

    # =========================================================================
    # Observability
    # =========================================================================

    def get_state(self) -> MemoryState:
        """Get complete memory state for observability."""
        # Compute statistics
        total_size = sum(e.size_bytes() for e in self._storage.values())

        timestamps = [e.stored_at for e in self._storage.values()]
        oldest = min(timestamps).isoformat() if timestamps else ""
        newest = max(timestamps).isoformat() if timestamps else ""

        # Determine health
        corrupted = self.check_integrity()
        if not self._storage:
            health = "pristine"
        elif len(corrupted) == 0:
            health = "healthy"
        elif len(corrupted) < len(self._storage) * 0.1:
            health = "degraded"
        else:
            health = "critical"

        return MemoryState(
            entries={k: e.to_memory_entry() for k, e in self._storage.items()},
            total_count=len(self._storage),
            total_size_bytes=total_size,
            oldest_entry=oldest,
            newest_entry=newest,
            health=health,
        )

    def get_entry(self, key: str) -> Optional[MemoryEntry]:
        """Get metadata for a specific entry."""
        entry = self._storage.get(key)
        if entry is None:
            return None
        return entry.to_memory_entry()


# =============================================================================
# CHITTA OWNED PROTOCOL - With OwnedProtocol integration
# =============================================================================

class ChittaOwnedProtocol(Chitta):
    """
    Chitta with full OwnedProtocol integration.

    Adds:
    - Protocol name
    - Lotus position
    - Lineage tracking
    """

    PROTOCOL_NAME: Final[str] = "chitta"

    @property
    def lotus_position(self) -> int:
        return LOTUS_POSITION

    @property
    def lotus_quarter(self) -> str:
        return LOTUS_QUARTER


# =============================================================================
# NULL CHITTA - For testing
# =============================================================================

class NullChitta:
    """
    The Forgetful Chitta - no actual storage.

    Used for testing without memory persistence.
    Still owned by PRAHLADA (memory is his domain).
    """

    @property
    def owner(self) -> Mahajana:
        return Mahajana.PRAHLADA

    @property
    def capacity(self) -> int:
        return 0

    @property
    def size(self) -> int:
        return 0

    def remember(
        self,
        key: str,
        value: MemoryValue,
        ttl_seconds: Optional[int] = None,
    ) -> bool:
        return True  # Accept but don't store

    def recall(self, key: str) -> Optional[MemoryValue]:
        return None

    def forget(self, key: str) -> bool:
        return False

    def has_memory(self, key: str) -> bool:
        return False

    def clear(self) -> int:
        return 0

    def survive(self, attack_type: AttackType, severity: float = 1.0) -> SurvivalResult:
        return SurvivalResult(
            survived=True,
            attack_type=attack_type.value,
            damage_mitigated=1.0,
            recovery_time_ms=0,
            entries_lost=0,
            entries_recovered=0,
            message="NullChitta has nothing to lose",
        )

    def heal(self) -> Tuple[int, int]:
        return (0, 0)

    def check_integrity(self) -> List[str]:
        return []

    def get_state(self) -> MemoryState:
        return MemoryState(
            entries={},
            total_count=0,
            total_size_bytes=0,
            oldest_entry="",
            newest_entry="",
            health="pristine",
        )

    def get_entry(self, key: str) -> Optional[MemoryEntry]:
        return None


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Ownership
    "OWNER",
    "LOTUS_POSITION",
    "LOTUS_QUARTER",
    "OWNED_OPCODES",
    # Config
    "ChittaConfig",
    # Protocol
    "ChittaProtocol",
    # Implementations
    "Chitta",
    "ChittaOwnedProtocol",
    "NullChitta",
]
