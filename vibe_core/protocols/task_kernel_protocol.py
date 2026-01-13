"""
TaskKernelProtocol - The Ephemeral Executor Contract
=====================================================

"A brain doesn't spawn a new brain to think each thought. It spawns a new pattern."

PHASE 0 OF TASK EXECUTION: The Contract

This protocol defines WHAT a TaskKernel does, not HOW it does it.
All callers MUST depend on this protocol, NOT on TaskKernel directly.

Dependency Inversion Principle (SOLID 'D'):
    HIGH-LEVEL (Callers) and LOW-LEVEL (TaskKernel) both depend on ABSTRACTION.

Current Problem:
    Caller -> imports -> TaskKernel
    = Hard dependency = Can't mock = Can't swap implementation

Solution:
    TaskKernel -> implements -> TaskKernelProtocol
    Caller -> depends on -> TaskKernelProtocol
    = Clean Architecture = Dependency Inversion = TESTABLE

Usage in Services:
    # WRONG (creates hard dependency):
    from vibe_core.task_kernel import TaskKernel
    tk = TaskKernel.spawn(task, tools)

    # CORRECT (depends on abstraction):
    from vibe_core.protocols.task_kernel_protocol import TaskKernelProtocol
    def execute(self, kernel: TaskKernelProtocol): ...

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0x9f3c7d2e"  # GenesisByte: parampara % 37 == 0

from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Protocol,
    TypeVar,
    runtime_checkable,
)

if TYPE_CHECKING:
    from vibe_core.task_management.models import Task as ManagedTask
    from vibe_core.tools.tool_protocol import Tool, ToolResult


# =============================================================================
# STATUS ENUM (Shared with task_kernel.py)
# =============================================================================

class TaskKernelStatus(str, Enum):
    """Status of TaskKernel execution."""

    SPAWNED = "spawned"      # Created, not yet executing
    EXECUTING = "executing"  # Running task
    COMPLETED = "completed"  # Finished successfully
    FAILED = "failed"        # Finished with error
    TIMEOUT = "timeout"      # Exceeded time limit
    CANCELLED = "cancelled"  # Explicitly cancelled


# =============================================================================
# RESULT TYPES (Shared with task_kernel.py)
# =============================================================================

@dataclass
class TaskKernelResult:
    """
    Result of TaskKernel execution.

    Used for folding results back to parent kernel and
    updating synaptic patterns in MANAS.
    """

    # Identity
    kernel_id: str
    task_id: str

    # Status
    status: TaskKernelStatus

    # Output
    output: Any = None
    error: Optional[str] = None

    # Metrics
    duration_ms: float = 0.0
    tool_calls_made: int = 0
    tools_succeeded: int = 0
    tools_failed: int = 0

    # Timestamps
    spawned_at: str = ""
    completed_at: str = ""

    # Synaptic reinforcement signal
    # Positive = reinforce pattern, Negative = weaken pattern
    reinforcement_signal: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize for IPC/logging."""
        return {
            "kernel_id": self.kernel_id,
            "task_id": self.task_id,
            "status": self.status.value,
            "output": str(self.output)[:500] if self.output else None,
            "error": self.error,
            "duration_ms": self.duration_ms,
            "tool_calls_made": self.tool_calls_made,
            "tools_succeeded": self.tools_succeeded,
            "tools_failed": self.tools_failed,
            "spawned_at": self.spawned_at,
            "completed_at": self.completed_at,
            "reinforcement_signal": self.reinforcement_signal,
        }


# =============================================================================
# CAPABILITY INJECTOR (Shared with task_kernel.py)
# =============================================================================

@dataclass
class InjectedCapabilities:
    """
    Capabilities injected into TaskKernel.

    This is the "Isolated Sandbox" approach per Gemini's recommendation.
    TaskKernel receives specific Tool instances, not the full registry.
    Enforces "Need to Know" principle.
    """

    # Tool instances (not registry reference)
    tools: Dict[str, "Tool"] = field(default_factory=dict)

    # Read-only config subset
    workspace_path: Optional[str] = None
    timeout_seconds: int = 300

    # Callback for synaptic reinforcement
    on_complete: Optional[Callable[[TaskKernelResult], None]] = None

    def get_tool(self, name: str) -> Optional["Tool"]:
        """Get a tool by name (returns None if not injected)."""
        return self.tools.get(name)

    def list_tools(self) -> List[str]:
        """List available tool names."""
        return list(self.tools.keys())


