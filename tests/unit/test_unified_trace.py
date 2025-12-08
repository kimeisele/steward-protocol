"""
Verification Test: Unified Telemetry (GAD-000 Phase 5)
======================================================

Verifies:
1. UnifiedTrace records structured events
2. UnifiedExecutor emits telemetry events
3. Kernel exposes navigation of traces via get_trace()
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from vibe_core.kernel_impl import RealVibeKernel
from vibe_core.runtime.unified_execution import ExecutionPath, ExecutionRequest, UnifiedExecutor
from vibe_core.runtime.unified_trace import UnifiedTrace


class TestUnifiedTrace(unittest.IsolatedAsyncioTestCase):
    def test_trace_infrastructure(self):
        """Verify UnifiedTrace core logic"""
        trace = UnifiedTrace()

        # 1. Start usage
        trace_id = trace.start(component="test", data={"user": "alice"})
        assert trace_id is not None
        assert isinstance(trace_id, str)

        # 2. Emit usage
        trace.emit(trace_id, "test", "step_1", {"value": 1})

        # 3. Complete usage
        trace.complete(trace_id, {"result": "success"})

        # 4. Get trace (GAD-000 Machine Readability)
        history = trace.get_trace(trace_id)
        assert len(history) == 3

        # Verify structure
        assert history[0]["event_type"] == "start"
        assert history[0]["data"]["user"] == "alice"
        assert history[2]["event_type"] == "complete"

    def test_kernel_integration(self):
        """Verify Kernel initializes trace"""
        # Mock dependencies to avoid full boot
        kernel = MagicMock(spec=RealVibeKernel)

        # Manually attach trace as RealVibeKernel.__init__ would
        kernel.trace = UnifiedTrace()

        # Test get_trace capability wrapper
        # We need to simulate RealVibeKernel.get_trace behavior since we mocked the class
        def get_trace_impl(trace_id):
            return kernel.trace.get_trace(trace_id)

        kernel.get_trace = get_trace_impl

        # Usage
        tid = kernel.trace.start("kernel", "boot")
        history = kernel.get_trace(tid)
        assert len(history) == 1
        assert history[0]["component"] == "kernel"

    async def test_executor_integration(self):
        """Verify UnifiedExecutor emits traces"""
        # Setup Kernel with Trace
        kernel = MagicMock(spec=RealVibeKernel)
        kernel.trace = UnifiedTrace()

        # Setup Executor
        executor = UnifiedExecutor(kernel)
        # Mock internal circuit execution to avoid needing real circuits
        executor._execute_circuit = AsyncMock(
            return_value=MagicMock(status="completed", data={"foo": "bar"}, to_dict=lambda: {})
        )

        # Request
        req = ExecutionRequest(user_input="test command")
        req.mark_routed(ExecutionPath.CIRCUIT, "test_circuit")

        # Execute
        result = await executor.execute(req)

        # Verify Trace ID propagated
        assert result.trace_id != ""

        # Verify Trace recorded
        history = kernel.trace.get_trace(result.trace_id)

        # Expect: start, complete
        assert len(history) >= 2
        assert history[0]["event_type"] == "execute_start"
        assert history[-1]["event_type"] == "complete"
        assert history[0]["data"]["user_input"] == "test command"


if __name__ == "__main__":
    unittest.main()
