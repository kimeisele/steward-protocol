"""
JsonTaskManager - Plugin-local JSON state store.
Implements Plugin Sovereignty: Each plugin owns its own state.
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger("PRANA.TaskManager.State")


class TaskStatus(Enum):
    """Task lifecycle states."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class StoredTask:
    """
    Immutable task representation for JSON storage.

    Note: This is a simplified task model for plugin-local persistence.
    For the full Task model with topology routing, see task_management.models.Task.
    For kernel scheduler tasks, see scheduling.task.Task.
    """

    id: str
    title: str
    description: str
    type: str = "general"
    status: str = TaskStatus.PENDING.value
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict = field(default_factory=dict)

    def to_dict(self):
        """Serialize to JSON-compatible dict."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "type": self.type,
            "status": self.status,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }


class JsonTaskManager:
    """Local JSON-based task storage (State Sovereignty Pattern)."""

    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.file_path = self.data_dir / "tasks.json"
        self._ensure_dir()
        self.tasks: Dict[str, StoredTask] = self._load()
        logger.info(f"🔓 JsonTaskManager initialized at {self.file_path}")

    def _ensure_dir(self):
        """Create data directory if it doesn't exist."""
        if not self.data_dir.exists():
            self.data_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"📁 Created state directory: {self.data_dir}")

    def _load(self) -> Dict[str, StoredTask]:
        """Load tasks from JSON file."""
        if not self.file_path.exists():
            logger.info("📄 No existing state file, starting fresh")
            return {}

        try:
            with open(self.file_path, "r") as f:
                data = json.load(f)
                tasks = {}
                for task_id, task_data in data.items():
                    tasks[task_id] = StoredTask(**task_data)
                logger.info(f"✅ Loaded {len(tasks)} tasks from state")
                return tasks
        except Exception as e:
            logger.error(f"❌ Failed to load state: {e}")
            return {}

    def _save(self):
        """Persist tasks to JSON file."""
        try:
            with open(self.file_path, "w") as f:
                data = {k: v.to_dict() for k, v in self.tasks.items()}
                json.dump(data, f, indent=2, default=str)
                logger.debug(f"💾 State persisted ({len(self.tasks)} tasks)")
        except Exception as e:
            logger.error(f"❌ Failed to save state: {e}")

    def add_task(self, title: str, description: str, type: str = "general", metadata: Dict = None) -> StoredTask:
        """Add a new task to the queue."""
        import uuid

        task_id = str(uuid.uuid4())[:8]
        task = StoredTask(
            id=task_id,
            title=title,
            description=description,
            type=type,
            status=TaskStatus.PENDING.value,
            metadata=metadata or {},
        )
        self.tasks[task_id] = task
        self._save()
        logger.info(f"➕ Task added: {title} ({task_id})")
        return task

    def get_task(self, task_id: str) -> Optional[StoredTask]:
        """Retrieve a specific task."""
        return self.tasks.get(task_id)

    def get_next_pending(self) -> Optional[StoredTask]:
        """Get the next pending task (FIFO order)."""
        for task in self.tasks.values():
            if task.status == TaskStatus.PENDING.value:
                return task
        return None

    def update_status(self, task_id: str, status: TaskStatus):
        """Update task status and timestamp."""
        if task_id in self.tasks:
            self.tasks[task_id].status = status.value if isinstance(status, TaskStatus) else status
            self.tasks[task_id].updated_at = datetime.utcnow().isoformat()
            self._save()
            logger.info(f"🔄 Task {task_id} → {self.tasks[task_id].status}")
        else:
            logger.warning(f"⚠️  Task {task_id} not found")

    def get_all_tasks(self) -> List[StoredTask]:
        """Get all tasks (for rendering)."""
        return sorted(self.tasks.values(), key=lambda t: t.created_at, reverse=True)

    def get_tasks_by_status(self, status: TaskStatus) -> List[StoredTask]:
        """Filter tasks by status."""
        status_val = status.value if isinstance(status, TaskStatus) else status
        return [t for t in self.tasks.values() if t.status == status_val]

    def delete_task(self, task_id: str):
        """Remove a task from the queue."""
        if task_id in self.tasks:
            del self.tasks[task_id]
            self._save()
            logger.info(f"🗑️  Task {task_id} deleted")

    def get_stats(self) -> Dict:
        """Return task statistics."""
        return {
            "total": len(self.tasks),
            "pending": len(self.get_tasks_by_status(TaskStatus.PENDING)),
            "in_progress": len(self.get_tasks_by_status(TaskStatus.IN_PROGRESS)),
            "completed": len(self.get_tasks_by_status(TaskStatus.COMPLETED)),
            "failed": len(self.get_tasks_by_status(TaskStatus.FAILED)),
            "blocked": len(self.get_tasks_by_status(TaskStatus.BLOCKED)),
        }
