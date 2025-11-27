"""Main task manager class."""

from pathlib import Path
from typing import Optional, List, Dict, Any
import json
import uuid
from datetime import datetime

from .models import Task, TaskStatus, ActiveMission, Roadmap
from .file_lock import FileLock
from .validator_registry import ValidatorRegistry, ValidationError
from .metrics import MetricsCollector
from .archive import TaskArchive
from .batch_operations import BatchOperations
from .next_task_generator import NextTaskGenerator
from .export_engine import ExportEngine


class TaskManager:
    """Main task management system."""

    def __init__(self, project_root: Path):
        """
        Initialize task manager.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        self.tasks_dir = self.project_root / ".vibe" / "state"
        self.config_dir = self.project_root / ".vibe" / "config"
        self.history_dir = self.project_root / ".vibe" / "history" / "mission_logs"

        # Create directories
        self.tasks_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.history_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.validator_registry = ValidatorRegistry()
        self.metrics_collector = MetricsCollector()
        self.archive = TaskArchive(self.tasks_dir / "archive")
        self.lock = FileLock(self.tasks_dir / ".lock")

        # Load data
        self.tasks: Dict[str, Task] = {}
        self.active_mission: Optional[ActiveMission] = None
        self.roadmap: Optional[Roadmap] = None

        self._load_tasks()
        self._load_mission()

    def _load_tasks(self):
        """Load tasks from disk."""
        tasks_file = self.tasks_dir / "tasks.json"

        if tasks_file.exists():
            try:
                with self.lock:
                    data = json.loads(tasks_file.read_text())
                    for task_id, task_data in data.items():
                        task = Task(
                            id=task_data["id"],
                            title=task_data["title"],
                            description=task_data.get("description", ""),
                            status=TaskStatus(task_data.get("status", "PENDING")),
                            priority=task_data.get("priority", 0),
                            assignee=task_data.get("assignee"),
                            tags=task_data.get("tags", []),
                        )
                        self.tasks[task_id] = task
            except Exception as e:
                print(f"Error loading tasks: {e}")

        # Update metrics
        self.metrics_collector.update_from_tasks(
            {task_id: task.to_dict() for task_id, task in self.tasks.items()}
        )

    def _load_mission(self):
        """Load active mission from disk."""
        mission_file = self.config_dir / "active_mission.json"

        if mission_file.exists():
            try:
                data = json.loads(mission_file.read_text())
                self.active_mission = ActiveMission(
                    id=data["id"],
                    title=data["title"],
                    description=data.get("description", ""),
                    current_task=data.get("current_task"),
                    completed_tasks=data.get("completed_tasks", []),
                    blocked_tasks=data.get("blocked_tasks", []),
                )
            except Exception as e:
                print(f"Error loading mission: {e}")

    def _save_tasks(self):
        """Save tasks to disk."""
        tasks_file = self.tasks_dir / "tasks.json"

        try:
            with self.lock:
                tasks_data = {
                    task_id: task.to_dict()
                    for task_id, task in self.tasks.items()
                }
                tasks_file.write_text(json.dumps(tasks_data, indent=2))
        except Exception as e:
            print(f"Error saving tasks: {e}")

    def _save_mission(self):
        """Save active mission to disk."""
        if not self.active_mission:
            return

        mission_file = self.config_dir / "active_mission.json"

        try:
            mission_file.write_text(
                json.dumps(self.active_mission.to_dict(), indent=2)
            )
        except Exception as e:
            print(f"Error saving mission: {e}")

    def add_task(self, title: str, description: str = "", priority: int = 0) -> Task:
        """
        Add a new task.

        Args:
            title: Task title
            description: Task description
            priority: Task priority (0-100)

        Returns:
            The created task

        Raises:
            ValidationError if task is invalid
        """
        task = Task(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            priority=priority,
            status=TaskStatus.PENDING,
        )

        # Validate
        self.validator_registry.validate_task(task)

        # Add to manager
        self.tasks[task.id] = task
        self._save_tasks()

        return task

    def update_task(self, task_id: str, **kwargs) -> Optional[Task]:
        """
        Update a task.

        Args:
            task_id: Task ID
            **kwargs: Fields to update (title, description, status, priority, assignee, tags)

        Returns:
            Updated task, or None if not found
        """
        if task_id not in self.tasks:
            return None

        task = self.tasks[task_id]
        task.updated_at = datetime.now()

        # Update fields
        if "title" in kwargs:
            task.title = kwargs["title"]
        if "description" in kwargs:
            task.description = kwargs["description"]
        if "status" in kwargs:
            task.status = kwargs["status"]
            if kwargs["status"] == TaskStatus.COMPLETED:
                task.completed_at = datetime.now()
        if "priority" in kwargs:
            task.priority = kwargs["priority"]
        if "assignee" in kwargs:
            task.assignee = kwargs["assignee"]
        if "tags" in kwargs:
            task.tags = kwargs["tags"]

        # Validate
        self.validator_registry.validate_task(task)

        # Save
        self._save_tasks()

        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self.tasks.get(task_id)

    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        priority: Optional[int] = None,
        tag: Optional[str] = None,
    ) -> List[Task]:
        """
        List tasks with optional filters.

        Args:
            status: Filter by status
            priority: Filter by priority (exact match)
            tag: Filter by tag

        Returns:
            List of filtered tasks
        """
        results = list(self.tasks.values())

        if status:
            results = BatchOperations.filter_by_status(self.tasks, status)

        if priority is not None:
            results = [t for t in results if t.priority == priority]

        if tag:
            results = [t for t in results if tag in t.tags]

        return sorted(results, key=lambda t: t.priority, reverse=True)

    def get_active_mission(self) -> Optional[ActiveMission]:
        """Get the active mission."""
        return self.active_mission

    def set_active_mission(self, title: str, description: str) -> ActiveMission:
        """
        Set the active mission.

        Args:
            title: Mission title
            description: Mission description

        Returns:
            The created mission
        """
        self.active_mission = ActiveMission(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
        )
        self._save_mission()
        return self.active_mission

    def get_next_task(self) -> Optional[Task]:
        """Get the next task to work on."""
        return NextTaskGenerator.get_next_task(self.tasks)

    def archive_task(self, task_id: str) -> bool:
        """Archive a task."""
        task = self.get_task(task_id)
        if not task:
            return False

        self.archive.archive_task(task)
        del self.tasks[task_id]
        self._save_tasks()

        return True

    def get_metrics(self) -> Dict[str, Any]:
        """Get task metrics."""
        return self.metrics_collector.get_metrics().to_dict()

    def export_tasks_json(self, output_path: Path) -> bool:
        """Export tasks to JSON."""
        return ExportEngine.export_to_json(self.tasks, output_path)

    def export_tasks_csv(self, output_path: Path) -> bool:
        """Export tasks to CSV."""
        return ExportEngine.export_to_csv(self.tasks, output_path)

    def export_tasks_markdown(self, output_path: Path) -> bool:
        """Export tasks to Markdown."""
        return ExportEngine.export_to_markdown(self.tasks, output_path)
