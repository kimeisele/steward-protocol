"""
COGNITIVE CYCLE PROTOCOL - The Sadhana Loop
============================================

Owner: JANAKA (Duty/Execution)
OpCode: EXEC_SERVICE

"The Orchestration IS the Mantra."

Janaka's domain includes not just task execution, but the CYCLES that
orchestrate work: PERCEIVE → ORIENT → DECIDE → ACT → PERSIST.

This is the OODA loop as Bhakti Yoga.

IMPLEMENTATION:
    vibe_core/orchestration_cycle.py implements this protocol.

WATERTIGHT: No Any types. All typed explicitly.
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0x89fb2038"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import (
    Callable,
    Dict,
    Final,
    List,
    Optional,
    Protocol,
    Tuple,
    TypedDict,
    TypeVar,
    Union,
    runtime_checkable,
)

from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode
from vibe_core.protocols.mahajanas.owned_protocol import OwnedProtocol, ProtocolState


# =============================================================================
# CONSTANTS
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.JANAKA

OWNED_OPCODES: Final[List[MantraOpCode]] = [
    MantraOpCode.STATE_SYNC,  # Cycle orchestration (duty check at each phase)
]


# =============================================================================
# WATERTIGHT TYPES (NO ANY!)
# =============================================================================


class CyclePhase(str, Enum):
    """Phases of a cognitive cycle (OODA Loop as Bhakti)."""
    PERCEIVE = "perceive"   # Gather observations
    ORIENT = "orient"       # Analyze context
    DECIDE = "decide"       # Choose actions
    ACT = "act"             # Execute decisions
    PERSIST = "persist"     # Record state
    RECOVER = "recover"     # Handle errors


class CycleStatus(str, Enum):
    """Status of a cycle execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    THROTTLED = "throttled"


# WATERTIGHT: The union of allowed observation/decision/action types
# Instead of List[Any], we use List[CycleElement]
CycleElement = Union[str, int, float, bool, Dict[str, str], List[str], None]


class PhaseResult(TypedDict, total=False):
    """
    Result from a single phase execution.
    WATERTIGHT - no Any!
    """
    phase: str                # CyclePhase value
    success: bool
    elements_count: int       # Number of observations/decisions/etc
    element_types: List[str]  # Python types of elements
    duration_ms: int
    error_message: str


class CycleContextState(TypedDict, total=False):
    """
    Serializable state of a cycle context.
    WATERTIGHT - no Any!
    """
    cycle_id: str
    parent_cycle_id: str
    trace_id: str
    cycle_name: str
    phase: str                # CyclePhase value
    status: str               # CycleStatus value
    observations_count: int
    orientations_count: int
    decisions_count: int
    actions_count: int
    has_result: bool
    error_count: int
    error_phases: List[str]
    start_time: str           # ISO timestamp
    elapsed_ms: int


class RetentionConfig(TypedDict, total=False):
    """
    Configuration for cycle retention (memory safety).
    WATERTIGHT - no Any!
    """
    max_completed_cycles: int
    max_error_cycles: int
    max_age_seconds: int
    enabled: bool


class CycleRegistryStats(TypedDict, total=False):
    """
    Statistics about the cycle registry.
    WATERTIGHT - no Any!
    """
    total_cycles: int
    active_cycles: int
    completed_cycles: int
    error_cycles: int
    retention_enabled: bool
    retention_max_completed: int
    retention_max_errors: int


class CycleState(TypedDict, total=False):
    """
    Full state of the cycle orchestration system.
    WATERTIGHT - no Any!
    """
    protocol_name: str
    owner: str
    is_chanting: bool
    active_cycle_ids: List[str]
    registry_stats: CycleRegistryStats
    health: str               # "pristine", "healthy", "degraded"


# =============================================================================
# COGNITIVE CYCLE PROTOCOL
# =============================================================================


