"""
PRAHLADA - The 7th Mahajana (Resilience/Memory)
===============================================
OpCode: FETCH_RES (Bit 9, Position 9 in Mahamantra)
Opulence: Virya (Strength/Valor)

The boy devotee. Tortured by Hiranyakashipu, protected by Nrisimha.
"Sravanam Kirtanam Vishnoh Smaranam..." - REMEMBERING.

PROTOCOL OWNERSHIP (Anti-Mayavad):
Prahlada is the PERSON responsible for all resilience.
Not abstract "memory" - PERSONAL protection by Prahlada.

OWNED PROTOCOLS:
- Memory Protection (ChittaProtocol - RAM)
- Long-term Storage (SmritiProtocol - Cache)
- Resource Fetching (FETCH_RES OpCode)
- Fault Tolerance
- Recovery from Attack
- Devotional Persistence

Prahlada survives what should kill him.
He is the Patron Saint of Memory.

SUBSTRATE CONNECTION (Level -1):
- ChittaProtocol → Prahlada (working memory)
- SmritiProtocol → Prahlada (long-term memory)

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import (
    Dict,
    Final,
    List,
    Optional,
    Protocol,
    Tuple,
    TypedDict,
    Union,
    runtime_checkable,
)

from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode


# =============================================================================
# PROTOCOL OWNERSHIP
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.PRAHLADA
LOTUS_POSITION: Final[int] = 9  # KARMA Quarter, Worker 1
LOTUS_QUARTER: Final[str] = "karma"

OWNED_PROTOCOLS: Final[List[str]] = [
    "prahlada",
    "memory",
    "chitta",
    "smriti",
    "resilience",
    "fault_tolerance",
]

OWNED_OPCODES: Final[List[MantraOpCode]] = [
    MantraOpCode.EXEC_SERVICE,  # Vyuha: Q3 Worker 1 (FETCH_RES now HEAD: Parashurama)
]


# =============================================================================
# WATERTIGHT STATE TYPES (No Any!)
# =============================================================================

# The union of allowed memory value types - WATERTIGHT
MemoryValue = Union[str, int, float, bool, bytes, None]


class MemoryEntry(TypedDict, total=False):
    """
    A single memory entry with metadata.
    WATERTIGHT - no Any!
    """
    key: str
    value_type: str  # Python type name
    value_repr: str  # String representation (for observability)
    value_hash: str  # Hash for integrity
    stored_at: str   # ISO timestamp
    expires_at: str  # ISO timestamp (empty = never)
    access_count: int
    last_accessed: str


class MemoryState(TypedDict, total=False):
    """
    Complete memory state for observability.
    WATERTIGHT - no Any!
    """
    entries: Dict[str, MemoryEntry]
    total_count: int
    total_size_bytes: int
    oldest_entry: str  # ISO timestamp
    newest_entry: str  # ISO timestamp
    health: str  # "pristine", "healthy", "degraded", "critical"


class AttackType(str, Enum):
    """Types of attacks Prahlada can survive."""
    MEMORY_OVERFLOW = "memory_overflow"
    DATA_CORRUPTION = "data_corruption"
    CACHE_POISON = "cache_poison"
    DOS = "denial_of_service"
    TIMEOUT = "timeout"
    ENTROPY_SPIKE = "entropy_spike"


class SurvivalResult(TypedDict, total=False):
    """
    Result of surviving an attack.
    WATERTIGHT - no Any!
    """
    survived: bool
    attack_type: str
    damage_mitigated: float  # 0.0-1.0
    recovery_time_ms: int
    entries_lost: int
    entries_recovered: int
    message: str


# =============================================================================
# PRAHLADA PROTOCOL (Main Memory Protocol)
# =============================================================================


@runtime_checkable
class PrahladaProtocol(Protocol):
    """
    The Resilience/Memory Protocol - Prahlada's domain.

    Any system that stores/retrieves memory must implement this.
    WATERTIGHT - no Any types!

    ANTI-MAYAVAD: Prahlada is the PERSON.
    Not abstract "memory" - PERSONAL protection.

    The Three Stages of Memory (Smaranam):
    1. STORE (remember) - Initial encoding
    2. HOLD (persist) - Retention against entropy
    3. RECALL (retrieve) - Retrieval from storage
    """

    @property
    def owner(self) -> Mahajana:
        """Always returns Mahajana.PRAHLADA."""
        ...

    # =========================================================================
    # Memory Operations (FETCH_RES OpCode)
    # =========================================================================

    def remember(self, key: str, value: MemoryValue) -> bool:
        """
        Store a memory. Returns True if accepted.
        Memory must survive entropy.
        WATERTIGHT: value is MemoryValue union, not Any.
        """
        ...

    def recall(self, key: str) -> Optional[MemoryValue]:
        """
        Recall a memory. Returns None if forgotten/decayed.
        WATERTIGHT: Returns MemoryValue union, not Any.
        """
        ...

    def forget(self, key: str) -> bool:
        """
        Intentionally forget a memory.
        Returns True if the memory existed and was removed.
        """
        ...

    def has_memory(self, key: str) -> bool:
        """Check if a memory exists."""
        ...

    # =========================================================================
    # Resilience (Survival)
    # =========================================================================

    def survive(self, attack_type: AttackType, severity: float = 1.0) -> SurvivalResult:
        """
        Survive an attack/failure.
        WATERTIGHT: attack_type is enum, severity is float.
        Returns structured SurvivalResult, not bool.
        """
        ...

    def heal(self) -> Tuple[int, int]:
        """
        Attempt to heal corrupted memories.
        Returns (healed_count, failed_count).
        """
        ...

    # =========================================================================
    # Observability
    # =========================================================================

    def get_state(self) -> MemoryState:
        """
        Get complete memory state for observability.
        WATERTIGHT: Returns MemoryState TypedDict, not Dict[str, Any].
        """
        ...

    def get_entry(self, key: str) -> Optional[MemoryEntry]:
        """Get metadata for a specific entry."""
        ...


# =============================================================================
# NULL PRAHLADA (For testing)
# =============================================================================


class NullPrahlada:
    """
    The Forgetful One.
    No memory persistence (for testing without state).

    Even in Null mode:
    - survives all attacks (Prahlada always survives)
    - returns None for recalls (nothing to remember)
    """

    @property
    def owner(self) -> Mahajana:
        return Mahajana.PRAHLADA

    def remember(self, key: str, value: MemoryValue) -> bool:
        return True  # Accept but don't store

    def recall(self, key: str) -> Optional[MemoryValue]:
        return None  # Nothing to recall

    def forget(self, key: str) -> bool:
        return False  # Nothing to forget

    def has_memory(self, key: str) -> bool:
        return False

    def survive(self, attack_type: AttackType, severity: float = 1.0) -> SurvivalResult:
        # Prahlada ALWAYS survives
        return SurvivalResult(
            survived=True,
            attack_type=attack_type.value,
            damage_mitigated=1.0,
            recovery_time_ms=0,
            entries_lost=0,
            entries_recovered=0,
            message="Prahlada survives through devotion",
        )

    def heal(self) -> Tuple[int, int]:
        return (0, 0)  # Nothing to heal

    def get_state(self) -> MemoryState:
        return MemoryState(
            entries={},
            total_count=0,
            total_size_bytes=0,
            health="pristine",
        )

    def get_entry(self, key: str) -> Optional[MemoryEntry]:
        return None


# =============================================================================
# PRAHLADA'S INSTRUCTION (For Memory Access)
# =============================================================================

@dataclass(frozen=True)
class SmaranamInstruction:
    """
    An instruction for memory access.

    Smaranam = Remembering (Third of the Nine Processes of Bhakti)

    This is the ATOMIC unit of memory operation.
    Used by ChittaProtocol and SmritiProtocol.
    """
    operation: str  # "store", "retrieve", "forget", "check"
    key: str
    value: Optional[MemoryValue] = None
    sovereign_id: Optional[str] = None  # For audit trail

    def to_dict(self) -> Dict[str, Union[str, int, float, bool, None]]:
        """Serialize for transmission."""
        result: Dict[str, Union[str, int, float, bool, None]] = {
            "operation": self.operation,
            "key": self.key,
        }
        if self.value is not None:
            if isinstance(self.value, bytes):
                result["value"] = self.value.hex()
                result["value_type"] = "bytes"
            else:
                result["value"] = self.value
                result["value_type"] = type(self.value).__name__
        if self.sovereign_id:
            result["sovereign_id"] = self.sovereign_id
        return result


# =============================================================================
# CHITTA - Working Memory (RAM)
# =============================================================================

from vibe_core.protocols.mahajanas.prahlada.chitta import (
    ChittaConfig,
    ChittaProtocol,
    Chitta,
    ChittaOwnedProtocol,
    NullChitta,
    LOTUS_POSITION as CHITTA_POSITION,
)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Ownership
    "OWNER",
    "OWNED_PROTOCOLS",
    "OWNED_OPCODES",
    # State Types (WATERTIGHT)
    "MemoryValue",
    "MemoryEntry",
    "MemoryState",
    "AttackType",
    "SurvivalResult",
    # Protocol
    "PrahladaProtocol",
    # Implementations
    "NullPrahlada",
    # Instructions
    "SmaranamInstruction",
    # Chitta - Working Memory (RAM)
    "ChittaConfig",
    "ChittaProtocol",
    "Chitta",
    "ChittaOwnedProtocol",
    "NullChitta",
    "CHITTA_POSITION",
]
