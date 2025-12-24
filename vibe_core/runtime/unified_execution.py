"""
UNIFIED EXECUTION MODEL (OPUS Architecture)
============================================

Single source of truth for request routing and execution.
Fixes all 8 BREAKS from OPUS_RUNTIME_SEPARATION analysis.

Components:
1. ExecutionRequest - Unified request tracking object (Moved to vibe_core.state.schema)
2. ExecutionResult - Unified result format (Moved to vibe_core.state.schema)
3. UnifiedRouter - Single router (replaces PlaybookRouter + MilkOceanRouter)
4. UnifiedExecutor - Single executor dispatcher

OPUS-200/201 INTEGRATION:
- QuantumReactor provides RESONANCE-BASED gating (Breaking the Binary)
- check_gate_resonant() computes continuous energy instead of boolean
- Actions MANIFEST when energy > inertia (not "allowed")
- Entropy chain provides cryptographic audit trail

Refs: docs/architecture/OPUS/OPUS_RUNTIME_SEPARATION.md
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

from vibe_core.runtime.layered_router import LayeredRouter
from vibe_core.state.schema import (
    ExecutionPath,
    ExecutionRequest,
    ExecutionResult,
    MilkOceanGate,
)

logger = logging.getLogger("UNIFIED_EXECUTION")

# =============================================================================
# UNIFIED ROUTER (BREAK 1 + BREAK 2 fix)
# =============================================================================


class UnifiedRouter:
    """
    One router to rule them all.

    Replaces:
    - PlaybookRouter (pattern matching)
    - MilkOceanRouter (gating)

    Now powered by LayeredRouter for intelligent 3-layer routing.
    Decision is made ONCE at routing time, not during execution.
    """

    # OPUS-200/201: Resonance thresholds
    RESONANCE_INERTIA = 0.5  # Default inertia for manifestation
    RESONANCE_CRITICAL = 0.85  # Above this = critical manifestation
    RESONANCE_QUEUE = 0.3  # Below inertia but above this = queue

    def __init__(self, kernel: Optional["RealVibeKernel"] = None):
        self._kernel = kernel
        self._circuits: Dict[str, Dict[str, Any]] = {}
        self._reactor = None  # Lazy-loaded

        # Initialize LayeredRouter
        self._layered = LayeredRouter(kernel=kernel)

        # Legacy fast commands (merged into Layer 1)
        self._fast_commands: Dict[str, str] = {
            "status": "SYSTEM_STATUS_V2",
            "help": "HELP_COMMAND",
            "agents": "LIST_AGENTS",
            "tools": "LIST_TOOLS",
            "health": "SYSTEM_STATUS_V2",
        }

        # Load circuits from kernel.envoy if available
        if kernel and hasattr(kernel, "envoy"):
            self._circuits = getattr(kernel.envoy, "_circuits", {})

        # Inject fast commands into LayeredRouter's exact index (Layer 1)
        for cmd, circuit_id in self._fast_commands.items():
            self._layered._exact_index[cmd] = circuit_id

    def inject_kernel(self, kernel: "RealVibeKernel"):
        """Inject kernel (for lazy initialization)"""
        self._kernel = kernel
        if hasattr(kernel, "envoy"):
            self._circuits = getattr(kernel.envoy, "_circuits", {})

        # Inject into LayeredRouter
        self._layered.inject_kernel(kernel)

    def route(self, user_input: str, source: str = "envoy", context: Optional[Dict] = None) -> ExecutionRequest:
        """
        Route user input to appropriate execution path.

        Decision made ONCE here via LayeredRouter.
        """
        # Use LayeredRouter for intelligent routing
        route_result = self._layered.route(user_input, context=context)

        # Convert RouteResult to ExecutionRequest
        request = ExecutionRequest(user_input=user_input, source=source)

        # Map LayeredRouter layers to ExecutionPath
        if route_result.layer in ("exact", "exact_prefix"):
            request.mark_routed(ExecutionPath.FAST_COMMAND, route_result.circuit_id, route_result.confidence)
            logger.info(
                f"[ROUTER] {route_result.layer} match: {route_result.circuit_id} "
                f"(confidence={route_result.confidence:.2f})"
            )
        elif route_result.layer in ("semantic", "context"):
            request.mark_routed(ExecutionPath.CIRCUIT, route_result.circuit_id, route_result.confidence)
            logger.info(
                f"[ROUTER] {route_result.layer} match: {route_result.circuit_id} "
                f"(confidence={route_result.confidence:.2f})"
            )
        else:
            request.mark_routed(ExecutionPath.FALLBACK, route_result.circuit_id, route_result.confidence)
            logger.info(f"[ROUTER] Fallback: {route_result.circuit_id}")

        # Store extracted params for executor
        request.phase_results["extracted_params"] = route_result.extracted_params

        return request

    def check_gate(self, request: ExecutionRequest) -> MilkOceanGate:
        """
        MilkOcean gate check (pre-execution).

        Returns gate decision - whether to allow, queue, or block.
        """
        # GAD-000: Security Checks
        if "DROP TABLE" in request.user_input or "sudo" in request.user_input:
            request.gate_decision = MilkOceanGate.BLOCK
            return MilkOceanGate.BLOCK

        # GAJENDRA PROTOCOL: Critical Request Handling
        # If request is explicitly marked critical or contains critical keywords
        is_critical = "CRITICAL" in request.user_input or "crit=True" in request.user_input

        if is_critical:
            request.gate_decision = MilkOceanGate.CRITICAL
            return MilkOceanGate.CRITICAL

        # For now, default to ALLOW (Queueing logic to be implemented in Phase 4)
        request.gate_decision = MilkOceanGate.ALLOW
        return MilkOceanGate.ALLOW

    # =========================================================================
    # OPUS-200/201: QUANTUM RESONANCE GATING (Breaking the Binary)
    # =========================================================================

    @property
    def reactor(self):
        """Lazy-load QuantumReactor for resonance computation."""
        if self._reactor is None:
            try:
                from vibe_core.reactor import QuantumReactor

                self._reactor = QuantumReactor(initial_inertia=self.RESONANCE_INERTIA)
                logger.info("[ROUTER] 🔥 QuantumReactor loaded for resonance gating")
            except ImportError as e:
                logger.debug(f"[ROUTER] QuantumReactor not available: {e}")
        return self._reactor

    def check_gate_resonant(self, request: ExecutionRequest, salt: str = "") -> MilkOceanGate:
        """
        OPUS-200/201: Resonance-based gate check.

        Instead of boolean allow/block, compute CONTINUOUS energy.
        Actions MANIFEST when energy > inertia.

        Args:
            request: The execution request
            salt: Cryptographic salt (session context)

        Returns:
            MilkOceanGate - but now derived from resonance, not boolean
        """
        if self.reactor is None:
            # Fallback to boolean gate if reactor unavailable
            return self.check_gate(request)

        try:
            from vibe_core.reactor import encode

            # Encode user intent as tensor
            intent_tensor = encode(request.user_input, salt)

            # Encode target action as tensor
            target_str = f"{request.execution_path.value}:{request.target_id}"
            target_tensor = encode(target_str, salt)

            # Compute resonance between intent and target
            field = self.reactor.resonate(intent_tensor, target_tensor)

            # Store resonance values in request
            request.mark_resonance(
                energy=field.total_energy,
                inertia=self.RESONANCE_INERTIA,
                field_hash=field.field_hash,
            )

            # Log the resonance computation
            status = "MANIFEST" if request.manifests else "PENDING"
            logger.info(f"[ROUTER] 🔮 Resonance: {request.user_input[:30]}... → E={field.total_energy:.3f} ({status})")

            return request.gate_decision

        except Exception as e:
            logger.warning(f"[ROUTER] Resonance computation failed: {e}")
            return self.check_gate(request)

    def manifest(self, user_input: str, source: str = "envoy", salt: str = "") -> ExecutionRequest:
        """
        OPUS-200/201: Complete manifestation flow.

        Routes AND computes resonance in one call.
        The request will have both routing decision AND resonance field.

        Args:
            user_input: The user's intent
            source: Origin of request
            salt: Cryptographic salt

        Returns:
            ExecutionRequest with routing + resonance data
        """
        # First, route normally
        request = self.route(user_input, source)

        # Then, compute resonance
        self.check_gate_resonant(request, salt)

        return request

    @property
    def kernel(self) -> Optional["RealVibeKernel"]:
        """Expose kernel for access by tests and other code."""
        return self._kernel

    def list_available_routes(self) -> list[Dict[str, str]]:
        """
        List all available routes (circuits).

        GAD-000 Compliance: Allows discovery of system capabilities.
        """
        routes = []
        for circuit_id, circuit_data in self._circuits.items():
            circuit_def = circuit_data.get("circuit", {})
            routes.append(
                {
                    "name": circuit_id,
                    "description": circuit_def.get("purpose", "No description available"),
                    "examples": circuit_def.get("intent_patterns", [])[:3],
                }
            )

        # Add fast commands
        for cmd, intent in self._fast_commands.items():
            routes.append({"name": cmd, "description": f"Fast command: {intent}", "examples": [cmd]})

        return routes


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

            request.mark_completed(result.data)
            result.duration_seconds = request.duration or 0.0
            result.request_id = request.request_id
            result.trace_id = trace_id

            # Telemetry: Complete trace
            if hasattr(self._kernel, "trace"):
                self._kernel.trace.complete(trace_id, data={"result": result.to_dict()})

            return result

        except Exception as e:
            request.mark_failed(str(e))
            logger.error(f"[EXECUTOR] Execution failed: {e}")

            # Telemetry: Error trace
            if hasattr(self._kernel, "trace"):
                self._kernel.trace.error(trace_id, error=str(e))

            return ExecutionResult(
                status="failed",
                error=str(e),
                execution_path=request.execution_path,
                target_id=request.target_id,
                request_id=request.request_id,
                trace_id=trace_id,
            )

    async def _execute_circuit(self, request: ExecutionRequest) -> ExecutionResult:
        """Execute a circuit via DeterministicExecutor"""
        if not self._circuit_executor:
            return ExecutionResult(
                status="failed",
                error="Circuit executor not available",
                execution_path=request.execution_path,
                target_id=request.target_id,
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
            status="completed" if raw_result.get("status") == "COMPLETED" else "failed",
            response=response,
            data=raw_result,
            execution_path=request.execution_path,
            target_id=request.target_id,
        )

    async def _execute_playbook(self, request: ExecutionRequest) -> ExecutionResult:
        """Execute a legacy playbook"""
        # For now, delegate to circuit executor (they share the same backend)
        return await self._execute_circuit(request)

    async def _execute_fallback(self, request: ExecutionRequest) -> ExecutionResult:
        """Handle unknown requests"""
        return ExecutionResult(
            status="completed",
            response=f"Unknown command: {request.user_input}",
            data={"fallback": True},
            execution_path=request.execution_path,
            target_id=request.target_id,
        )


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def create_unified_runtime(kernel: "RealVibeKernel") -> tuple:
    """
    Create unified router and executor for a kernel.

    Returns:
        (UnifiedRouter, UnifiedExecutor) tuple
    """
    router = UnifiedRouter(kernel)
    executor = UnifiedExecutor(kernel)
    return router, executor