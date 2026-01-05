"""
NAGA Flood: TaskManager.

Phase 3A: Paradox Resolution - Task execution must be profiled.

Surgical Overrides:
- add_task: CHITRAGUPTA profiling + SESHA audit
- update_task: CHITRAGUPTA profiling + SESHA audit
- set_active_mission: SESHA audit

NAGA Assignment:
- SESHA: Audit trail for all task operations
- CHITRAGUPTA: Performance profiling and metrics
"""

import logging
import time
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from vibe_core.naga.mixins import ChitraguptaMixin, SeshaMixin
from vibe_core.task_management.task_manager import TaskManager

if TYPE_CHECKING:
    from vibe_core.io_service import KernelIOService
    from vibe_core.task_management.models import ActiveMission, Task

logger = logging.getLogger("NAGA.FLOOD.TASKMANAGER")


class FloodedTaskManager(SeshaMixin, ChitraguptaMixin, TaskManager):
    """
    NAGA-Flooded TaskManager.

    Original TaskManager wrapped with:
    - SESHA: Audit logging for all task operations
    - CHITRAGUPTA: Performance profiling and metrics

    isinstance(flooded, TaskManager) == True  # Preserved!
    """

    def add_task(
        self,
        title: str,
        description: str = "",
        priority: str = "medium",
        agent: Optional[str] = None,
        depends_on: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> "Task":
        """
        Add a task - with NAGA protection.

        CHITRAGUPTA: Profile task creation time
        SESHA: Audit trail for task creation
        """
        start_time = time.time()

        # === SESHA: Record add attempt ===
        if self.sesha:
            self.sesha.record_event(
                event_type="task.add.start",
                source="FloodedTaskManager",
                details={"title": title, "priority": priority, "agent": agent},
            )

        # === Execute original add ===
        task = super().add_task(
            title=title,
            description=description,
            priority=priority,
            agent=agent,
            depends_on=depends_on,
            tags=tags,
            context=context,
        )

        # === CHITRAGUPTA: Profile creation time ===
        elapsed_ms = (time.time() - start_time) * 1000
        if self.chitragupta:
            self.chitragupta.record_profile(
                operation="task.add",
                duration_ms=elapsed_ms,
                metadata={"task_id": task.id, "priority": priority},
            )

        # === SESHA: Record success ===
        if self.sesha:
            self.sesha.record_event(
                event_type="task.add.complete",
                source="FloodedTaskManager",
                details={
                    "task_id": task.id,
                    "duration_ms": elapsed_ms,
                },
            )

        return task

    def update_task(self, task_id: str, **kwargs) -> Optional["Task"]:
        """
        Update a task - with NAGA protection.

        CHITRAGUPTA: Profile update time
        SESHA: Audit trail for task update
        """
        start_time = time.time()

        # === SESHA: Record update attempt ===
        if self.sesha:
            self.sesha.record_event(
                event_type="task.update.start",
                source="FloodedTaskManager",
                details={"task_id": task_id, "fields": list(kwargs.keys())},
            )

        # === Execute original update ===
        task = super().update_task(task_id, **kwargs)

        # === CHITRAGUPTA: Profile update time ===
        elapsed_ms = (time.time() - start_time) * 1000
        if self.chitragupta:
            self.chitragupta.record_profile(
                operation="task.update",
                duration_ms=elapsed_ms,
                metadata={"task_id": task_id, "fields_updated": len(kwargs)},
            )

        # === SESHA: Record result ===
        if self.sesha:
            self.sesha.record_event(
                event_type="task.update.complete" if task else "task.update.not_found",
                source="FloodedTaskManager",
                details={
                    "task_id": task_id,
                    "success": task is not None,
                    "duration_ms": elapsed_ms,
                },
            )

        return task

    def set_active_mission(self, title: str, description: str) -> "ActiveMission":
        """
        Set active mission - with NAGA protection.

        SESHA: Audit trail for mission changes (important for governance)
        """
        # === SESHA: Record mission change ===
        if self.sesha:
            old_mission = self.active_mission.title if self.active_mission else None
            self.sesha.record_event(
                event_type="mission.set",
                source="FloodedTaskManager",
                details={
                    "new_title": title,
                    "old_title": old_mission,
                    "description": description[:100],  # Truncate for log
                },
            )

        # === Execute original ===
        mission = super().set_active_mission(title, description)

        return mission

    def archive_task(self, task_id: str) -> bool:
        """
        Archive a task - with NAGA protection.

        SESHA: Audit trail for task archival
        """
        # === SESHA: Record archive attempt ===
        if self.sesha:
            self.sesha.record_event(
                event_type="task.archive.start",
                source="FloodedTaskManager",
                details={"task_id": task_id},
            )

        # === Execute original ===
        success = super().archive_task(task_id)

        # === SESHA: Record result ===
        if self.sesha:
            self.sesha.record_event(
                event_type="task.archive.complete",
                source="FloodedTaskManager",
                details={"task_id": task_id, "success": success},
            )

        return success


# =============================================================================
# Factory
# =============================================================================


def get_flooded_task_manager(
    project_root: Path,
    io_service: Optional["KernelIOService"] = None,
) -> FloodedTaskManager:
    """Get a NAGA-flooded TaskManager."""
    return FloodedTaskManager(project_root=project_root, io_service=io_service)
