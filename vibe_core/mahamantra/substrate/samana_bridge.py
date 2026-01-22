"""
SAMANA BRIDGE - TaskKernel ↔ ShadowReactor Integration via Nadi
================================================================

"samānas tu samānāt prāṇāt sarvāṇi prāṇāni samīkarotīti"
"Samana balances all the pranas equally."

SAMANA (समान) is the prana that balances, distributes, and digests.
It sits between PRANA (incoming) and APANA (outgoing), processing and distributing.

In our architecture:
- PRANA = User ↔ System (incoming requests)
- APANA = Agent ↔ Agent (peer communication)
- SAMANA = Kernel ↔ Shadow (work distribution)

THE SAMANA BRIDGE:
==================

    TaskKernel         ShadowReactor
        |                   |
        |    SAMANA NADI    |
        +--------↔----------+
               |
           NadiType.SAMANA

OPERATIONS:
===========

1. DISPATCH: ShadowReactor dispatches work to TaskKernel
   - on_bhoga: Queue tasks for execution
   - on_switch: Trigger batch execution at position 8
   - on_prasadam: Collect and fold results

2. FOLD: TaskKernel folds results back to ShadowReactor
   - TaskKernelResult → NadiMessage → ShadowReactor
   - Reinforcement signals flow back

3. HEARTBEAT: Both send health signals via Nadi
   - Detect stale/dead kernels
   - Auto-recovery on failure

DERIVED FROM SEED.PY:
=====================
- Uses NadiType.SAMANA (index 4)
- All timing from PRANA_DURATION_MS / TICK_INTERVAL_MS
- Buffer sizes from NADI_RESONANCE (72)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "parashurama"  # Position 8 - THE SWITCH
__position__ = 8
__genesis__ = "0xd2f4c898"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, Final, List, Optional, Tuple
from uuid import uuid4

# =============================================================================
# IMPORT FROM NADI (SSOT)
# =============================================================================
from vibe_core.mahamantra.substrate.nadi import (
    LocalNadi,
    NadiConnection,
    NadiMessage,
    NadiOp,
    NadiPriority,
    NadiProtocol,
    NadiStats,
    NadiType,
    NADI_CAPACITY,
    NADI_TIMEOUT_MS,
    get_nadi,
)

# Import from seed for derived constants
from vibe_core.mahamantra.substrate.seed import (
    NADI_RESONANCE,
    PRANA_DURATION_MS,
    TICK_INTERVAL_MS,
    SHARANAGATI,
    WORDS,
)

# GAD compliance
from vibe_core.mahamantra.protocols._gad import GADBase

# Protocol types (TYPE_CHECKING to avoid circular imports)
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from vibe_core.protocols.task_kernel_protocol import (
        TaskKernelProtocol,
        TaskKernelResult,
    )
    from vibe_core.mahamantra.reactor.shadow_protocol import (
        ShadowReactorProtocol,
        ShadowState,
    )


# =============================================================================
# DERIVED CONSTANTS - All from NADI_RESONANCE and SEED
# =============================================================================

# Maximum kernels per reactor = SHARANAGATI (6)
# One kernel per Sharanagati limb - "need to know" principle
MAX_KERNELS_PER_REACTOR: Final[int] = SHARANAGATI  # 6

# Dispatch batch size = WORDS / 2 = 8 (half mantra)
# Bhoga phase has 8 positions, so max 8 tasks per batch
DISPATCH_BATCH_SIZE: Final[int] = WORDS // 2  # 8

# Result fold timeout = PRANA_DURATION_MS × 2 = 8 seconds
# Allow 2 breath cycles for results to return
FOLD_TIMEOUT_MS: Final[int] = PRANA_DURATION_MS * 2  # 8000ms

# Heartbeat check interval = TICK_INTERVAL_MS × NADI_RESONANCE / 9
# = 250 × 72 / 9 = 250 × 8 = 2000ms = 2 seconds
SAMANA_HEARTBEAT_MS: Final[int] = (TICK_INTERVAL_MS * NADI_RESONANCE) // 9  # 2000ms

# Verification
assert MAX_KERNELS_PER_REACTOR == 6, "Max kernels = SHARANAGATI"
assert DISPATCH_BATCH_SIZE == 8, "Batch size = WORDS/2 (Bhoga phase)"
assert FOLD_TIMEOUT_MS == 8000, "Fold timeout = 8 seconds"
assert SAMANA_HEARTBEAT_MS == 2000, "Heartbeat = 2 seconds"


# =============================================================================
# SAMANA MESSAGE TYPES
# =============================================================================

class SamanaMessageType:
    """
    Message types for Samana bridge.

    Not an enum to allow extensibility.
    """
    # Dispatch operations
    DISPATCH = "dispatch"        # Shadow → Kernel: Execute this task
    DISPATCH_BATCH = "dispatch_batch"  # Shadow → Kernel: Execute batch

    # Fold operations
    FOLD = "fold"                # Kernel → Shadow: Here's my result
    FOLD_BATCH = "fold_batch"    # Kernel → Shadow: Here are batch results

    # Lifecycle
    SPAWN = "spawn"              # Shadow → Kernel: Spawn new kernel
    TERMINATE = "terminate"      # Either → Other: Shutdown gracefully
    HEARTBEAT = "heartbeat"      # Bidirectional: I'm alive

    # Control
    PAUSE = "pause"              # Shadow → Kernel: Pause execution
    RESUME = "resume"            # Shadow → Kernel: Resume execution


# =============================================================================
# SAMANA DISPATCH REQUEST
# =============================================================================

@dataclass
class SamanaDispatch:
    """
    A dispatch request from ShadowReactor to TaskKernel.

    Contains task info and context for execution.
    """
    dispatch_id: str
    task_id: str
    task_description: str
    position: int  # Lotus position (0-15)
    phase: str     # bhoga/prasadam/return
    priority: NadiPriority = NadiPriority.RAJAS
    timeout_ms: int = FOLD_TIMEOUT_MS
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_nadi_payload(self) -> Dict[str, Any]:
        """Convert to Nadi message payload."""
        return {
            "type": SamanaMessageType.DISPATCH,
            "dispatch_id": self.dispatch_id,
            "task_id": self.task_id,
            "task_description": self.task_description,
            "position": self.position,
            "phase": self.phase,
            "timeout_ms": self.timeout_ms,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_nadi_payload(cls, payload: Dict[str, Any]) -> "SamanaDispatch":
        """Create from Nadi message payload."""
        return cls(
            dispatch_id=payload["dispatch_id"],
            task_id=payload["task_id"],
            task_description=payload["task_description"],
            position=payload["position"],
            phase=payload["phase"],
            timeout_ms=payload.get("timeout_ms", FOLD_TIMEOUT_MS),
            payload=payload.get("payload", {}),
            timestamp=datetime.fromisoformat(payload["timestamp"]),
        )


# =============================================================================
# SAMANA FOLD RESULT
# =============================================================================

@dataclass
class SamanaFold:
    """
    A fold result from TaskKernel to ShadowReactor.

    Contains execution result and reinforcement signal.
    """
    fold_id: str
    dispatch_id: str  # Links back to dispatch
    kernel_id: str
    status: str  # completed/failed/timeout
    output: Any = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    reinforcement_signal: float = 0.0  # +1 = good, -1 = bad
    timestamp: datetime = field(default_factory=datetime.now)

    def to_nadi_payload(self) -> Dict[str, Any]:
        """Convert to Nadi message payload."""
        return {
            "type": SamanaMessageType.FOLD,
            "fold_id": self.fold_id,
            "dispatch_id": self.dispatch_id,
            "kernel_id": self.kernel_id,
            "status": self.status,
            "output": str(self.output)[:1000] if self.output else None,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "reinforcement_signal": self.reinforcement_signal,
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_nadi_payload(cls, payload: Dict[str, Any]) -> "SamanaFold":
        """Create from Nadi message payload."""
        return cls(
            fold_id=payload["fold_id"],
            dispatch_id=payload["dispatch_id"],
            kernel_id=payload["kernel_id"],
            status=payload["status"],
            output=payload.get("output"),
            error=payload.get("error"),
            duration_ms=payload.get("duration_ms", 0.0),
            reinforcement_signal=payload.get("reinforcement_signal", 0.0),
            timestamp=datetime.fromisoformat(payload["timestamp"]),
        )


# =============================================================================
# SAMANA BRIDGE - The Integration Layer
# =============================================================================

class SamanaBridge(GADBase):
    """
    The Samana Bridge - TaskKernel ↔ ShadowReactor Integration.

    Uses NadiType.SAMANA for all communication.
    GAD-000 compliant.

    LIFECYCLE:
    ==========
    1. Shadow creates SamanaBridge at startup
    2. Bridge creates Nadi endpoint for kernel communication
    3. On dispatch: Shadow sends SamanaDispatch via Nadi
    4. On fold: Kernel sends SamanaFold via Nadi
    5. Bridge manages kernel pool and result aggregation
    """

    def __init__(
        self,
        reactor_id: str,
        max_kernels: int = MAX_KERNELS_PER_REACTOR,
    ):
        super().__init__()  # Initialize GADBase

        self._reactor_id = reactor_id
        self._max_kernels = min(max_kernels, MAX_KERNELS_PER_REACTOR)

        # Nadi endpoint for this bridge
        self._nadi = LocalNadi(
            endpoint_id=f"samana_{reactor_id}",
            nadi_type=NadiType.SAMANA,
        )

        # Kernel tracking
        self._active_kernels: Dict[str, str] = {}  # kernel_id → dispatch_id
        self._pending_dispatches: Dict[str, SamanaDispatch] = {}  # dispatch_id → dispatch
        self._completed_folds: Dict[str, SamanaFold] = {}  # dispatch_id → fold

        # Callbacks
        self._on_fold: Optional[Callable[[SamanaFold], None]] = None

        # Stats
        self._dispatches_sent = 0
        self._folds_received = 0

    # =========================================================================
    # PROPERTIES
    # =========================================================================

    @property
    def reactor_id(self) -> str:
        return self._reactor_id

    @property
    def active_kernel_count(self) -> int:
        return len(self._active_kernels)

    @property
    def pending_dispatch_count(self) -> int:
        return len(self._pending_dispatches)

    @property
    def can_dispatch(self) -> bool:
        """Can we dispatch more work?"""
        return self.active_kernel_count < self._max_kernels

    # =========================================================================
    # GAD COMPLIANCE
    # =========================================================================

    def discover(self) -> Dict[str, object]:
        """GAD Discoverability."""
        return {
            "service": "samana_bridge",
            "mahajana": __mahajana__,
            "position": __position__,
            "genesis": __genesis__,
            "reactor_id": self._reactor_id,
            "nadi_type": NadiType.SAMANA.name,
            "max_kernels": self._max_kernels,
            "capabilities": [
                "dispatch",
                "fold",
                "batch_dispatch",
                "batch_fold",
            ],
        }

    def get_state(self) -> Dict[str, object]:
        """GAD Observability."""
        return {
            "reactor_id": self._reactor_id,
            "active_kernels": self.active_kernel_count,
            "pending_dispatches": self.pending_dispatch_count,
            "completed_folds": len(self._completed_folds),
            "dispatches_sent": self._dispatches_sent,
            "folds_received": self._folds_received,
            "can_dispatch": self.can_dispatch,
            "heartbeat": self.heartbeat.get_summary(),
        }

    def detect_drift(self) -> List[str]:
        """GAD Drift Detection."""
        issues = []

        # Check for stale dispatches (older than FOLD_TIMEOUT_MS)
        now = datetime.now()
        for dispatch_id, dispatch in self._pending_dispatches.items():
            age_ms = (now - dispatch.timestamp).total_seconds() * 1000
            if age_ms > FOLD_TIMEOUT_MS:
                issues.append(f"Stale dispatch: {dispatch_id} ({age_ms:.0f}ms)")

        # Check kernel count
        if self.active_kernel_count > self._max_kernels:
            issues.append(f"Kernel overflow: {self.active_kernel_count}/{self._max_kernels}")

        return issues

    def test_tapas(self) -> bool:
        """GAD Tapas: Resource efficiency."""
        # Check we're not wasting resources on stale dispatches
        stale_count = len(self.detect_drift())
        return stale_count < self._max_kernels // 2

    def test_saucam(self) -> bool:
        """GAD Saucam: Connection purity."""
        # Check Nadi is using correct type
        return self._nadi.nadi_type == NadiType.SAMANA

    # =========================================================================
    # DISPATCH - Shadow → Kernel
    # =========================================================================

    def dispatch(
        self,
        task_id: str,
        task_description: str,
        position: int,
        phase: str,
        priority: NadiPriority = NadiPriority.RAJAS,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Dispatch a task to an available kernel.

        Returns dispatch_id if queued, None if no capacity.
        """
        if not self.can_dispatch:
            return None

        dispatch_id = f"dispatch_{uuid4().hex[:8]}"
        dispatch = SamanaDispatch(
            dispatch_id=dispatch_id,
            task_id=task_id,
            task_description=task_description,
            position=position,
            phase=phase,
            priority=priority,
            payload=payload or {},
        )

        # Queue the dispatch
        self._pending_dispatches[dispatch_id] = dispatch
        self._dispatches_sent += 1

        # Create Nadi message
        message = NadiMessage(
            source=self._nadi.endpoint_id,
            target="*",  # Broadcast to available kernels
            nadi_type=NadiType.SAMANA,
            operation=NadiOp.DELEGATE,
            payload=dispatch.to_nadi_payload(),
            priority=priority,
        )

        # Send via Nadi
        self._nadi.broadcast(NadiOp.DELEGATE, dispatch.to_nadi_payload())

        return dispatch_id

    def dispatch_batch(
        self,
        tasks: List[Tuple[str, str, Dict[str, Any]]],
        position: int,
        phase: str,
    ) -> List[str]:
        """
        Dispatch a batch of tasks.

        Args:
            tasks: List of (task_id, description, payload) tuples
            position: Current Lotus position
            phase: Current phase

        Returns:
            List of dispatch_ids for queued tasks
        """
        dispatch_ids = []

        for task_id, description, payload in tasks[:DISPATCH_BATCH_SIZE]:
            dispatch_id = self.dispatch(
                task_id=task_id,
                task_description=description,
                position=position,
                phase=phase,
                payload=payload,
            )
            if dispatch_id:
                dispatch_ids.append(dispatch_id)
            else:
                break  # No more capacity

        return dispatch_ids

    # =========================================================================
    # FOLD - Kernel → Shadow
    # =========================================================================

    def register_kernel(self, kernel_id: str, dispatch_id: str) -> bool:
        """
        Register a kernel as handling a dispatch.

        Called when kernel accepts a dispatch.
        """
        if dispatch_id not in self._pending_dispatches:
            return False

        self._active_kernels[kernel_id] = dispatch_id
        return True

    def fold(self, fold: SamanaFold) -> bool:
        """
        Receive a fold result from a kernel.

        Returns True if fold was accepted.
        """
        dispatch_id = fold.dispatch_id

        # Validate dispatch exists
        if dispatch_id not in self._pending_dispatches:
            return False

        # Store fold
        self._completed_folds[dispatch_id] = fold
        self._folds_received += 1

        # Remove from pending
        del self._pending_dispatches[dispatch_id]

        # Remove kernel from active
        kernel_to_remove = None
        for kernel_id, d_id in self._active_kernels.items():
            if d_id == dispatch_id:
                kernel_to_remove = kernel_id
                break
        if kernel_to_remove:
            del self._active_kernels[kernel_to_remove]

        # Trigger callback
        if self._on_fold:
            self._on_fold(fold)

        return True

    def receive_folds(self) -> List[SamanaFold]:
        """
        Receive all pending fold messages from Nadi.

        Call this in the prasadam phase to collect results.
        """
        folds = []

        for message in self._nadi.receive_all():
            if message.operation == NadiOp.RECEIVE:
                payload = message.payload
                if payload.get("type") == SamanaMessageType.FOLD:
                    fold = SamanaFold.from_nadi_payload(payload)
                    if self.fold(fold):
                        folds.append(fold)

        return folds

    def get_fold(self, dispatch_id: str) -> Optional[SamanaFold]:
        """Get a completed fold by dispatch_id."""
        return self._completed_folds.get(dispatch_id)

    def set_on_fold(self, callback: Callable[[SamanaFold], None]) -> None:
        """Set callback for when folds are received."""
        self._on_fold = callback

    # =========================================================================
    # HEARTBEAT
    # =========================================================================

    def pulse(self) -> bool:
        """
        Send heartbeat and check kernel health.

        Returns True if healthy.
        """
        # Prune stale dispatches
        now = datetime.now()
        stale = []
        for dispatch_id, dispatch in self._pending_dispatches.items():
            age_ms = (now - dispatch.timestamp).total_seconds() * 1000
            if age_ms > FOLD_TIMEOUT_MS * 2:  # 2x timeout = definitely stale
                stale.append(dispatch_id)

        for dispatch_id in stale:
            # Create timeout fold
            fold = SamanaFold(
                fold_id=f"timeout_{uuid4().hex[:8]}",
                dispatch_id=dispatch_id,
                kernel_id="timeout",
                status="timeout",
                error="Dispatch timed out",
                reinforcement_signal=-0.5,  # Negative reinforcement
            )
            self.fold(fold)

        # Also chant for GADBase
        self.chant()

        return len(stale) == 0

    # =========================================================================
    # STATS
    # =========================================================================

    def get_stats(self) -> Dict[str, Any]:
        """Get bridge statistics."""
        return {
            "reactor_id": self._reactor_id,
            "active_kernels": self.active_kernel_count,
            "max_kernels": self._max_kernels,
            "pending_dispatches": self.pending_dispatch_count,
            "completed_folds": len(self._completed_folds),
            "dispatches_sent": self._dispatches_sent,
            "folds_received": self._folds_received,
            "nadi_stats": self._nadi.get_stats().__dict__,
        }


# =============================================================================
# FACTORY FUNCTION
# =============================================================================

def create_samana_bridge(
    reactor_id: str,
    max_kernels: int = MAX_KERNELS_PER_REACTOR,
) -> SamanaBridge:
    """
    Create a SamanaBridge for a ShadowReactor.

    Args:
        reactor_id: ID of the owning ShadowReactor
        max_kernels: Maximum concurrent kernels (default: SHARANAGATI = 6)

    Returns:
        SamanaBridge instance
    """
    return SamanaBridge(reactor_id, max_kernels)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "MAX_KERNELS_PER_REACTOR",
    "DISPATCH_BATCH_SIZE",
    "FOLD_TIMEOUT_MS",
    "SAMANA_HEARTBEAT_MS",
    # Message types
    "SamanaMessageType",
    # Data structures
    "SamanaDispatch",
    "SamanaFold",
    # Bridge
    "SamanaBridge",
    # Factory
    "create_samana_bridge",
]
