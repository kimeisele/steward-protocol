"""Task generation logic for determining next tasks."""

from typing import Optional, List, Dict
from .models import Task, TaskStatus
from .batch_operations import BatchOperations


class NextTaskGenerator:
    """Determines the next task to work on."""

    @staticmethod
    def get_next_task(tasks: Dict[str, Task]) -> Optional[Task]:
        """
        Get the next task to work on.

        Priority order:
        1. In-progress tasks (resume them)
        2. Blocked tasks (unblock if possible)
        3. Highest priority pending tasks

        Args:
            tasks: Dictionary of all tasks

        Returns:
            Next task to work on, or None if none available
        """
        # Check for in-progress tasks
        in_progress = BatchOperations.filter_by_status(tasks, TaskStatus.IN_PROGRESS)
        if in_progress:
            # Resume highest priority in-progress task
            return max(in_progress, key=lambda t: t.priority)

        # Check for pending tasks
        pending = BatchOperations.filter_by_status(tasks, TaskStatus.PENDING)
        if pending:
            # Get highest priority pending task
            return max(pending, key=lambda t: t.priority)

        # Check for blocked tasks
        blocked = BatchOperations.filter_by_status(tasks, TaskStatus.BLOCKED)
        if blocked:
            # Get highest priority blocked task
            return max(blocked, key=lambda t: t.priority)

        # No tasks available
        return None

    @staticmethod
    def get_next_tasks(tasks: Dict[str, Task], count: int = 5) -> List[Task]:
        """
        Get the next N tasks in priority order.

        Args:
            tasks: Dictionary of all tasks
            count: Number of tasks to return

        Returns:
            List of next tasks, up to count
        """
        # Get all non-archived tasks
        candidates = [
            task for task in tasks.values()
            if task.status != TaskStatus.ARCHIVED
        ]

        # Sort by status priority, then by priority value
        status_priority = {
            TaskStatus.IN_PROGRESS: 3,
            TaskStatus.PENDING: 2,
            TaskStatus.BLOCKED: 1,
            TaskStatus.COMPLETED: 0,
        }

        candidates.sort(
            key=lambda t: (status_priority.get(t.status, 0), t.priority),
            reverse=True
        )

        return candidates[:count]

    @staticmethod
    def get_critical_tasks(tasks: Dict[str, Task]) -> List[Task]:
        """
        Get all critical (high priority) tasks.

        Args:
            tasks: Dictionary of all tasks

        Returns:
            List of critical tasks (priority >= 80)
        """
        return BatchOperations.filter_by_priority(
            tasks,
            min_priority=80,
            max_priority=100
        )

    @staticmethod
    def suggest_next_action(tasks: Dict[str, Task]) -> str:
        """
        Suggest the next action based on task state.

        Args:
            tasks: Dictionary of all tasks

        Returns:
            Suggestion message
        """
        pending = len(BatchOperations.filter_by_status(tasks, TaskStatus.PENDING))
        in_progress = len(BatchOperations.filter_by_status(tasks, TaskStatus.IN_PROGRESS))
        blocked = len(BatchOperations.filter_by_status(tasks, TaskStatus.BLOCKED))

        if blocked > 0:
            return f"⚠️ {blocked} tasks are blocked. Unblock them to continue."

        if in_progress > 0:
            return f"▶️ Resume {in_progress} in-progress tasks."

        if pending > 0:
            return f"📋 Start work on {pending} pending tasks."

        return "✅ All tasks complete!"
