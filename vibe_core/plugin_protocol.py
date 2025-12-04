from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel


class KernelPlugin(ABC):
    """
    Base class for all Vibe Kernel Plugins.

    Plugins extend the kernel's functionality without modifying the core.
    They are the "Avatars" of the Vishnu Kernel.
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

    def on_task_completed(self, kernel: "RealVibeKernel", task_id: str, result: Any) -> None:
        """Called when a task completes successfully."""
        pass

    def on_task_failed(self, kernel: "RealVibeKernel", task_id: str, error: str) -> None:
        """Called when a task fails."""
        pass
