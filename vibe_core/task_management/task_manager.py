"""Main task manager class."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

import yaml

from vibe_core.narasimha import get_narasimha
from vibe_core.topology import get_agent_placement
from vibe_core.utils import atomic_write_json

from .archive import TaskArchive
from .batch_operations import BatchOperations
from .export_engine import ExportEngine
from .file_lock import FileLock
from .metrics import MetricsCollector
from .models import ActiveMission, Roadmap, Task, TaskStatus
from .next_task_generator import NextTaskGenerator
from .validator_registry import ValidationError, ValidatorRegistry

if TYPE_CHECKING:
    from vibe_core.io_service import KernelIOService

logger = logging.getLogger("TASK_MANAGER")


class TaskManager:
    """Main task management system."""

    def __init__(self, project_root: Path, io_service: Optional["KernelIOService"] = None):
        """
        Initialize task manager.

        Args:
            project_root: Root directory of the project
            io_service: Optional KernelIOService for centralized file writes
        """
        self.project_root = Path(project_root)
        self.tasks_dir = self.project_root / ".vibe" / "state"
        self.config_dir = self.project_root / ".vibe" / "config"
        self.history_dir = self.project_root / ".vibe" / "history" / "mission_logs"
        self._io_service = io_service

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
        self._load_roadmap()

    def _load_tasks(self):
        """Load tasks from disk with VIMANA self-healing."""
        tasks_file = self.tasks_dir / "tasks.json"

        # Try loading from JSON (cache layer)
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
                            subtasks=task_data.get("subtasks", []),
                            metadata=task_data.get("metadata", {}),
                            # Topology fields (Gap 4.1 persistence fix)
                            topology_layer=task_data.get("topology_layer"),
                            varna=task_data.get("varna"),
                            routing_priority=task_data.get("routing_priority"),
                            roadmap_id=task_data.get("roadmap_id"),
                        )
                        self.tasks[task_id] = task
            except Exception as e:
                print(f"Error loading tasks from JSON: {e}")

        # OPUS-213: JSON is now the only persistence layer (no SQLite fallback)

        # Update metrics
        self.metrics_collector.update_from_tasks({task_id: task.to_dict() for task_id, task in self.tasks.items()})

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

    def _write_json(self, path: Path, content: str) -> bool:
        """
        Write JSON content through I/O Service or fallback.

        Args:
            path: Path to write to
            content: JSON content to write

        Returns:
            True if write succeeded, False otherwise
        """
        if self._io_service:
            from vibe_core.io_service import DocumentType

            result = self._io_service.write_document(
                name=str(path.relative_to(self.project_root)),
                content=content,
                doc_type=DocumentType.SNAPSHOT,
                writer_id="TASK_MANAGER",
                add_header=False,
            )
            if not result.success:
                logger.error(f"❌ I/O Service write failed: {result.error}")
                return False
            return True
        else:
            # Fallback: direct write (standalone/test mode only)
            try:
                path.write_text(content, encoding="utf-8")
                return True
            except Exception as e:
                logger.error(f"❌ Direct write failed: {e}")
                return False

    def _save_tasks(self):
        """Save tasks to disk with atomic write (OPUS-213)."""
        tasks_file = self.tasks_dir / "tasks.json"

        try:
            with self.lock:
                tasks_data = {task_id: task.to_dict() for task_id, task in self.tasks.items()}
                # OPUS-213: Atomic Write for crash-safety
                atomic_write_json(tasks_file, tasks_data)
        except Exception as e:
            print(f"Error saving tasks: {e}")

    def _save_mission(self):
        """Save active mission to disk."""
        if not self.active_mission:
            return

        mission_file = self.config_dir / "active_mission.json"

        try:
            content = json.dumps(self.active_mission.to_dict(), indent=2)
            if not self._write_json(mission_file, content):
                print("Error saving mission: Failed to write file")
        except Exception as e:
            print(f"Error saving mission: {e}")

    def _load_roadmap(self):
        """Load roadmap from disk with VIMANA self-healing."""
        roadmap_path = self.config_dir / "roadmap.yaml"

        # Try loading from YAML (cache layer)
        if roadmap_path.exists():
            try:
                with open(roadmap_path, "r") as f:
                    data = yaml.safe_load(f)

                self.roadmap = Roadmap(
                    id=data["id"],
                    name=data["name"],
                    description=data["description"],
                    missions=data.get("missions", []),
                    created_at=datetime.fromisoformat(data["created_at"]),
                    updated_at=datetime.fromisoformat(data["updated_at"]),
                    metadata=data.get("metadata", {}),
                )
            except Exception as e:
                print(f"Error loading roadmap from YAML: {e}")

        # OPUS-213: YAML is now the only persistence layer for roadmaps

    def _save_roadmap(self):
        """Save roadmap to disk."""
        if not self.roadmap:
            return

        roadmap_path = self.config_dir / "roadmap.yaml"

        try:
            with open(roadmap_path, "w") as f:
                yaml.dump(self.roadmap.to_dict(), f)
        except Exception as e:
            print(f"Error saving roadmap: {e}")

    def add_task(
        self,
        title: str,
        description: str = "",
        priority: int = 0,
        assigned_agent: Optional[str] = None,
        roadmap_id: Optional[str] = None,
    ) -> Task:
        """
        Add a new task with topology-aware routing and optional roadmap linking.

        Args:
            title: Task title
            description: Task description
            priority: Task priority (0-100)
            assigned_agent: Optional agent ID to assign task to (e.g., "herald", "civic")
            roadmap_id: Optional roadmap ID to link task to (auto-links to active roadmap if None)

        Returns:
            The created task with topology annotations

        Raises:
            ValidationError if task is invalid or blocked by Narasimha
        """
        # Security check: Scan task content through Narasimha (Adharma Block)
        narasimha = get_narasimha()
        task_content = f"{title}\n{description}"

        threat = narasimha.audit_agent(agent_id="TASK_MANAGER", agent_code=task_content, agent_state={})

        if threat and threat.severity.value in ["red", "apocalypse"]:
            raise ValidationError(f"Task blocked by Narasimha (Adharma Block): {threat.description}")

        # Auto-link to active roadmap if no roadmap_id provided
        final_roadmap_id = roadmap_id if roadmap_id else (self.roadmap.id if self.roadmap else None)

        task = Task(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            priority=priority,
            status=TaskStatus.PENDING,
            assignee=assigned_agent,
            roadmap_id=final_roadmap_id,
        )

        # LEGACY ROUTER REMOVED (MilkOcean)
        # TODO: Integrate with UnifiedRouter for dynamic prioritization
        milk_ocean_priority = 1  # Default MEDIUM

        # Topology-aware routing (Gap 4.1 closure - Part 1)
        if assigned_agent:
            placement = get_agent_placement(assigned_agent)
            if placement:
                # Annotate task with Bhu-Mandala placement
                task.topology_layer = placement.layer
                task.varna = placement.varna

        # Set routing priority (from MilkOcean or default)
        task.routing_priority = milk_ocean_priority

        # Validate
        self.validator_registry.validate_task(task)

        # OPUS-213: Single persistence layer
        self.tasks[task.id] = task
        self._save_tasks()

        # 4. Add task to roadmap if roadmap_id is set
        if task.roadmap_id and self.roadmap and task.roadmap_id == self.roadmap.id:
            if task.id not in self.roadmap.missions:
                self.roadmap.missions.append(task.id)
                self.update_roadmap(missions=self.roadmap.missions)

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

        # OPUS-213: Single persistence layer
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

    def create_roadmap(self, name: str, description: str, missions: List[str] = None) -> Roadmap:
        """
        Create a new roadmap.

        Args:
            name: Roadmap name
            description: Roadmap description
            missions: Optional list of mission IDs

        Returns:
            The created roadmap
        """
        roadmap = Roadmap(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            missions=missions or [],
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )

        self.roadmap = roadmap

        # OPUS-213: Single persistence layer
        self._save_roadmap()

        return roadmap

    def update_roadmap(self, **kwargs) -> Optional[Roadmap]:
        """
        Update current roadmap.

        Args:
            **kwargs: Fields to update (name, description, missions, metadata)

        Returns:
            Updated roadmap, or None if no roadmap is active
        """
        if not self.roadmap:
            return None

        for key, value in kwargs.items():
            if hasattr(self.roadmap, key):
                setattr(self.roadmap, key, value)

        self.roadmap.updated_at = datetime.now()

        # OPUS-213: Single persistence layer
        self._save_roadmap()

        return self.roadmap

    def assign_tasks_to_roadmap(self, task_ids: List[str], roadmap_id: str) -> bool:
        """
        Assign tasks to a roadmap.

        Args:
            task_ids: List of task IDs to assign
            roadmap_id: Roadmap ID to assign to

        Returns:
            True if assignment succeeded
        """
        for task in self.tasks.values():
            if task.id in task_ids:
                task.roadmap_id = roadmap_id

        self._save_tasks()
        return True
