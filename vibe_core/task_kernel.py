"""
TASK KERNEL - Lightweight Ephemeral Execution Context (OPUS-175)
================================================================

"A brain doesn't spawn a new brain to think each thought. It spawns a new pattern."

TaskKernel is a minimal execution context for single-task execution.
Unlike RealVibeKernel (5+ second boot), TaskKernel boots in ~100ms.

Key Design Decisions (Per Gemini Review):
1. Option B: Isolated Sandbox - No shared ToolRegistry
2. Capability Injector - Receives Tool instances, not registry
3. One Kernel per Intent - Atomic, not batched
4. Synaptic Reinforcement - Success/failure updates MANAS patterns

Architecture:
    Parent Kernel                 TaskKernel
         │                             │
         ├── spawn(task, tools) ──────►│
         │                             │
         │    ◄── execute() ───────────│
         │                             │
         ├── fold_result(result) ◄─────│
         │                             │
         ▼                             ▼
    Update Synapses              Process exits

Boot Comparison:
    RealVibeKernel: 5+ seconds (plugins, prakriti, lineage, gateway)
    TaskKernel: ~100ms (tools only, in-memory ledger)

Usage:
    from vibe_core.task_kernel import TaskKernel

    # Spawn from parent kernel
    task_kernel = TaskKernel.spawn(
        task=managed_task,
        tools=[read_file_tool, write_file_tool],
        parent=parent_kernel,
        timeout=300,
    )

    # Execute (async)
    result = await task_kernel.execute()

    # Fold result back (includes synaptic reinforcement)
    parent_kernel.fold_task_result(result)
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel
    from vibe_core.task_management.models import Task as ManagedTask
    from vibe_core.tools.tool_protocol import Tool, ToolCall, ToolResult

logger = logging.getLogger("TASK_KERNEL")


# =============================================================================
# RESULT TYPES
# =============================================================================


class TaskKernelStatus(str, Enum):
    """Status of TaskKernel execution."""

    SPAWNED = "spawned"  # Created, not yet executing
    EXECUTING = "executing"  # Running task
    COMPLETED = "completed"  # Finished successfully
    FAILED = "failed"  # Finished with error
    TIMEOUT = "timeout"  # Exceeded time limit
    CANCELLED = "cancelled"  # Explicitly cancelled


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
    execution_time_ms: float = 0.0
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
            "execution_time_ms": self.execution_time_ms,
            "tool_calls_made": self.tool_calls_made,
            "tools_succeeded": self.tools_succeeded,
            "tools_failed": self.tools_failed,
            "spawned_at": self.spawned_at,
            "completed_at": self.completed_at,
            "reinforcement_signal": self.reinforcement_signal,
        }


# =============================================================================
# CAPABILITY INJECTOR
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
# TASK KERNEL
# =============================================================================


class TaskKernel:
    """
    Lightweight Ephemeral Execution Kernel.

    Boot time: ~100ms (vs 5+ seconds for RealVibeKernel)
    Memory: ~50MB (vs ~500MB for full kernel)
    Plugins: ZERO (no plugin loading)
    State: In-memory only (no Prakriti persistence)
    """

    def __init__(
        self,
        task: "ManagedTask",
        capabilities: InjectedCapabilities,
        parent_id: Optional[str] = None,
    ):
        """
        Initialize TaskKernel.

        Args:
            task: The ManagedTask to execute
            capabilities: Injected tools and config (Capability Injector pattern)
            parent_id: ID of parent kernel (for result folding)
        """
        # Identity
        self.kernel_id = f"tk_{uuid.uuid4().hex[:8]}"
        self.task = task
        self.parent_id = parent_id

        # Capabilities (no registry access!)
        self._capabilities = capabilities
        self._tools = capabilities.tools

        # In-memory ledger (no persistence)
        self._events: List[Dict[str, Any]] = []

        # Execution state
        self._status = TaskKernelStatus.SPAWNED
        self._result: Optional[TaskKernelResult] = None
        self._tool_calls_made = 0
        self._tools_succeeded = 0
        self._tools_failed = 0

        # Timestamps
        self._spawned_at = datetime.utcnow().isoformat()
        self._started_at: Optional[float] = None
        self._completed_at: Optional[str] = None

        logger.info(f"⚡ TaskKernel spawned: {self.kernel_id} (task={task.id[:8]}, tools={len(self._tools)})")

    # =========================================================================
    # STATIC FACTORY
    # =========================================================================

    @staticmethod
    def spawn(
        task: "ManagedTask",
        tools: List["Tool"],
        parent: Optional["RealVibeKernel"] = None,
        timeout: int = 300,
        on_complete: Optional[Callable[[TaskKernelResult], None]] = None,
    ) -> "TaskKernel":
        """
        Spawn a new TaskKernel for a task.

        This is the preferred way to create TaskKernel instances.
        It enforces the Capability Injector pattern.

        Args:
            task: The ManagedTask to execute
            tools: List of Tool instances to inject (NOT registry)
            parent: Optional parent kernel (for workspace path)
            timeout: Execution timeout in seconds
            on_complete: Optional callback for synaptic reinforcement

        Returns:
            TaskKernel instance ready for execute()

        Example:
            kernel = TaskKernel.spawn(
                task=my_task,
                tools=[read_file_tool, write_file_tool],
                parent=parent_kernel,
                timeout=300,
            )
            result = await kernel.execute()
        """
        # Build capabilities from tools list
        tools_dict = {tool.name: tool for tool in tools}

        # Extract workspace from parent if available
        workspace = None
        parent_id = None
        if parent:
            parent_id = str(id(parent))
            if hasattr(parent, "config") and parent.config:
                try:
                    workspace = str(parent.config.paths.workspace)
                except Exception:
                    pass

        capabilities = InjectedCapabilities(
            tools=tools_dict,
            workspace_path=workspace,
            timeout_seconds=timeout,
            on_complete=on_complete,
        )

        return TaskKernel(task=task, capabilities=capabilities, parent_id=parent_id)

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
        self._status = TaskKernelStatus.EXECUTING
        self._started_at = time.time()

        self._record_event("TASK_START", {"task_id": self.task.id})

        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                self._execute_task(),
                timeout=self._capabilities.timeout_seconds,
            )

            self._status = TaskKernelStatus.COMPLETED
            self._record_event("TASK_COMPLETE", {"output": str(result)[:200]})

            # Build result
            self._result = self._build_result(
                status=TaskKernelStatus.COMPLETED,
                output=result,
            )

        except asyncio.TimeoutError:
            self._status = TaskKernelStatus.TIMEOUT
            error_msg = f"Task exceeded timeout ({self._capabilities.timeout_seconds}s)"
            self._record_event("TASK_TIMEOUT", {"error": error_msg})

            self._result = self._build_result(
                status=TaskKernelStatus.TIMEOUT,
                error=error_msg,
            )

        except asyncio.CancelledError:
            self._status = TaskKernelStatus.CANCELLED
            self._record_event("TASK_CANCELLED", {})

            self._result = self._build_result(
                status=TaskKernelStatus.CANCELLED,
                error="Task was cancelled",
            )

        except Exception as e:
            self._status = TaskKernelStatus.FAILED
            error_msg = str(e)
            self._record_event("TASK_FAILED", {"error": error_msg})

            self._result = self._build_result(
                status=TaskKernelStatus.FAILED,
                error=error_msg,
            )

        # Invoke synaptic reinforcement callback if provided
        if self._capabilities.on_complete and self._result:
            try:
                self._capabilities.on_complete(self._result)
            except Exception as e:
                logger.warning(f"Synaptic callback failed: {e}")

        return self._result

    async def _execute_task(self) -> Any:
        """
        Execute the task logic.

        This is where we interpret the ManagedTask and use injected tools.
        Override in subclasses for specialized execution patterns.

        Returns:
            Task output (varies by task type)
        """
        # Default implementation: Check for tool-based execution
        # ManagedTask metadata may contain tool_call spec
        metadata = self.task.metadata or {}

        if "tool_call" in metadata:
            # Execute as tool call
            tool_spec = metadata["tool_call"]
            return await self._execute_tool_call(
                tool_name=tool_spec.get("tool"),
                parameters=tool_spec.get("parameters", {}),
            )

        if "action" in metadata:
            # Execute as action (simplified tool call)
            return await self._execute_action(
                action=metadata["action"],
                context=metadata.get("context", {}),
            )

        # Fallback: Return task description as "acknowledged"
        return {
            "acknowledged": True,
            "task_id": self.task.id,
            "title": self.task.title,
            "description": self.task.description,
        }

    async def _execute_tool_call(
        self,
        tool_name: str,
        parameters: Dict[str, Any],
    ) -> "ToolResult":
        """
        Execute a tool call.

        Args:
            tool_name: Name of tool to call
            parameters: Tool parameters

        Returns:
            ToolResult from tool execution

        Raises:
            ValueError: If tool not available
        """
        self._tool_calls_made += 1

        # Check if tool is injected
        tool = self._capabilities.get_tool(tool_name)
        if not tool:
            available = self._capabilities.list_tools()
            self._tools_failed += 1
            raise ValueError(f"Tool '{tool_name}' not injected. Available tools: {available}")

        # Validate parameters
        try:
            tool.validate(parameters)
        except (ValueError, TypeError) as e:
            self._tools_failed += 1
            from vibe_core.tools.tool_protocol import ToolResult

            return ToolResult(success=False, error=f"Validation failed: {e}")

        # Execute tool
        self._record_event("TOOL_CALL", {"tool": tool_name, "params": parameters})

        result = tool.execute(parameters)

        if result.success:
            self._tools_succeeded += 1
            self._record_event("TOOL_SUCCESS", {"tool": tool_name})
        else:
            self._tools_failed += 1
            self._record_event("TOOL_FAILED", {"tool": tool_name, "error": result.error})

        return result

    async def _execute_action(
        self,
        action: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute an action (high-level intent).

        This maps actions to tool calls based on action type.

        Args:
            action: Action name (e.g., "read", "write", "analyze")
            context: Action context (e.g., {"path": "/tmp/file.txt"})

        Returns:
            Action result
        """
        # Map common actions to tools
        action_mapping = {
            "read": ("read_file", ["path"]),
            "write": ("write_file", ["path", "content"]),
            "list": ("list_directory", ["path"]),
            "search": ("search_file", ["path", "pattern"]),
        }

        if action in action_mapping:
            tool_name, param_keys = action_mapping[action]
            parameters = {k: context.get(k) for k in param_keys if k in context}

            result = await self._execute_tool_call(tool_name, parameters)
            return {
                "action": action,
                "success": result.success,
                "output": result.output,
                "error": result.error,
            }

        # Unknown action - return as acknowledged
        return {
            "action": action,
            "acknowledged": True,
            "context": context,
        }

    # =========================================================================
    # RESULT BUILDING
    # =========================================================================

    def _build_result(
        self,
        status: TaskKernelStatus,
        output: Any = None,
        error: Optional[str] = None,
    ) -> TaskKernelResult:
        """
        Build TaskKernelResult with reinforcement signal.

        Reinforcement signal calculation:
        - Success with high tool success rate: +1.0
        - Success with some tool failures: +0.5
        - Timeout: -0.3 (partial punishment)
        - Failure: -1.0 (full punishment)
        - Cancelled: 0.0 (neutral)
        """
        self._completed_at = datetime.utcnow().isoformat()

        # Calculate execution time
        execution_time_ms = 0.0
        if self._started_at:
            execution_time_ms = (time.time() - self._started_at) * 1000

        # Calculate reinforcement signal
        reinforcement = self._calculate_reinforcement(status)

        return TaskKernelResult(
            kernel_id=self.kernel_id,
            task_id=self.task.id,
            status=status,
            output=output,
            error=error,
            execution_time_ms=execution_time_ms,
            tool_calls_made=self._tool_calls_made,
            tools_succeeded=self._tools_succeeded,
            tools_failed=self._tools_failed,
            spawned_at=self._spawned_at,
            completed_at=self._completed_at,
            reinforcement_signal=reinforcement,
        )

    def _calculate_reinforcement(self, status: TaskKernelStatus) -> float:
        """
        Calculate synaptic reinforcement signal.

        This signal is used by MANAS to update pattern weights:
        - Positive: Reinforce the pattern that led to this task
        - Negative: Weaken the pattern

        Returns:
            Float in range [-1.0, 1.0]
        """
        if status == TaskKernelStatus.COMPLETED:
            # Success - calculate based on tool success rate
            if self._tool_calls_made == 0:
                return 0.8  # No tools used, still successful

            success_rate = self._tools_succeeded / self._tool_calls_made
            return 0.5 + (0.5 * success_rate)  # Range: 0.5 to 1.0

        elif status == TaskKernelStatus.TIMEOUT:
            # Timeout - partial punishment
            return -0.3

        elif status == TaskKernelStatus.FAILED:
            # Failure - full punishment
            return -1.0

        elif status == TaskKernelStatus.CANCELLED:
            # Cancelled - neutral (external decision)
            return 0.0

        else:
            # Unknown - neutral
            return 0.0

    # =========================================================================
    # LEDGER (In-Memory Only)
    # =========================================================================

    def _record_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """
        Record event to in-memory ledger.

        Note: This is NOT persisted. For audit, results are folded
        back to parent kernel's ledger.
        """
        event = {
            "kernel_id": self.kernel_id,
            "task_id": self.task.id,
            "event_type": event_type,
            "details": details,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._events.append(event)
        logger.debug(f"[{self.kernel_id}] {event_type}: {details}")

    def get_events(self) -> List[Dict[str, Any]]:
        """Get all recorded events (for debugging/auditing)."""
        return self._events.copy()

    # =========================================================================
    # STATUS
    # =========================================================================

    @property
    def status(self) -> TaskKernelStatus:
        """Get current status."""
        return self._status

    @property
    def result(self) -> Optional[TaskKernelResult]:
        """Get result (None if not yet completed)."""
        return self._result

    def get_status(self) -> Dict[str, Any]:
        """Get full status for monitoring."""
        return {
            "kernel_id": self.kernel_id,
            "task_id": self.task.id,
            "status": self._status.value,
            "parent_id": self.parent_id,
            "tools_available": list(self._tools.keys()),
            "tool_calls_made": self._tool_calls_made,
            "spawned_at": self._spawned_at,
            "completed_at": self._completed_at,
        }


# =============================================================================
# PARENT KERNEL INTEGRATION
# =============================================================================


def fold_result_to_parent(
    parent: "RealVibeKernel",
    result: TaskKernelResult,
) -> Dict[str, Any]:
    """
    Fold TaskKernel result back to parent kernel.

    This is called after TaskKernel completes to:
    1. Record result in parent's ledger
    2. Trigger synaptic reinforcement in MANAS
    3. Update task status in TaskManager

    Args:
        parent: The parent RealVibeKernel
        result: TaskKernelResult from TaskKernel.execute()

    Returns:
        Dict with fold status and actions taken
    """
    actions = []

    # 1. Record in parent's ledger
    if hasattr(parent, "_ledger"):
        parent._ledger.record_event(
            event_type="TASK_KERNEL_RESULT",
            agent_id="TASK_KERNEL",
            details=result.to_dict(),
        )
        actions.append("ledger_recorded")

    # 2. Trigger synaptic reinforcement in MANAS (if available)
    if hasattr(parent, "_plugins"):
        for plugin in parent._plugins:
            if hasattr(plugin, "on_task_kernel_result"):
                try:
                    plugin.on_task_kernel_result(parent, result)
                    actions.append(f"plugin_{plugin.plugin_id}_notified")
                except Exception as e:
                    logger.warning(f"Plugin {plugin.plugin_id} failed on result: {e}")

    # 3. Log completion
    logger.info(
        f"✅ TaskKernel {result.kernel_id} folded to parent "
        f"(status={result.status.value}, reinforcement={result.reinforcement_signal:.2f})"
    )

    return {
        "folded": True,
        "kernel_id": result.kernel_id,
        "task_id": result.task_id,
        "actions": actions,
    }


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "TaskKernel",
    "TaskKernelResult",
    "TaskKernelStatus",
    "InjectedCapabilities",
    "fold_result_to_parent",
]
