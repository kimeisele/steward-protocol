"""
InMemoryScheduler - FIFO Task Scheduler Implementation

Extracted from kernel_impl.py to reduce kernel size.
This is a pure scheduler - no cosmic logic, no governance.
Task filtering is handled by plugins via on_task_submit hook.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x6ba726f2"  # GenesisByte: parampara % 37 == 0

import logging
from collections import deque
from typing import TYPE_CHECKING, Any, Dict, Optional

from .task import Task

if TYPE_CHECKING:
    pass

logger = logging.getLogger("SCHEDULER")


class InMemoryScheduler:
    """FIFO Task Scheduler - Pure queue management.

    This is a PURE scheduler - no cosmic logic, no governance.
    Task filtering is handled by plugins via on_task_submit hook.

    The scheduler only knows how to:
    1. Accept tasks into the queue
    2. Return the next task (FIFO)
    3. Track completion status
    """

    def __init__(self):
        # Priority Queue: Lists of tasks keyed by priority (0=Critical, 1=High, 2=Medium, 3=Low)
        # Standard priority is 2.
        self.queues: Dict[int, deque] = {
            0: deque(),  # Critical
            1: deque(),  # High
            2: deque(),  # Medium
            3: deque(),  # Low
        }
        self.executing: Optional[Task] = None
        self.completed: Dict[str, Task] = {}
        # GAD-000 Test 5: Idempotency cache
        self._idempotency_cache: Dict[str, Dict[str, Any]] = {}

    def submit_task(self, task: Task, idempotency_key: Optional[str] = None) -> str:
        """Submit task to priority queue, return task_id.

        NOTE: Task validation (Sarga cycle, governance, etc.) is handled
        by plugins via on_task_submit hook BEFORE this method is called.
        This method is a pure queue operation.

        GAD-000 Test 5: Idempotency support.
        """
        import time

        # Check idempotency cache
        if idempotency_key:
            existing = self._idempotency_cache.get(idempotency_key)
            if existing:
                logger.info(f"Task skipped (idempotent): {idempotency_key} -> {existing['task_id']}")
                return existing["task_id"]

        # Normalize priority (default to 2 if missing or invalid)
        priority = getattr(task, "priority", 2)
        if not isinstance(priority, int) or priority not in self.queues:
            priority = 2

        self.queues[priority].append(task)
        logger.info(f"Task queued (P{priority}): {task.task_id} for {task.agent_id}")

        # Store in idempotency cache
        if idempotency_key:
            self._idempotency_cache[idempotency_key] = {"task_id": task.task_id, "timestamp": time.time()}
        return task.task_id

    def next_task(self) -> Optional[Task]:
        """Pop next task from highest priority queue."""
        # Iterate from P0 (Critical) to P3 (Low)
        for priority in sorted(self.queues.keys()):
            if self.queues[priority]:
                task = self.queues[priority].popleft()
                self.executing = task
                return task
        return None

    def get_queue_status(self) -> Dict[str, Any]:
        """Get queue statistics per priority."""
        return {
            "queue_length": sum(len(q) for q in self.queues.values()),
            "by_priority": {p: len(q) for p, q in self.queues.items()},
            "executing": self.executing.task_id if self.executing else None,
            "completed": len(self.completed),
        }

    def requeue_task(self, task: Task) -> None:
        """Re-queue a deferred task (bypasses Sarga validation)."""
        priority = getattr(task, "priority", 2)
        if priority not in self.queues:
            priority = 2

        # Re-queue at the FRONT of the priority queue (Standard LIFO for retry)
        self.queues[priority].appendleft(task)
        logger.debug(f"Task re-queued (P{priority}): {task.task_id} (deferred)")
