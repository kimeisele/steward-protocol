"""
SHAMBHU - The 3rd Mahajana (Destruction/Cleanup)
================================================

POSITION: 3 (GENESIS Quarter, BIND_CTX OpCode)

Lord Shiva (Shambhu) - The Destroyer.
The auspicious one who destroys for regeneration.
Maheshvara - the greatest devotee of Vishnu.

DERIVED FROM MAHAMANTRA:
    Position 3 -> guardian=SHAMBHU, opcode=BIND_CTX, quarter=GENESIS
    All properties derived from truth table. No manual wiring.

Shambhu destroys, but only what needs to be destroyed.
Destruction is SEVA - it makes room for new creation.

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

from vibe_core.mahamantra import WorkerProtocol, Mahajana, MantraOpCode


# =============================================================================
# SHAMBHU PROTOCOL BASE - Derives from MantraPosition 3
# =============================================================================

class ShambhuProtocolBase(WorkerProtocol):
    """
    Shambhu protocol ownership - DERIVED from Mahamantra position 3.

    NO MANUAL WIRING:
        _position_index = 3 is the ONLY configuration.
        Everything else derived from truth table.

    DERIVED PROPERTIES:
        guardian()  -> Mahajana.SHAMBHU
        opcode()    -> MantraOpCode.BIND_CTX
        quarter()   -> Quarter.GENESIS
        is_head()   -> False (Worker position)
        parampara_vector() -> 148 (% 37 == 0)
    """
    _position_index: ClassVar[int] = 3  # THE ONLY CONFIGURATION


# NO MANUAL WIRING - Everything derived from mahamantra[3]


# =============================================================================
# WATERTIGHT STATE TYPES (No Any!)
# =============================================================================

class DestructionType(str, Enum):
    """Types of destruction."""
    GARBAGE = "garbage"       # Unused memory
    ORPHAN = "orphan"         # Orphaned resources
    EXPIRED = "expired"       # Timed-out entries
    CORRUPTED = "corrupted"   # Damaged data
    REQUESTED = "requested"   # Explicitly requested


class DestructionResult(TypedDict, total=False):
    """
    Result of destruction/cleanup.
    WATERTIGHT - no Any!
    """
    success: bool
    items_destroyed: int
    bytes_freed: int
    duration_ms: int
    error_message: str


class DestructionState(TypedDict, total=False):
    """
    State of destruction/cleanup.
    WATERTIGHT - no Any!
    """
    last_collection: str      # ISO timestamp
    items_pending: int
    total_destroyed: int
    total_bytes_freed: int
    is_destroyed: bool
    health: str               # "pristine", "healthy", "degraded"


# =============================================================================
# SHAMBHU PROTOCOL
# =============================================================================


@runtime_checkable
class ShambhuProtocol(Protocol):
    """
    The Destruction/Cleanup Protocol - Shambhu's domain.

    DERIVED: Position 3 -> SHAMBHU, BIND_CTX, GENESIS
    WATERTIGHT - no Any types!
    """

    @classmethod
    def position_index(cls) -> int:
        """Position 3 in the Mahamantra."""
        ...

    def collect(self, destruction_type: DestructionType = DestructionType.GARBAGE) -> DestructionResult:
        """GARBAGE_COLLECT: Perform garbage collection."""
        ...

    def destroy(self, target_id: str) -> bool:
        """Explicitly destroy a specific target. Returns True if destroyed."""
        ...

    def is_destroyed(self) -> bool:
        """Check if this resource has been destroyed."""
        ...

    def can_destroy(self) -> bool:
        """Check if destruction is allowed."""
        ...

    def schedule_destruction(self, target_id: str, delay_ms: int) -> bool:
        """Schedule destruction for later."""
        ...

    def get_state(self) -> DestructionState:
        """Get destruction state. WATERTIGHT."""
        ...


# =============================================================================
# NULL SHAMBHU
# =============================================================================


class NullShambhu(ShambhuProtocolBase):
    """
    The Preserver. No destruction (for testing).

    Inherits from ShambhuProtocolBase -> position 3 -> SHAMBHU.
    """

    def collect(self, destruction_type: DestructionType = DestructionType.GARBAGE) -> DestructionResult:
        return DestructionResult(
            success=True,
            items_destroyed=0,
            bytes_freed=0,
            duration_ms=0,
            error_message="",
        )

    def destroy(self, target_id: str) -> bool:
        return True  # Pretend success

    def is_destroyed(self) -> bool:
        return False

    def can_destroy(self) -> bool:
        return False  # Cannot be destroyed

    def schedule_destruction(self, target_id: str, delay_ms: int) -> bool:
        return True

    def get_state(self) -> DestructionState:
        return DestructionState(
            items_pending=0,
            total_destroyed=0,
            total_bytes_freed=0,
            is_destroyed=False,
            health="pristine",
        )


# =============================================================================
# TRANSFORMATION PROTOCOL (Shambhu's Breaking & Routing)
# =============================================================================

from vibe_core.protocols.mahajanas.shambhu.transformation import (
    # Types
    TransformationType,
    ConcernType,
    MixedConcern,
    TransformationPlan,
    TransformationResult,
    TransformationState,
    # Registry
    MIXED_FILE_REGISTRY,
    # Protocol
    TransformationProtocol,
    # Null implementation
    NullTransformation,
)

# =============================================================================
# GC - Garbage Collection
# =============================================================================

from vibe_core.protocols.mahajanas.shambhu.gc import (
    GCStrategy,
    ManagedObject,
    GCResult,
    GCStats,
    GCProtocol,
    GarbageCollector,
    NullGC,
    LOTUS_POSITION as GC_POSITION,
)


__all__ = [
    # Protocol Base (MantraProtocol derivative) - THE ONLY SOURCE
    "ShambhuProtocolBase",
    # Destruction Types (WATERTIGHT)
    "DestructionType",
    "DestructionResult",
    "DestructionState",
    # Destruction Protocol
    "ShambhuProtocol",
    "NullShambhu",
    # Transformation Types (WATERTIGHT)
    "TransformationType",
    "ConcernType",
    "MixedConcern",
    "TransformationPlan",
    "TransformationResult",
    "TransformationState",
    # Transformation Registry
    "MIXED_FILE_REGISTRY",
    # Transformation Protocol
    "TransformationProtocol",
    "NullTransformation",
    # GC (Garbage Collection)
    "GCStrategy",
    "ManagedObject",
    "GCResult",
    "GCStats",
    "GCProtocol",
    "GarbageCollector",
    "NullGC",
]
