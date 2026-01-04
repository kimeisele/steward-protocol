"""
UNIFIED EXECUTION CORE - Routing Only (OPUS-301 Boot Optimization)
===================================================================

OPUS-301: Split for lazy loading - Core loaded at boot, Full loaded on first use.

Core contains:
- UnifiedRouter (routing logic)
- Route decision making
- Gate checking

Full (unified_execution_full.py) contains:
- UnifiedExecutor (execution logic)
- Heavy imports (DeterministicExecutor, etc.)

This reduces boot time by ~265ms by deferring executor imports.
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

from vibe_core.runtime.layered_router import LayeredRouter
from vibe_core.state.schema import (
    ExecutionPath,
    ExecutionRequest,
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

        # Map LayeredRouter reason (exact/exact_prefix/semantic/context/fallback) to ExecutionPath
        if route_result.reason in ("exact", "exact_prefix"):
            request.mark_routed(ExecutionPath.FAST_COMMAND, route_result.target_id, route_result.confidence)
            logger.info(
                f"[ROUTER] {route_result.reason} match: {route_result.target_id} "
                f"(confidence={route_result.confidence:.2f})"
            )
        elif route_result.reason in ("semantic", "context", "akshara"):
            request.mark_routed(ExecutionPath.CIRCUIT, route_result.target_id, route_result.confidence)
            logger.info(
                f"[ROUTER] {route_result.reason} match: {route_result.target_id} "
                f"(confidence={route_result.confidence:.2f})"
            )
        else:
            request.mark_routed(ExecutionPath.FALLBACK, route_result.target_id, route_result.confidence)
            logger.info(f"[ROUTER] Fallback: {route_result.target_id}")

        # Store extracted params for executor
        request.phase_results["extracted_params"] = route_result.params

        return request

    def check_gate(self, request: ExecutionRequest) -> MilkOceanGate:
        """
        MilkOcean gate check (pre-execution).

        P0-2: Uses KaliyaFilter for real pattern matching instead of string-match.

        Returns gate decision - whether to allow, queue, or block.
        """
        # P0-2: Use KaliyaFilter for toxicity detection
        try:
            from gateway.takshaka_lite import KaliyaFilter

            kaliya = KaliyaFilter()
            score, patterns = kaliya.scan(request.user_input)

            if score >= 0.3:  # Toxicity threshold
                logger.warning(f"[GATE] Blocked by Kaliya (score={score:.2f}, patterns={patterns})")
                request.gate_decision = MilkOceanGate.BLOCK
                return MilkOceanGate.BLOCK
        except ImportError:
            # Fallback to legacy string matching if Kaliya not available
            if "DROP TABLE" in request.user_input.upper() or "sudo" in request.user_input.lower():
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