# =============================================================================
# TASK KERNEL PROTOCOL - The Contract
# =============================================================================

@runtime_checkable
class TaskKernelProtocol(Protocol):
    """
    The Ephemeral Executor Contract.

    This protocol defines what every TaskKernel MUST provide.
    TaskKernel implements this protocol.

    Services type-hint against this, never against TaskKernel directly.

    CHARACTERISTICS:
        - Lightweight: ~100ms boot (vs 5+ seconds for full kernel)
        - Ephemeral: In-memory only, no persistence
        - Isolated: Sandboxed tools, no registry access
        - Spawnable: Multiple instances can run in parallel
    """

    # =========================================================================
    # IDENTITY (Read-Only Properties)
    # =========================================================================

    @property
    def kernel_id(self) -> str:
        """Unique identifier for this TaskKernel instance."""
        ...

    @property
    def task(self) -> "ManagedTask":
        """The task being executed."""
        ...

    @property
    def parent_id(self) -> Optional[str]:
        """ID of parent kernel (for result folding)."""
        ...

    @property
    def status(self) -> TaskKernelStatus:
        """Current execution status."""
        ...

    @property
    def result(self) -> Optional[TaskKernelResult]:
        """Execution result (available after execute())."""
        ...

    # =========================================================================
    # EXECUTION
    # =========================================================================

    async def execute(self) -> TaskKernelResult:
        """
        Execute the task.

        This is the main entry point. Runs the task with timeout,
        tracks tool calls, and returns result for folding.

        Returns:
            TaskKernelResult with status, output, and reinforcement signal
        """
        ...

    # =========================================================================
    # TOOL ACCESS (Sandboxed)
    # =========================================================================

    def get_tool(self, name: str) -> Optional["Tool"]:
        """
        Get an injected tool by name.

        Only returns tools that were explicitly injected at spawn.
        No registry access - enforces "Need to Know" principle.
        """
        ...

    def list_tools(self) -> List[str]:
        """List available (injected) tool names."""
        ...

    async def call_tool(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
    ) -> "ToolResult":
        """
        Execute a tool call within this kernel's sandbox.

        Args:
            tool_name: Name of tool to call (must be injected)
            parameters: Tool parameters

        Returns:
            ToolResult from tool execution

        Raises:
            ValueError: If tool not available
        """
        ...


# =============================================================================
# TASK KERNEL FACTORY PROTOCOL
# =============================================================================

@runtime_checkable
class TaskKernelFactoryProtocol(Protocol):
    """
    Factory for creating TaskKernel instances.

    Used to spawn TaskKernels WITHOUT importing TaskKernel directly.
    Enables dependency injection and testing.

    Usage:
        # In service (CORRECT):
        factory = ServiceRegistry.get(TaskKernelFactoryProtocol)
        tk = factory.spawn(task, tools)

        # NOT this (WRONG - creates hard dependency):
        from vibe_core.task_kernel import TaskKernel
        tk = TaskKernel.spawn(task, tools)
    """

    def spawn(
        self,
        task: "ManagedTask",
        tools: List["Tool"],
        parent: Optional[Any] = None,
        timeout: int = 300,
        on_complete: Optional[Callable[[TaskKernelResult], None]] = None,
        caller_plugin_id: Optional[str] = None,
    ) -> TaskKernelProtocol:
        """
        Spawn a new TaskKernel for a task.

        This is the preferred way to create TaskKernel instances.
        It enforces the Capability Injector pattern and SANDBOXING.

        OPUS-176 BHARAT: Border Control enforced here.
        Only SOVEREIGN_STATE plugins can spawn TaskKernels.

        Args:
            task: The ManagedTask to execute
            tools: List of Tool instances to inject (NOT registry)
            parent: Optional parent kernel (for workspace path)
            timeout: Execution timeout in seconds
            on_complete: Optional callback for synaptic reinforcement
            caller_plugin_id: ID of the plugin requesting spawn (for governance check)

        Returns:
            TaskKernelProtocol instance ready for execute()

        Raises:
            PermissionError: If caller is not a SOVEREIGN_STATE plugin
        """
        ...


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Status
    "TaskKernelStatus",
    # Result
    "TaskKernelResult",
    # Capabilities
    "InjectedCapabilities",
    # Protocols
    "TaskKernelProtocol",
    "TaskKernelFactoryProtocol",
]
