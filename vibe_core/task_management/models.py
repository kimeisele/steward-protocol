"""
Task management data models.

OPUS-122: Task Alignment
========================
TaskStatus moved to vibe_core/task_types.py (SSOT).
Task class now has alias ManagedTask for semantic clarity.

TWO Task types exist in the codebase (by design - OPUS-122 validated):

1. scheduling.task.DispatchTask (was Task)
   - Purpose: Kernel task dispatch to agents
   - Fields: agent_id, payload, task_id, priority
   - Used by: Kernel, Agents, Cartridges
   - Semantic: "Message envelope" - lightweight dispatch unit

2. task_management.models.Task (alias: ManagedTask) - THIS FILE
   - Purpose: User-facing task management with rich metadata
   - Fields: title, description, subtasks, assignee, topology routing
   - Used by: UI, Task Manager, Roadmaps
   - Semantic: "Project card" - rich management model

These are semantically different and intentionally parallel.
Do NOT merge them - they serve different layers of the system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, object

# OPUS-122: Import canonical TaskStatus from SSOT
from vibe_core.task_types import TaskStatus


@dataclass
class Task:
    """Individual task model."""

    id: str
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    assignee: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    subtasks: List[str] = field(default_factory=list)
    metadata: Dict[str, object] = field(default_factory=dict)
    # Topology-aware routing fields
    topology_layer: Optional[str] = None  # Bhu Mandala layer (BRAHMALOKA|JANALOKA|...|BHURLOKA)
    varna: Optional[str] = None  # Vedic class (BRAHMANA|KSHATRIYA|VAISHYA|SHUDRA)
    routing_priority: Optional[int] = None  # MilkOcean priority (0-3)
    roadmap_id: Optional[str] = None  # Which roadmap this belongs to

    def to_dict(self) -> Dict[str, object]:
        """Convert task to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": (self.completed_at.isoformat() if self.completed_at else None),
            "assignee": self.assignee,
            "tags": self.tags,
            "subtasks": self.subtasks,
            "metadata": self.metadata,
            "topology_layer": self.topology_layer,
            "varna": self.varna,
            "routing_priority": self.routing_priority,
            "roadmap_id": self.roadmap_id,
        }


@dataclass
class ActiveMission:
    """Current active mission model."""

    id: str
    title: str
    description: str
    current_task: Optional[str] = None
    completed_tasks: List[str] = field(default_factory=list)
    blocked_tasks: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        """Convert mission to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "current_task": self.current_task,
            "completed_tasks": self.completed_tasks,
            "blocked_tasks": self.blocked_tasks,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
        }


@dataclass
class Roadmap:
    """Roadmap for organizing multiple missions."""

    id: str
    name: str
    description: str
    missions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, object]:
        """Convert roadmap to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "missions": self.missions,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
        }


# =============================================================================
# OPUS-122: SEMANTIC ALIAS
# =============================================================================
# ManagedTask is an alias for Task to clarify its purpose when imported
# alongside scheduling.task.DispatchTask.
#
# Usage:
#   from vibe_core.task_management.models import ManagedTask
#   from vibe_core.scheduling.task import DispatchTask
# =============================================================================

ManagedTask = Task

__all__ = [
    "Task",
    "ManagedTask",  # Semantic alias (OPUS-122)
    "TaskStatus",  # Re-exported from SSOT
    "ActiveMission",
    "Roadmap",
]
