"""
SHAMBHU - The 3rd Mahajana (Destruction/Cleanup)
================================================
OpCode: GARBAGE_COLLECT (Bit 7, Position 7 in Mahamantra)
Opulence: Vairagya (Renunciation)

Lord Shiva (Shambhu) - The Destroyer.
The auspicious one who destroys for regeneration.
Maheshvara - the greatest devotee of Vishnu.

PROTOCOL OWNERSHIP (Anti-Mayavad):
Shambhu is the PERSON responsible for all destruction/cleanup.
Not abstract "garbage collection" - PERSONAL destruction by Shambhu.

OWNED PROTOCOLS:
- Garbage Collection (GARBAGE_COLLECT OpCode)
- Resource Cleanup
- Memory Deallocation
- Process Termination
- Graceful Shutdown

Shambhu destroys, but only what needs to be destroyed.
Destruction is SEVA - it makes room for new creation.

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
    TypedDict,
    Union,
    runtime_checkable,
)

from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode


# =============================================================================
# PROTOCOL OWNERSHIP
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.SHAMBHU

OWNED_PROTOCOLS: Final[List[str]] = [
    "shambhu",
    "destruction",
    "cleanup",
    "garbage_collection",
    "termination",
]

OWNED_OPCODES: Final[List[MantraOpCode]] = [
    MantraOpCode.BIND_CTX,  # Vyuha: Q1 Worker 3 (GARBAGE_COLLECT -> Kapila)
]


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
    WATERTIGHT - no Any types!
    """

    @property
    def owner(self) -> Mahajana:
        """Always returns Mahajana.SHAMBHU."""
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


class NullShambhu:
    """The Preserver. No destruction (for testing)."""

    @property
    def owner(self) -> Mahajana:
        return Mahajana.SHAMBHU

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


__all__ = [
    "OWNER", "OWNED_PROTOCOLS", "OWNED_OPCODES",
    "DestructionType", "DestructionResult", "DestructionState",
    "ShambhuProtocol", "NullShambhu",
]
