"""
JANAKA - The 8th Mahajana (Duty/Execution)
==========================================

POSITION: 10 (KARMA Quarter, CHECK_DHARMA OpCode)

King Janaka - The Karma Yogi.
Ruled a kingdom while being internally renounced.
Father of Sita. Host of great sages.

DERIVED FROM MAHAMANTRA:
    Position 10 -> guardian=JANAKA, opcode=CHECK_DHARMA, quarter=KARMA
    All properties derived from truth table. No manual wiring.

Janaka ACTS but is not BOUND by action.
He serves the Sovereign while ruling.

WATERTIGHT: No Any types. All typed explicitly.
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0x04621792"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import (
    Callable,
    ClassVar,
    Dict,
    List,
    Optional,
    Protocol,
    Tuple,
    TypedDict,
    TypeVar,
    Union,
    runtime_checkable,
)

from vibe_core.mahamantra import WorkerProtocol, Mahajana, MantraOpCode, ProtocolRegistry


# =============================================================================
# JANAKA PROTOCOL BASE - Derives from MantraPosition 10
# =============================================================================

@ProtocolRegistry.register
class JanakaProtocolBase(WorkerProtocol):
    """
    Janaka protocol ownership - DERIVED from Mahamantra position 10.

    NO MANUAL WIRING:
        _position_index = 10 is the ONLY configuration.
        Everything else derived from truth table.

    DERIVED PROPERTIES:
        guardian()  -> Mahajana.JANAKA
        opcode()    -> MantraOpCode.STATE_SYNC
        quarter()   -> Quarter.KARMA
        is_head()   -> False (Worker position)
        parampara_vector() -> 407 (% 37 == 0)
    """
    _position_index: ClassVar[int] = 10  # THE ONLY CONFIGURATION


# NO MANUAL WIRING - Everything derived from mahamantra[10]


# =============================================================================
# WATERTIGHT STATE TYPES (No Any!)
# =============================================================================

# The union of allowed task input/output types - WATERTIGHT
TaskValue = Union[str, int, float, bool, Dict[str, str], List[str], bytes, None]


class TaskStatus(str, Enum):
    """Status of a task execution."""
    PENDING = "pending"       # Waiting to start
    RUNNING = "running"       # Currently executing
    COMPLETED = "completed"   # Finished successfully
    FAILED = "failed"         # Finished with error
    CANCELLED = "cancelled"   # Stopped before completion
    BLOCKED = "blocked"       # Waiting on dependency


class TaskPriority(str, Enum):
    """Priority levels for tasks."""
    CRITICAL = "critical"     # Immediate execution
    HIGH = "high"             # Before normal tasks
    NORMAL = "normal"         # Standard priority
    LOW = "low"               # When resources available
    BACKGROUND = "background" # Only when idle


class Task(TypedDict, total=False):
    """
    A task to be executed.
    WATERTIGHT - no Any!
    """
    id: str                   # Unique task ID
    name: str                 # Human-readable name
    status: str               # TaskStatus value
    priority: str             # TaskPriority value
    input_type: str           # Python type of input
    input_repr: str           # String representation of input
    output_type: str          # Python type of output (if completed)
    output_repr: str          # String representation of output
    error_message: str        # Error if failed
    created_at: str           # ISO timestamp
    started_at: str           # ISO timestamp (empty if not started)
    completed_at: str         # ISO timestamp (empty if not completed)
    sovereign_id: str         # Who requested this task


class ExecutionResult(TypedDict, total=False):
    """
    Result of executing a task.
    WATERTIGHT - no Any!
    """
    success: bool
    task_id: str
    output_type: str          # Python type of output
    output_repr: str          # String representation
    execution_time_ms: int
    error_message: str        # Empty if success


class ExecutionState(TypedDict, total=False):
    """
    Complete execution state for observability.
    WATERTIGHT - no Any!
    """
    pending_tasks: List[Task]
    running_tasks: List[Task]
    completed_count: int
    failed_count: int
    total_karma: float        # Accumulated work debt
    is_busy: bool
    health: str               # "pristine", "healthy", "degraded", "blocked"


class CheckResult(TypedDict):
    """Result of check operation. WATERTIGHT - no Any!"""
    success: bool
    target: str
    pending: int
    running: int
    completed: int
    health: str


# =============================================================================
# TASK HANDLER TYPE (For type-safe execution)
# =============================================================================

class TaskHandler(Protocol):
    """Protocol for task handlers - WATERTIGHT."""
    def __call__(self, task_input: TaskValue) -> TaskValue:
        """Execute a task and return result."""
        ...


# =============================================================================
# JANAKA PROTOCOL (Main Execution Protocol)
# =============================================================================


@runtime_checkable
class JanakaProtocol(Protocol):
    """
    The Execution/Duty Protocol - Janaka's domain.

    DERIVED: Position 10 -> JANAKA, CHECK_DHARMA, KARMA
    WATERTIGHT - no Any types!

    The Three Aspects of Karma Yoga:
    1. ACCEPT (receive) - Accept the duty without attachment
    2. EXECUTE (perform) - Perform with full dedication
    3. RELEASE (offer) - Offer the result without expectation
    """

    @classmethod
    def position_index(cls) -> int:
        """Position 10 in the Mahamantra."""
        ...

    # =========================================================================
    # Task Management (EXEC_SERVICE OpCode)
    # =========================================================================

    def submit(
        self,
        name: str,
        task_input: TaskValue,
        priority: TaskPriority = TaskPriority.NORMAL,
        sovereign_id: str = "",
    ) -> str:
        """
        Submit a task for execution.
        WATERTIGHT: task_input is TaskValue union, not Any.
        Returns task_id.
        """
        ...

    def execute(self, task_id: str) -> ExecutionResult:
        """
        Execute a task immediately.
        WATERTIGHT: Returns ExecutionResult, not Any.
        """
        ...

    def cancel(self, task_id: str) -> bool:
        """
        Cancel a pending/running task.
        Returns True if cancelled.
        """
        ...

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        ...

    def get_result(self, task_id: str) -> Optional[ExecutionResult]:
        """Get result of a completed task."""
        ...

    # =========================================================================
    # Execution Control
    # =========================================================================

    def is_busy(self) -> bool:
        """Check if currently executing tasks."""
        ...

    def pause(self) -> bool:
        """
        Pause execution of new tasks.
        Running tasks complete, pending tasks wait.
        """
        ...

    def resume(self) -> bool:
        """Resume execution of pending tasks."""
        ...

    # =========================================================================
    # Karma Yoga (Detachment)
    # =========================================================================

    def get_karma(self) -> float:
        """
        Get accumulated karma (work debt).
        0.0 = fully detached (ideal Karma Yoga).
        >0 = accumulated attachment to results.

        Karma accumulates when:
        - Tasks fail without proper error handling
        - Resources are not released
        - Results are cached when not needed
        """
        ...

    def release_karma(self) -> float:
        """
        Release accumulated karma through proper cleanup.
        Returns the amount released.
        """
        ...

    # =========================================================================
    # Observability
    # =========================================================================

    def get_state(self) -> ExecutionState:
        """
        Get complete execution state.
        WATERTIGHT: Returns ExecutionState TypedDict, not Dict[str, Any].
        """
        ...


# =============================================================================
# NULL JANAKA (For testing)
# =============================================================================


class NullJanaka(JanakaProtocolBase):
    """
    The Inactive King.
    No service execution (for testing without agents).

    Inherits from JanakaProtocolBase -> position 10 -> JANAKA.

    Even in Null mode:
    - accepts tasks silently
    - returns empty results
    - maintains 0.0 karma (perfect detachment)
    """

    def submit(
        self,
        name: str,
        task_input: TaskValue,
        priority: TaskPriority = TaskPriority.NORMAL,
        sovereign_id: str = "",
    ) -> str:
        return "null-task-0"

    def execute(self, task_id: str) -> ExecutionResult:
        return ExecutionResult(
            success=True,
            task_id=task_id,
            output_type="NoneType",
            output_repr="None",
            execution_time_ms=0,
            error_message="",
        )

    def cancel(self, task_id: str) -> bool:
        return False  # Nothing to cancel

    def get_task(self, task_id: str) -> Optional[Task]:
        return None

    def get_result(self, task_id: str) -> Optional[ExecutionResult]:
        return None

    def is_busy(self) -> bool:
        return False

    def pause(self) -> bool:
        return True

    def resume(self) -> bool:
        return True

    def get_karma(self) -> float:
        return 0.0  # Perfect detachment

    def release_karma(self) -> float:
        return 0.0  # Nothing to release

    def get_state(self) -> ExecutionState:
        return ExecutionState(
            pending_tasks=[],
            running_tasks=[],
            completed_count=0,
            failed_count=0,
            total_karma=0.0,
            is_busy=False,
            health="pristine",
        )

    def check(self, target: str = "status") -> "CheckResult":
        """CLI: Check execution state (dharma check). WATERTIGHT."""
        state = self.get_state()
        return CheckResult(
            success=True,
            target=target,
            pending=len(state.get("pending_tasks", [])),
            running=len(state.get("running_tasks", [])),
            completed=state.get("completed_count", 0),
            health=state.get("health", "unknown"),
        )


# =============================================================================
# JANAKA'S INSTRUCTION (For Execution)
# =============================================================================

@dataclass(frozen=True)
class SankalpaInstruction:
    """
    An instruction for execution.

    Sankalpa = Intent/Will (The driving force of action)

    This is the ATOMIC unit of execution intent.
    Used by SankalpaProtocol and task schedulers.
    """
    operation: str  # "submit", "execute", "cancel", "pause", "resume"
    task_name: str
    task_input: Optional[TaskValue] = None
    priority: TaskPriority = TaskPriority.NORMAL
    sovereign_id: Optional[str] = None  # For audit trail

    def to_dict(self) -> Dict[str, Union[str, int, float, bool, None]]:
        """Serialize for transmission."""
        result: Dict[str, Union[str, int, float, bool, None]] = {
            "operation": self.operation,
            "task_name": self.task_name,
            "priority": self.priority.value,
        }
        if self.task_input is not None:
            if isinstance(self.task_input, (dict, list, bytes)):
                result["task_input"] = str(self.task_input)
                result["input_type"] = type(self.task_input).__name__
            else:
                result["task_input"] = self.task_input
                result["input_type"] = type(self.task_input).__name__
        if self.sovereign_id:
            result["sovereign_id"] = self.sovereign_id
        return result


# =============================================================================
# CYCLE PROTOCOL (Orchestration Loops)
# =============================================================================

from vibe_core.protocols.mahajanas.janaka.cycle import (
    CyclePhase,
    CycleStatus,
    CycleElement,
    PhaseResult,
    CycleContextState,
    RetentionConfig,
    CycleRegistryStats,
    CycleState,
    CognitiveCycleProtocol,
    CycleRegistryProtocol,
    CycleOwnedProtocol,
    NullCognitiveCycle,
    NullCycleRegistry,
)

# =============================================================================
# SCHEDULER - Task Scheduling
# =============================================================================

from vibe_core.protocols.mahajanas.janaka.scheduler import (
    SchedulingAlgorithm,
    ScheduledTask,
    TaskExecutor,
    SchedulerProtocol,
    Scheduler,
    NullScheduler,
    LOTUS_POSITION as SCHEDULER_POSITION,
)

# =============================================================================
# MIGRATED TYPES - Accessed via mahamantra.mod.janaka
# =============================================================================

from vibe_core.protocols.mahajanas.janaka.types import (
    # prana.py
    SessionStartConfig,
    HeartbeatConfig,
    KernelConfig,
    OpusConfig,
    LimitsConfig,
    PranaConfig,
    load_config,
    is_kernel_running,
    ensure_kernel_running,
    get_last_heartbeat,
    record_heartbeat,
    # task_types.py (TaskStatus already defined above)
)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Protocol Base (MantraProtocol derivative) - THE ONLY SOURCE
    "JanakaProtocolBase",
    # State Types (WATERTIGHT)
    "TaskValue",
    "TaskStatus",
    "TaskPriority",
    "Task",
    "ExecutionResult",
    "ExecutionState",
    "CheckResult",
    # Handler Protocol
    "TaskHandler",
    # Protocol
    "JanakaProtocol",
    # Implementations
    "NullJanaka",
    # Instructions
    "SankalpaInstruction",
    # Cycle Protocol (WATERTIGHT)
    "CyclePhase",
    "CycleStatus",
    "CycleElement",
    "PhaseResult",
    "CycleContextState",
    "RetentionConfig",
    "CycleRegistryStats",
    "CycleState",
    "CognitiveCycleProtocol",
    "CycleRegistryProtocol",
    "CycleOwnedProtocol",
    "NullCognitiveCycle",
    "NullCycleRegistry",
    # Scheduler (Task Scheduling)
    "SchedulingAlgorithm",
    "ScheduledTask",
    "TaskExecutor",
    "SchedulerProtocol",
    "Scheduler",
    "NullScheduler",
    # Service (Real Implementation)
    "JanakaService",
    # === MIGRATED TYPES (mahamantra.mod.janaka) ===
    # prana.py
    "SessionStartConfig",
    "HeartbeatConfig",
    "KernelConfig",
    "OpusConfig",
    "LimitsConfig",
    "PranaConfig",
    "load_config",
    "is_kernel_running",
    "ensure_kernel_running",
    "get_last_heartbeat",
    "record_heartbeat",
]

# =============================================================================
# JANAKA SERVICE - The Real Implementation
# =============================================================================

# LAZY IMPORT to avoid circular dependency with scheduling/task.py
# JanakaService is loaded on first access via __getattr__

def __getattr__(name: str):
    """Lazy import for JanakaService to avoid circular import."""
    if name == "JanakaService":
        from vibe_core.protocols.mahajanas.janaka.service import JanakaService
        return JanakaService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
