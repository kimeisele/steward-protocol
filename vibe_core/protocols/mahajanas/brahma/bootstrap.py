"""
BOOTSTRAP - System Genesis Protocol
====================================

OWNER: BRAHMA (The Creator)
POSITION: 1 (GENESIS Quarter)
OPCODE: SYS_WAKE, LOAD_ROOT, ALLOC_MEM

Brahma emerged from the lotus and created the universe.
This is the model for system bootstrap: orderly genesis.

SHASTRA BASIS:
    Brahma woke on the lotus, saw only darkness.
    He heard "tapa" (austerity) and meditated for 1000 celestial years.
    Then he received knowledge from Vishnu and created.

    Bootstrap follows this pattern:
    1. WAKE - System awakens (SYS_WAKE)
    2. DISCOVER - Find root configuration (LOAD_ROOT)
    3. PREPARE - Allocate resources (ALLOC_MEM)
    4. INITIALIZE - Initialize subsystems
    5. READY - System operational

WATERTIGHT: No Any types. All typed explicitly.
"""
from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1

import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Dict, Final, List, Optional, Protocol, Tuple, runtime_checkable

from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode

from vibe_core.protocols.mahajanas.brahma import (
    GenesisPhase,
    GenesisState,
    AllocationResult,
)


# =============================================================================
# OWNERSHIP DECLARATION
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.BRAHMA
LOTUS_POSITION: Final[int] = 1
LOTUS_QUARTER: Final[str] = "genesis"

OWNED_OPCODES: Final[List[MantraOpCode]] = [
    MantraOpCode.LOAD_ROOT,
]


# =============================================================================
# BOOTSTRAP PHASE
# =============================================================================

class BootstrapPhase(str, Enum):
    """Phases of system bootstrap."""
    DORMANT = "dormant"           # Before boot
    WAKING = "waking"             # SYS_WAKE
    DISCOVERING = "discovering"   # Finding config
    PREPARING = "preparing"       # Allocating resources
    INITIALIZING = "initializing" # Starting subsystems
    READY = "ready"               # Fully operational
    FAILED = "failed"             # Boot failed


# =============================================================================
# BOOTSTRAP STEP
# =============================================================================

BootstrapHook = Callable[[], bool]


@dataclass
class BootstrapStep:
    """A single step in the bootstrap sequence."""
    name: str
    phase: BootstrapPhase
    hook: BootstrapHook
    timeout_ms: int = 5000
    required: bool = True
    order: int = 0


@dataclass(frozen=True)
class BootstrapResult:
    """Result of bootstrap."""
    success: bool
    phase: BootstrapPhase
    duration_ms: int
    steps_completed: int
    steps_failed: int
    message: str


# =============================================================================
# BOOTSTRAP PROTOCOL
# =============================================================================

@runtime_checkable
class BootstrapProtocol(Protocol):
    """
    The System Bootstrap Protocol - Brahma's Genesis.

    OWNER: Mahajana.BRAHMA

    Coordinates orderly system startup like Brahma's creation.
    """

    @property
    def owner(self) -> Mahajana:
        """Always returns Mahajana.BRAHMA."""
        ...

    @property
    def phase(self) -> BootstrapPhase:
        """Current bootstrap phase."""
        ...

    @property
    def is_ready(self) -> bool:
        """Check if system is ready."""
        ...

    def register_step(self, step: BootstrapStep) -> bool:
        """Register a bootstrap step."""
        ...

    def boot(self, timeout_ms: int = 30000) -> BootstrapResult:
        """Execute bootstrap sequence."""
        ...

    def get_state(self) -> GenesisState:
        """Get bootstrap state."""
        ...


# =============================================================================
# BOOTSTRAP IMPLEMENTATION
# =============================================================================

