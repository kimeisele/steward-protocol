"""Batch operations for task management."""

from typing import List, Dict, Callable, Any
from .models import Task, TaskStatus


class BatchOperations:
    """Handles batch operations on tasks."""

    @staticmethod
    def filter_tasks(
        tasks: Dict[str, Task], predicate: Callable[[Task], bool]
    ) -> List[Task]:
        """
        Filter tasks based on predicate.

        Args:
            tasks: Dictionary of tasks
            predicate: Function that returns True for tasks to keep

        Returns:
            List of filtered tasks
        """
        return [task for task in tasks.values() if predicate(task)]

    @staticmethod
    def filter_by_status(tasks: Dict[str, Task], status: TaskStatus) -> List[Task]:
        """
        Get all tasks with a specific status.

        Args:
            tasks: Dictionary of tasks
            status: Status to filter by

        Returns:
            List of tasks with matching status
        """
        return [task for task in tasks.values() if task.status == status]

    @staticmethod
    def filter_by_priority(
        tasks: Dict[str, Task], min_priority: int = 0, max_priority: int = 100
    ) -> List[Task]:
        """
        Get tasks within a priority range.

        Args:
            tasks: Dictionary of tasks
            min_priority: Minimum priority (inclusive)
            max_priority: Maximum priority (inclusive)

        Returns:
            List of tasks within priority range
        """
        return [
            task
            for task in tasks.values()
            if min_priority <= task.priority <= max_priority
        ]

    @staticmethod
    def filter_by_tag(tasks: Dict[str, Task], tag: str) -> List[Task]:
        """
        Get all tasks with a specific tag.

        Args:
            tasks: Dictionary of tasks
            tag: Tag to filter by

        Returns:
            List of tasks with the tag
        """
        return [task for task in tasks.values() if tag in task.tags]

    @staticmethod
    def bulk_update_status(
        tasks: Dict[str, Task], task_ids: List[str], new_status: TaskStatus
    ) -> int:
        """
        Update status for multiple tasks.

        Args:
            tasks: Dictionary of tasks
            task_ids: List of task IDs to update
            new_status: New status to set

        Returns:
            Number of tasks updated
        """
        updated = 0
        for task_id in task_ids:
            if task_id in tasks:
                tasks[task_id].status = new_status
                updated += 1
        return updated

    @staticmethod
    def bulk_add_tag(tasks: Dict[str, Task], task_ids: List[str], tag: str) -> int:
        """
        Add a tag to multiple tasks.

        Args:
            tasks: Dictionary of tasks
            task_ids: List of task IDs to update
            tag: Tag to add

        Returns:
            Number of tasks updated
        """
        updated = 0
        for task_id in task_ids:
            if task_id in tasks and tag not in tasks[task_id].tags:
                tasks[task_id].tags.append(tag)
                updated += 1
        return updated

    @staticmethod
    def bulk_remove_tag(tasks: Dict[str, Task], task_ids: List[str], tag: str) -> int:
        """
        Remove a tag from multiple tasks.

        Args:
            tasks: Dictionary of tasks
            task_ids: List of task IDs to update
            tag: Tag to remove

        Returns:
            Number of tasks updated
        """
        updated = 0
        for task_id in task_ids:
            if task_id in tasks and tag in tasks[task_id].tags:
                tasks[task_id].tags.remove(tag)
                updated += 1
        return updated

    @staticmethod
    def sort_tasks(
        tasks: List[Task], key: str = "priority", reverse: bool = True
    ) -> List[Task]:
        """
        Sort tasks by a field.

        Args:
            tasks: List of tasks to sort
            key: Field to sort by (priority, created_at, updated_at)
            reverse: If True, sort descending

        Returns:
            Sorted list of tasks
        """
        if key == "priority":
            return sorted(tasks, key=lambda t: t.priority, reverse=reverse)
        elif key == "created_at":
            return sorted(tasks, key=lambda t: t.created_at, reverse=reverse)
        elif key == "updated_at":
            return sorted(tasks, key=lambda t: t.updated_at, reverse=reverse)
        else:
            return tasks
