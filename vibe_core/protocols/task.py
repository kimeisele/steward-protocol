"""
OPUS-212: Task Protocol - Core Interface for Work Management.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

from vibe_core.task_types import TaskStatus


@runtime_checkable
class TaskService(Protocol):
    """The central interface for system-wide task management."""

    def add_task(
        self,
        title: str,
        description: str = "",
        priority: int = 0,
        assigned_agent: Optional[str] = None,
        roadmap_id: Optional[str] = None,
    ) -> Any:
        """Adds a new task to the system."""
        ...

    def update_task(self, task_id: str, **kwargs) -> Optional[Any]:
        """Updates an existing task."""
        ...

    def get_task(self, task_id: str) -> Optional[Any]:
        """Retrieves a task by ID."""
        ...

    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        priority: Optional[int] = None,
        tag: Optional[str] = None,
    ) -> List[Any]:
        """Lists tasks with optional filters."""
        ...