class Bootstrap:
    """
    Brahma's Bootstrap - System Genesis.

    OWNER: Mahajana.BRAHMA

    Coordinates orderly system startup:
    1. Wake - Consciousness begins
    2. Discover - Find configuration
    3. Prepare - Allocate resources
    4. Initialize - Start subsystems
    5. Ready - Operational
    """

    def __init__(self) -> None:
        """Initialize bootstrap coordinator."""
        self._phase = BootstrapPhase.DORMANT
        self._steps: Dict[BootstrapPhase, List[BootstrapStep]] = {
            BootstrapPhase.WAKING: [],
            BootstrapPhase.DISCOVERING: [],
            BootstrapPhase.PREPARING: [],
            BootstrapPhase.INITIALIZING: [],
        }
        self._boot_time: Optional[str] = None
        self._steps_completed = 0
        self._steps_failed = 0

    @property
    def owner(self) -> Mahajana:
        return Mahajana.BRAHMA

    @property
    def phase(self) -> BootstrapPhase:
        return self._phase

    @property
    def is_ready(self) -> bool:
        return self._phase == BootstrapPhase.READY

    def register_step(self, step: BootstrapStep) -> bool:
        """Register a bootstrap step."""
        if step.phase not in self._steps:
            return False
        self._steps[step.phase].append(step)
        # Sort by order
        self._steps[step.phase].sort(key=lambda s: s.order)
        return True

    def boot(self, timeout_ms: int = 30000) -> BootstrapResult:
        """Execute bootstrap sequence."""
        start_time = time.time()
        self._steps_completed = 0
        self._steps_failed = 0

        phases = [
            BootstrapPhase.WAKING,
            BootstrapPhase.DISCOVERING,
            BootstrapPhase.PREPARING,
            BootstrapPhase.INITIALIZING,
        ]

        for phase in phases:
            self._phase = phase

            for step in self._steps[phase]:
                # Check timeout
                elapsed = (time.time() - start_time) * 1000
                if elapsed > timeout_ms:
                    self._phase = BootstrapPhase.FAILED
                    return BootstrapResult(
                        success=False,
                        phase=self._phase,
                        duration_ms=int(elapsed),
                        steps_completed=self._steps_completed,
                        steps_failed=self._steps_failed,
                        message="Bootstrap timeout",
                    )

                # Execute step
                try:
                    if step.hook():
                        self._steps_completed += 1
                    else:
                        self._steps_failed += 1
                        if step.required:
                            self._phase = BootstrapPhase.FAILED
                            return BootstrapResult(
                                success=False,
                                phase=self._phase,
                                duration_ms=int((time.time() - start_time) * 1000),
                                steps_completed=self._steps_completed,
                                steps_failed=self._steps_failed,
                                message=f"Required step failed: {step.name}",
                            )
                except Exception as e:
                    self._steps_failed += 1
                    if step.required:
                        self._phase = BootstrapPhase.FAILED
                        return BootstrapResult(
                            success=False,
                            phase=self._phase,
                            duration_ms=int((time.time() - start_time) * 1000),
                            steps_completed=self._steps_completed,
                            steps_failed=self._steps_failed,
                            message=f"Step error: {step.name}: {e}",
                        )

        # Success
        self._phase = BootstrapPhase.READY
        self._boot_time = datetime.now().isoformat()

        return BootstrapResult(
            success=True,
            phase=self._phase,
            duration_ms=int((time.time() - start_time) * 1000),
            steps_completed=self._steps_completed,
            steps_failed=self._steps_failed,
            message="Bootstrap complete",
        )

    def get_state(self) -> GenesisState:
        """Get bootstrap state."""
        return GenesisState(
            phase=self._phase.value,
            wake_time=self._boot_time or "",
            root_loaded=self._phase in (BootstrapPhase.READY, BootstrapPhase.INITIALIZING),
            memory_allocated_bytes=0,
            creation_id=f"brahma-{hash(self._boot_time or '')}",
            health="healthy" if self._phase == BootstrapPhase.READY else "degraded",
        )


# =============================================================================
# NULL BOOTSTRAP
# =============================================================================

class NullBootstrap:
    """Instant bootstrap - for testing."""

    @property
    def owner(self) -> Mahajana:
        return Mahajana.BRAHMA

    @property
    def phase(self) -> BootstrapPhase:
        return BootstrapPhase.READY

    @property
    def is_ready(self) -> bool:
        return True

    def register_step(self, step: BootstrapStep) -> bool:
        return True

    def boot(self, timeout_ms: int = 30000) -> BootstrapResult:
        return BootstrapResult(
            success=True, phase=BootstrapPhase.READY, duration_ms=0,
            steps_completed=0, steps_failed=0, message="NullBootstrap - instant ready",
        )

    def get_state(self) -> GenesisState:
        return GenesisState(phase="ready", root_loaded=True, health="pristine")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "OWNER", "LOTUS_POSITION", "LOTUS_QUARTER", "OWNED_OPCODES",
    "BootstrapPhase", "BootstrapStep", "BootstrapResult", "BootstrapHook",
    "BootstrapProtocol", "Bootstrap", "NullBootstrap",
]
