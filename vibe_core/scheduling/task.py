"""
Task Definition for VibeOS Scheduler

Tasks are the unit of work in VibeOS. Agents receive tasks from the kernel
scheduler, process them, and return results.

OPUS-122: Task Alignment
========================
- TaskStatus moved to vibe_core/task_types.py (SSOT)
- Task renamed to DispatchTask for semantic clarity
- Backward compatibility aliases preserved

DispatchTask vs ManagedTask:
- DispatchTask (this file): Lightweight dispatch unit for agent execution
- ManagedTask (task_management/models.py): Rich project management model

These are semantically different - DispatchTask is a "message envelope",
ManagedTask is a "project card".
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict

# OPUS-122: Import canonical TaskStatus from SSOT
from vibe_core.task_types import TaskStatus


@dataclass
class DispatchTask:
    """
    OPUS-122: Renamed from Task to DispatchTask for semantic clarity.

    Lightweight task dispatch unit passed to VibeAgent.process().
    This is a "message envelope" - minimal data for agent execution.

    NOT to be confused with task_management.models.Task (ManagedTask)
    which is a rich project management model with title, assignee, etc.

    Fields:
        agent_id: Target agent ID to dispatch to
        payload: Task data/parameters for the agent
        task_id: Unique identifier (auto-generated UUID)
        priority: Scheduling priority (0 = normal)
        created_at: ISO timestamp when task was created
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


# =============================================================================
# BACKWARD COMPATIBILITY ALIASES (OPUS-122)
# =============================================================================

# Alias for backward compatibility - existing code imports Task
Task = DispatchTask

__all__ = [
    "DispatchTask",
    "Task",  # Backward compat alias
    "TaskStatus",  # Re-export from SSOT
]
