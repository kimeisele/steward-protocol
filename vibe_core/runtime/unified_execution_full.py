"""
UNIFIED EXECUTION FULL - Executor Only (OPUS-301 Boot Optimization)
====================================================================

OPUS-301: Split for lazy loading - Core loaded at boot, Full loaded on first use.
OPUS-307 Phase I.1: ExecutorSingularity - ALL execution routes to CognitiveCircuitExecutor.

Full contains:
- UnifiedExecutor (execution logic)
- ExecutorSingularity (OPUS-307: unified execution)
- Heavy imports (DeterministicExecutor as fallback)

Core (unified_execution_core.py) contains:
- UnifiedRouter (routing logic)
- Route decision making

This reduces boot time by ~265ms by deferring executor imports until first execution.
"""

import logging
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from vibe_core.cartridges.system.envoy.executor_singularity import ExecutorSingularity
    from vibe_core.kernel_impl import RealVibeKernel

from vibe_core.state.schema import (
    ExecutionPath,
    ExecutionRequest,
    ExecutionResult,
)

logger = logging.getLogger("UNIFIED_EXECUTION")

# OPUS-307: ExecutorSingularity flag
EXECUTOR_SINGULARITY_ENABLED = True  # Set to False to fallback to DeterministicExecutor

# =============================================================================
# UNIFIED EXECUTOR (BREAK 4 + BREAK 6 fix)
# =============================================================================


class UnifiedExecutor:
    """
    Execute based on routing decision.

    Features:
    - Eager initialization (BREAK 4 fix - no lazy loading race conditions)
    - All async (BREAK 6 fix - consistent async boundaries)
    - OPUS-307 Phase I.1: ExecutorSingularity - ALL execution via CognitiveCircuitExecutor
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

        # OPUS-307: ExecutorSingularity (primary)
        self._singularity: Optional["ExecutorSingularity"] = None
        if EXECUTOR_SINGULARITY_ENABLED:
            self._init_singularity()

        # DeterministicExecutor (fallback only)
        self._circuit_executor = None
        if not EXECUTOR_SINGULARITY_ENABLED or self._singularity is None:
            self._init_circuit_executor()

        logger.info("[EXECUTOR] UnifiedExecutor initialized (eager)")

    def _init_singularity(self):
        """
        OPUS-307 Phase I.1: Initialize ExecutorSingularity.

        This is the unified executor that routes ALL execution
        through CognitiveCircuitExecutor.
        """
        try:
            from vibe_core.cartridges.system.envoy.executor_singularity import (
                create_executor_singularity,
            )

            self._singularity = create_executor_singularity(self._kernel)
            logger.info("[EXECUTOR] 🎯 ExecutorSingularity ready (OPUS-307 Phase I.1)")
        except Exception as e:
            logger.warning(f"[EXECUTOR] ExecutorSingularity not available, falling back: {e}")
            self._singularity = None

    def _init_circuit_executor(self):
        """Initialize circuit executor with ephemeral storage (OPUS Phase 2) - FALLBACK ONLY"""
        try:
            from vibe_core.cartridges.system.envoy.deterministic_executor import DeterministicExecutor

            self._circuit_executor = DeterministicExecutor(ephemeral=self._ephemeral)
            logger.info("[EXECUTOR] DeterministicExecutor ready (fallback)")
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
        Execute a circuit.

        OPUS-307 Phase I.1: Routes to ExecutorSingularity (CognitiveCircuitExecutor)
        with DeterministicExecutor as fallback.
        """
        # OPUS-307: Try ExecutorSingularity first
        if self._singularity is not None:
            try:
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
            except Exception as e:
                logger.warning(f"[EXECUTOR] Singularity failed, trying fallback: {e}")
                # Fall through to DeterministicExecutor

        # Fallback: DeterministicExecutor
        if not self._circuit_executor:
            return ExecutionResult(
                success=False,
                error="No executor available",
                result={"target_id": request.target_id},
            )

        # Execute circuit via legacy executor
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
            result={
                "response": response,
                "data": raw_result,
                "target_id": request.target_id,
                "execution_mode": "deterministic",
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
