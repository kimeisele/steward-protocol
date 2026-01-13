"""
SCHEDULER - Task Scheduling Protocol
====================================

OWNER: JANAKA (The Karma Yogi)
POSITION: 10 (KARMA Quarter)
OPCODE: EXEC_SERVICE

Janaka ruled a kingdom while being internally renounced.
He scheduled the affairs of state without attachment.

SHASTRA BASIS:
    King Janaka was a perfect Karma Yogi:
    - He ACTED (ruled the kingdom)
    - He was NOT ATTACHED (internally renounced)
    - He SERVED (all actions offered to Vishnu)

    "karmaṇy evādhikāras te mā phaleṣu kadācana"
    "You have a right to perform your prescribed duty,
    but you are not entitled to the fruits of action."
    — Bhagavad Gita 2.47

SCHEDULING ALGORITHMS:
    - FIFO: First In First Out
    - PRIORITY: Higher priority first
    - ROUND_ROBIN: Time-sliced execution
    - DEADLINE: Earliest deadline first

WATERTIGHT: No Any types. All typed explicitly.
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0x3e8ffa40"  # GenesisByte: parampara % 37 == 0

import heapq
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Deque, Dict, Final, List, Optional, Protocol, runtime_checkable

from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode

from vibe_core.protocols.mahajanas.janaka import (
    TaskValue,
    TaskStatus,
    TaskPriority,
    Task,
    ExecutionResult,
    ExecutionState,
)


# =============================================================================
# OWNERSHIP DECLARATION
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.JANAKA
LOTUS_POSITION: Final[int] = 10
LOTUS_QUARTER: Final[str] = "karma"

OWNED_OPCODES: Final[List[MantraOpCode]] = [
    MantraOpCode.STATE_SYNC,  # EXEC_SERVICE
]


# =============================================================================
# SCHEDULING ALGORITHM
# =============================================================================

class SchedulingAlgorithm(str, Enum):
    """Task scheduling algorithms."""
    FIFO = "fifo"                 # First In First Out
    PRIORITY = "priority"         # Priority-based
    ROUND_ROBIN = "round_robin"   # Time-sliced
    DEADLINE = "deadline"         # Earliest deadline first


# =============================================================================
# SCHEDULED TASK
# =============================================================================

TaskExecutor = Callable[[TaskValue], TaskValue]


@dataclass
class ScheduledTask:
    """A task in the scheduler."""
    task_id: str
    name: str
    priority: TaskPriority
    status: TaskStatus
    executor: TaskExecutor
    input_value: TaskValue
    output_value: Optional[TaskValue] = None
    created_at: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: str = ""

    def __lt__(self, other: "ScheduledTask") -> bool:
        """For priority queue comparison."""
        priority_order = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.NORMAL: 2,
            TaskPriority.LOW: 3,
            TaskPriority.BACKGROUND: 4,
        }
        return priority_order[self.priority] < priority_order[other.priority]

    def to_task(self) -> Task:
        """Convert to Task TypedDict."""
        return Task(
            id=self.task_id,
            name=self.name,
            status=self.status.value,
            priority=self.priority.value,
            input_type=type(self.input_value).__name__ if self.input_value else "NoneType",
            input_repr=repr(self.input_value)[:100] if self.input_value else "",
            output_type=type(self.output_value).__name__ if self.output_value else "",
            output_repr=repr(self.output_value)[:100] if self.output_value else "",
            error_message=self.error_message,
            created_at=self.created_at.isoformat(),
            started_at=self.started_at.isoformat() if self.started_at else "",
            completed_at=self.completed_at.isoformat() if self.completed_at else "",
        )


# =============================================================================
# SCHEDULER PROTOCOL
# =============================================================================

@runtime_checkable
class SchedulerProtocol(Protocol):
    """
    The Task Scheduling Protocol - Janaka's Queue.

    OWNER: Mahajana.JANAKA

    Like Janaka who scheduled kingdom affairs without attachment,
    this scheduler manages tasks without bias.
    """

    @property
    def owner(self) -> Mahajana:
        """Always returns Mahajana.JANAKA."""
        ...

    @property
    def algorithm(self) -> SchedulingAlgorithm:
        """Current scheduling algorithm."""
        ...

    @property
    def pending_count(self) -> int:
        """Number of pending tasks."""
        ...

    # Task Management
    def schedule(
        self,
        name: str,
        executor: TaskExecutor,
        input_value: TaskValue,
        priority: TaskPriority = TaskPriority.NORMAL,
        deadline: Optional[datetime] = None,
    ) -> str:
        """Schedule a task. Returns task_id."""
        ...

    def cancel(self, task_id: str) -> bool:
        """Cancel a pending task."""
        ...

    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        """Get a task by ID."""
        ...

    # Execution
    def run_next(self) -> Optional[ExecutionResult]:
        """Run the next scheduled task."""
        ...

    def run_all(self, max_tasks: int = 100) -> List[ExecutionResult]:
        """Run all pending tasks."""
        ...

    # State
    def get_state(self) -> ExecutionState:
        """Get scheduler state."""
        ...


# =============================================================================
# SCHEDULER IMPLEMENTATION
# =============================================================================

class Scheduler:
    """
    Janaka's Scheduler - Task Queue Management.

    OWNER: Mahajana.JANAKA

    Features:
    - Multiple scheduling algorithms
    - Priority-based execution
    - Deadline support
    - Karma tracking (work debt)
    """

    def __init__(self, algorithm: SchedulingAlgorithm = SchedulingAlgorithm.PRIORITY) -> None:
        """Initialize scheduler."""
        self._algorithm = algorithm
        self._task_counter = 0
        self._tasks: Dict[str, ScheduledTask] = {}

        # Queues for different algorithms
        self._fifo_queue: Deque[str] = deque()
        self._priority_queue: List[ScheduledTask] = []
        self._round_robin_index = 0

        # Stats
        self._completed_count = 0
        self._failed_count = 0
        self._total_karma = 0.0

    @property
    def owner(self) -> Mahajana:
        return Mahajana.JANAKA

    @property
    def algorithm(self) -> SchedulingAlgorithm:
        return self._algorithm

    @property
    def pending_count(self) -> int:
        return len([t for t in self._tasks.values() if t.status == TaskStatus.PENDING])

    def schedule(
        self,
        name: str,
        executor: TaskExecutor,
        input_value: TaskValue,
        priority: TaskPriority = TaskPriority.NORMAL,
        deadline: Optional[datetime] = None,
    ) -> str:
        """Schedule a task."""
        self._task_counter += 1
        task_id = f"task-{self._task_counter}"

        task = ScheduledTask(
            task_id=task_id,
            name=name,
            priority=priority,
            status=TaskStatus.PENDING,
            executor=executor,
            input_value=input_value,
            deadline=deadline,
        )

        self._tasks[task_id] = task

        # Add to appropriate queue
        if self._algorithm == SchedulingAlgorithm.FIFO:
            self._fifo_queue.append(task_id)
        elif self._algorithm == SchedulingAlgorithm.PRIORITY:
            heapq.heappush(self._priority_queue, task)
        elif self._algorithm == SchedulingAlgorithm.DEADLINE:
            # Sort by deadline
            heapq.heappush(self._priority_queue, task)
        # ROUND_ROBIN uses FIFO queue
        else:
            self._fifo_queue.append(task_id)

        return task_id

    def cancel(self, task_id: str) -> bool:
        """Cancel a pending task."""
        task = self._tasks.get(task_id)
        if task is None or task.status != TaskStatus.PENDING:
            return False

        task.status = TaskStatus.CANCELLED
        return True

    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        """Get a task by ID."""
        return self._tasks.get(task_id)

    def run_next(self) -> Optional[ExecutionResult]:
        """Run the next scheduled task."""
        task = self._get_next_task()
        if task is None:
            return None

        return self._execute_task(task)

    def run_all(self, max_tasks: int = 100) -> List[ExecutionResult]:
        """Run all pending tasks."""
        results: List[ExecutionResult] = []
        for _ in range(max_tasks):
            result = self.run_next()
            if result is None:
                break
            results.append(result)
        return results

    def _get_next_task(self) -> Optional[ScheduledTask]:
        """Get the next task based on algorithm."""
        if self._algorithm == SchedulingAlgorithm.FIFO:
            while self._fifo_queue:
                task_id = self._fifo_queue.popleft()
                task = self._tasks.get(task_id)
                if task and task.status == TaskStatus.PENDING:
                    return task

        elif self._algorithm == SchedulingAlgorithm.PRIORITY:
            while self._priority_queue:
                task = heapq.heappop(self._priority_queue)
                if task.status == TaskStatus.PENDING:
                    return task

        elif self._algorithm == SchedulingAlgorithm.DEADLINE:
            # Sort by deadline, then priority
            pending = [t for t in self._tasks.values() if t.status == TaskStatus.PENDING]
            if pending:
                pending.sort(key=lambda t: (t.deadline or datetime.max, t))
                return pending[0]

        elif self._algorithm == SchedulingAlgorithm.ROUND_ROBIN:
            if self._fifo_queue:
                task_id = self._fifo_queue.popleft()
                task = self._tasks.get(task_id)
                if task and task.status == TaskStatus.PENDING:
                    return task

        return None

    def _execute_task(self, task: ScheduledTask) -> ExecutionResult:
        """Execute a single task."""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()
        start_time = time.time()

        try:
            task.output_value = task.executor(task.input_value)
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            self._completed_count += 1

            return ExecutionResult(
                success=True,
                task_id=task.task_id,
                output_type=type(task.output_value).__name__ if task.output_value else "NoneType",
                output_repr=repr(task.output_value)[:100] if task.output_value else "",
                execution_time_ms=int((time.time() - start_time) * 1000),
                error_message="",
            )

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.now()
            self._failed_count += 1
            self._total_karma += 1.0  # Karma accumulates on failure

            return ExecutionResult(
                success=False,
                task_id=task.task_id,
                output_type="",
                output_repr="",
                execution_time_ms=int((time.time() - start_time) * 1000),
                error_message=str(e),
            )

    def get_state(self) -> ExecutionState:
        """Get scheduler state."""
        pending = [t.to_task() for t in self._tasks.values() if t.status == TaskStatus.PENDING]
        running = [t.to_task() for t in self._tasks.values() if t.status == TaskStatus.RUNNING]

        return ExecutionState(
            pending_tasks=pending,
            running_tasks=running,
            completed_count=self._completed_count,
            failed_count=self._failed_count,
            total_karma=self._total_karma,
            is_busy=len(running) > 0,
            health="healthy" if self._failed_count < self._completed_count else "degraded",
        )


# =============================================================================
# NULL SCHEDULER
# =============================================================================

class NullScheduler:
    """Null scheduler - instant execution."""

    @property
    def owner(self) -> Mahajana:
        return Mahajana.JANAKA

    @property
    def algorithm(self) -> SchedulingAlgorithm:
        return SchedulingAlgorithm.FIFO

    @property
    def pending_count(self) -> int:
        return 0

    def schedule(self, name: str, executor: TaskExecutor, input_value: TaskValue, priority: TaskPriority = TaskPriority.NORMAL, deadline: Optional[datetime] = None) -> str:
        return "null-task"

    def cancel(self, task_id: str) -> bool:
        return True

    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        return None

    def run_next(self) -> Optional[ExecutionResult]:
        return None

    def run_all(self, max_tasks: int = 100) -> List[ExecutionResult]:
        return []

    def get_state(self) -> ExecutionState:
        return ExecutionState(pending_tasks=[], running_tasks=[], completed_count=0, failed_count=0, total_karma=0.0, is_busy=False, health="pristine")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "OWNER", "LOTUS_POSITION", "LOTUS_QUARTER", "OWNED_OPCODES",
    "SchedulingAlgorithm", "ScheduledTask", "TaskExecutor",
    "SchedulerProtocol", "Scheduler", "NullScheduler",
]
