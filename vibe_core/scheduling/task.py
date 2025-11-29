"""
Task Definition for VibeOS Scheduler

Tasks are the unit of work in VibeOS. Agents receive tasks from the kernel
scheduler, process them, and return results.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict


class TaskStatus(str, Enum):
    """Task lifecycle states"""

    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"


@dataclass
class Task:
    """
    Task object passed to VibeAgent.process()

    Represents a unit of work that an agent should perform.
    """

    agent_id: str  # Target agent ID
    payload: Dict[str, Any]  # Task data/parameters
    task_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    priority: int = 0
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Serialize task to dictionary"""
        return {
            "task_id": self.task_id,
            "agent_id": self.agent_id,
            "payload": self.payload,
            "priority": self.priority,
            "created_at": self.created_at,
        }
