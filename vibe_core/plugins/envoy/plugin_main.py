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
1. Owns routing infrastructure (PlaybookRouter, MilkOceanRouter)
2. Uses kernel hooks to intercept and route requests
3. Provides public API via kernel.envoy.*
4. Connects to circuit/playbook execution

Pattern: Same as StewardProtocolPlugin (the Golden Plugin Standard)
"""

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

        # Routers (lazy loaded)
        self._playbook_router = None
        self._milk_ocean_router = None

        # Circuit registry {circuit_id: circuit_data}
        self._circuits: Dict[str, Dict[str, Any]] = {}

        # Playbook registry {playbook_name: playbook_data}
        self._playbooks: Dict[str, Dict[str, Any]] = {}

        # Pending requests {request_id: request_data}
        self._pending_requests: Dict[str, Dict[str, Any]] = {}

        # Request history (last N)
        self._request_history: List[Dict[str, Any]] = []
        self._max_history = 50

    # =========================================================================
    # KERNEL HOOKS
    # =========================================================================

    def on_boot(self, kernel: "RealVibeKernel") -> None:
        """
        Called when kernel boots.

        Register as THE envoy plugin on the kernel.
        Initialize routers and load circuits.
        """
        self._kernel = kernel

        # Register as kernel.envoy
        kernel.envoy = self

        # Load config
        self._load_config()

        # Initialize routers
        self._init_routers()

        # Discover circuits and playbooks
        self._discover_circuits()
        self._discover_playbooks()

        logger.info("📬 ENVOY Plugin booted")
        logger.info(f"   Circuits: {len(self._circuits)}")
        logger.info(f"   Playbooks: {len(self._playbooks)}")
        logger.info("   Shell is now PLUGIN-BASED (kernel.envoy)")

    def on_tick(self, kernel: "RealVibeKernel") -> None:
        """
        Called on each kernel tick.

        Process pending ENVOY requests if any.
        """
        # Process completed tasks and update request status
        self._process_completed_tasks()

    def on_shutdown(self, kernel: "RealVibeKernel") -> None:
        """Clean up on shutdown."""
        logger.info(f"📬 ENVOY Plugin shutting down ({len(self._request_history)} requests processed)")

    # =========================================================================
    # PUBLIC API (accessible via kernel.envoy.*)
    # =========================================================================

    def route(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Route user intent to a circuit or playbook.

        This is the main entry point for the ENVOY shell.
        Uses PlaybookRouter for pattern matching (no LLM).

        Args:
            user_input: The user's natural language request
            context: Optional context dict (session, git, tests, etc.)

        Returns:
            Route result with task, description, confidence, source
        """
        if not self._playbook_router:
            return {
                "error": "Router not initialized",
                "task": "fallback",
                "description": "ENVOY router not ready",
                "confidence": "none",
            }

        ctx = context or self._build_default_context()

        try:
            route = self._playbook_router.route(user_input, ctx)
            return {
                "task": route.task,
                "description": route.description,
                "confidence": route.confidence,
                "source": route.source,
            }
        except Exception as e:
            logger.error(f"📬 Routing failed: {e}")
            return {
                "error": str(e),
                "task": "fallback",
                "description": "Routing failed",
                "confidence": "none",
            }

    def execute_circuit(self, circuit_id: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a circuit by ID.

        Args:
            circuit_id: The circuit identifier
            params: Optional parameters for the circuit

        Returns:
            Execution result
        """
        if circuit_id not in self._circuits:
            return {"error": f"Circuit '{circuit_id}' not found", "status": "FAILED"}

        circuit = self._circuits[circuit_id]
        logger.info(f"📬 Executing circuit: {circuit_id}")

        # TODO: Wire to DeterministicExecutor or CircuitEngine
        # For now, return circuit info
        return {
            "circuit_id": circuit_id,
            "status": "QUEUED",
            "circuit": circuit,
            "params": params or {},
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

        Returns:
            List of playbook summaries
        """
        if not self._playbook_router:
            return []

        return self._playbook_router.list_available_routes()

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
            "routers": {
                "playbook_router": self._playbook_router is not None,
                "milk_ocean_router": self._milk_ocean_router is not None,
            },
            "circuits": len(self._circuits),
            "playbooks": len(self._playbooks),
            "pending_requests": len(self._pending_requests),
            "history_size": len(self._request_history),
            "config_loaded": self._config is not None,
        }

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

    def _init_routers(self) -> None:
        """Initialize routing infrastructure."""
        # Initialize PlaybookRouter
        try:
            from vibe_core.runtime.playbook_router import PlaybookRouter

            self._playbook_router = PlaybookRouter()
            logger.debug("📬 PlaybookRouter initialized")
        except Exception as e:
            logger.warning(f"📬 Could not init PlaybookRouter: {e}")

        # Initialize MilkOceanRouter (optional, for Brahma Protocol)
        try:
            from vibe_core.cartridges.system.envoy.tools.milk_ocean import MilkOceanRouter

            self._milk_ocean_router = MilkOceanRouter()
            logger.debug("📬 MilkOceanRouter initialized")
        except Exception as e:
            logger.debug(f"📬 MilkOceanRouter not available: {e}")

    def _discover_circuits(self) -> None:
        """Discover circuits from YAML files."""
        import yaml

        circuits_path = self._project_root / "vibe_core" / "playbook" / "circuits"

        if not circuits_path.exists():
            logger.warning("📬 Circuits directory not found")
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
        """Discover playbooks from registry."""
        if self._playbook_router:
            # Playbooks are loaded by PlaybookRouter from _registry.yaml
            routes = self._playbook_router.registry.get("routes", [])
            for route in routes:
                name = route.get("name", "")
                if name:
                    self._playbooks[name] = route

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
