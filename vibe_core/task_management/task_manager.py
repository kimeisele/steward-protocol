"""Main task manager class."""

from pathlib import Path
from typing import Optional, List, Dict, Any
import json
import yaml
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
from vibe_core.narasimha import get_narasimha, ThreatLevel
from vibe_core.topology import get_agent_placement


class TaskManager:
    """Main task management system."""

    def __init__(self, project_root: Path, milk_ocean_router=None):
        """
        Initialize task manager.

        Args:
            project_root: Root directory of the project
            milk_ocean_router: Optional MilkOceanRouter instance for request routing
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

        # VIMANA DUAL-CORE PERSISTENCE (GAD-3000)
        # Initialize SQLiteStore for immortal persistence
        from vibe_core.store.sqlite_store import SQLiteStore
        db_path = self.project_root / "data" / "vibe_agency.db"
        self.sqlite_store = SQLiteStore(str(db_path))

        # MilkOcean Router for task request routing (Gap 4.1 closure)
        self.milk_ocean_router = milk_ocean_router
        if not self.milk_ocean_router:
            try:
                from steward.system_agents.envoy.tools.milk_ocean import MilkOceanRouter
                self.milk_ocean_router = MilkOceanRouter()
            except ImportError:
                # MilkOceanRouter not available, fall back to None
                self.milk_ocean_router = None

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
                        )
                        self.tasks[task_id] = task
            except Exception as e:
                print(f"Error loading tasks from JSON: {e}")

        # VIMANA SELF-HEALING: Hydrate from SQLite if JSON missing or empty
        if not tasks_file.exists() or len(self.tasks) == 0:
            self._hydrate_from_sqlite()

        # Update metrics
        self.metrics_collector.update_from_tasks(
            {task_id: task.to_dict() for task_id, task in self.tasks.items()}
        )

    def _hydrate_from_sqlite(self):
        """
        VIMANA SELF-HEALING: Regenerate tasks from SQLite if JSON missing.

        This ensures the system can never lose data, even if .vibe/ directory is deleted.
        """
        try:
            print("🔄 VIMANA: Hydrating tasks from SQLite ledger...")
            sqlite_tasks = self.sqlite_store.get_all_tasks()

            for sqlite_task in sqlite_tasks:
                # Reconstruct Task object from SQLite data
                task = Task(
                    id=sqlite_task["id"],
                    title=sqlite_task["description"].split(":")[0] if ":" in sqlite_task["description"] else sqlite_task["description"],
                    description=sqlite_task["description"].split(":", 1)[1].strip() if ":" in sqlite_task["description"] else "",
                    status=TaskStatus(sqlite_task["status"].upper()),
                    priority=0,  # SQLite doesn't store priority, default to 0
                    assignee=None,
                    tags=[],
                )
                self.tasks[task.id] = task

            print(f"   ✅ Hydrated {len(sqlite_tasks)} tasks from SQLite")

            # Regenerate JSON cache
            if sqlite_tasks:
                self._save_tasks()
        except Exception as e:
            print(f"   ⚠️  Failed to hydrate from SQLite: {e}")

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

    def _load_roadmap(self):
        """Load roadmap from disk with VIMANA self-healing."""
        roadmap_path = self.config_dir / "roadmap.yaml"

        # Try loading from YAML (cache layer)
        if roadmap_path.exists():
            try:
                with open(roadmap_path, 'r') as f:
                    data = yaml.safe_load(f)

                self.roadmap = Roadmap(
                    id=data['id'],
                    name=data['name'],
                    description=data['description'],
                    missions=data.get('missions', []),
                    created_at=datetime.fromisoformat(data['created_at']),
                    updated_at=datetime.fromisoformat(data['updated_at']),
                    metadata=data.get('metadata', {})
                )
            except Exception as e:
                print(f"Error loading roadmap from YAML: {e}")

        # VIMANA SELF-HEALING: Hydrate from SQLite if YAML missing
        if not roadmap_path.exists() or not self.roadmap:
            self._hydrate_roadmap_from_sqlite()

    def _hydrate_roadmap_from_sqlite(self):
        """
        VIMANA SELF-HEALING: Regenerate roadmap from SQLite if YAML missing.

        This ensures roadmaps persist across container restarts.
        """
        try:
            roadmaps = self.sqlite_store.get_all_roadmaps()
            if roadmaps:
                # Load the most recent roadmap
                latest = roadmaps[0]
                self.roadmap = Roadmap(
                    id=latest['id'],
                    name=latest['name'],
                    description=latest['description'],
                    missions=latest.get('missions', []),
                    created_at=datetime.fromisoformat(latest['created_at'].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(latest['updated_at'].replace('Z', '+00:00')),
                    metadata=latest.get('metadata', {})
                )
                print(f"🔄 VIMANA: Hydrated roadmap '{self.roadmap.name}' from SQLite")
                # Regenerate YAML cache
                self._save_roadmap()
        except Exception as e:
            print(f"   ⚠️  Failed to hydrate roadmap from SQLite: {e}")

    def _save_roadmap(self):
        """Save roadmap to disk."""
        if not self.roadmap:
            return

        roadmap_path = self.config_dir / "roadmap.yaml"

        try:
            with open(roadmap_path, 'w') as f:
                yaml.dump(self.roadmap.to_dict(), f)
        except Exception as e:
            print(f"Error saving roadmap: {e}")

    def add_task(
        self,
        title: str,
        description: str = "",
        priority: int = 0,
        assigned_agent: Optional[str] = None,
        roadmap_id: Optional[str] = None
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

        threat = narasimha.audit_agent(
            agent_id="TASK_MANAGER",
            agent_code=task_content,
            agent_state={}
        )

        if threat and threat.severity.value in ["red", "apocalypse"]:
            raise ValidationError(
                f"Task blocked by Narasimha (Adharma Block): {threat.description}"
            )

        task = Task(
            id=str(uuid.uuid4()),
            title=title,
            description=description,
            priority=priority,
            status=TaskStatus.PENDING,
            assignee=assigned_agent,
        )

        # NEW: Topology-aware routing (Gap 4.1 closure)
        if assigned_agent:
            placement = get_agent_placement(assigned_agent)
            if placement:
                # Annotate task with Bhu-Mandala placement
                task.topology_layer = placement.layer
                task.varna = placement.varna
                # routing_priority set by MilkOcean if available (0-3)
                task.routing_priority = 1  # Default medium priority

        # Validate
        self.validator_registry.validate_task(task)

        # VIMANA DUAL WRITE
        # 1. Add to in-memory dict
        self.tasks[task.id] = task

        # 2. Write to JSON (speed/cache)
        self._save_tasks()

        # 3. Write to SQLite (immortality/audit trail)
        try:
            self.sqlite_store.add_task(
                task_id=task.id,
                description=f"{task.title}: {task.description}",
                status=task.status.value.lower(),
            )
        except Exception as e:
            print(f"⚠️  SQLite write failed: {e}")

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

        # VIMANA DUAL WRITE
        # 1. Write to JSON (speed/cache)
        self._save_tasks()

        # 2. Write to SQLite (immortality/audit trail)
        try:
            self.sqlite_store.update_task_status(
                task_id=task.id,
                status=task.status.value.lower(),
            )
        except Exception as e:
            print(f"⚠️  SQLite update failed: {e}")

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
            updated_at=datetime.now()
        )

        self.roadmap = roadmap

        # VIMANA DUAL WRITE
        # 1. Write to YAML (cache)
        self._save_roadmap()

        # 2. Write to SQLite (immortality)
        try:
            self.sqlite_store.add_roadmap(
                roadmap_id=roadmap.id,
                name=roadmap.name,
                description=roadmap.description,
                missions=roadmap.missions,
                created_at=roadmap.created_at.isoformat(),
                updated_at=roadmap.updated_at.isoformat(),
                metadata=roadmap.metadata,
            )
        except Exception as e:
            print(f"⚠️  SQLite roadmap write failed: {e}")

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

        # VIMANA DUAL WRITE
        # 1. Write to YAML (cache)
        self._save_roadmap()

        # 2. Write to SQLite (immortality)
        try:
            self.sqlite_store.add_roadmap(
                roadmap_id=self.roadmap.id,
                name=self.roadmap.name,
                description=self.roadmap.description,
                missions=self.roadmap.missions,
                created_at=self.roadmap.created_at.isoformat(),
                updated_at=self.roadmap.updated_at.isoformat(),
                metadata=self.roadmap.metadata,
            )
        except Exception as e:
            print(f"⚠️  SQLite roadmap update failed: {e}")

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
