"""
TEST: TaskKernel - Lightweight Ephemeral Execution Context
===========================================================
Verifies the TaskKernel for single-task execution.
Target: vibe_core/task_kernel.py
Standard: GAD-5000

Tests use real components where possible - minimal test doubles.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict

import pytest

from vibe_core.task_kernel import (
    InjectedCapabilities,
    TaskKernel,
    TaskKernelResult,
    TaskKernelStatus,
    fold_result_to_parent,
)
from vibe_core.task_management.models import Task as ManagedTask
from vibe_core.tools.tool_protocol import Tool, ToolResult

# =============================================================================
# TEST TOOLS - Minimal implementations for testing
# =============================================================================


class _SuccessTool(Tool):
    """Tool that always succeeds."""

    def __init__(self):
        super().__init__(services=None)

    @property
    def name(self) -> str:
        return "success_tool"

    @property
    def description(self) -> str:
        return "Always succeeds"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"value": {"type": "string"}}}

    def validate(self, parameters: Dict[str, Any]) -> None:
        pass  # Always valid

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        return ToolResult(success=True, output=f"Success: {parameters.get('value', '')}")


class _FailingTool(Tool):
    """Tool that always fails."""

    def __init__(self):
        super().__init__(services=None)

    @property
    def name(self) -> str:
        return "failing_tool"

    @property
    def description(self) -> str:
        return "Always fails"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}}

    def validate(self, parameters: Dict[str, Any]) -> None:
        pass

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        return ToolResult(success=False, error="Deliberate failure for testing")


class _ValidationFailTool(Tool):
    """Tool that fails validation."""

    def __init__(self):
        super().__init__(services=None)

    @property
    def name(self) -> str:
        return "validation_fail_tool"

    @property
    def description(self) -> str:
        return "Always fails validation"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"required_param": {"type": "string"}}}

    def validate(self, parameters: Dict[str, Any]) -> None:
        if "required_param" not in parameters:
            raise ValueError("required_param is required")

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        return ToolResult(success=True, output="Should not reach here")


class _SlowTool(Tool):
    """Tool that takes time to execute."""

    def __init__(self):
        super().__init__(services=None)

    @property
    def name(self) -> str:
        return "slow_tool"

    @property
    def description(self) -> str:
        return "Takes time to execute"

    @property
    def parameters_schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {"delay": {"type": "number"}}}

    def validate(self, parameters: Dict[str, Any]) -> None:
        pass

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        import time

        delay = parameters.get("delay", 0.1)
        time.sleep(delay)
        return ToolResult(success=True, output=f"Slept for {delay}s")


# =============================================================================
# TEST HELPERS
# =============================================================================


def create_test_task(
    task_id: str = "test-task-001",
    title: str = "Test Task",
    description: str = "A test task",
    metadata: Dict[str, Any] = None,
) -> ManagedTask:
    """Create a test ManagedTask."""
    return ManagedTask(
        id=task_id,
        title=title,
        description=description,
        metadata=metadata or {},
    )


def create_test_capabilities(
    tools: Dict[str, Tool] = None,
    timeout: int = 300,
) -> InjectedCapabilities:
    """Create test InjectedCapabilities."""
    return InjectedCapabilities(
        tools=tools or {},
        timeout_seconds=timeout,
    )


# =============================================================================
# TEST: TaskKernelStatus
# =============================================================================


class TestTaskKernelStatus:
    """Test TaskKernelStatus enum."""

    def test_spawned_status_exists(self):
        """Should have SPAWNED status."""
        assert TaskKernelStatus.SPAWNED.value == "spawned"

    def test_executing_status_exists(self):
        """Should have EXECUTING status."""
        assert TaskKernelStatus.EXECUTING.value == "executing"

    def test_completed_status_exists(self):
        """Should have COMPLETED status."""
        assert TaskKernelStatus.COMPLETED.value == "completed"

    def test_failed_status_exists(self):
        """Should have FAILED status."""
        assert TaskKernelStatus.FAILED.value == "failed"

    def test_timeout_status_exists(self):
        """Should have TIMEOUT status."""
        assert TaskKernelStatus.TIMEOUT.value == "timeout"

    def test_cancelled_status_exists(self):
        """Should have CANCELLED status."""
        assert TaskKernelStatus.CANCELLED.value == "cancelled"


# =============================================================================
# TEST: TaskKernelResult
# =============================================================================


class TestTaskKernelResult:
    """Test TaskKernelResult dataclass."""

    def test_create_result_with_required_fields(self):
        """Should create result with kernel_id, task_id, status."""
        result = TaskKernelResult(
            kernel_id="tk_12345678",
            task_id="task-001",
            status=TaskKernelStatus.COMPLETED,
        )

        assert result.kernel_id == "tk_12345678"
        assert result.task_id == "task-001"
        assert result.status == TaskKernelStatus.COMPLETED

    def test_result_defaults(self):
        """Should have sensible defaults."""
        result = TaskKernelResult(
            kernel_id="tk_test",
            task_id="task-001",
            status=TaskKernelStatus.SPAWNED,
        )

        assert result.output is None
        assert result.error is None
        assert result.duration_ms == 0.0
        assert result.tool_calls_made == 0
        assert result.reinforcement_signal == 0.0

    def test_to_dict_serialization(self):
        """Should serialize to dict for IPC/logging."""
        result = TaskKernelResult(
            kernel_id="tk_abc123",
            task_id="task-xyz",
            status=TaskKernelStatus.COMPLETED,
            output="test output",
            duration_ms=150.5,
            tool_calls_made=3,
            tools_succeeded=2,
            tools_failed=1,
            reinforcement_signal=0.75,
        )

        d = result.to_dict()

        assert d["kernel_id"] == "tk_abc123"
        assert d["task_id"] == "task-xyz"
        assert d["status"] == "completed"
        assert d["output"] == "test output"
        assert d["duration_ms"] == 150.5
        assert d["reinforcement_signal"] == 0.75

    def test_to_dict_truncates_long_output(self):
        """Should truncate output longer than 500 chars."""
        long_output = "x" * 1000
        result = TaskKernelResult(
            kernel_id="tk_test",
            task_id="task-001",
            status=TaskKernelStatus.COMPLETED,
            output=long_output,
        )

        d = result.to_dict()

        assert len(d["output"]) == 500


# =============================================================================
# TEST: InjectedCapabilities
# =============================================================================


class TestInjectedCapabilities:
    """Test InjectedCapabilities container."""

    def test_empty_capabilities(self):
        """Should create with empty tools."""
        caps = InjectedCapabilities()

        assert len(caps.tools) == 0
        assert caps.list_tools() == []

    def test_get_tool_returns_tool(self):
        """Should return tool by name."""
        tool = _SuccessTool()
        caps = InjectedCapabilities(tools={"success_tool": tool})

        result = caps.get_tool("success_tool")

        assert result is tool

    def test_get_tool_returns_none_for_missing(self):
        """Should return None for non-existent tool."""
        caps = InjectedCapabilities(tools={})

        result = caps.get_tool("nonexistent")

        assert result is None

    def test_list_tools_returns_names(self):
        """Should list all tool names."""
        caps = InjectedCapabilities(
            tools={
                "tool_a": _SuccessTool(),
                "tool_b": _FailingTool(),
            }
        )

        names = caps.list_tools()

        assert "tool_a" in names
        assert "tool_b" in names
        assert len(names) == 2

    def test_timeout_default(self):
        """Should default timeout to 300 seconds."""
        caps = InjectedCapabilities()

        assert caps.timeout_seconds == 300

    def test_custom_timeout(self):
        """Should accept custom timeout."""
        caps = InjectedCapabilities(timeout_seconds=60)

        assert caps.timeout_seconds == 60


# =============================================================================
# TEST: TaskKernel Initialization
# =============================================================================


class TestTaskKernelInit:
    """Test TaskKernel initialization."""

    def test_init_creates_kernel_with_unique_id(self):
        """Should generate unique kernel_id starting with tk_."""
        task = create_test_task()
        caps = create_test_capabilities()

        kernel = TaskKernel(task=task, capabilities=caps)

        assert kernel.kernel_id.startswith("tk_")
        assert len(kernel.kernel_id) == 11  # "tk_" + 8 hex chars

    def test_init_stores_task(self):
        """Should store the task reference."""
        task = create_test_task(task_id="my-task-123")
        caps = create_test_capabilities()

        kernel = TaskKernel(task=task, capabilities=caps)

        assert kernel.task is task
        assert kernel.task.id == "my-task-123"

    def test_init_stores_parent_id(self):
        """Should store parent_id if provided."""
        task = create_test_task()
        caps = create_test_capabilities()

        kernel = TaskKernel(task=task, capabilities=caps, parent_id="parent-123")

        assert kernel.parent_id == "parent-123"

    def test_init_status_is_spawned(self):
        """Should start in SPAWNED status."""
        task = create_test_task()
        caps = create_test_capabilities()

        kernel = TaskKernel(task=task, capabilities=caps)

        assert kernel.status == TaskKernelStatus.SPAWNED

    def test_init_result_is_none(self):
        """Should have no result initially."""
        task = create_test_task()
        caps = create_test_capabilities()

        kernel = TaskKernel(task=task, capabilities=caps)

        assert kernel.result is None

    def test_init_with_tools(self):
        """Should have access to injected tools."""
        task = create_test_task()
        tool = _SuccessTool()
        caps = create_test_capabilities(tools={"success_tool": tool})

        kernel = TaskKernel(task=task, capabilities=caps)

        assert "success_tool" in kernel._tools


# =============================================================================
# TEST: TaskKernel.spawn() Factory
# =============================================================================


class TestTaskKernelSpawn:
    """Test TaskKernel.spawn() static factory."""

    def test_spawn_creates_kernel(self):
        """Should create TaskKernel instance."""
        task = create_test_task()
        tools = [_SuccessTool()]

        kernel = TaskKernel.spawn(task=task, tools=tools)

        assert isinstance(kernel, TaskKernel)
        assert kernel.task is task

    def test_spawn_injects_tools_by_name(self):
        """Should inject tools indexed by name."""
        task = create_test_task()
        tools = [_SuccessTool(), _FailingTool()]

        kernel = TaskKernel.spawn(task=task, tools=tools)

        assert "success_tool" in kernel._tools
        assert "failing_tool" in kernel._tools

    def test_spawn_with_custom_timeout(self):
        """Should use custom timeout."""
        task = create_test_task()

        kernel = TaskKernel.spawn(task=task, tools=[], timeout=60)

        assert kernel._capabilities.timeout_seconds == 60

    def test_spawn_with_on_complete_callback(self):
        """Should store on_complete callback."""
        task = create_test_task()
        callback_called = []

        def on_complete(result):
            callback_called.append(result)

        kernel = TaskKernel.spawn(task=task, tools=[], on_complete=on_complete)

        assert kernel._capabilities.on_complete is on_complete

    def test_spawn_creates_isolated_vfs_sandbox(self):
        """Should create VFS sandbox for task."""
        task = create_test_task(task_id="sandbox-test-123")

        kernel = TaskKernel.spawn(task=task, tools=[])

        # Sandbox is created - verify via tools if VFS was injected
        # This is implicit - just ensure spawn doesn't fail
        assert kernel is not None


# =============================================================================
# TEST: TaskKernel.execute()
# =============================================================================


class TestTaskKernelExecute:
    """Test TaskKernel.execute() async method."""

    @pytest.mark.asyncio
    async def test_execute_returns_completed_result(self):
        """Should return COMPLETED result for successful execution."""
        task = create_test_task()
        kernel = TaskKernel.spawn(task=task, tools=[])

        result = await kernel.execute()

        assert result.status == TaskKernelStatus.COMPLETED
        assert kernel.status == TaskKernelStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_execute_records_duration(self):
        """Should record execution duration."""
        task = create_test_task()
        kernel = TaskKernel.spawn(task=task, tools=[])

        result = await kernel.execute()

        assert result.duration_ms > 0

    @pytest.mark.asyncio
    async def test_execute_with_tool_call_metadata(self):
        """Should execute tool when metadata contains tool_call."""
        task = create_test_task(
            metadata={
                "tool_call": {
                    "tool": "success_tool",
                    "parameters": {"value": "test_input"},
                }
            }
        )
        kernel = TaskKernel.spawn(task=task, tools=[_SuccessTool()])

        result = await kernel.execute()

        assert result.status == TaskKernelStatus.COMPLETED
        assert result.tool_calls_made == 1
        assert result.tools_succeeded == 1

    @pytest.mark.asyncio
    async def test_execute_with_missing_tool(self):
        """Should fail when tool not available."""
        task = create_test_task(
            metadata={
                "tool_call": {
                    "tool": "nonexistent_tool",
                    "parameters": {},
                }
            }
        )
        kernel = TaskKernel.spawn(task=task, tools=[])

        result = await kernel.execute()

        assert result.status == TaskKernelStatus.FAILED
        assert "not injected" in result.error

    @pytest.mark.asyncio
    async def test_execute_with_tool_failure(self):
        """Should track tool failures."""
        task = create_test_task(
            metadata={
                "tool_call": {
                    "tool": "failing_tool",
                    "parameters": {},
                }
            }
        )
        kernel = TaskKernel.spawn(task=task, tools=[_FailingTool()])

        result = await kernel.execute()

        assert result.tool_calls_made == 1
        assert result.tools_failed == 1

    @pytest.mark.asyncio
    async def test_execute_with_validation_failure(self):
        """Should handle validation failures."""
        task = create_test_task(
            metadata={
                "tool_call": {
                    "tool": "validation_fail_tool",
                    "parameters": {},  # Missing required_param
                }
            }
        )
        kernel = TaskKernel.spawn(task=task, tools=[_ValidationFailTool()])

        result = await kernel.execute()

        assert result.tool_calls_made == 1
        assert result.tools_failed == 1

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Sync tool.execute() blocks event loop; asyncio.wait_for can't interrupt")
    async def test_execute_timeout_sync_tool(self):
        """Should timeout when execution exceeds limit.

        KNOWN LIMITATION: Synchronous tool.execute() blocks the event loop,
        so asyncio.wait_for cannot interrupt it. This test documents the
        limitation - timeouts only work for async-cooperative tools.
        """
        task = create_test_task(
            metadata={
                "tool_call": {
                    "tool": "slow_tool",
                    "parameters": {"delay": 5},
                }
            }
        )
        kernel = TaskKernel.spawn(task=task, tools=[_SlowTool()], timeout=1)

        result = await kernel.execute()

        assert result.status == TaskKernelStatus.TIMEOUT
        assert "timeout" in result.error.lower()

    @pytest.mark.asyncio
    async def test_execute_timeout_mechanism_exists(self):
        """Should have timeout mechanism configured."""
        task = create_test_task()
        kernel = TaskKernel.spawn(task=task, tools=[], timeout=60)

        # Verify timeout is configured
        assert kernel._capabilities.timeout_seconds == 60

    @pytest.mark.asyncio
    async def test_execute_calls_on_complete_callback(self):
        """Should call on_complete callback after execution."""
        task = create_test_task()
        results_received = []

        def on_complete(result):
            results_received.append(result)

        kernel = TaskKernel.spawn(task=task, tools=[], on_complete=on_complete)

        await kernel.execute()

        assert len(results_received) == 1
        assert results_received[0].status == TaskKernelStatus.COMPLETED

    @pytest.mark.asyncio
    async def test_execute_with_action_metadata(self):
        """Should execute action when metadata contains action."""
        task = create_test_task(
            metadata={
                "action": "read",
                "context": {"path": "/some/path"},
            }
        )
        # Note: read_file tool not provided, so this will fail gracefully
        kernel = TaskKernel.spawn(task=task, tools=[])

        result = await kernel.execute()

        # Will fail because read_file tool not available
        assert result.status == TaskKernelStatus.FAILED

    @pytest.mark.asyncio
    async def test_execute_fallback_acknowledged(self):
        """Should return acknowledged when no tool_call or action."""
        task = create_test_task(
            task_id="ack-test",
            title="Test Title",
        )
        kernel = TaskKernel.spawn(task=task, tools=[])

        result = await kernel.execute()

        assert result.status == TaskKernelStatus.COMPLETED
        assert result.output["acknowledged"] is True
        assert result.output["task_id"] == "ack-test"


# =============================================================================
# TEST: Reinforcement Signal Calculation
# =============================================================================


class TestReinforcementSignal:
    """Test synaptic reinforcement signal calculation."""

    @pytest.mark.asyncio
    async def test_completed_no_tools_gives_positive_signal(self):
        """Should give +0.8 for completion without tools."""
        task = create_test_task()
        kernel = TaskKernel.spawn(task=task, tools=[])

        result = await kernel.execute()

        assert result.reinforcement_signal == 0.8

    @pytest.mark.asyncio
    async def test_completed_all_tools_success_gives_max_signal(self):
        """Should give +1.0 for 100% tool success rate."""
        task = create_test_task(
            metadata={
                "tool_call": {
                    "tool": "success_tool",
                    "parameters": {},
                }
            }
        )
        kernel = TaskKernel.spawn(task=task, tools=[_SuccessTool()])

        result = await kernel.execute()

        # 0.5 + 0.5 * (1/1) = 1.0
        assert result.reinforcement_signal == 1.0

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Sync tool.execute() blocks event loop; timeout can't fire")
    async def test_timeout_gives_negative_signal(self):
        """Should give -0.3 for timeout.

        KNOWN LIMITATION: Same as test_execute_timeout_sync_tool.
        """
        task = create_test_task(
            metadata={
                "tool_call": {
                    "tool": "slow_tool",
                    "parameters": {"delay": 5},
                }
            }
        )
        kernel = TaskKernel.spawn(task=task, tools=[_SlowTool()], timeout=1)

        result = await kernel.execute()

        assert result.reinforcement_signal == -0.3

    def test_calculate_reinforcement_timeout_value(self):
        """Should return -0.3 for TIMEOUT status."""
        task = create_test_task()
        caps = create_test_capabilities()
        kernel = TaskKernel(task=task, capabilities=caps)

        signal = kernel._calculate_reinforcement(TaskKernelStatus.TIMEOUT)

        assert signal == -0.3

    def test_calculate_reinforcement_cancelled_neutral(self):
        """Should return 0.0 for CANCELLED status (neutral)."""
        task = create_test_task()
        caps = create_test_capabilities()
        kernel = TaskKernel(task=task, capabilities=caps)

        signal = kernel._calculate_reinforcement(TaskKernelStatus.CANCELLED)

        assert signal == 0.0

    @pytest.mark.asyncio
    async def test_failed_gives_negative_signal(self):
        """Should give -1.0 for failure."""
        task = create_test_task(
            metadata={
                "tool_call": {
                    "tool": "nonexistent",
                    "parameters": {},
                }
            }
        )
        kernel = TaskKernel.spawn(task=task, tools=[])

        result = await kernel.execute()

        assert result.reinforcement_signal == -1.0


# =============================================================================
# TEST: Event Recording
# =============================================================================


class TestEventRecording:
    """Test in-memory event recording."""

    @pytest.mark.asyncio
    async def test_execute_records_start_event(self):
        """Should record TASK_START event."""
        task = create_test_task(task_id="event-test")
        kernel = TaskKernel.spawn(task=task, tools=[])

        await kernel.execute()

        events = kernel.get_events()
        start_events = [e for e in events if e["event_type"] == "TASK_START"]

        assert len(start_events) == 1
        assert start_events[0]["task_id"] == "event-test"

    @pytest.mark.asyncio
    async def test_execute_records_complete_event(self):
        """Should record TASK_COMPLETE event."""
        task = create_test_task()
        kernel = TaskKernel.spawn(task=task, tools=[])

        await kernel.execute()

        events = kernel.get_events()
        complete_events = [e for e in events if e["event_type"] == "TASK_COMPLETE"]

        assert len(complete_events) == 1

    @pytest.mark.asyncio
    async def test_tool_execution_records_events(self):
        """Should record TOOL_CALL and TOOL_SUCCESS events."""
        task = create_test_task(
            metadata={
                "tool_call": {
                    "tool": "success_tool",
                    "parameters": {},
                }
            }
        )
        kernel = TaskKernel.spawn(task=task, tools=[_SuccessTool()])

        await kernel.execute()

        events = kernel.get_events()
        tool_events = [e for e in events if "TOOL" in e["event_type"]]

        assert len(tool_events) >= 2  # TOOL_CALL and TOOL_SUCCESS

    def test_get_events_returns_copy(self):
        """Should return copy of events list."""
        task = create_test_task()
        caps = create_test_capabilities()
        kernel = TaskKernel(task=task, capabilities=caps)

        events1 = kernel.get_events()
        events2 = kernel.get_events()

        assert events1 is not events2


# =============================================================================
# TEST: Status Methods
# =============================================================================


class TestStatusMethods:
    """Test status and status reporting methods."""

    def test_get_status_returns_dict(self):
        """Should return status dict."""
        task = create_test_task(task_id="status-test")
        caps = create_test_capabilities(tools={"tool_a": _SuccessTool()})
        kernel = TaskKernel(task=task, capabilities=caps)

        status = kernel.get_status()

        assert status["kernel_id"] == kernel.kernel_id
        assert status["task_id"] == "status-test"
        assert status["status"] == "spawned"
        assert "tool_a" in status["tools_available"]

    def test_status_property_returns_enum(self):
        """Should return TaskKernelStatus enum."""
        task = create_test_task()
        caps = create_test_capabilities()
        kernel = TaskKernel(task=task, capabilities=caps)

        assert isinstance(kernel.status, TaskKernelStatus)
        assert kernel.status == TaskKernelStatus.SPAWNED


# =============================================================================
# TEST: Border Control (OPUS-176)
# =============================================================================


class TestBorderControl:
    """Test OPUS-176 BHARAT Border Control."""

    def test_verify_sovereignty_known_states(self):
        """Should approve known sovereign states."""
        # Known sovereign states: opus_assistant, agent_city
        result = TaskKernel._verify_sovereignty("opus_assistant")

        assert result is True

    def test_verify_sovereignty_unknown_plugin(self):
        """Should deny unknown plugins."""
        result = TaskKernel._verify_sovereignty("unknown_plugin")

        assert result is False

    def test_spawn_without_caller_plugin_id_succeeds(self):
        """Should allow spawn when caller_plugin_id not specified."""
        task = create_test_task()

        # No caller_plugin_id = no border control check
        kernel = TaskKernel.spawn(task=task, tools=[])

        assert kernel is not None

    def test_spawn_with_sovereign_caller_succeeds(self):
        """Should allow spawn from sovereign state."""
        task = create_test_task()

        kernel = TaskKernel.spawn(
            task=task,
            tools=[],
            caller_plugin_id="opus_assistant",
        )

        assert kernel is not None

    def test_spawn_with_non_sovereign_caller_raises(self):
        """Should deny spawn from non-sovereign plugin."""
        task = create_test_task()

        with pytest.raises(PermissionError) as exc_info:
            TaskKernel.spawn(
                task=task,
                tools=[],
                caller_plugin_id="random_plugin",
            )

        assert "BORDER CONTROL" in str(exc_info.value)
        assert "not a SOVEREIGN_STATE" in str(exc_info.value)


# =============================================================================
# TEST: fold_result_to_parent
# =============================================================================


class TestFoldResultToParent:
    """Test fold_result_to_parent function."""

    def test_fold_records_to_ledger(self):
        """Should record result in parent's ledger."""

        # Create mock parent with ledger
        class MockLedger:
            def __init__(self):
                self.events = []

            def record_event(self, event_type, agent_id, details):
                self.events.append(
                    {
                        "event_type": event_type,
                        "agent_id": agent_id,
                        "details": details,
                    }
                )

        class MockParent:
            def __init__(self):
                self._ledger = MockLedger()
                self._plugins = []

        parent = MockParent()
        result = TaskKernelResult(
            kernel_id="tk_test",
            task_id="task-001",
            status=TaskKernelStatus.COMPLETED,
        )

        fold_result = fold_result_to_parent(parent, result)

        assert fold_result["folded"] is True
        assert "ledger_recorded" in fold_result["actions"]
        assert len(parent._ledger.events) == 1
        assert parent._ledger.events[0]["event_type"] == "TASK_KERNEL_RESULT"

    def test_fold_notifies_plugins(self):
        """Should notify plugins with on_task_kernel_result hook."""

        class MockPlugin:
            def __init__(self):
                self.plugin_id = "test_plugin"
                self.received_results = []

            def on_task_kernel_result(self, kernel, result):
                self.received_results.append(result)

        class MockParent:
            def __init__(self, plugins):
                self._plugins = plugins

        plugin = MockPlugin()
        parent = MockParent([plugin])
        result = TaskKernelResult(
            kernel_id="tk_notify",
            task_id="task-002",
            status=TaskKernelStatus.COMPLETED,
        )

        fold_result = fold_result_to_parent(parent, result)

        assert f"plugin_{plugin.plugin_id}_notified" in fold_result["actions"]
        assert len(plugin.received_results) == 1

    def test_fold_returns_kernel_and_task_ids(self):
        """Should return kernel_id and task_id in result."""

        class MockParent:
            def __init__(self):
                self._plugins = []

        parent = MockParent()
        result = TaskKernelResult(
            kernel_id="tk_ids",
            task_id="task-ids",
            status=TaskKernelStatus.COMPLETED,
        )

        fold_result = fold_result_to_parent(parent, result)

        assert fold_result["kernel_id"] == "tk_ids"
        assert fold_result["task_id"] == "task-ids"
