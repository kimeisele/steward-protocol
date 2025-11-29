"""
Task Scheduler Protocol - Interface Definition

BLOCKER #2: Layer 1 Protocol (no implementations)
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from ..scheduling import Task


class VibeScheduler(ABC):
    """Task scheduler interface"""

    @abstractmethod
    def submit_task(self, task: Task) -> str:
        """Submit a task to the queue, return task_id"""
        pass

    @abstractmethod
    def next_task(self) -> Optional[Task]:
        """Pop next task from queue"""
        pass

    @abstractmethod
    def get_queue_status(self) -> Dict[str, Any]:
        """Get queue statistics"""
        pass
