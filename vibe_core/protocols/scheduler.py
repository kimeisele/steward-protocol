"""
Scheduler Protocol - Hot-Swappable Task Scheduler

PROMPT.md: "Protocol statt konkrete Klassen (Dependency Inversion)"

This protocol enables swapping InMemoryScheduler for other implementations
(e.g., Redis-backed, distributed) without modifying kernel code.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0xbb18fce0"  # GenesisByte: parampara % 37 == 0

from typing import TYPE_CHECKING, Any, Dict, List, Optional, Protocol, TypedDict, runtime_checkable

if TYPE_CHECKING:
    from vibe_core.scheduling.task import DispatchTask


class QueueStatus(TypedDict, total=False):
    """Scheduler queue statistics."""

    queue_length: int
    pending_count: int
    processing_count: int
    completed_count: int
    failed_count: int
    oldest_pending_age_ms: float


@runtime_checkable
class SchedulerProtocol(Protocol):
    """
    Protocol for task scheduling.

    Implementations:
        - InMemoryScheduler (default, FIFO queue)
        - Future: DistributedScheduler, PriorityScheduler

    Usage:
        scheduler = ServiceRegistry.get(SchedulerProtocol)
        task_id = scheduler.submit_task(task)
        next_task = scheduler.next_task()
    """

    def submit_task(self, task: "DispatchTask") -> str:
        """
        Submit a task to the queue.

        Args:
            task: Task object with task_id, agent_id, payload

        Returns:
            task_id: The task's unique identifier
        """
        ...

    def next_task(self) -> Optional["DispatchTask"]:
        """
        Get next task from queue (FIFO).

        Returns:
            Task object or None if queue is empty
        """
        ...

    def get_queue_status(self) -> QueueStatus:
        """
        Get queue statistics.

        Returns:
            Dict with pending, in_progress, completed counts
        """
        ...

    @property
    def pending_tasks(self) -> List["DispatchTask"]:
        """Get list of pending tasks."""
        ...

    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a pending task.

        Args:
            task_id: ID of task to cancel

        Returns:
            True if cancelled, False if not found or already running
        """
        ...

    def get_task_status(self, task_id: str) -> Optional[str]:
        """
        Get status of a task.

        Args:
            task_id: ID of task

        Returns:
            Status string or None if not found
        """
        ...
