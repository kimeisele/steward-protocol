"""
UNIFIED EXECUTION FULL - Executor Only (OPUS-301 Boot Optimization)
====================================================================

OPUS-301: Split for lazy loading - Core loaded at boot, Full loaded on first use.
OPUS-307 Phase I.2: ExecutorSingularity - THE ONLY executor. No fallback.

Full contains:
- UnifiedExecutor (execution logic)
- ExecutorSingularity (OPUS-307: unified execution)

Core (unified_execution_core.py) contains:
- UnifiedRouter (routing logic)
- Route decision making

This reduces boot time by ~265ms by deferring executor imports until first execution.

OPUS-307 Phase I.2: DeterministicExecutor REMOVED. Singularity or FAIL.
"Ein Executor, eine Engine, eine Wahrheit."
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from vibe_core.cartridges.system.envoy.executor_singularity import ExecutorSingularity
    from vibe_core.kernel_impl import RealVibeKernel

from vibe_core.state.schema import (
    ExecutionPath,
    ExecutionRequest,
    ExecutionResult,
)

logger = logging.getLogger("UNIFIED_EXECUTION")

# =============================================================================
# UNIFIED EXECUTOR (BREAK 4 + BREAK 6 fix)
# =============================================================================


class UnifiedExecutor:
    """
    Execute based on routing decision.

    OPUS-307 Phase I.2: ExecutorSingularity is THE ONLY executor.
    No fallback. No DeterministicExecutor. One engine, one truth.

    Features:
    - Eager initialization (BREAK 4 fix - no lazy loading race conditions)
    - All async (BREAK 6 fix - consistent async boundaries)
    - ExecutorSingularity routes ALL execution via CognitiveCircuitExecutor
    """

    def __init__(self, kernel: "RealVibeKernel", ephemeral=None):
        """
        Eager initialization - ExecutorSingularity created at construction time.

        Args:
            kernel: The kernel instance
            ephemeral: EphemeralStorage instance (reserved for future use)

        Raises:
            RuntimeError: If ExecutorSingularity fails to initialize
        """
        self._kernel = kernel
        self._ephemeral = ephemeral

        # OPUS-307 Phase I.2: ExecutorSingularity is THE ONLY executor
        self._singularity: "ExecutorSingularity" = self._init_singularity()

        logger.info("[EXECUTOR] 🎯 UnifiedExecutor ready (Singularity mode)")

    def _init_singularity(self) -> "ExecutorSingularity":
        """
        OPUS-307 Phase I.2: Initialize ExecutorSingularity.

        This is THE unified executor. No fallback. If this fails, execution fails.

        Returns:
            ExecutorSingularity instance

        Raises:
            RuntimeError: If initialization fails
        """
        from vibe_core.cartridges.system.envoy.executor_singularity import (
            create_executor_singularity,
        )

        singularity = create_executor_singularity(self._kernel)
        logger.info("[EXECUTOR] 🎯 ExecutorSingularity initialized (OPUS-307 Phase I.2)")
        return singularity

    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        """
        Execute based on pre-determined path.

        The routing decision was already made - we just execute.
        """
        request.mark_executing()

        # Telemetry: Start trace (GAD-000 Phase 5)
        trace_id = ""
        if hasattr(self._kernel, "trace"):
            trace_id = self._kernel.trace.start(
                component="executor",
                event_type="execute_start",
                data={
                    "request_id": request.request_id,
                    "execution_path": request.execution_path.value,
                    "target_id": request.target_id,
                    "user_input": request.user_input,
                },
            )

        try:
            # OPUS-307: All paths route to _execute_circuit (ExecutorSingularity)
            # ExecutionPath.PLAYBOOK removed - was dead code (never set by UnifiedRouter)
            if request.execution_path in (ExecutionPath.FAST_COMMAND, ExecutionPath.CIRCUIT):
                result = await self._execute_circuit(request)
            else:
                result = await self._execute_fallback(request)

            request.mark_completed(result.result)
            result.execution_time_ms = int((request.duration or 0.0) * 1000)
            result.trace_id = trace_id

            # Telemetry: Complete trace
            if hasattr(self._kernel, "trace"):
                self._kernel.trace.complete(trace_id, data={"success": result.success})

            return result

        except Exception as e:
            request.mark_failed(str(e))
            logger.error(f"[EXECUTOR] Execution failed: {e}")

            # Telemetry: Error trace
            if hasattr(self._kernel, "trace"):
                self._kernel.trace.error(trace_id, error=str(e))

            return ExecutionResult(
                success=False,
                error=str(e),
                trace_id=trace_id,
                result={"request_id": request.request_id, "target_id": request.target_id},
            )

    async def _execute_circuit(self, request: ExecutionRequest) -> ExecutionResult:
        """
        Execute a circuit via ExecutorSingularity.

        OPUS-307 Phase I.2: No fallback. Singularity or FAIL.
        """
        raw_result = await self._singularity.execute(
            playbook_or_circuit_id=request.target_id,
            user_input=request.user_input,
            intent_vector=None,
        )

        # Extract rendered response
        details = raw_result.get("details", {})
        rendered = details.get("rendered", {})
        if isinstance(rendered, dict):
            response = rendered.get("rendered", "")
        elif isinstance(rendered, str):
            response = rendered
        else:
            response = raw_result.get("output", "")

        return ExecutionResult(
            success=raw_result.get("status") == "COMPLETED",
            result={
                "response": response,
                "data": raw_result,
                "target_id": request.target_id,
                "execution_mode": "singularity",
            },
        )

    # OPUS-307: _execute_playbook() REMOVED - was dead code
    # UnifiedRouter never sets ExecutionPath.PLAYBOOK
    # All playbooks converted to circuits by ExecutorSingularity

    async def _execute_fallback(self, request: ExecutionRequest) -> ExecutionResult:
        """Handle unknown requests"""
        return ExecutionResult(
            success=True,
            result={
                "response": f"Unknown command: {request.user_input}",
                "fallback": True,
                "target_id": request.target_id,
            },
        )
