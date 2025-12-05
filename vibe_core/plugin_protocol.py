from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from vibe_core import Task
    from vibe_core.kernel_impl import RealVibeKernel


class KernelPlugin(ABC):
    """
    Base class for all Vibe Kernel Plugins.

    Plugins extend the kernel's functionality without modifying the core.
    They are the "Avatars" of the Vishnu Kernel.

    FINAL HOOKS (Kernel will NEVER change after this):
    ═══════════════════════════════════════════════════
    LIFECYCLE:
    - on_boot: Kernel initialization
    - on_tick_pre/post: Every kernel tick
    - on_shutdown: Kernel shutdown

    AGENT LIFECYCLE:
    - on_agent_registered: New agent joins
    - on_agent_unregistered: Agent removed (Narasimha destruction)

    TASK LIFECYCLE:
    - on_task_submit: COSMIC GATE for task submission (Sarga cycle)
    - on_task_pre_assign: GOVERNANCE GATE for task assignment (Varna/Ashrama)
    - on_task_completed/failed: Task lifecycle

    CAPABILITY:
    - on_capability_check: CAPABILITY GATE for tool access (Protocol enforcement)

    TOOL EXECUTION:
    - on_tool_execute: TOOL GATE for execution (Rate limiting, Audit)
    - on_tool_executed: Post-execution hook (Logging, Metrics)
    ═══════════════════════════════════════════════════
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

    def on_agent_unregistered(self, kernel: "RealVibeKernel", agent_id: str) -> None:
        """
        Called when an agent is unregistered/destroyed.

        Use cases:
        - Cleanup governance state (Varna/Ashrama records)
        - Update trust scores
        - Log destruction event

        Args:
            kernel: The kernel instance
            agent_id: ID of the agent being removed
        """
        pass

    def on_capability_check(self, kernel: "RealVibeKernel", agent_id: str, capability: str) -> Optional[bool]:
        """
        CAPABILITY GATE: Called when capability access is checked.

        This is the PROTOCOL ENFORCEMENT hook - plugins can VETO capability access.
        This enables:
        - STEWARD Protocol attestation requirements
        - Trust-based capability gating
        - Rate limiting per capability
        - Delegation chain verification

        Return values:
            True  = Explicitly ALLOW (override other plugins)
            False = Explicitly DENY (VETO - blocks access)
            None  = No opinion (let other plugins and registry decide)

        Evaluation order:
        1. CapabilityRegistry.has_capability() must pass first
        2. All plugins are called
        3. If ANY plugin returns False → DENIED
        4. If ANY plugin returns True → ALLOWED (fast path)
        5. If all plugins return None → ALLOWED (default)

        Args:
            kernel: The kernel instance
            agent_id: Agent requesting the capability
            capability: The capability being checked (e.g., "write_file")

        Returns:
            True (allow), False (deny), or None (no opinion)
        """
        return None  # Default: no opinion

    def on_tool_execute(
        self,
        kernel: "RealVibeKernel",
        agent_id: str,
        tool_name: str,
        parameters: dict,
    ) -> Optional[bool]:
        """
        TOOL EXECUTION GATE: Called before every tool execution.

        This hook enables:
        - Audit trail for all tool calls
        - Rate limiting per tool
        - Tool-specific security checks
        - Usage tracking for billing/quotas

        Return values:
            True  = Explicitly ALLOW
            False = VETO (block execution)
            None  = No opinion (default - allow)

        Args:
            kernel: The kernel instance
            agent_id: Agent executing the tool
            tool_name: Name of the tool being called
            parameters: Tool parameters (read-only)

        Returns:
            True (allow), False (deny), or None (no opinion)
        """
        return None  # Default: no opinion

    def on_tool_executed(
        self,
        kernel: "RealVibeKernel",
        agent_id: str,
        tool_name: str,
        parameters: dict,
        result: Any,
        success: bool,
    ) -> None:
        """
        Called after tool execution completes (success or failure).

        This hook enables:
        - Audit logging
        - Metrics collection
        - Result modification (via wrappers, not mutation)
        - Error tracking

        Args:
            kernel: The kernel instance
            agent_id: Agent that executed the tool
            tool_name: Name of the tool
            parameters: Tool parameters used
            result: Tool result (output or error)
            success: Whether execution succeeded
        """
        pass
