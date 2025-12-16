"""
VISNU KERNEL - Plugin Protocol
==============================

The Kernel is EXACTLY 1008 lines of code (symbolic: Visnu's 1008 names).
Everything else is a Plugin.

This protocol defines the contract between Kernel and Plugins.
Safety features based on Senior Architecture Review:
- Dependencies (topological sort, not magic priority integers)
- Config Injection (no global get_config())
- Error Boundaries (plugins can't crash the kernel)
- State Isolation (plugins own their state)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Set

if TYPE_CHECKING:
    from vibe_core import Task
    from vibe_core.cli.monitors import SystemMonitor
    from vibe_core.kernel_impl import RealVibeKernel


class PluginError(Exception):
    """Base exception for plugin errors."""

    pass


class PluginResult(Enum):
    """Result of a plugin hook execution."""

    OK = "ok"  # Success
    ERROR = "error"  # Recoverable error (logged, continue)
    FATAL = "fatal"  # Unrecoverable (unload plugin)


class PulsePhase(Enum):
    """
    Execution phases for pulse cycle - ordered by dependency.

    OPUS-087 PRANA: Plugins declare their phase for deterministic ordering.
    Heartbeat (macro-cycle) executes plugins in phase order:
    SENSORS → COGNITION → ACTUATORS → CLEANUP

    This prevents race conditions where e.g. a reporter plugin
    tries to read data before a sensor has collected it.
    """
    SENSORS = 1    # Drishti - Collect data first
    COGNITION = 2  # Manas - Then think
    ACTUATORS = 3  # Karma - Then act
    CLEANUP = 4    # Shuddhi - Finally cleanup


@dataclass
class HookResult:
    """
    Result wrapper for plugin hooks.

    Plugins should return this instead of raising exceptions.
    The kernel uses this for error boundaries.
    """

    status: PluginResult = PluginResult.OK
    error_message: Optional[str] = None
    data: Any = None

    @classmethod
    def ok(cls, data: Any = None) -> "HookResult":
        return cls(status=PluginResult.OK, data=data)

    @classmethod
    def error(cls, message: str) -> "HookResult":
        return cls(status=PluginResult.ERROR, error_message=message)

    @classmethod
    def fatal(cls, message: str) -> "HookResult":
        return cls(status=PluginResult.FATAL, error_message=message)


class KernelPlugin(ABC):
    """
    Base class for all Visnu Kernel Plugins.

    Plugins extend the kernel's functionality without modifying the core.
    They are the "Avatars" of the Visnu Kernel (1008 LOC).

    SAFETY FEATURES (Senior Review):
    ================================
    1. DEPENDENCIES: Explicit, not magic priority integers
       - Use `dependencies` property to declare what you need
       - Kernel boots plugins in topological order (DAG)

    2. CONFIG INJECTION: No global get_config()
       - on_boot receives plugin-specific config
       - Plugins only see their section, not everything

    3. ERROR BOUNDARIES: Plugins can't crash the kernel
       - Hooks return HookResult, not exceptions
       - Kernel has supervisor/circuit breaker

    4. STATE ISOLATION: Plugins own their state
       - No writing to kernel attributes
       - Communication via APIs and Events only

    HOOK CONTRACT:
    ==============
    LIFECYCLE:
    - on_boot: Kernel initialization (receives config)
    - on_tick_pre/post: Every kernel tick
    - on_shutdown: Kernel shutdown

    AGENT LIFECYCLE:
    - on_agent_pre_register: GATE - can veto registration
    - on_agent_registered: New agent joins
    - on_agent_unregistered: Agent removed

    TASK LIFECYCLE:
    - on_task_submit: COSMIC GATE for task submission
    - on_task_pre_assign: GOVERNANCE GATE for task assignment
    - on_task_completed/failed: Task lifecycle

    CAPABILITY:
    - on_capability_check: CAPABILITY GATE for tool access

    TOOL EXECUTION:
    - on_tool_execute: TOOL GATE for execution
    - on_tool_executed: Post-execution hook
    """

    # Plugin-owned state (not shared with kernel)
    _state: Dict[str, Any] = field(default_factory=dict)

    @property
    @abstractmethod
    def plugin_id(self) -> str:
        """Unique identifier for this plugin."""
        pass

    @property
    def dependencies(self) -> Set[str]:
        """
        Plugins this one depends on.

        The kernel boots plugins in topological order.
        If PluginA depends on PluginB, B boots first.

        Example:
            @property
            def dependencies(self) -> Set[str]:
                return {"capability", "governance"}

        Returns:
            Set of plugin_ids that must boot before this one
        """
        return set()

    @property
    def priority(self) -> int:
        """
        DEPRECATED: Use dependencies instead.

        Kept for backward compatibility. Only used as tiebreaker
        when no dependency relationship exists.

        Standard Priorities:
        - 0-99: System/Core Plugins
        - 100-199: Standard Features
        - 200+: Optional/User Plugins
        """
        return 100

    def on_boot(
        self,
        kernel: "RealVibeKernel",
        config: Optional[Dict[str, Any]] = None,
    ) -> HookResult:
        """
        Called once when the kernel initializes.

        CONFIG INJECTION: The kernel passes only the plugin's config section.
        Don't call get_config() globally - use the injected config.

        Args:
            kernel: The kernel instance (for API registration)
            config: Plugin-specific config from config/<plugin_id>.yaml

        Returns:
            HookResult indicating success/failure
        """
        return HookResult.ok()

    def on_tick_pre(self, kernel: "RealVibeKernel") -> HookResult:
        """
        Called at the start of every kernel tick.

        PERFORMANCE: Keep this FAST. No DB queries, no I/O.
        Use for input processing (e.g., reading SETTINGS.md).

        Returns:
            HookResult indicating success/failure
        """
        return HookResult.ok()

    def on_tick_post(self, kernel: "RealVibeKernel") -> HookResult:
        """
        Called at the end of every kernel tick.

        PERFORMANCE: Keep this FAST. No DB queries, no I/O.
        Use for output generation (e.g., updating status).

        Returns:
            HookResult indicating success/failure
        """
        return HookResult.ok()

    def on_shutdown(self, kernel: "RealVibeKernel") -> HookResult:
        """
        Called when the kernel shuts down.

        Clean up plugin state, close connections, etc.

        Returns:
            HookResult indicating success/failure
        """
        return HookResult.ok()

    # =========================================================================
    # OPUS-087 PRANA: PULSE LIFECYCLE (Macro-Cycle / Heartbeat)
    # =========================================================================

    @property
    def pulse_phase(self) -> PulsePhase:
        """
        Declare execution phase for on_pulse ordering.

        Phases execute in order: SENSORS → COGNITION → ACTUATORS → CLEANUP

        Override to change default (ACTUATORS).

        Example:
            @property
            def pulse_phase(self) -> PulsePhase:
                return PulsePhase.SENSORS  # Runs first in pulse cycle

        Returns:
            PulsePhase enum value
        """
        return PulsePhase.ACTUATORS

    def on_pulse(
        self,
        kernel: "RealVibeKernel",
        transaction: Any,  # PulseTransaction from prana_orchestrator
    ) -> HookResult:
        """
        Called during heartbeat pulse (macro-cycle).

        OPUS-087 PRANA: This runs OUT-OF-PROCESS (GitHub Actions headless mode).
        Do NOT assume kernel is fully initialized.

        IMPORTANT: Do NOT commit to Git directly! Register mutations instead.

        Args:
            kernel: The kernel instance (may be minimal in headless mode)
            transaction: PulseTransaction - register mutations here

        Returns:
            HookResult with optional data for reporting

        Example:
            def on_pulse(self, kernel, transaction) -> HookResult:
                # Collect data
                karma = self.calculate_karma_decay()

                # Register mutation (don't apply directly!)
                transaction.register(StateMutation(
                    plugin_id=self.plugin_id,
                    action="decay_karma",
                    target="karma.json",
                    payload={"agent_id": "envoy", "delta": karma}
                ))

                return HookResult.ok(data={"decayed": karma})
        """
        return HookResult.ok()

    def on_agent_pre_register(self, kernel: "RealVibeKernel", agent: Any) -> bool:
        """
        AGENT REGISTRATION GATE: Called BEFORE agent registration.

        Return False to VETO registration, True to allow.

        Use cases:
        - Constitutional Oath verification (STEWARD Protocol)
        - Trust level checks
        - Capability validation

        Args:
            kernel: The kernel instance
            agent: The agent attempting to register

        Returns:
            True to allow registration, False to VETO
        """
        return True

    def on_agent_registered(self, kernel: "RealVibeKernel", agent_id: str) -> None:
        """Called when a new agent is registered."""
        pass

    def on_agent_unregistered(self, kernel: "RealVibeKernel", agent_id: str) -> None:
        """
        Called when an agent is unregistered/destroyed.

        Use cases:
        - Cleanup governance state (Varna/Ashrama records)
        - Update trust scores
        - Log destruction event
        """
        pass

    def on_task_submit(self, kernel: "RealVibeKernel", task: "Task") -> bool:
        """
        COSMIC GATE: Called BEFORE a task enters the scheduler queue.

        Return False to reject the task, True to allow.

        Use cases:
        - Sarga Cycle (NIGHT_OF_BRAHMA blocks non-maintenance tasks)
        - Global rate limiting
        - System-wide task filtering

        Returns:
            True to allow task into queue, False to reject
        """
        return True

    def on_task_pre_assign(
        self,
        kernel: "RealVibeKernel",
        agent_id: str,
        task: "Task",
    ) -> bool:
        """
        GOVERNANCE GATE: Called BEFORE a task is assigned to an agent.

        Return False to block the task, True to allow.

        Use cases:
        - Paused agents (return False)
        - Lifecycle restrictions (BRAHMACHARI can't write)
        - Rate limiting
        - Permission checks

        Returns:
            True to allow task assignment, False to veto/block
        """
        return True

    def on_task_completed(
        self,
        kernel: "RealVibeKernel",
        task_id: str,
        result: Any,
    ) -> None:
        """Called when a task completes successfully."""
        pass

    def on_task_failed(
        self,
        kernel: "RealVibeKernel",
        task_id: str,
        error: str,
    ) -> None:
        """Called when a task fails."""
        pass

    def on_capability_check(
        self,
        kernel: "RealVibeKernel",
        agent_id: str,
        capability: str,
    ) -> Optional[bool]:
        """
        CAPABILITY GATE: Called when capability access is checked.

        Return values:
            True  = Explicitly ALLOW (override other plugins)
            False = Explicitly DENY (VETO - blocks access)
            None  = No opinion (let other plugins decide)

        Evaluation order:
        1. CapabilityRegistry.has_capability() must pass first
        2. All plugins are called
        3. If ANY plugin returns False → DENIED
        4. If ANY plugin returns True → ALLOWED (fast path)
        5. If all plugins return None → ALLOWED (default)
        """
        return None

    def on_tool_execute(
        self,
        kernel: "RealVibeKernel",
        agent_id: str,
        tool_name: str,
        parameters: dict,
    ) -> Optional[bool]:
        """
        TOOL EXECUTION GATE: Called before every tool execution.

        Return values:
            True  = Explicitly ALLOW
            False = VETO (block execution)
            None  = No opinion (default - allow)
        """
        return None

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

        Use cases:
        - Audit logging
        - Metrics collection
        - Error tracking
        """
        pass

    # =========================================================================
    # INTROSPECTION PROTOCOL (Glass Box)
    # =========================================================================

    def get_monitors(self) -> List["SystemMonitor"]:
        """
        Return system monitors exposed by this plugin.

        The CLI discovers these to enable `steward observe` commands.
        Each monitor provides a view into the plugin's internal state.

        Returns:
            List of SystemMonitor instances
        """
        return []

    # =========================================================================
    # PLUGIN API REGISTRATION
    # =========================================================================

    def get_api(self) -> Optional[Any]:
        """
        Return an API object for other plugins to use.

        The kernel registers this as: kernel.api(plugin_id)

        Example:
            class GovernancePlugin(KernelPlugin):
                def get_api(self):
                    return GovernanceAPI(self)

            # Usage by other plugins:
            governance = kernel.api("governance")
            varna = governance.get_varna(agent_id)

        Returns:
            API object or None if no API exposed
        """
        return None
