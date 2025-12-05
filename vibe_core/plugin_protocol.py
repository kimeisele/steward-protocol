from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from vibe_core import Task
    from vibe_core.kernel_impl import RealVibeKernel


class KernelPlugin(ABC):
    """
    Base class for all Vibe Kernel Plugins.

    Plugins extend the kernel's functionality without modifying the core.
    They are the "Avatars" of the Vishnu Kernel.

    FINAL HOOKS (Kernel will NEVER change after this):
    - on_boot: Kernel initialization
    - on_tick_pre/post: Every kernel tick
    - on_shutdown: Kernel shutdown
    - on_agent_registered: New agent joins
    - on_task_submit: COSMIC GATE for task submission (Sarga cycle)
    - on_task_pre_assign: GOVERNANCE GATE for task assignment (Varna/Ashrama)
    - on_task_completed/failed: Task lifecycle
    """

    @property
    @abstractmethod
    def plugin_id(self) -> str:
        """Unique identifier for this plugin."""
        pass

    @property
    def priority(self) -> int:
        """
        Execution order (lower = earlier).

        Standard Priorities:
        - 0-99: System/Core Plugins (e.g., UI Sync)
        - 100-199: Standard Features
        - 200+: Optional/User Plugins
        """
        return 100

    def on_boot(self, kernel: "RealVibeKernel") -> None:
        """Called once when the kernel initializes."""
        pass

    def on_tick_pre(self, kernel: "RealVibeKernel") -> None:
        """
        Called at the start of every kernel tick.
        Use this for input processing (e.g., reading SETTINGS.md).
        """
        pass

    def on_tick_post(self, kernel: "RealVibeKernel") -> None:
        """
        Called at the end of every kernel tick.
        Use this for output generation (e.g., updating status).
        """
        pass

    def on_shutdown(self, kernel: "RealVibeKernel") -> None:
        """Called when the kernel shuts down."""
        pass

    def on_agent_registered(self, kernel: "RealVibeKernel", agent_id: str) -> None:
        """Called when a new agent is registered."""
        pass

    def on_task_submit(self, kernel: "RealVibeKernel", task: "Task") -> bool:
        """
        Called BEFORE a task enters the scheduler queue.

        This is the COSMIC GATE - plugins can VETO task submission.
        Return False to reject the task, True to allow.

        Use cases:
        - Sarga Cycle (NIGHT_OF_BRAHMA blocks non-maintenance tasks)
        - Global rate limiting
        - System-wide task filtering

        Args:
            kernel: The kernel instance
            task: The task being submitted

        Returns:
            True to allow task into queue, False to reject

        Raises:
            ValueError: If rejecting, plugin should raise with reason
        """
        return True  # Default: allow all tasks

    def on_task_pre_assign(self, kernel: "RealVibeKernel", agent_id: str, task: "Task") -> bool:
        """
        Called BEFORE a task is assigned to an agent.

        This is the GOVERNANCE HOOK - plugins can VETO task assignment.
        Return False to block the task, True to allow.

        Use cases:
        - Paused agents (return False)
        - Lifecycle restrictions (BRAHMACHARI can't write)
        - Rate limiting
        - Permission checks

        Args:
            kernel: The kernel instance
            agent_id: Agent that would receive the task
            task: The task to be assigned

        Returns:
            True to allow task assignment, False to veto/block
        """
        return True  # Default: allow all tasks

    def on_task_completed(self, kernel: "RealVibeKernel", task_id: str, result: Any) -> None:
        """Called when a task completes successfully."""
        pass

    def on_task_failed(self, kernel: "RealVibeKernel", task_id: str, error: str) -> None:
        """Called when a task fails."""
        pass
