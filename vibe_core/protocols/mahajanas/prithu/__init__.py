"""
PRITHU - The 1st Avatara (System Wake)
======================================

POSITION: 0 (GENESIS Quarter HEAD, SYS_WAKE OpCode)

King Prithu - The First Civilizer.
Milked the Earth to provide all necessities.
The original administrator who made the Earth habitable.

DERIVED FROM MAHAMANTRA:
    Position 0 -> guardian=PRITHU, opcode=SYS_WAKE, quarter=GENESIS
    All properties derived from truth table. No manual wiring.

HEAD POSITION:
    This is a HEAD (Avatara) position, not a WORKER (Mahajana).
    HEADs are at positions 0, 4, 8, 12 (first of each quarter).
    They initiate action; Workers execute.

DOMAIN:
- System Initialization
- Resource Allocation (milking the Earth)
- Infrastructure Setup
- Bootstrap Sequence

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
    runtime_checkable,
)

from vibe_core.mahamantra import HeadProtocol, Avatara, MantraOpCode


# =============================================================================
# PRITHU PROTOCOL BASE - Derives from MantraPosition 0
# =============================================================================

class PrithuProtocolBase(HeadProtocol):
    """
    Prithu protocol ownership - DERIVED from Mahamantra position 0.

    NO MANUAL WIRING:
        _position_index = 0 is the ONLY configuration.
        Everything else derived from truth table.

    DERIVED PROPERTIES:
        guardian()  -> Avatara.PRITHU
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
# PRITHU PROTOCOL
# =============================================================================


@runtime_checkable
class PrithuProtocol(Protocol):
    """
    The System Wake Protocol - Prithu's domain.

    DERIVED: Position 0 -> PRITHU, SYS_WAKE, GENESIS
    WATERTIGHT - no Any types!

    As Prithu milked the Earth to provide all necessities,
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

    def get_state(self) -> WakeState:
        """Get wake state. WATERTIGHT."""
        ...


# =============================================================================
# NULL PRITHU (For testing)
# =============================================================================


class NullPrithu(PrithuProtocolBase):
    """
    The Sleeping One.
    No real system wake (for testing without infrastructure).

    Inherits from PrithuProtocolBase -> position 0 -> PRITHU.
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

__all__ = [
    # Protocol Base (HeadProtocol derivative) - THE ONLY SOURCE
    "PrithuProtocolBase",
    # State Types (WATERTIGHT)
    "WakePhase",
    "WakeResult",
    "WakeState",
    "WakeCliResult",
    # Protocol
    "PrithuProtocol",
    # Implementations
    "NullPrithu",
]