@runtime_checkable
class CognitiveCycleProtocol(Protocol):
    """
    Protocol for Cognitive Cycles (OODA Loop).

    Owner: JANAKA
    OpCode: EXEC_SERVICE (via CHECK_DHARMA)

    The Sadhana Loop: PERCEIVE → ORIENT → DECIDE → ACT → PERSIST.
    Each phase corresponds to a Pada of the Mahamantra.

    WATERTIGHT - no Any types in interface!
    """

    @property
    def cycle_name(self) -> str:
        """Human-readable cycle name (e.g., 'cognitive_kernel')."""
        ...

    @property
    def rate_limit_seconds(self) -> int:
        """Minimum seconds between cycles (0 = no limit)."""
        ...

    @property
    def timeout_seconds(self) -> int:
        """Max runtime for entire cycle (0 = no timeout)."""
        ...

    @property
    def recovery_enabled(self) -> bool:
        """Should we catch and recover from errors?"""
        ...

    @property
    def parent_cycle_id(self) -> Optional[str]:
        """Holon wiring: ID of parent cycle that spawned this one."""
        ...

    # =========================================================================
    # Phase Execution
    # =========================================================================

    def perceive(self) -> PhaseResult:
        """
        PERCEIVE: Gather observations from the environment.
        Returns structured PhaseResult.
        """
        ...

    def orient(self, observations_count: int) -> PhaseResult:
        """
        ORIENT: Analyze observations and establish context.
        Returns structured PhaseResult.
        """
        ...

    def decide(self, orientations_count: int) -> PhaseResult:
        """
        DECIDE: Choose actions based on analysis.
        Returns structured PhaseResult.
        """
        ...

    def act(self, decisions_count: int) -> PhaseResult:
        """
        ACT: Execute the decisions.
        Returns structured PhaseResult.
        """
        ...

    def persist(self) -> PhaseResult:
        """
        PERSIST: Record state for future cycles.
        Returns structured PhaseResult.
        """
        ...

    def recover(self, error_phases: List[str]) -> bool:
        """
        RECOVER: Handle errors from failed phases.
        Returns True if recovered successfully.
        """
        ...

    # =========================================================================
    # Cycle Management
    # =========================================================================

    def orchestrate(self, force: bool = False) -> Optional[CycleContextState]:
        """
        Run the full Sadhana Loop.
        Returns the cycle context state, or None if throttled.
        """
        ...

    def get_context_state(self) -> CycleContextState:
        """
        Get current cycle context state.
        WATERTIGHT - returns CycleContextState, not Dict[str, Any].
        """
        ...

    def is_running(self) -> bool:
        """Check if cycle is currently executing."""
        ...

    def get_last_cycle_time(self) -> Optional[str]:
        """Get ISO timestamp of last cycle completion."""
        ...


# =============================================================================
# CYCLE REGISTRY PROTOCOL
# =============================================================================


@runtime_checkable
class CycleRegistryProtocol(Protocol):
    """
    Protocol for Cycle Registry (lifecycle management).

    Manages all active/completed/error cycles with retention policy.
    WATERTIGHT - no Any types!
    """

    def register_cycle(self, context_state: CycleContextState) -> None:
        """Register a new cycle as active."""
        ...

    def complete_cycle(self, cycle_id: str) -> None:
        """Mark cycle as complete. Applies retention policy."""
        ...

    def error_cycle(self, cycle_id: str, error_phases: List[str]) -> None:
        """Mark cycle as failed. Keeps more errors for debugging."""
        ...

    def get_active_cycles(self) -> List[CycleContextState]:
        """Get currently running cycles."""
        ...

    def get_completed_cycles(self, limit: int = 100) -> List[CycleContextState]:
        """Get recently completed cycles."""
        ...

    def get_error_cycles(self, limit: int = 100) -> List[CycleContextState]:
        """Get recently failed cycles."""
        ...

    def get_stats(self) -> CycleRegistryStats:
        """Get registry statistics. WATERTIGHT."""
        ...

    def get_retention_config(self) -> RetentionConfig:
        """Get current retention configuration."""
        ...


# =============================================================================
# OWNED PROTOCOL WRAPPER
# =============================================================================


class CycleOwnedProtocol(OwnedProtocol):
    """
    OwnedProtocol wrapper for CognitiveCycle.

    Allows cycles to:
    - Be owned by JANAKA
    - Chant the Mahamantra
    - Pass GAD-000 audits
    - Be traceable to source
    """

    OWNER = Mahajana.JANAKA
    OPCODES = list(OWNED_OPCODES)
    PROTOCOL_NAME = "cognitive_cycle"
    DESCRIPTION = "The Sadhana Loop - OODA as Bhakti"

    def __init__(self, cycle: CognitiveCycleProtocol) -> None:
        super().__init__()
        self._cycle = cycle

    def get_state(self) -> ProtocolState:
        """Return current state. WATERTIGHT - no Any!"""
        return ProtocolState(
            protocol_name=self.PROTOCOL_NAME,
            owner=self.OWNER.value,
            is_chanting=self.is_chanting,
            heartbeat_position=self._heartbeat.word_position,
            mantra_count=self._heartbeat.mantra_count,
            mala_count=self._heartbeat.mala_count,
            gad_compliant=True,
        )

    @property
    def cycle(self) -> CognitiveCycleProtocol:
        """Access the underlying cycle."""
        return self._cycle


