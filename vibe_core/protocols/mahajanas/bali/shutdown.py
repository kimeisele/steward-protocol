"""
SHUTDOWN - Graceful Shutdown Protocol
=====================================

OWNER: BALI (The Surrendered King)
POSITION: 13 (MOKSHA Quarter)
OPCODE: OPTIMIZE (YIELD_CPU)

Bali surrendered EVERYTHING to Vamana - even his kingdom.
This is the model for graceful shutdown: orderly surrender of all resources.

SHASTRA BASIS:
    When Vamana asked for three steps of land, Bali gave it.
    When Vamana covered the earth with one step and the heavens
    with another, Bali offered his head for the third step.

    This is PRAPATTI - complete surrender.

    In code: A system that cannot surrender = INFINITE LOOPS
    = HIRANYAKASHIPU (Bali's grandfather who REFUSED to surrender)

SHUTDOWN PHASES:
    1. PREPARE  - Announce shutdown, stop accepting new work
    2. DRAIN    - Wait for in-flight operations to complete
    3. RELEASE  - Release all held resources
    4. STOP     - Final termination
    5. (ABORT)  - Emergency termination (skip phases)

WATERTIGHT: No Any types. All typed explicitly.
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "bali"
__position__ = 13
__genesis__ = "0x6f84049c"  # GenesisByte: parampara % 37 == 0

import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Dict, Final, List, Optional, Protocol, runtime_checkable

from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode

from vibe_core.protocols.mahajanas.bali import (
    SurrenderType,
    SurrenderResult,
    SurrenderState,
)


# =============================================================================
# OWNERSHIP DECLARATION - Bali OWNS this protocol
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.BALI
LOTUS_POSITION: Final[int] = 13  # MOKSHA Quarter, Worker 1
LOTUS_QUARTER: Final[str] = "moksha"

OWNED_OPCODES: Final[List[MantraOpCode]] = [
    MantraOpCode.IO_FLUSH,  # YIELD_CPU
]


# =============================================================================
# SHUTDOWN PHASES
# =============================================================================

class ShutdownPhase(str, Enum):
    """Phases of graceful shutdown."""
    RUNNING = "running"       # Normal operation
    PREPARE = "prepare"       # Preparing for shutdown
    DRAIN = "drain"           # Draining in-flight work
    RELEASE = "release"       # Releasing resources
    STOPPED = "stopped"       # Fully stopped
    ABORTED = "aborted"       # Emergency abort


class ShutdownReason(str, Enum):
    """Reasons for shutdown."""
    REQUESTED = "requested"   # User/admin requested
    TIMEOUT = "timeout"       # Exceeded time limit
    ERROR = "error"           # Unrecoverable error
    RESOURCE = "resource"     # Resource exhaustion
    SIGNAL = "signal"         # OS signal (SIGTERM, etc.)
    PRAPATTI = "prapatti"     # Full surrender (like Bali)


# =============================================================================
# SHUTDOWN RESULT
# =============================================================================

@dataclass(frozen=True)
class ShutdownResult:
    """Result of a shutdown operation."""
    success: bool
    phase: ShutdownPhase
    reason: ShutdownReason
    duration_ms: int
    resources_released: int
    pending_drained: int
    message: str

    def to_surrender_result(self) -> SurrenderResult:
        """Convert to SurrenderResult for BaliProtocol compatibility."""
        return SurrenderResult(
            success=self.success,
            surrender_type=SurrenderType.SHUTDOWN.value,
            resources_released=self.resources_released,
            timestamp=datetime.now().isoformat(),
            message=self.message,
        )


# =============================================================================
# SHUTDOWN HOOK - Callback during shutdown
# =============================================================================

ShutdownHook = Callable[[ShutdownPhase], bool]


@dataclass
class ShutdownHookEntry:
    """A registered shutdown hook."""
    name: str
    hook: ShutdownHook
    phase: ShutdownPhase  # Which phase to run in
    priority: int = 0     # Higher = runs first
    timeout_ms: int = 5000


# =============================================================================
# SHUTDOWN PROTOCOL
# =============================================================================

@runtime_checkable
class ShutdownProtocol(Protocol):
    """
    The Graceful Shutdown Protocol - Bali's Prapatti.

    OWNER: Mahajana.BALI

    Like Bali who surrendered orderly to Vamana,
    this protocol ensures clean shutdown:
    - Announce intention
    - Drain pending work
    - Release resources
    - Final stop

    ANTI-MAYAVAD:
    - No Any types
    - Bali OWNS shutdown
    - Resources have PERSONAL owners (tracked)
    """

    @property
    def owner(self) -> Mahajana:
        """Always returns Mahajana.BALI."""
        ...

    @property
    def phase(self) -> ShutdownPhase:
        """Current shutdown phase."""
        ...

    @property
    def is_shutting_down(self) -> bool:
        """Check if shutdown is in progress."""
        ...

    # =========================================================================
    # Shutdown Operations
    # =========================================================================

    def initiate(self, reason: ShutdownReason = ShutdownReason.REQUESTED) -> bool:
        """
        Initiate graceful shutdown.
        Returns True if shutdown started.
        """
        ...

    def abort(self, reason: str = "") -> ShutdownResult:
        """
        Emergency abort - skip phases, stop immediately.
        Like Hiranyakashipu's end - no grace.
        """
        ...

    def wait(self, timeout_ms: int = 30000) -> ShutdownResult:
        """
        Wait for shutdown to complete.
        Returns result when done or timeout.
        """
        ...

    # =========================================================================
    # Hook Management
    # =========================================================================

    def register_hook(
        self,
        name: str,
        hook: ShutdownHook,
        phase: ShutdownPhase = ShutdownPhase.RELEASE,
        priority: int = 0,
        timeout_ms: int = 5000,
    ) -> bool:
        """Register a shutdown hook."""
        ...

    def unregister_hook(self, name: str) -> bool:
        """Unregister a shutdown hook."""
        ...

    # =========================================================================
    # Resource Tracking
    # =========================================================================

    def track_resource(self, resource_id: str, release_hook: Callable[[], bool]) -> bool:
        """Track a resource for release during shutdown."""
        ...

    def untrack_resource(self, resource_id: str) -> bool:
        """Untrack a resource (already released)."""
        ...

    # =========================================================================
    # State
    # =========================================================================

    def get_state(self) -> SurrenderState:
        """Get shutdown state."""
        ...


# =============================================================================
# SHUTDOWN COORDINATOR - Implementation
# =============================================================================

class ShutdownCoordinator:
    """
    Bali's Shutdown Coordinator - Graceful Prapatti.

    OWNER: Mahajana.BALI

    Coordinates orderly shutdown like Bali's surrender:
    1. PREPARE: Stop accepting new work
    2. DRAIN: Complete in-flight operations
    3. RELEASE: Free all resources
    4. STOP: Final termination

    Features:
    - Phase-based shutdown
    - Hook callbacks
    - Resource tracking
    - Timeout handling
    """

    def __init__(
        self,
        drain_timeout_ms: int = 10000,
        release_timeout_ms: int = 5000,
    ) -> None:
        """Initialize shutdown coordinator."""
        self._phase = ShutdownPhase.RUNNING
        self._reason: Optional[ShutdownReason] = None
        self._start_time: Optional[float] = None
        self._drain_timeout_ms = drain_timeout_ms
        self._release_timeout_ms = release_timeout_ms

        # Hooks by phase
        self._hooks: Dict[ShutdownPhase, List[ShutdownHookEntry]] = {
            ShutdownPhase.PREPARE: [],
            ShutdownPhase.DRAIN: [],
            ShutdownPhase.RELEASE: [],
        }

        # Resources to release
        self._resources: Dict[str, Callable[[], bool]] = {}

        # Stats
        self._resources_released = 0
        self._pending_drained = 0

    @property
    def owner(self) -> Mahajana:
        return Mahajana.BALI

    @property
    def phase(self) -> ShutdownPhase:
        return self._phase

    @property
    def is_shutting_down(self) -> bool:
        return self._phase not in (ShutdownPhase.RUNNING, ShutdownPhase.STOPPED, ShutdownPhase.ABORTED)

    # =========================================================================
    # Shutdown Operations
    # =========================================================================

    def initiate(self, reason: ShutdownReason = ShutdownReason.REQUESTED) -> bool:
        """Initiate graceful shutdown."""
        if self._phase != ShutdownPhase.RUNNING:
            return False  # Already shutting down

        self._reason = reason
        self._start_time = time.time()
        self._phase = ShutdownPhase.PREPARE

        # Run prepare hooks
        self._run_phase_hooks(ShutdownPhase.PREPARE)

        # Move to drain
        self._phase = ShutdownPhase.DRAIN
        self._run_phase_hooks(ShutdownPhase.DRAIN)

        # Move to release
        self._phase = ShutdownPhase.RELEASE
        self._release_all_resources()
        self._run_phase_hooks(ShutdownPhase.RELEASE)

        # Final stop
        self._phase = ShutdownPhase.STOPPED
        return True

    def abort(self, reason: str = "") -> ShutdownResult:
        """Emergency abort - no grace."""
        self._phase = ShutdownPhase.ABORTED
        self._reason = ShutdownReason.ERROR

        elapsed_ms = int((time.time() - (self._start_time or time.time())) * 1000)

        return ShutdownResult(
            success=True,
            phase=ShutdownPhase.ABORTED,
            reason=ShutdownReason.ERROR,
            duration_ms=elapsed_ms,
            resources_released=0,
            pending_drained=0,
            message=f"Emergency abort: {reason}" if reason else "Emergency abort",
        )

    def wait(self, timeout_ms: int = 30000) -> ShutdownResult:
        """Wait for shutdown to complete."""
        start = time.time()

        while self._phase not in (ShutdownPhase.STOPPED, ShutdownPhase.ABORTED):
            elapsed = (time.time() - start) * 1000
            if elapsed > timeout_ms:
                return self.abort("Shutdown timeout")
            time.sleep(0.01)  # 10ms poll

        elapsed_ms = int((time.time() - (self._start_time or start)) * 1000)

        return ShutdownResult(
            success=self._phase == ShutdownPhase.STOPPED,
            phase=self._phase,
            reason=self._reason or ShutdownReason.REQUESTED,
            duration_ms=elapsed_ms,
            resources_released=self._resources_released,
            pending_drained=self._pending_drained,
            message="Shutdown complete" if self._phase == ShutdownPhase.STOPPED else "Shutdown aborted",
        )

    # =========================================================================
    # Hook Management
    # =========================================================================

    def register_hook(
        self,
        name: str,
        hook: ShutdownHook,
        phase: ShutdownPhase = ShutdownPhase.RELEASE,
        priority: int = 0,
        timeout_ms: int = 5000,
    ) -> bool:
        """Register a shutdown hook."""
        if phase not in self._hooks:
            return False

        entry = ShutdownHookEntry(
            name=name,
            hook=hook,
            phase=phase,
            priority=priority,
            timeout_ms=timeout_ms,
        )

        self._hooks[phase].append(entry)
        # Sort by priority (descending)
        self._hooks[phase].sort(key=lambda e: e.priority, reverse=True)
        return True

    def unregister_hook(self, name: str) -> bool:
        """Unregister a shutdown hook."""
        for phase_hooks in self._hooks.values():
            for i, entry in enumerate(phase_hooks):
                if entry.name == name:
                    phase_hooks.pop(i)
                    return True
        return False

    def _run_phase_hooks(self, phase: ShutdownPhase) -> None:
        """Run all hooks for a phase."""
        for entry in self._hooks.get(phase, []):
            try:
                entry.hook(phase)
            except Exception:
                pass  # Hooks should not block shutdown

    # =========================================================================
    # Resource Tracking
    # =========================================================================

    def track_resource(self, resource_id: str, release_hook: Callable[[], bool]) -> bool:
        """Track a resource for release during shutdown."""
        if resource_id in self._resources:
            return False
        self._resources[resource_id] = release_hook
        return True

    def untrack_resource(self, resource_id: str) -> bool:
        """Untrack a resource (already released)."""
        if resource_id not in self._resources:
            return False
        del self._resources[resource_id]
        return True

    def _release_all_resources(self) -> None:
        """Release all tracked resources."""
        for resource_id, release_hook in list(self._resources.items()):
            try:
                if release_hook():
                    self._resources_released += 1
            except Exception:
                pass  # Best effort
            finally:
                del self._resources[resource_id]

    # =========================================================================
    # State
    # =========================================================================

    def get_state(self) -> SurrenderState:
        """Get shutdown state."""
        return SurrenderState(
            can_surrender=self._phase == ShutdownPhase.RUNNING,
            is_surrendered=self._phase in (ShutdownPhase.STOPPED, ShutdownPhase.ABORTED),
            total_yields=0,
            total_releases=self._resources_released,
            last_surrender=datetime.now().isoformat() if self._phase == ShutdownPhase.STOPPED else "",
            health="pristine" if self._phase == ShutdownPhase.RUNNING else "stopped",
        )


# =============================================================================
# NULL SHUTDOWN - For testing
# =============================================================================

class NullShutdown:
    """
    The Immortal Process - cannot be shut down.

    Documents the ANTI-PATTERN (Hiranyakashipu).
    Used for testing.
    """

    @property
    def owner(self) -> Mahajana:
        return Mahajana.BALI

    @property
    def phase(self) -> ShutdownPhase:
        return ShutdownPhase.RUNNING

    @property
    def is_shutting_down(self) -> bool:
        return False

    def initiate(self, reason: ShutdownReason = ShutdownReason.REQUESTED) -> bool:
        return True  # Pretend it worked

    def abort(self, reason: str = "") -> ShutdownResult:
        return ShutdownResult(
            success=True,
            phase=ShutdownPhase.ABORTED,
            reason=ShutdownReason.REQUESTED,
            duration_ms=0,
            resources_released=0,
            pending_drained=0,
            message="NullShutdown - instant abort",
        )

    def wait(self, timeout_ms: int = 30000) -> ShutdownResult:
        return ShutdownResult(
            success=True,
            phase=ShutdownPhase.STOPPED,
            reason=ShutdownReason.REQUESTED,
            duration_ms=0,
            resources_released=0,
            pending_drained=0,
            message="NullShutdown - instant complete",
        )

    def register_hook(self, name: str, hook: ShutdownHook, phase: ShutdownPhase = ShutdownPhase.RELEASE, priority: int = 0, timeout_ms: int = 5000) -> bool:
        return True

    def unregister_hook(self, name: str) -> bool:
        return True

    def track_resource(self, resource_id: str, release_hook: Callable[[], bool]) -> bool:
        return True

    def untrack_resource(self, resource_id: str) -> bool:
        return True

    def get_state(self) -> SurrenderState:
        return SurrenderState(
            can_surrender=True,
            is_surrendered=False,
            total_yields=0,
            total_releases=0,
            health="pristine",
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Ownership
    "OWNER",
    "LOTUS_POSITION",
    "LOTUS_QUARTER",
    "OWNED_OPCODES",
    # Enums
    "ShutdownPhase",
    "ShutdownReason",
    # Types
    "ShutdownResult",
    "ShutdownHook",
    "ShutdownHookEntry",
    # Protocol
    "ShutdownProtocol",
    # Implementations
    "ShutdownCoordinator",
    "NullShutdown",
]
