"""Task management data models."""

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import Optional, List, Any, Dict
from pathlib import Path


class TaskStatus(str, Enum):
    """Task status states."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    ARCHIVED = "ARCHIVED"


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
    metadata: Dict[str, Any] = field(default_factory=dict)
    # Topology-aware routing fields
    topology_layer: Optional[str] = None  # Bhu Mandala layer (BRAHMALOKA|JANALOKA|...|BHURLOKA)
    varna: Optional[str] = None           # Vedic class (BRAHMANA|KSHATRIYA|VAISHYA|SHUDRA)
    routing_priority: Optional[int] = None # MilkOcean priority (0-3)

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "assignee": self.assignee,
            "tags": self.tags,
            "subtasks": self.subtasks,
            "metadata": self.metadata,
            "topology_layer": self.topology_layer,
            "varna": self.varna,
            "routing_priority": self.routing_priority,
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
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
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
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
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
