"""
InMemoryScheduler - FIFO Task Scheduler Implementation

Extracted from kernel_impl.py to reduce kernel size.
This is a pure scheduler - no cosmic logic, no governance.
Task filtering is handled by plugins via on_task_submit hook.
"""

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
        self.queue: deque = deque()
        self.executing: Optional[Task] = None
        self.completed: Dict[str, Task] = {}
        # GAD-000 Test 5: Idempotency cache
        self._idempotency_cache: Dict[str, Dict[str, Any]] = {}

    def submit_task(self, task: Task, idempotency_key: Optional[str] = None) -> str:
        """Submit task to queue, return task_id.

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

        self.queue.append(task)
        logger.info(f"Task queued: {task.task_id} for {task.agent_id}")

        # Store in idempotency cache
        if idempotency_key:
            self._idempotency_cache[idempotency_key] = {"task_id": task.task_id, "timestamp": time.time()}

        return task.task_id

    def next_task(self) -> Optional[Task]:
        """Pop next task from queue"""
        if self.queue:
            task = self.queue.popleft()
            self.executing = task
            return task
        return None

    def get_queue_status(self) -> Dict[str, Any]:
        """Get queue statistics"""
        return {
            "queue_length": len(self.queue),
            "executing": self.executing.task_id if self.executing else None,
            "completed": len(self.completed),
        }

    def requeue_task(self, task: Task) -> None:
        """Re-queue a deferred task (bypasses Sarga validation)."""
        self.queue.append(task)
        logger.debug(f"Task re-queued: {task.task_id} (deferred)")
