"""
SARGA CYCLE PLUGIN - The Cosmic Gate of Task Submission

This plugin implements the Brahma Cycle (DAY/NIGHT of Brahma).
It is OPTIONAL and SWAPPABLE - the scheduler doesn't depend on it.

The Sarga Model:
- DAY_OF_BRAHMA: Creation cycle - all task types allowed
- NIGHT_OF_BRAHMA: Maintenance cycle - only maintenance tasks allowed

This plugin:
1. Owns the Sarga cycle state and task type restrictions
2. Uses on_task_submit hook to VETO non-maintenance tasks during night
3. Can be replaced with different scheduling restrictions

Philosophy:
"The kernel is Vishnu - unchanging. The cosmic cycles are the Devatas -
 they observe and restrict without modifying the eternal substrate."
"""

import logging
from typing import TYPE_CHECKING, Set

from vibe_core.plugin_protocol import KernelPlugin

# Lazy import to prevent circular dependencies
# from vibe_core.sarga import Cycle, get_sarga

if TYPE_CHECKING:
    from vibe_core import Task
    from vibe_core.protocols.kernel_protocol import KernelProtocol

logger = logging.getLogger("SARGA_CYCLE")


class SargaCyclePlugin(KernelPlugin):
    """
    Sarga Cycle Plugin - Day/Night of Brahma Enforcement.

    This plugin provides:
    - Task type restriction during NIGHT_OF_BRAHMA
    - Only maintenance tasks allowed during night cycle

    Priority: 5 (very early - cosmic gate before governance)
    """

    # Task types allowed during NIGHT_OF_BRAHMA
    MAINTENANCE_TASK_TYPES: Set[str] = {
        "bugfix",
        "fix",
        "maintenance",
        "refactor",
        "cleanup",
        "optimization",
        "performance",
        "security",
        "test",
        "debug",
    }

    @property
    def plugin_id(self) -> str:
        return "sarga_cycle"

    @property
    def priority(self) -> int:
        return 5  # Very early - cosmic gate is fundamental

    def on_boot(self, kernel: "KernelProtocol") -> None:
        """Called when kernel boots."""
        from vibe_core.sarga import get_sarga

        sarga = get_sarga()
        cycle = sarga.get_cycle()
        logger.info(f"🌌 Sarga Cycle Plugin booted (current: {cycle.value.upper()}_OF_BRAHMA)")
        logger.info("   Cosmic gate is now PLUGIN-BASED (not hardcoded in scheduler)")

    def on_task_submit(self, kernel: "KernelProtocol", task: "Task") -> bool:
        """
        COSMIC GATE: Check if task type is allowed during current cycle.

        During NIGHT_OF_BRAHMA, only maintenance tasks are allowed.
        Returns False and raises ValueError to reject non-maintenance tasks.
        """
        from vibe_core.sarga import Cycle, get_sarga

        sarga = get_sarga()
        current_cycle = sarga.get_cycle()

        # During NIGHT_OF_BRAHMA, restrict task types
        if current_cycle == Cycle.NIGHT_OF_BRAHMA:
            task_type = ""
            if task.payload:
                task_type = task.payload.get("type", "").lower()

            # Check if task type is allowed during night cycle
            if task_type and task_type not in self.MAINTENANCE_TASK_TYPES:
                logger.warning(
                    f"🌙 Task {task.task_id} blocked: type '{task_type}' not allowed during NIGHT_OF_BRAHMA. "
                    f"Only maintenance tasks permitted."
                )
                raise ValueError(
                    f"Task type '{task_type}' not allowed during NIGHT_OF_BRAHMA. "
                    f"Only maintenance tasks are permitted: {', '.join(sorted(self.MAINTENANCE_TASK_TYPES))}"
                )

            logger.info(f"🌙 Task {task.task_id} approved for NIGHT_OF_BRAHMA (maintenance cycle)")

        elif current_cycle == Cycle.DAY_OF_BRAHMA:
            logger.debug(f"☀️  Task {task.task_id} approved for DAY_OF_BRAHMA (creation cycle)")

        return True  # Allow task

    def on_shutdown(self, kernel: "KernelProtocol") -> None:
        """Clean up on shutdown."""
        logger.info("🌌 Sarga Cycle Plugin shutting down")
