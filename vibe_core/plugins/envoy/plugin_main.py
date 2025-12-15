"""
ENVOY PLUGIN - The System Shell
================================

ENVOY is the AOS (Agent Operating System) Shell.
It routes user intent to circuits, playbooks, and agents.

Like STEWARD, ENVOY is FRAKTAL:
1. The Concept (intent routing, system shell)
2. The Plugin (kernel connection, hooks)
3. The Avatar (EnvoyCartridge agent)

This plugin:
1. Owns routing infrastructure (UnifiedRouter - replaces PlaybookRouter + MilkOceanRouter)
2. Uses kernel hooks to intercept and route requests
3. Provides public API via kernel.envoy.*
4. Connects to circuit/playbook execution via UnifiedExecutor

Architecture: OPUS RUNTIME SEPARATION (docs/architecture/OPUS/OPUS_RUNTIME_SEPARATION.md)
Pattern: Same as StewardProtocolPlugin (the Golden Plugin Standard)
"""

import asyncio
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from vibe_core.plugin_protocol import KernelPlugin

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("ENVOY_PLUGIN")


class EnvoyPlugin(KernelPlugin):
    """
    ENVOY Plugin - The System Shell for Agent City.

    This plugin provides:
    - Intent routing (user request -> circuit/playbook)
    - Circuit discovery and execution
    - Agent spawning coordination
    - ENVOY.md bidirectional interface support

    Priority: 15 (after steward_protocol, before interface)
    """

    @property
    def plugin_id(self) -> str:
        return "envoy"

    @property
    def priority(self) -> int:
        return 15  # After steward_protocol (5), before interface (50)

    def __init__(self):
        """Initialize ENVOY state."""
        self._kernel: Optional["RealVibeKernel"] = None
        self._project_root: Path = Path.cwd()

        # Config (from Phoenix envoy.yaml)
        self._config = None

        # EphemeralStorage (OPUS Phase 2: kernel-bound, not global)
        from vibe_core.playbook.ephemeral_storage import EphemeralStorage

        self._ephemeral = EphemeralStorage()

        # UNIFIED ROUTER + EXECUTOR (OPUS Architecture)
        # Replaces _playbook_router and _milk_ocean_router
        self._unified_router = None
        self._unified_executor = None

        # Legacy routers (OPUS Phase 2: REMOVED - use _unified_router instead)
        # Properties below provide deprecation warnings for backwards compatibility

        # Circuit registry {circuit_id: circuit_data}
        self._circuits: Dict[str, Dict[str, Any]] = {}

        # Playbook registry {playbook_name: playbook_data}
        self._playbooks: Dict[str, Dict[str, Any]] = {}

        # Pending requests {request_id: request_data}
        self._pending_requests: Dict[str, Dict[str, Any]] = {}

        # Request history (last N)
        self._request_history: List[Dict[str, Any]] = []
        self._max_history = 50

        # Lazy-loaded executor (legacy)
        self._executor = None

    # =========================================================================
    # KERNEL HOOKS
    # =========================================================================

    def on_boot(self, kernel: "RealVibeKernel") -> None:
        """
        Called when kernel boots.

        Register as THE envoy plugin on the kernel.
        Initialize unified router + executor (OPUS Architecture).
        Register EnvoyCartridge as the actual agent for task execution.

        BOOT ORDER DEPENDENCY: ToolsPlugin (priority=5) MUST boot before EnvoyPlugin (priority=15).
        See docs/architecture/OPUS/004-BOOT-SEQUENCE-AUDIT.md for boot order documentation.
        """
        self._kernel = kernel

        # DEFENSIVE CHECK: Verify ToolsPlugin booted first (priority 5 < 15)
        # This is a critical dependency - EnvoyPlugin needs tool_registry for circuit execution
        if not hasattr(kernel, "tool_registry") or kernel.tool_registry is None:
            raise RuntimeError(
                "CRITICAL: ToolsPlugin (priority=5) must boot before EnvoyPlugin (priority=15)! "
                "tool_registry not found on kernel. Check plugin priorities in manifest.json."
            )

        # Register as kernel.envoy
        kernel.envoy = self

        # Load config
        self._load_config()

        # ═══════════════════════════════════════════════════════════════════════════
        # CRITICAL: Circuit discovery MUST happen BEFORE router initialization!
        # The UnifiedRouter reads self._circuits during inject_kernel().
        # If we call _init_unified_runtime() first, router will have 0 circuits!
        # See: docs/architecture/OPUS/004-BOOT-SEQUENCE-AUDIT.md (Circular Reference Risk)
        # ═══════════════════════════════════════════════════════════════════════════
        self._discover_circuits()
        self._discover_playbooks()

        # Initialize UNIFIED ROUTER + EXECUTOR (OPUS Architecture)
        # OPUS Phase 2: Legacy routers removed - only UnifiedRouter exists
        self._init_unified_runtime()

        # Register EnvoyCartridge as the actual agent
        # This connects ENVOY.md requests -> Task -> EnvoyCartridge.process()
        self._register_envoy_agent(kernel)

        logger.info("📬 ENVOY Plugin booted (OPUS Architecture)")
        logger.info(f"   Circuits: {len(self._circuits)}")
        logger.info(f"   Playbooks: {len(self._playbooks)}")
        logger.info(f"   UnifiedRouter: {'OK' if self._unified_router else 'FAIL'}")
        logger.info(f"   UnifiedExecutor: {'OK' if self._unified_executor else 'FAIL'}")

    def on_tick(self, kernel: "RealVibeKernel") -> None:
        """
        Called on each kernel tick.

        Process pending ENVOY requests if any.
        """
        # Process completed tasks and update request status
        self._process_completed_tasks()

    def on_shutdown(self, kernel: "RealVibeKernel") -> None:
        """Clean up on shutdown."""
        # Clear ephemeral storage (OPUS Phase 2: proper lifecycle management)
        if hasattr(self, "_ephemeral") and self._ephemeral:
            cleared_count = self._ephemeral.clear()
            logger.info(f"📬 Ephemeral storage cleared: {cleared_count} entries")

        logger.info(f"📬 ENVOY Plugin shutting down ({len(self._request_history)} requests processed)")

    # =========================================================================
    # PUBLIC API (accessible via kernel.envoy.*)
    # =========================================================================

    def route(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Route user intent to a circuit or playbook.

        OPUS Phase 2: Now uses UnifiedRouter instead of legacy PlaybookRouter.

        Args:
            user_input: The user's natural language request
            context: Optional context dict (session, git, tests, etc.)

        Returns:
            Route result with task, description, confidence, source
        """
        if not self._unified_router:
            return {
                "error": "Router not initialized",
                "task": "fallback",
                "description": "ENVOY router not ready",
                "confidence": "none",
            }

        try:
            # Use UnifiedRouter (OPUS Phase 2)
            request = self._unified_router.route(user_input, source="envoy")

            # Convert float confidence to string labels expected by tests/envoy_sync
            confidence_str = self._confidence_to_label(request.confidence)

            return {
                "task": request.target_id,
                "description": f"{request.execution_path.value}: {request.target_id}",
                "confidence": confidence_str,
                "source": request.source,
            }
        except Exception as e:
            logger.error(f"📬 Routing failed: {e}")
            return {
                "error": str(e),
                "task": "fallback",
                "description": "Routing failed",
                "confidence": "none",
            }

    def _confidence_to_label(self, confidence: float) -> str:
        """
        Convert float confidence (0.0-1.0) to string label.

        Args:
            confidence: Float confidence score

        Returns:
            String label: "explicit", "contextual", or "suggested"
        """
        if confidence >= 0.8:
            return "explicit"
        elif confidence >= 0.5:
            return "contextual"
        else:
            return "suggested"

    def execute_circuit(self, circuit_id: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a circuit by ID using DeterministicExecutor.

        GAD-6000: Real circuit execution via action handlers.
        No more stubs - actual QUERY_GRAPH, RENDER_TEMPLATE, etc.

        Args:
            circuit_id: The circuit identifier
            params: Optional parameters for the circuit

        Returns:
            Execution result with rendered output
        """
        if circuit_id not in self._circuits:
            return {"error": f"Circuit '{circuit_id}' not found", "status": "FAILED"}

        _ = self._circuits[circuit_id]  # Validate circuit exists
        logger.info(f"📬 Executing circuit: {circuit_id}")

        try:
            # Get the DeterministicExecutor (lazy init)
            if not hasattr(self, "_executor") or self._executor is None:
                from vibe_core.cartridges.system.envoy.deterministic_executor import DeterministicExecutor

                self._executor = DeterministicExecutor()
                logger.info("📬 DeterministicExecutor initialized")

            # Execute circuit via DeterministicExecutor
            import asyncio

            result = asyncio.get_event_loop().run_until_complete(
                self._executor.execute(
                    playbook_id=circuit_id,
                    user_input=params.get("user_input", "") if params else "",
                    intent_vector=params.get("intent_vector") if params else None,
                    kernel=self._kernel,
                )
            )

            logger.info(f"📬 Circuit {circuit_id} completed: {result.get('status')}")
            return result

        except Exception as e:
            logger.error(f"📬 Circuit execution failed: {e}")
            return {
                "circuit_id": circuit_id,
                "status": "FAILED",
                "error": str(e),
            }

    def list_circuits(self) -> List[Dict[str, Any]]:
        """
        List all available circuits.

        Returns:
            List of circuit summaries
        """
        return [
            {
                "id": cid,
                "domain": c.get("circuit", {}).get("domain", "-"),
                "version": c.get("circuit", {}).get("version", "-"),
                "description": c.get("circuit", {}).get("description", ""),
            }
            for cid, c in self._circuits.items()
        ]

    def list_playbooks(self) -> List[Dict[str, Any]]:
        """
        List all available playbooks (routes).

        OPUS Phase 2: Returns circuits as playbooks (circuits replace playbooks).

        Returns:
            List of playbook summaries
        """
        # OPUS Phase 2: Circuits are the new playbooks
        # Return circuits in playbook format for backwards compatibility
        return [
            {
                "name": cid,
                "description": c.get("circuit", {}).get("description", ""),
                "domain": c.get("circuit", {}).get("domain", "-"),
            }
            for cid, c in self._circuits.items()
        ]

    def get_routes(self) -> List[Dict[str, str]]:
        """
        Get all available routes for ENVOY.md display.

        Returns:
            List of {name, description} dicts
        """
        routes = []

        # Add playbook routes
        for pb in self.list_playbooks():
            routes.append({"name": pb["name"], "description": pb.get("description", "")})

        # Add circuit routes
        for circuit in self.list_circuits():
            routes.append({"name": circuit["id"], "description": circuit.get("description", "Circuit")})

        return routes

    def submit_request(self, request: str, source: str = "envoy.md") -> Dict[str, Any]:
        """
        Submit a user request for processing.

        Routes the request and queues a task.

        Args:
            request: The user's request text
            source: Where the request came from

        Returns:
            Submission result with request_id
        """
        import uuid
        from datetime import datetime

        request_id = f"req_{uuid.uuid4().hex[:8]}"

        # Route the request
        route_result = self.route(request)

        # Create request record
        record = {
            "request_id": request_id,
            "request": request,
            "source": source,
            "route": route_result,
            "status": "ROUTED",
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Store in pending
        self._pending_requests[request_id] = record

        # Submit as task if we have a scheduler
        if self._kernel and hasattr(self._kernel, "scheduler"):
            try:
                from vibe_core import Task

                task = Task(
                    agent_id="envoy",
                    payload={
                        "type": "envoy_request",
                        "request_id": request_id,
                        "request": request,
                        "route": route_result,
                    },
                )
                task_id = self._kernel.scheduler.submit_task(task)
                record["task_id"] = task_id
                record["status"] = "QUEUED"
                logger.info(f"📬 Request {request_id} queued as task {task_id}")
            except Exception as e:
                logger.error(f"📬 Failed to queue task: {e}")
                record["error"] = str(e)

        return record

    def get_status(self) -> Dict[str, Any]:
        """
        Get ENVOY plugin status.

        Returns:
            Status dict with routing info, pending requests, etc.
        """
        return {
            "plugin_id": self.plugin_id,
            "architecture": "OPUS",  # OPUS Phase 2: Always OPUS now
            "routers": {
                "unified_router": self._unified_router is not None,
                "unified_executor": self._unified_executor is not None,
                # OPUS Phase 2: Legacy routers removed
            },
            "circuits": len(self._circuits),
            "playbooks": len(self._circuits),  # OPUS Phase 2: playbooks = circuits
            "pending_requests": len(self._pending_requests),
            "history_size": len(self._request_history),
            "config_loaded": self._config is not None,
        }

    def execute_unified(self, user_input: str, source: str = "envoy") -> Dict[str, Any]:
        """
        Execute user input via UNIFIED ARCHITECTURE (OPUS).

        This is the new main entry point that uses:
        - UnifiedRouter for routing decisions
        - UnifiedExecutor for execution

        Args:
            user_input: The user's request
            source: Where the request came from

        Returns:
            ExecutionResult as dict
        """
        if not self._unified_router or not self._unified_executor:
            return {
                "status": "failed",
                "error": "OPUS Runtime not initialized",
                "response": "Internal error: Unified execution not available",
            }

        # Route
        request = self._unified_router.route(user_input, source)

        # Check gate
        gate = self._unified_router.check_gate(request)
        if gate.value == "block":
            return {
                "status": "blocked",
                "error": "Request blocked by MilkOcean gate",
                "response": "Request was blocked",
            }

        # Execute
        try:
            result = asyncio.get_event_loop().run_until_complete(self._unified_executor.execute(request))
            return result.to_dict()
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "response": f"Execution failed: {e}",
            }

    def execute_mission(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """
        The Single Point of Execution.
        The Brain (Manas) determines intent, The Envoy (Hand) executes.

        NO PUSSY MODE (OPUS-076): Real execution via ToolRegistry.

        Args:
            intent: The intent dictionary (from Manas)

        Returns:
            Execution result dict signed by Envoy
        """
        if not isinstance(intent, dict):
            # Handle object form if necessary
            try:
                intent = intent.to_dict()
            except AttributeError:
                pass

        mission_id = intent.get("id", "unknown")
        action = intent.get("action", "unknown")
        # Support both 'params' (Sankalpa) and 'args' (Tool) conventions
        params = intent.get("params", {}) or intent.get("args", {})

        logger.info(f"🔫 ENVOY [LIVE FIRE]: Processing mission {mission_id} -> {action}")

        # 1. Get Tool Registry from Kernel
        try:
            # Try to get from kernel (Best practice)
            registry = getattr(self._kernel, "tool_registry", None)
            if not registry and hasattr(self._kernel, "get_service"):
                registry = self._kernel.get_service("tool_registry")
        except Exception as e:
            logger.warning(f"⚠️ Failed to get registry from kernel: {e}")
            registry = None

        if not registry:
            # Fallback: Pragmatic import for testing/headless
            try:
                from vibe_core.tools.tool_registry import default_registry  # noqa

                # Assuming default_registry exists in module, if not we fail hard
                # But based on user request, we should try.
                # Actually, let's fail if kernel registry missing for safety in V1
                pass
            except ImportError:
                pass

            if not registry:
                logger.error("❌ CRITICAL: ToolRegistry not found. Cannot execute.")
                return {
                    "status": "error",
                    "message": "CRITICAL: ToolRegistry not found. Cannot execute.",
                    "signed_by": "Envoy",
                }

        # 2. Find the Tool
        # Registry API: has(tool_name) -> bool
        if not registry.has(action):
            logger.error(f"❌ ENVOY: Tool '{action}' not found in registry.")
            return {
                "status": "error",
                "message": f"Tool '{action}' not known. Available: {registry.list_tools()}",
                "signed_by": "Envoy",
            }

        # 3. EXECUTE (The Point of No Return)
        try:
            logger.info(f"⚡ ENVOY: Executing '{action}' with params: {list(params.keys())}")

            # Create ToolCall object (Required by Registry)
            from vibe_core.tools.tool_protocol import ToolCall

            # Use 'envoy' as the authorized agent
            call = ToolCall(tool_name=action, parameters=params, caller_agent_id="envoy")

            # Execute via Registry (handles governance/capabilities)
            tool_result = registry.execute(call)

            if tool_result.success:
                logger.info(f"✅ ENVOY: Mission Accomplished. Output len: {len(str(tool_result.output))}")
                return {
                    "status": "success",
                    "executed_by": "Envoy",
                    "tool": action,
                    "result": tool_result.output,
                    "mission_id": mission_id,
                    "signed_by": "Envoy",
                }
            else:
                logger.error(f"💥 ENVOY: Tool Execution Failed: {tool_result.error}")
                return {"status": "error", "error": tool_result.error, "signed_by": "Envoy"}

        except Exception as e:
            logger.error(f"💥 ENVOY: Execution FAILED (Exception): {e}")
            import traceback

            return {"status": "error", "error": str(e), "traceback": traceback.format_exc(), "signed_by": "Envoy"}

    # =========================================================================
    # PUBLIC ROUTER ACCESS
    # =========================================================================

    @property
    def router(self):
        """
        Access the UnifiedRouter instance.

        Returns the current _unified_router or None if not initialized.
        """
        return self._unified_router

    # =========================================================================
    # DEPRECATED LEGACY ROUTER PROPERTIES (OPUS Phase 2)
    # =========================================================================

    @property
    def _playbook_router(self):
        """
        DEPRECATED: Legacy playbook router removed in OPUS Phase 2.
        Use execute_unified() or _unified_router instead.
        """
        import warnings

        warnings.warn(
            "Legacy _playbook_router is deprecated. Use execute_unified() or _unified_router instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        # Return a wrapper that redirects to unified router
        return self._unified_router if self._unified_router else None

    @property
    def _milk_ocean_router(self):
        """
        DEPRECATED: Legacy MilkOcean router removed in OPUS Phase 2.
        Use _unified_router.check_gate() instead.
        """
        import warnings

        warnings.warn(
            "Legacy _milk_ocean_router is deprecated. Use _unified_router.check_gate() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return None

    # =========================================================================
    # PRIVATE METHODS
    # =========================================================================

    def _load_config(self) -> None:
        """Load ENVOY config from Phoenix."""
        try:
            # TODO: Create envoy.yaml config section
            # For now, use defaults
            self._config = {"enabled": True}
            logger.debug("📬 ENVOY config: using defaults")
        except Exception as e:
            logger.warning(f"📬 Could not load ENVOY config: {e}")

    def _init_unified_runtime(self) -> None:
        """
        Initialize UNIFIED ROUTER + EXECUTOR (OPUS Architecture).

        This replaces the legacy PlaybookRouter + MilkOceanRouter with a
        single unified routing and execution system.

        Now uses LayeredRouter for intelligent 3-layer routing:
        - Layer 1: Exact match (circuit.intent_patterns)
        - Layer 2: Semantic match (semantic_grounding.intent_patterns)
        - Layer 3: Context-aware (Ephemeral + Knowledge Graph)

        Fixes:
        - BREAK 1: Dual Routing -> Single UnifiedRouter (powered by LayeredRouter)
        - BREAK 2: Path Uncertainty -> Decision at routing time
        - BREAK 4: Lazy Init -> Eager initialization
        - BREAK 5: Result Mismatch -> Unified ExecutionResult
        """
        try:
            from vibe_core.runtime.unified_execution import UnifiedExecutor, UnifiedRouter

            # Create router with kernel (LayeredRouter created internally)
            self._unified_router = UnifiedRouter(self._kernel)

            # Inject kernel to initialize LayeredRouter with circuits and dependencies
            self._unified_router.inject_kernel(self._kernel)

            # Create executor with eager initialization and ephemeral storage
            # (OPUS Phase 2: dependency injection, not global singleton)
            self._unified_executor = UnifiedExecutor(self._kernel, ephemeral=self._ephemeral)

            logger.info("📬 OPUS Runtime initialized (UnifiedRouter + UnifiedExecutor)")
            logger.info("📬 LayeredRouter active (3-layer cascade: exact, semantic, context)")
        except Exception as e:
            logger.error(f"📬 Failed to init OPUS Runtime: {e}")
            self._unified_router = None
            self._unified_executor = None

    def _discover_circuits(self) -> None:
        """Discover circuits from YAML files."""
        import yaml

        # Phase 6: Load from Genesis Pack if available
        if hasattr(self._kernel, "genesis_path") and self._kernel.genesis_path:
            circuits_path = self._kernel.genesis_path / "circuits"
            logger.info(f"📬 Loading circuits from Genesis Pack: {circuits_path}")
        else:
            # Fallback to legacy path
            circuits_path = self._project_root / "vibe_core" / "playbook" / "circuits"
            logger.warning(f"📬 Genesis not found - using legacy circuits: {circuits_path}")

        if not circuits_path.exists():
            logger.warning(f"📬 Circuits directory not found: {circuits_path}")
            return

        for yaml_file in circuits_path.glob("*.yaml"):
            if yaml_file.name.startswith("_"):
                continue  # Skip templates/internals

            try:
                with open(yaml_file) as f:
                    data = yaml.safe_load(f)

                if data and "circuit" in data:
                    circuit_id = data["circuit"].get("id", yaml_file.stem)
                    self._circuits[circuit_id] = data
                    logger.debug(f"📬 Discovered circuit: {circuit_id}")
            except Exception as e:
                logger.warning(f"📬 Could not load circuit {yaml_file}: {e}")

    def _discover_playbooks(self) -> None:
        """
        Discover playbooks from registry.

        OPUS Phase 2: Playbooks are now circuits - this method is deprecated.
        Circuits are discovered in _discover_circuits() instead.
        """
        # OPUS Phase 2: Circuits replace playbooks
        # Legacy playbooks registry is no longer used
        logger.debug("📬 Playbook discovery skipped (OPUS Phase 2: using circuits)")
        pass

    def _build_default_context(self) -> Dict[str, Any]:
        """Build default context for routing."""
        return {
            "session": {"phase": "CODING"},
            "git": {"uncommitted": 0},
            "tests": {"failing_count": 0},
        }

    def _process_completed_tasks(self) -> None:
        """Process completed tasks and update request status."""
        if not self._kernel or not hasattr(self._kernel, "scheduler"):
            return

        # Check for completed tasks
        completed = getattr(self._kernel.scheduler, "completed", {})

        for request_id, record in list(self._pending_requests.items()):
            task_id = record.get("task_id")
            if task_id and task_id in completed:
                task = completed[task_id]
                error = getattr(task, "error", None)
                result = getattr(task, "result", None)

                record["status"] = "COMPLETED" if not error else "FAILED"
                record["result"] = str(result) if result else None
                record["error"] = str(error) if error else None

                # Move to history
                self._request_history.append(record)
                del self._pending_requests[request_id]

                # Trim history
                if len(self._request_history) > self._max_history:
                    self._request_history = self._request_history[-self._max_history :]

    def _register_envoy_agent(self, kernel: "RealVibeKernel") -> None:
        """
        Register EnvoyCartridge as the actual agent for task execution.

        This is the missing link that connects:
        ENVOY.md -> EnvoySync -> Task(agent_id="envoy") -> Scheduler -> EnvoyCartridge.process()

        Without this, tasks queued for "envoy" would fail with "Agent not found".
        """
        try:
            from vibe_core.cartridges.system.envoy.cartridge_main import EnvoyCartridge

            # Check if envoy agent already registered (avoid duplicate)
            if "envoy" in kernel._agent_registry:
                logger.debug("📬 EnvoyCartridge already registered, skipping")
                return

            # Create and register the EnvoyCartridge
            envoy_agent = EnvoyCartridge()
            kernel.register_agent(envoy_agent, spawn_process=False)  # In-process execution

            logger.info("📬 EnvoyCartridge registered as agent (task execution enabled)")

        except Exception as e:
            logger.error(f"📬 Failed to register EnvoyCartridge: {e}")
            logger.warning("📬 ENVOY.md requests will fail - no agent to execute tasks")
