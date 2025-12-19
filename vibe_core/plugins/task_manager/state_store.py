"""
JsonTaskManager - Plugin-local JSON state store.
Implements Plugin Sovereignty: Each plugin owns its own state.

OPUS-122: Task Alignment
========================
TaskStatus moved to vibe_core/task_types.py (SSOT).
This file now imports from the canonical location.

BACKWARD COMPATIBILITY:
This file previously used lowercase status values in JSON storage.
We maintain lowercase in the JSON files for existing data compatibility,
but use the canonical UPPERCASE TaskStatus enum internally.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# OPUS-122: Import canonical TaskStatus from SSOT
from vibe_core.task_types import TaskStatus

logger = logging.getLogger("PRANA.TaskManager.State")


# =============================================================================
# OPUS-122: JSON Storage Value Mapping
# =============================================================================
# JSON files use lowercase values for backward compatibility.
# These mappings convert between canonical TaskStatus and storage format.
# =============================================================================


def _status_to_storage(status: TaskStatus) -> str:
    """Convert TaskStatus enum to lowercase storage value."""
    return status.value.lower()


def _storage_to_status(value: str) -> TaskStatus:
    """Convert lowercase storage value to TaskStatus enum."""
    return TaskStatus(value.upper())


@dataclass
class StoredTask:
    """
    Immutable task representation for JSON storage.

    OPUS-122: Updated references:
    - For the full Task model with topology routing, see task_management.models.ManagedTask
    - For kernel scheduler tasks, see scheduling.task.DispatchTask
    - TaskStatus imported from vibe_core.task_types (SSOT)

    Note: status field stores lowercase values for JSON backward compatibility.
    """

    id: str
    title: str
    description: str
    type: str = "general"
    status: str = "pending"  # OPUS-122: lowercase for JSON compat
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
            status=_status_to_storage(TaskStatus.PENDING),  # OPUS-122: use mapping
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
        pending_value = _status_to_storage(TaskStatus.PENDING)  # OPUS-122
        for task in self.tasks.values():
            if task.status == pending_value:
                return task
        return None

    def update_status(self, task_id: str, status: TaskStatus):
        """Update task status and timestamp."""
        if task_id in self.tasks:
            # OPUS-122: Convert to lowercase storage format
            if isinstance(status, TaskStatus):
                self.tasks[task_id].status = _status_to_storage(status)
            else:
                # Handle string input - normalize and convert
                self.tasks[task_id].status = status.lower()
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
        # OPUS-122: Convert to lowercase storage format for comparison
        if isinstance(status, TaskStatus):
            status_val = _status_to_storage(status)
        else:
            status_val = status.lower()
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
