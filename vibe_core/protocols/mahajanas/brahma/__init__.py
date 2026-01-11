"""
BRAHMA - The 1st Mahajana (Creation/Genesis)
============================================

POSITION: 1 (GENESIS Quarter, LOAD_ROOT OpCode)

Lord Brahma - The Creator.
Born from the lotus growing from Vishnu's navel.
First living entity in the material creation.

DERIVED FROM MAHAMANTRA:
    Position 1 -> guardian=BRAHMA, opcode=LOAD_ROOT, quarter=GENESIS
    All properties derived from truth table. No manual wiring.

Brahma creates, but he is NOT the Supreme.
He is the first created being, not the creator.

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
    Tuple,
    TypedDict,
    Union,
    runtime_checkable,
)

from vibe_core.mahamantra import WorkerProtocol, Mahajana, MantraOpCode, ProtocolRegistry


# =============================================================================
# BRAHMA PROTOCOL BASE - Derives from MantraPosition 1
# =============================================================================

@ProtocolRegistry.register
class BrahmaProtocolBase(WorkerProtocol):
    """
    Brahma protocol ownership - DERIVED from Mahamantra position 1.

    NO MANUAL WIRING:
        _position_index = 1 is the ONLY configuration.
        Everything else derived from truth table.

    DERIVED PROPERTIES:
        guardian()  -> Mahajana.BRAHMA
        opcode()    -> MantraOpCode.LOAD_ROOT
        quarter()   -> Quarter.GENESIS
        is_head()   -> False (Worker position)
        parampara_vector() -> 74 (% 37 == 0)
    """
    _position_index: ClassVar[int] = 1  # THE ONLY CONFIGURATION


# NO MANUAL WIRING - Everything derived from mahamantra[1]


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


class CreateCliResult(TypedDict):
    """Result of CLI create operation. WATERTIGHT - no Any!"""
    success: bool
    phase: str
    is_created: bool
    health: str


# =============================================================================
# BRAHMA PROTOCOL
# =============================================================================


@runtime_checkable
class BrahmaProtocol(Protocol):
    """
    The Creation/Genesis Protocol - Brahma's domain.

    DERIVED: Position 1 -> BRAHMA, LOAD_ROOT, GENESIS
    WATERTIGHT - no Any types!
    """

    @classmethod
    def position_index(cls) -> int:
        """Position 1 in the Mahamantra."""
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


class NullBrahma(BrahmaProtocolBase):
    """
    The Uncreated. No genesis (for testing).

    Inherits from BrahmaProtocolBase -> position 1 -> BRAHMA.
    """

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

    def create_cli(self, target: str = "genesis") -> CreateCliResult:
        """CLI: Create/initialize. WATERTIGHT."""
        state = self.get_state()
        return CreateCliResult(
            success=True,
            phase=state.get("phase", "active"),
            is_created=self.is_created(),
            health=state.get("health", "pristine"),
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

# =============================================================================
# BRAHMA SERVICE - The Real Implementation
# =============================================================================

from vibe_core.protocols.mahajanas.brahma.service import BrahmaService

__all__ = [
    # Protocol Base (MantraProtocol derivative) - THE ONLY SOURCE
    "BrahmaProtocolBase",
    # Genesis Types (WATERTIGHT)
    "GenesisPhase", "GenesisState", "AllocationResult", "CreateCliResult",
    # Protocol
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
    # Service (Real Implementation)
    "BrahmaService",
]
