"""Task management performance metrics."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any
import json


@dataclass
class TaskMetrics:
    """Metrics for task performance."""

    total_tasks: int = 0
    completed_tasks: int = 0
    pending_tasks: int = 0
    blocked_tasks: int = 0
    archived_tasks: int = 0
    avg_completion_time: float = 0.0
    completion_rate: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "total_tasks": self.total_tasks,
            "completed_tasks": self.completed_tasks,
            "pending_tasks": self.pending_tasks,
            "blocked_tasks": self.blocked_tasks,
            "archived_tasks": self.archived_tasks,
            "avg_completion_time": self.avg_completion_time,
            "completion_rate": self.completion_rate,
            "metadata": self.metadata,
        }


class MetricsCollector:
    """Collects and calculates task metrics."""

    def __init__(self):
        """Initialize metrics collector."""
        self.metrics = TaskMetrics()
        self.task_completion_times: Dict[str, float] = {}

    def update_from_tasks(self, tasks: Dict[str, Any]):
        """
        Update metrics from task collection.

        Args:
            tasks: Dictionary of tasks keyed by ID
        """
        statuses = {}
        completion_times = []

        for task_id, task in tasks.items():
            status = task.get("status", "PENDING")
            statuses[status] = statuses.get(status, 0) + 1

            # Calculate completion time if available
            if (
                status == "COMPLETED"
                and task.get("completed_at")
                and task.get("created_at")
            ):
                try:
                    created = datetime.fromisoformat(task["created_at"])
                    completed = datetime.fromisoformat(task["completed_at"])
                    completion_time = (completed - created).total_seconds()
                    completion_times.append(completion_time)
                except:
                    pass

        # Update metrics
        self.metrics.total_tasks = len(tasks)
        self.metrics.completed_tasks = statuses.get("COMPLETED", 0)
        self.metrics.pending_tasks = statuses.get("PENDING", 0)
        self.metrics.blocked_tasks = statuses.get("BLOCKED", 0)
        self.metrics.archived_tasks = statuses.get("ARCHIVED", 0)

        # Calculate averages
        if completion_times:
            self.metrics.avg_completion_time = sum(completion_times) / len(
                completion_times
            )

        if self.metrics.total_tasks > 0:
            self.metrics.completion_rate = (
                self.metrics.completed_tasks / self.metrics.total_tasks * 100
            )

    def get_metrics(self) -> TaskMetrics:
        """Get current metrics."""
        return self.metrics
