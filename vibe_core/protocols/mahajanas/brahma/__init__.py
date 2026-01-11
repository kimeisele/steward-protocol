"""
BRAHMA - The 1st Mahajana (Creation/Genesis)
============================================
OpCodes: SYS_WAKE (Bit 1), LOAD_ROOT (Bit 2), ALLOC_MEM (Bit 3)
         Position 1-3 in Mahamantra
Opulence: Sri (Beauty/Creation)

Lord Brahma - The Creator.
Born from the lotus growing from Vishnu's navel.
First living entity in the material creation.

PROTOCOL OWNERSHIP (Anti-Mayavad):
Brahma is the PERSON responsible for all creation/genesis.
Not abstract "initialization" - PERSONAL creation by Brahma.

OWNED PROTOCOLS:
- System Wake (SYS_WAKE OpCode)
- Root Loading (LOAD_ROOT OpCode)
- Memory Allocation (ALLOC_MEM OpCode)
- Genesis/Bootstrap
- Initial State Creation

Brahma creates, but he is NOT the Supreme.
He is the first created being, not the creator.

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

OWNER: Final[Mahajana] = Mahajana.BRAHMA
LOTUS_POSITION: Final[int] = 1  # GENESIS Quarter, Worker 1
LOTUS_QUARTER: Final[str] = "genesis"

OWNED_PROTOCOLS: Final[List[str]] = [
    "brahma",
    "creation",
    "genesis",
    "bootstrap",
    "initialization",
]

OWNED_OPCODES: Final[List[MantraOpCode]] = [
    MantraOpCode.LOAD_ROOT,  # Vyuha: Q1 Worker 1 (SYS_WAKE now HEAD: Prithu)
]


# =============================================================================
# WATERTIGHT STATE TYPES (No Any!)
# =============================================================================

class GenesisPhase(str, Enum):
    """Phases of creation."""
    DORMANT = "dormant"       # Before creation
    AWAKENING = "awakening"   # SYS_WAKE
    LOADING = "loading"       # LOAD_ROOT
    ALLOCATING = "allocating" # ALLOC_MEM
    ACTIVE = "active"         # Fully created
    DISSOLVING = "dissolving" # Being destroyed


class GenesisState(TypedDict, total=False):
    """
    State of creation/genesis.
    WATERTIGHT - no Any!
    """
    phase: str                # GenesisPhase value
    wake_time: str            # ISO timestamp
    root_loaded: bool
    memory_allocated_bytes: int
    creation_id: str          # Unique ID for this creation cycle
    health: str               # "pristine", "healthy", "degraded"


class AllocationResult(TypedDict, total=False):
    """
    Result of memory allocation.
    WATERTIGHT - no Any!
    """
    success: bool
    allocated_bytes: int
    address: str              # Memory address (as hex string)
    error_message: str


# =============================================================================
# BRAHMA PROTOCOL
# =============================================================================


@runtime_checkable
class BrahmaProtocol(Protocol):
    """
    The Creation/Genesis Protocol - Brahma's domain.
    WATERTIGHT - no Any types!
    """

    @property
    def owner(self) -> Mahajana:
        """Always returns Mahajana.BRAHMA."""
        ...

    def wake(self, sovereign_id: str) -> bool:
        """SYS_WAKE: Wake the system. Returns True if awakened."""
        ...

    def load_root(self, root_path: str) -> bool:
        """LOAD_ROOT: Load root configuration. Returns True if loaded."""
        ...

    def alloc_mem(self, size_bytes: int) -> AllocationResult:
        """ALLOC_MEM: Allocate memory. Returns allocation result."""
        ...

    def get_phase(self) -> GenesisPhase:
        """Get current creation phase."""
        ...

    def is_created(self) -> bool:
        """Check if creation is complete."""
        ...

    def get_creation_timestamp(self) -> str:
        """Returns ISO timestamp of creation."""
        ...

    def get_state(self) -> GenesisState:
        """Get complete genesis state. WATERTIGHT."""
        ...


# =============================================================================
# NULL BRAHMA
# =============================================================================


class NullBrahma:
    """The Uncreated. No genesis (for testing)."""

    @property
    def owner(self) -> Mahajana:
        return Mahajana.BRAHMA

    def wake(self, sovereign_id: str) -> bool:
        return True

    def load_root(self, root_path: str) -> bool:
        return True

    def alloc_mem(self, size_bytes: int) -> AllocationResult:
        return AllocationResult(
            success=True,
            allocated_bytes=size_bytes,
            address="0x0",
            error_message="",
        )

    def get_phase(self) -> GenesisPhase:
        return GenesisPhase.ACTIVE

    def is_created(self) -> bool:
        return True

    def get_creation_timestamp(self) -> str:
        return datetime.now().isoformat()

    def get_state(self) -> GenesisState:
        return GenesisState(
            phase="active",
            root_loaded=True,
            memory_allocated_bytes=0,
            health="pristine",
        )


from vibe_core.protocols.mahajanas.brahma.di import (
    ServiceRegistryProtocol,
    ServiceRegistryOwnedProtocol,
    NullServiceRegistry,
    ServiceInfo,
    RegistryStats,
    DIProtocolState,
)

# =============================================================================
# BOOTSTRAP - System Genesis
# =============================================================================

from vibe_core.protocols.mahajanas.brahma.bootstrap import (
    BootstrapPhase,
    BootstrapStep,
    BootstrapResult,
    BootstrapProtocol,
    Bootstrap,
    NullBootstrap,
    LOTUS_POSITION as BOOTSTRAP_POSITION,
)

__all__ = [
    # Genesis
    "OWNER", "OWNED_PROTOCOLS", "OWNED_OPCODES",
    "GenesisPhase", "GenesisState", "AllocationResult",
    "BrahmaProtocol", "NullBrahma",
    # DI (Service Registry)
    "ServiceRegistryProtocol",
    "ServiceRegistryOwnedProtocol",
    "NullServiceRegistry",
    "ServiceInfo",
    "RegistryStats",
    "DIProtocolState",
    # Bootstrap (System Genesis)
    "BootstrapPhase",
    "BootstrapStep",
    "BootstrapResult",
    "BootstrapProtocol",
    "Bootstrap",
    "NullBootstrap",
    "BOOTSTRAP_POSITION",
]
