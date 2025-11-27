"""Task generation logic for determining next tasks."""

from typing import Optional, List, Dict
from .models import Task, TaskStatus
from .batch_operations import BatchOperations


class NextTaskGenerator:
    """Determines the next task to work on with topology-aware routing."""

    @staticmethod
    def _topology_aware_sort_key(task: Task) -> tuple:
        """
        Generate sort key for topology-aware task routing.

        Priority order (Gap 4.1 - Fractal Architecture):
        1. Routing priority (MilkOcean 0-3: LOW=0, MEDIUM=1, HIGH=2, CRITICAL=3)
        2. Topology layer (Bhu Mandala: closer to BRAHMALOKA = higher)
        3. Task priority (user-defined 0-100)
        4. Varna (BRAHMANA > KSHATRIYA > VAISHYA > SHUDRA)

        Args:
            task: Task to generate key for

        Returns:
            Tuple for sorting (higher = more important)
        """
        # Layer priority (Bhu Mandala hierarchy)
        layer_priority = {
            "BRAHMALOKA": 7,  # Highest - Creators
            "JANALOKA": 6,    # Wisdom
            "TAPOLOKA": 5,    # Austerity
            "MAHARLOKA": 4,   # Great
            "SVARLOKA": 3,    # Heaven
            "BHUVARLOKA": 2,  # Intermediate
            "BHURLOKA": 1,    # Earth/Boundary
        }.get(task.topology_layer or "BHURLOKA", 1)

        # Varna priority (Vedic hierarchy)
        varna_priority = {
            "BRAHMANA": 4,  # Priests/Knowledge
            "KSHATRIYA": 3, # Warriors/Protection
            "VAISHYA": 2,   # Merchants/Commerce
            "SHUDRA": 1,    # Service/Labor
        }.get(task.varna or "SHUDRA", 1)

        # Routing priority (MilkOcean 4-tier system)
        routing_priority = task.routing_priority or 1

        # User priority (0-100)
        user_priority = task.priority

        return (routing_priority, layer_priority, user_priority, varna_priority)

    @staticmethod
    def get_next_task(tasks: Dict[str, Task]) -> Optional[Task]:
        """
        Get the next task to work on with topology-aware routing.

        Priority order:
        1. In-progress tasks (resume them) - topology-sorted
        2. Pending tasks - topology-sorted
        3. Blocked tasks (unblock if possible) - topology-sorted

        Topology routing respects:
        - MilkOcean routing priority (0-3)
        - Bhu Mandala layer (BRAHMALOKA → BHURLOKA)
        - User-defined priority (0-100)
        - Varna classification

        Args:
            tasks: Dictionary of all tasks

        Returns:
            Next task to work on, or None if none available
        """
        # Check for in-progress tasks
        in_progress = BatchOperations.filter_by_status(tasks, TaskStatus.IN_PROGRESS)
        if in_progress:
            # Resume highest priority in-progress task (topology-aware)
            return max(in_progress, key=NextTaskGenerator._topology_aware_sort_key)

        # Check for pending tasks
        pending = BatchOperations.filter_by_status(tasks, TaskStatus.PENDING)
        if pending:
            # Get highest priority pending task (topology-aware)
            return max(pending, key=NextTaskGenerator._topology_aware_sort_key)

        # Check for blocked tasks
        blocked = BatchOperations.filter_by_status(tasks, TaskStatus.BLOCKED)
        if blocked:
            # Get highest priority blocked task (topology-aware)
            return max(blocked, key=NextTaskGenerator._topology_aware_sort_key)

        # No tasks available
        return None

    @staticmethod
    def get_next_tasks(tasks: Dict[str, Task], count: int = 5) -> List[Task]:
        """
        Get the next N tasks in topology-aware priority order.

        Args:
            tasks: Dictionary of all tasks
            count: Number of tasks to return

        Returns:
            List of next tasks, up to count (topology-sorted)
        """
        # Get all non-archived tasks
        candidates = [
            task for task in tasks.values()
            if task.status != TaskStatus.ARCHIVED
        ]

        # Sort by status priority, then by topology-aware key
        status_priority = {
            TaskStatus.IN_PROGRESS: 3,
            TaskStatus.PENDING: 2,
            TaskStatus.BLOCKED: 1,
            TaskStatus.COMPLETED: 0,
        }

        candidates.sort(
            key=lambda t: (
                status_priority.get(t.status, 0),
                NextTaskGenerator._topology_aware_sort_key(t)
            ),
            reverse=True
        )

        return candidates[:count]

    @staticmethod
    def get_critical_tasks(tasks: Dict[str, Task]) -> List[Task]:
        """
        Get all critical (high priority) tasks.

        Args:
            tasks: Dictionary of all tasks

        Returns:
            List of critical tasks (priority >= 80)
        """
        return BatchOperations.filter_by_priority(
            tasks,
            min_priority=80,
            max_priority=100
        )

    @staticmethod
    def suggest_next_action(tasks: Dict[str, Task]) -> str:
        """
        Suggest the next action based on task state.

        Args:
            tasks: Dictionary of all tasks

        Returns:
            Suggestion message
        """
        pending = len(BatchOperations.filter_by_status(tasks, TaskStatus.PENDING))
        in_progress = len(BatchOperations.filter_by_status(tasks, TaskStatus.IN_PROGRESS))
        blocked = len(BatchOperations.filter_by_status(tasks, TaskStatus.BLOCKED))

        if blocked > 0:
            return f"⚠️ {blocked} tasks are blocked. Unblock them to continue."

        if in_progress > 0:
            return f"▶️ Resume {in_progress} in-progress tasks."

        if pending > 0:
            return f"📋 Start work on {pending} pending tasks."

        return "✅ All tasks complete!"
