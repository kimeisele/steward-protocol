"""
VYASA - The 1st Avatara (System Wake)
======================================

POSITION: 0 (GENESIS Quarter HEAD, SYS_WAKE OpCode)

Sage Vyasa - The First Revealer.
Wakes the system by reciting the Eternal Truth (Config).
The original author who compiles the reality.

DERIVED FROM MAHAMANTRA:
    Position 0 -> guardian=VYASA, opcode=SYS_WAKE, quarter=GENESIS
    All properties derived from truth table. No manual wiring.

HEAD POSITION:
    This is a HEAD (Avatara) position, not a WORKER (Mahajana).
    HEADs are at positions 0, 4, 8, 12 (first of each quarter).
    They initiate action; Workers execute.

DOMAIN:
- System Initialization (Knowledge Injection)
- Resource Allocation (Distributing the Vedas/Config)
- Infrastructure Setup (The Library of Reality)
- Bootstrap Sequence

WATERTIGHT: No Any types. All typed explicitly.
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x00000000"  # GenesisByte: parampara % 37 == 0

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
    runtime_checkable,
)

from vibe_core.mahamantra import HeadProtocol, Avatara, MantraOpCode, ProtocolRegistry


# =============================================================================
# VYASA PROTOCOL BASE - Derives from MantraPosition 0
# =============================================================================

@ProtocolRegistry.register
class VyasaProtocolBase(HeadProtocol):
    """
    Vyasa protocol ownership - DERIVED from Mahamantra position 0.

    NO MANUAL WIRING:
        _position_index = 0 is the ONLY configuration.
        Everything else derived from truth table.

    DERIVED PROPERTIES:
        guardian()  -> Avatara.VYASA
        opcode()    -> MantraOpCode.SYS_WAKE
        quarter()   -> Quarter.GENESIS
        is_head()   -> True (HEAD position)
        parampara_vector() -> 37 (% 37 == 0)
    """
    _position_index: ClassVar[int] = 0  # THE ONLY CONFIGURATION


# NO MANUAL WIRING - Everything derived from mahamantra[0]


# =============================================================================
# WATERTIGHT STATE TYPES (No Any!)
# =============================================================================

class WakePhase(str, Enum):
    """Phases of system wake."""
    DORMANT = "dormant"       # Not started
    BOOTSTRAP = "bootstrap"   # Initial bootstrap
    RESOURCES = "resources"   # Loading resources
    SERVICES = "services"     # Starting services
    READY = "ready"           # System ready
    FAILED = "failed"         # Wake failed


class WakeResult(TypedDict, total=False):
    """
    Result of wake operation.
    WATERTIGHT - no Any!
    """
    success: bool
    phase: str                # WakePhase value
    timestamp: str            # ISO timestamp
    services_started: int
    resources_loaded: int
    error_message: str


class WakeState(TypedDict, total=False):
    """
    State of system wake.
    WATERTIGHT - no Any!
    """
    current_phase: str        # WakePhase value
    is_awake: bool
    wake_time: str            # ISO timestamp
    uptime_seconds: int
    total_wakes: int
    health: str               # "pristine", "healthy", "degraded"


class WakeCliResult(TypedDict):
    """Result of CLI wake operation. WATERTIGHT - no Any!"""
    success: bool
    phase: str
    is_awake: bool
    health: str


# =============================================================================
# VYASA PROTOCOL
# =============================================================================


@runtime_checkable
class VyasaProtocol(Protocol):
    """
    The System Wake Protocol - Vyasa's domain.

    DERIVED: Position 0 -> VYASA, SYS_WAKE, GENESIS
    WATERTIGHT - no Any types!

    As Vyasa milked the Earth to provide all necessities,
    this protocol wakes the system and provides all resources.
    """

    @classmethod
    def position_index(cls) -> int:
        """Position 0 in the Mahamantra."""
        ...

    def wake(self) -> WakeResult:
        """SYS_WAKE: Wake the system from dormant state."""
        ...

    def is_awake(self) -> bool:
        """Check if system is awake."""
        ...

    def get_phase(self) -> WakePhase:
        """Get current wake phase."""
        ...

    def bootstrap(self) -> WakeResult:
        """Run bootstrap sequence."""
        ...

    def load_resources(self) -> int:
        """Load system resources. Returns count loaded."""
        ...

    def start_services(self) -> int:
        """Start system services. Returns count started."""
        ...

    def shutdown(self) -> WakeResult:
        """Graceful shutdown (return to dormant)."""
        ...

    def execute(self, command: str) -> str:
        """
        Execute an Infrastructure Command.
        The Scepter's interface to Matter.
        """
        ...

    def scan(self, path: str = ".") -> str:
        """
        Scan the filesystem.
        """
        ...


# =============================================================================
# NULL VYASA (For testing)
# =============================================================================


class NullVyasa(VyasaProtocolBase):
    """
    The Sleeping One.
    No real system wake (for testing without infrastructure).

    Inherits from VyasaProtocolBase -> position 0 -> VYASA.
    """

    def wake(self) -> WakeResult:
        return WakeResult(
            success=True,
            phase=WakePhase.READY.value,
            timestamp=datetime.now().isoformat(),
            services_started=0,
            resources_loaded=0,
        )

    def is_awake(self) -> bool:
        return True  # Always "awake" in null mode

    def get_phase(self) -> WakePhase:
        return WakePhase.READY

    def bootstrap(self) -> WakeResult:
        return WakeResult(
            success=True,
            phase=WakePhase.BOOTSTRAP.value,
            timestamp=datetime.now().isoformat(),
        )

    def load_resources(self) -> int:
        return 0

    def start_services(self) -> int:
        return 0

    def shutdown(self) -> WakeResult:
        return WakeResult(
            success=True,
            phase=WakePhase.DORMANT.value,
            timestamp=datetime.now().isoformat(),
        )

    def get_state(self) -> WakeState:
        return WakeState(
            current_phase=WakePhase.READY.value,
            is_awake=True,
            total_wakes=0,
            health="pristine",
        )

    def wake_cli(self, target: str = "system") -> WakeCliResult:
        """CLI: Wake the system. WATERTIGHT."""
        result = self.wake()
        state = self.get_state()
        return WakeCliResult(
            success=result.get("success", True),
            phase=result.get("phase", "ready"),
            is_awake=self.is_awake(),
            health=state.get("health", "pristine"),
        )


# =============================================================================
# EXPORTS
# =============================================================================

# =============================================================================
# VYASA SERVICE - The Real Implementation (wraps legacy boot_orchestrator.py)
# =============================================================================

# LAZY IMPORT to avoid circular dependency with boot_mode migration
# VyasaService is loaded on first access via __getattr__

# =============================================================================
# MIGRATED TYPES - Accessed via mahamantra.mod.vyasa
# =============================================================================

from vibe_core.protocols.mahajanas.vyasa.types import (
    # boot_mode.py
    BootMode,
    # process_manager.py
    ProcessStatus,
    ProcessManager,
    AgentProcessInfo,
)

__all__ = [
    # Protocol Base (HeadProtocol derivative) - THE ONLY SOURCE
    "VyasaProtocolBase",
    # State Types (WATERTIGHT)
    "WakePhase",
    "WakeResult",
    "WakeState",
    "WakeCliResult",
    # Protocol
    "VyasaProtocol",
    # Implementations
    "NullVyasa",
    # Service (Real Implementation)
    "VyasaService",
    # === MIGRATED TYPES (mahamantra.mod.vyasa) ===
    # boot_mode.py
    "BootMode",
    # process_manager.py
    "ProcessStatus",
    "ProcessManager",
    "AgentProcessInfo",
]


def __getattr__(name: str):
    """Lazy import for VyasaService to avoid circular import."""
    if name == "VyasaService":
        from vibe_core.protocols.mahajanas.vyasa.service import VyasaService
        return VyasaService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
