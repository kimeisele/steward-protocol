"""
UNIFIED EXECUTION FULL - Executor Only (OPUS-301 Boot Optimization)
====================================================================

OPUS-301: Split for lazy loading - Core loaded at boot, Full loaded on first use.

Full contains:
- UnifiedExecutor (execution logic)
- Heavy imports (DeterministicExecutor, etc.)

Core (unified_execution_core.py) contains:
- UnifiedRouter (routing logic)
- Route decision making

This reduces boot time by ~265ms by deferring executor imports until first execution.
"""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
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

    Features:
    - Eager initialization (BREAK 4 fix - no lazy loading race conditions)
    - All async (BREAK 6 fix - consistent async boundaries)
    - Delegates to specialized executors
    """

    def __init__(self, kernel: "RealVibeKernel", ephemeral=None):
        """
        Eager initialization - all executors created at construction time.
        No lazy loading = no race conditions.

        Args:
            kernel: The kernel instance
            ephemeral: EphemeralStorage instance (OPUS Phase 2: dependency injection)
        """
        self._kernel = kernel
        self._ephemeral = ephemeral

        # Import and initialize executors eagerly
        self._circuit_executor = None
        self._init_circuit_executor()

        logger.info("[EXECUTOR] UnifiedExecutor initialized (eager)")

    def _init_circuit_executor(self):
        """Initialize circuit executor with ephemeral storage (OPUS Phase 2)"""
        try:
            from vibe_core.cartridges.system.envoy.deterministic_executor import DeterministicExecutor

            self._circuit_executor = DeterministicExecutor(ephemeral=self._ephemeral)
            logger.info("[EXECUTOR] DeterministicExecutor ready")
        except Exception as e:
            logger.warning(f"[EXECUTOR] DeterministicExecutor not available: {e}")

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
            if request.execution_path == ExecutionPath.FAST_COMMAND:
                result = await self._execute_circuit(request)
            elif request.execution_path == ExecutionPath.CIRCUIT:
                result = await self._execute_circuit(request)
            elif request.execution_path == ExecutionPath.PLAYBOOK:
                result = await self._execute_playbook(request)
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
        """Execute a circuit via DeterministicExecutor"""
        if not self._circuit_executor:
            return ExecutionResult(
                success=False,
                error="Circuit executor not available",
                result={"target_id": request.target_id},
            )

        # Execute circuit
        raw_result = await self._circuit_executor.execute(
            playbook_id=request.target_id,
            user_input=request.user_input,
            intent_vector=None,
            kernel=self._kernel,
        )

        # Extract rendered response
        details = raw_result.get("details", {})
        rendered = details.get("rendered", {})
        response = rendered.get("rendered", "") if isinstance(rendered, dict) else ""

        return ExecutionResult(
            success=raw_result.get("status") == "COMPLETED",
            result={"response": response, "data": raw_result, "target_id": request.target_id},
        )

    async def _execute_playbook(self, request: ExecutionRequest) -> ExecutionResult:
        """Execute a legacy playbook"""
        # For now, delegate to circuit executor (they share the same backend)
        return await self._execute_circuit(request)

    async def _execute_fallback(self, request: ExecutionRequest) -> ExecutionResult:
        """Handle unknown requests"""
        return ExecutionResult(
            success=True,
            result={"response": f"Unknown command: {request.user_input}", "fallback": True, "target_id": request.target_id},
        )