# =============================================================================
# NULL IMPLEMENTATION
# =============================================================================


class NullCognitiveCycle:
    """
    Null implementation for testing.
    All phases succeed silently.
    """

    @property
    def cycle_name(self) -> str:
        return "null_cycle"

    @property
    def rate_limit_seconds(self) -> int:
        return 0

    @property
    def timeout_seconds(self) -> int:
        return 0

    @property
    def recovery_enabled(self) -> bool:
        return False

    @property
    def parent_cycle_id(self) -> Optional[str]:
        return None

    def perceive(self) -> PhaseResult:
        return PhaseResult(
            phase="perceive",
            success=True,
            elements_count=0,
            element_types=[],
            duration_ms=0,
            error_message="",
        )

    def orient(self, observations_count: int) -> PhaseResult:
        return PhaseResult(
            phase="orient",
            success=True,
            elements_count=0,
            element_types=[],
            duration_ms=0,
            error_message="",
        )

    def decide(self, orientations_count: int) -> PhaseResult:
        return PhaseResult(
            phase="decide",
            success=True,
            elements_count=0,
            element_types=[],
            duration_ms=0,
            error_message="",
        )

    def act(self, decisions_count: int) -> PhaseResult:
        return PhaseResult(
            phase="act",
            success=True,
            elements_count=0,
            element_types=[],
            duration_ms=0,
            error_message="",
        )

    def persist(self) -> PhaseResult:
        return PhaseResult(
            phase="persist",
            success=True,
            elements_count=0,
            element_types=[],
            duration_ms=0,
            error_message="",
        )

    def recover(self, error_phases: List[str]) -> bool:
        return True

    def orchestrate(self, force: bool = False) -> Optional[CycleContextState]:
        return CycleContextState(
            cycle_id="null-cycle-0",
            parent_cycle_id="",
            trace_id="null-trace-0",
            cycle_name="null_cycle",
            phase="persist",
            status="completed",
            observations_count=0,
            orientations_count=0,
            decisions_count=0,
            actions_count=0,
            has_result=False,
            error_count=0,
            error_phases=[],
            start_time=datetime.now().isoformat(),
            elapsed_ms=0,
        )

    def get_context_state(self) -> CycleContextState:
        return CycleContextState(
            cycle_id="null-cycle-0",
            parent_cycle_id="",
            trace_id="null-trace-0",
            cycle_name="null_cycle",
            phase="persist",
            status="completed",
            observations_count=0,
            orientations_count=0,
            decisions_count=0,
            actions_count=0,
            has_result=False,
            error_count=0,
            error_phases=[],
            start_time=datetime.now().isoformat(),
            elapsed_ms=0,
        )

    def is_running(self) -> bool:
        return False

    def get_last_cycle_time(self) -> Optional[str]:
        return None


class NullCycleRegistry:
    """
    Null implementation for testing.
    Tracks nothing.
    """

    def register_cycle(self, context_state: CycleContextState) -> None:
        pass

    def complete_cycle(self, cycle_id: str) -> None:
        pass

    def error_cycle(self, cycle_id: str, error_phases: List[str]) -> None:
        pass

    def get_active_cycles(self) -> List[CycleContextState]:
        return []

    def get_completed_cycles(self, limit: int = 100) -> List[CycleContextState]:
        return []

    def get_error_cycles(self, limit: int = 100) -> List[CycleContextState]:
        return []

    def get_stats(self) -> CycleRegistryStats:
        return CycleRegistryStats(
            total_cycles=0,
            active_cycles=0,
            completed_cycles=0,
            error_cycles=0,
            retention_enabled=True,
            retention_max_completed=100,
            retention_max_errors=500,
        )

    def get_retention_config(self) -> RetentionConfig:
        return RetentionConfig(
            max_completed_cycles=100,
            max_error_cycles=500,
            max_age_seconds=0,
            enabled=True,
        )


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "OWNER",
    "OWNED_OPCODES",
    # Enums
    "CyclePhase",
    "CycleStatus",
    # Types (WATERTIGHT)
    "CycleElement",
    "PhaseResult",
    "CycleContextState",
    "RetentionConfig",
    "CycleRegistryStats",
    "CycleState",
    # Protocols
    "CognitiveCycleProtocol",
    "CycleRegistryProtocol",
    # Owned wrapper
    "CycleOwnedProtocol",
    # Null implementations
    "NullCognitiveCycle",
    "NullCycleRegistry",
]
