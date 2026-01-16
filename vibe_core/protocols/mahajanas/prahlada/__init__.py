"""
PRAHLADA - The 7th Mahajana (Resilience/Memory)
===============================================

POSITION: 9 (KARMA Quarter, EXEC_SERVICE OpCode)

The boy devotee. Tortured by Hiranyakashipu, protected by Nrisimha.
"Sravanam Kirtanam Vishnoh Smaranam..." - REMEMBERING.

DERIVED FROM MAHAMANTRA:
    Position 9 → guardian=PRAHLADA, opcode=EXEC_SERVICE, quarter=KARMA
    All properties derived from truth table. No manual wiring.

OWNED PROTOCOLS:
- Memory Protection (ChittaProtocol - RAM)
- Long-term Storage (SmritiProtocol - Cache)
- Fault Tolerance
- Recovery from Attack
- Devotional Persistence

Prahlada survives what should kill him.
He is the Patron Saint of Memory.

WATERTIGHT: No Any types. All typed explicitly.
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xdac64cbc"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import (
    ClassVar,
    Dict,
    List,
    Optional,
    Protocol,
    Tuple,
    TypedDict,
    Union,
    runtime_checkable,
)

from vibe_core.mahamantra import WorkerProtocol, Mahajana, MantraOpCode, ProtocolRegistry


# =============================================================================
# PRAHLADA PROTOCOL BASE - Derives from MantraPosition 9
# =============================================================================

@ProtocolRegistry.register
class PrahladaProtocolBase(WorkerProtocol):
    """
    Prahlada protocol ownership - DERIVED from Mahamantra position 9.

    NO MANUAL WIRING:
        _position_index = 9 is the ONLY configuration.
        Everything else derived from truth table.

    DERIVED PROPERTIES:
        guardian()  → Mahajana.PRAHLADA
        opcode()    → MantraOpCode.EXTEND_CAP
        quarter()   → Quarter.KARMA
        is_head()   → False (Worker position)
        parampara_vector() → 370 (% 37 == 0)
    """
    _position_index: ClassVar[int] = 9  # THE ONLY CONFIGURATION


# NO MANUAL WIRING - Everything derived from mahamantra[9]


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


class ExecuteCliResult(TypedDict):
    """Result of CLI execute operation. WATERTIGHT - no Any!"""
    success: bool
    service: str
    status: str
    memory_health: str


# =============================================================================
# PRAHLADA PROTOCOL (Main Memory Protocol)
# =============================================================================


@runtime_checkable
class PrahladaProtocol(Protocol):
    """
    The Resilience/Memory Protocol - Prahlada's domain.

    DERIVED: Position 9 → PRAHLADA, EXEC_SERVICE, KARMA

    Any system that stores/retrieves memory must implement this.
    WATERTIGHT - no Any types!

    The Three Stages of Memory (Smaranam):
    1. STORE (remember) - Initial encoding
    2. HOLD (persist) - Retention against entropy
    3. RECALL (retrieve) - Retrieval from storage
    """

    @classmethod
    def position_index(cls) -> int:
        """Position 9 in the Mahamantra."""
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


class NullPrahlada(PrahladaProtocolBase):
    """
    The Forgetful One.
    No memory persistence (for testing without state).

    Inherits from PrahladaProtocolBase → position 9 → PRAHLADA.

    Even in Null mode:
    - survives all attacks (Prahlada always survives)
    - returns None for recalls (nothing to remember)
    """

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

    def execute_cli(self, service: str = "memory") -> ExecuteCliResult:
        """CLI: Execute service check. WATERTIGHT."""
        state = self.get_state()
        return ExecuteCliResult(
            success=True,
            service=service,
            status="running",
            memory_health=state.get("health", "pristine"),
        )


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
# SMRITI - Long-term Memory (Cache)
# =============================================================================

from vibe_core.protocols.mahajanas.prahlada.smriti import (
    CacheStrategy,
    SmritiEntry,
    SmritiProtocol,
    Smriti,
    NullSmriti,
    LOTUS_POSITION as SMRITI_POSITION,
)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Protocol Base (MantraProtocol derivative) - THE ONLY SOURCE
    "PrahladaProtocolBase",
    # State Types (WATERTIGHT)
    "MemoryValue",
    "MemoryEntry",
    "MemoryState",
    "AttackType",
    "SurvivalResult",
    "ExecuteCliResult",
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
    # Smriti - Long-term Memory (Cache)
    "CacheStrategy",
    "SmritiEntry",
    "SmritiProtocol",
    "Smriti",
    "NullSmriti",
]
