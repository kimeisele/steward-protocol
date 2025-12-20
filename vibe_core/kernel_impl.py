"""
⚙️ REAL VIBE KERNEL IMPLEMENTATION ⚙️
=====================================

This is an actual working implementation of the VibeKernel that:
1. Manages a process table of agents
2. Runs a real task scheduler
3. Maintains an immutable ledger
4. Registers agent manifests

This is NOT a mock. This is real execution context for cartridges.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.boot_mode import BootMode
    from vibe_core.cartridges.system.civic.economy_agent import CivicBank
    from vibe_core.phoenix import PhoenixConfig

# Governance is handled by plugins (vibe_core/plugins/vedic_governance.py)
# Kernel has no governance types - access via kernel.governance

from .capability_registry import CapabilityRegistry  # Phase 2: Capability Revocation
from .errors import kernel_fault  # GAD-000 Compliance

# DocRenderer: Extracted markdown rendering logic
from .event_bus import get_event_bus  # Phase 2: Event Bus
from .gateway.api import NetworkGateway  # Phase 18: The Network (Sangha)

# I/O Service: Central file operation controller (see docs/architecture/KERNEL_IO_ARCHITECTURE.md)
from .io_service import KernelIOService
from .kernel import (
    KernelStatus,
    ManifestRegistry,
    VibeKernel,
    VibeLedger,
    VibeScheduler,
)
from .kernel_ops import (
    check_system_health as _check_system_health_impl,
)
from .kernel_ops import (
    execute_playbook as _execute_playbook_impl,
)
from .kernel_ops import (
    grant_repo_access as _grant_repo_access_impl,
)
from .kernel_ops import (
    narasimha_destroy_agent as _narasimha_destroy_agent_impl,
)
from .kernel_ops import (
    pulse as _pulse_impl,
)
from .kernel_ops import (
    sync_resource_quotas as _sync_resource_quotas_impl,
)
from .ledger import InMemoryLedger, SQLiteLedger
from .lineage import LineageChain, LineageEventType  # Phase 5: Parampara Blockchain
from .manifest_registry import InMemoryManifestRegistry
from .narasimha import ThreatIndicator, get_narasimha  # Phase 7: Kill-Switch
from .network_proxy import KernelNetworkProxy  # Phase 4: Network Isolation
from .plugin_loader import PluginLoader  # Phase 1: Plugin System
from .process_manager import ProcessManager  # Phase 2: Process Isolation
from .protocols import AgentManifest, VibeAgent
from .resource_manager import ResourceManager  # Phase 3: Resource Isolation

# Unified Execution: Single source of truth for routing (replaces PlaybookRouter)
from .runtime.unified_execution import create_unified_runtime
from .scheduling import InMemoryScheduler, Task

# Sync modules: Extracted bidirectional markdown interfaces
# NOTE: ToolRegistry and ToolDiscovery are now handled by ToolsPlugin (Phase 2 Extraction)

# Import Auditor for immune system (optional)
try:
    from vibe_core.cartridges.system.auditor.tools.invariant_tool import get_judge

    AUDITOR_AVAILABLE = True
except ImportError:
    AUDITOR_AVAILABLE = False
    logger_setup = logging.getLogger("VIBE_KERNEL")
    logger_setup.warning("⚠️  Auditor not available - immune system disabled")

# Import Constitutional Oath verification (Governance Gate - SECURITY FIX: P0.3)
try:
    # Check for availability without unused import
    import importlib.util

    if importlib.util.find_spec("vibe_core.bridge"):
        from vibe_core.bridge import ConstitutionalOath  # noqa: F401

        OATH_ENFORCEMENT_AVAILABLE = True
    else:
        raise ImportError("vibe_core.bridge not found")
except ImportError as e:
    # PHOENIX VIMANA: Graceful degradation by default (STEWARD_REQUIRE_OATH=true for strict mode)
    import os

    if os.environ.get("STEWARD_REQUIRE_OATH", "false").lower() == "true":
        # Strict mode: Production environments should set STEWARD_REQUIRE_OATH=true
        raise RuntimeError(f"CRITICAL: Constitutional Oath module required but failed to load: {e}")
    else:
        # Graceful degradation: System runs with reduced security capabilities
        OATH_ENFORCEMENT_AVAILABLE = False
        logger_setup = logging.getLogger("VIBE_KERNEL")
        logger_setup.warning(f"⚠️  Constitutional Oath unavailable ({e}) - running in degraded mode")


logger = logging.getLogger("VIBE_KERNEL")


# Helper classes: Extracted to reduce kernel size
# Kernel Operations: Extracted isolated methods


def _get_config():
    """Get PhoenixConfig with fallback for standalone usage."""
    try:
        from vibe_core.phoenix.config import get_config

        return get_config()
    except Exception:
        # Fallback for standalone/testing - return None to use defaults
        return None


class RealVibeKernel(VibeKernel):
    """
    🩸 THE REAL VIBE KERNEL 🩸

    This is not a mock. This is actual execution runtime for VibeOS cartridges.

    Capabilities:
    - Process table (agent registry)
    - Real task scheduler (FIFO queue)
    - Immutable ledger (append-only)
    - Manifest registry (agent identity)
    - Kernel injection (dependency injection pattern)
    - Ephemeral Cities (4D Hypercube - spawn child kernels with custom configs)
    """

    # SAMSARA CONFIG: Maximum entropy (ledger events) before Pralaya (pruning) occurs
    MAX_ENTROPY_EVENTS = 1000

    def __init__(
        self,
        ledger_path: str | None = None,
        config: "PhoenixConfig | None" = None,
        parent: "RealVibeKernel | None" = None,
        load_plugins: bool = True,
    ):
        """
        Initialize the kernel.

        Args:
            ledger_path: Path to ledger database (":memory:" for in-memory, None for config default)
            config: Optional PhoenixConfig for dependency injection.
                    If None, uses global get_config() singleton.
                    For ephemeral child kernels, pass custom config.
            parent: Optional parent kernel (for ephemeral cities).
                    Child kernels can access parent for result folding.
            load_plugins: If True, auto-discover and boot plugins (default: True).
                          Set False for isolated testing or minimal boot.
        """
        # 4D Hypercube: Store config and parent reference
        self._config = config
        self._parent = parent
        self._child_kernels: list["RealVibeKernel"] = []
        self._is_ephemeral = parent is not None
        self._load_plugins = load_plugins

        # Resolve ledger path from config if not provided
        if ledger_path is None:
            phoenix_config = _get_config()
            if phoenix_config and hasattr(phoenix_config, "paths"):
                # OPUS-025: Must use resolve() to expand template variables
                # Direct attribute access returns literal "{root}/vibe_ledger.db"
                ledger_path = str(phoenix_config.paths.data.resolve("vibe_ledger"))
            else:
                ledger_path = "data/vibe_ledger.db"  # Fallback default

        self._agent_registry: Dict[str, VibeAgent] = {}
        self._scheduler = InMemoryScheduler()
        self._completed_tasks: Dict[str, Any] = {}  # Temporary result cache for async IPC
        # Use SQLiteLedger for persistence (not in-memory)
        if ledger_path == ":memory:":
            self._ledger = InMemoryLedger()
            logger.info("🚀 Vibe Kernel initialized (in-memory ledger)")
        else:
            self._ledger = SQLiteLedger(ledger_path)
            logger.info(f"🚀 Vibe Kernel initialized (persistent ledger at {ledger_path})")
        self._manifest_registry = InMemoryManifestRegistry()
        self._status = KernelStatus.STOPPED
        self.ledger_path = ledger_path

        # Load immune system (Auditor)
        self._auditor = None
        if AUDITOR_AVAILABLE:
            self._auditor = get_judge()
            logger.info("🛡️  Immune system loaded (Auditor attached)")

        # Phase 2: Process Manager
        self.process_manager = ProcessManager()

        # Phase 3: Resource Manager
        self.resource_manager = ResourceManager()
        self._last_quota_sync = 0  # Timestamp of last credit→quota sync
        self._last_pulse_time = 0  # Timestamp of last heartbeat pulse

        # Markdown UI Manager (Centralized UI Coordination)
        # self._ui_manager = MarkdownUIManager(self)  # DEPRECATED: Handled by Plugins
        # logger.info("🖥️  Markdown UI Manager initialized")

        # Phase 4: Network Proxy
        self.network = KernelNetworkProxy(kernel=self)

        # Phase 5: Parampara Lineage Chain
        phoenix_config = _get_config()
        if phoenix_config and hasattr(phoenix_config, "paths"):
            lineage_path = str(phoenix_config.paths.system.resolve("lineage_db"))
        else:
            # OPUS-025: Fallback with Path pattern
            from pathlib import Path

            lineage_path = str(Path("/tmp") / "vibe_os" / "kernel" / "lineage.db")
        self.lineage = LineageChain(db_path=lineage_path)
        logger.info("⛓️  Parampara chain initialized")

        # Economic Substrate (Lazy Loaded)
        self._bank = None
        self._vault = None

        # Phase 4: Data Exchange Store (Inter-Agent Communication)
        # {agent_id: {key: value}} - Published data from agents
        self._data_store: Dict[str, Dict[str, Any]] = {}
        logger.info("📡 Data Exchange Store initialized (Phase 4: Wiring)")

        # GOVERNANCE PLUGIN SLOT
        # Governance is handled by plugins (e.g., VedicGovernancePlugin)
        # The plugin sets kernel.governance = self on boot
        # This keeps the kernel CLEAN and governance SWAPPABLE
        self.governance: Optional[Any] = None

        # SECURITY (ARCH-HARDENING): Capability Registry with Revocation
        # Stores agent capabilities with support for selective revocation
        # Telemetry: Unified Execution Trace (GAD-000 Phase 5)
        from vibe_core.runtime.unified_trace import UnifiedTrace

        self.trace = UnifiedTrace()

        # OPUS-009: PRAKRITI Unified State Engine
        from vibe_core.state import Prakriti

        prakriti_db_path = None
        if phoenix_config and hasattr(phoenix_config, "paths"):
            try:
                prakriti_db_path = phoenix_config.paths.data.resolve("vibe_ledger")
            except Exception:
                pass

        self.prakriti = Prakriti(db_path=prakriti_db_path)

        # Phase 2: Capability Registry (Must be before plugins)
        self._capability_registry = CapabilityRegistry(ledger=self._ledger)

        # I/O SERVICE: Central file operation controller
        # IMPORTANT: Must be initialized BEFORE tool discovery
        # Tools may inject io_service during registration via set_io_service()
        # All file writes MUST go through this service.
        # Plugins produce content, Kernel writes through self.io
        # See: docs/architecture/KERNEL_IO_ARCHITECTURE.md
        self.io = KernelIOService(self)
        logger.info("📁 Kernel I/O Service initialized (central file controller)")

        # Phase 6: Universal Tool Registry
        # EXTRACTED TO PLUGIN: ToolsPlugin handles registry initialization
        # Plugin sets kernel.tool_registry on boot
        # See: vibe_core/plugins/tools/plugin_main.py
        self.tool_registry = None  # Set by ToolsPlugin.on_boot()

        # Phase 7: NARASIMHA Kill-Switch (Hypervisor Level)
        # SECURITY FIX: Wire destruction handlers so Narasimha can actually kill agents
        self._narasimha = get_narasimha()
        self._narasimha.register_destruction_handler(self._narasimha_destroy_agent)
        logger.info("⚡ Narasimha Protocol wired (destruction handlers active)")

        # Phase 2: Event Bus (Agent Communication & Reactive Patterns)
        # Allows agents to subscribe to system-wide events
        # Supports loose coupling between agents
        self._event_bus = get_event_bus()
        logger.info("🎵 Event Bus initialized (pub/sub ready)")

        # Unified Execution Runtime (Router + Executor)
        # Replaces legacy PlaybookRouter and MilkOceanRouter
        self._unified_router, self._unified_executor = create_unified_runtime(self)
        self._playbook_router = self._unified_router  # Alias for backward compatibility (temporarily)

        # PLUGIN SYSTEM (The Avatars of Vishnu)
        # Phase 1: Load and boot all plugins
        # Phase 6: Load Cognitive Packs (Genesis)
        self.genesis_path = None
        self._plugin_metadata = {}

        if self._load_plugins:
            import os
            from pathlib import Path

            # OPUS-020 Phase 3: Support custom plugin paths via env var
            # Usage: VIBE_PLUGIN_PATH=dist/plugins:custom/plugins python -m vibe_core.cli boot
            custom_paths_env = os.environ.get("VIBE_PLUGIN_PATH", "")
            if custom_paths_env:
                scan_paths = [Path(p.strip()) for p in custom_paths_env.split(":") if p.strip()]
                logger.info(f"🔌 Using custom plugin paths from VIBE_PLUGIN_PATH: {scan_paths}")
            else:
                # Default: Scan both plugins and knowledge directories
                scan_paths = [Path("vibe_core/plugins"), Path("knowledge")]

            # Use discover_and_load to get metadata (needed for cognitive packs)
            self._plugins_map, self._plugin_metadata = PluginLoader.discover_and_load(scan_paths=scan_paths)
            self._plugins = list(self._plugins_map.values())

            # OPUS-112: Auto-register plugin capabilities from manifest (VEDA-4)
            for plugin_id, meta in self._plugin_metadata.items():
                if meta.manifest:
                    caps = meta.manifest.get("capabilities", [])
                    if caps:
                        self._capability_registry.register_agent(plugin_id, caps)
                        logger.debug(f"🔐 Plugin '{plugin_id}' capabilities registered: {caps}")

            # Check for Genesis Cognitive Pack
            genesis_meta = self._plugin_metadata.get("genesis_knowledge")
            if genesis_meta and genesis_meta.loaded_successfully:
                # Use manifest parent dir (entry_path is None for data-only packs)
                self.genesis_path = genesis_meta.manifest_path.parent if genesis_meta.manifest_path else None
                logger.info(f"🧠 Genesis Knowledge Pack loaded at: {self.genesis_path}")
                if genesis_meta.manifest.get("version"):
                    logger.info(f"   Version: {genesis_meta.manifest.get('version')}")
            else:
                logger.warning(
                    "⚠️ Genesis Knowledge Pack NOT found or failed to load - System running without base knowledge"
                )

            for plugin in self._plugins:
                plugin.on_boot(self)
        else:
            self._plugins = []
            self._plugins = []
            logger.info("🛡️ Vibe Kernel booted in Safe Mode (plugins disabled)")

        # Phase 18: Network Gateway (Sangha)
        # Using Async Sidecar pattern (Thread + Loop) to avoid blocking sync kernel
        self.gateway = NetworkGateway(self.prakriti)
        self._gateway_thread = None
        self._gateway_loop = None

    # =========================================================================
    # 4D HYPERCUBE: Phoenix Config & Ephemeral Cities
    # =========================================================================

    @property
    def config(self) -> "PhoenixConfig":
        """
        Get the kernel's configuration.

        Returns injected config if provided, otherwise global singleton.
        This enables fractal kernel spawning with custom configs.
        """
        if self._config is not None:
            return self._config

        # Lazy import to avoid circular dependencies
        from vibe_core.phoenix import get_config

        return get_config()

    @property
    def is_ephemeral(self) -> bool:
        """Check if this is an ephemeral child kernel."""
        return self._is_ephemeral

    @property
    def parent_kernel(self) -> "RealVibeKernel | None":
        """Get parent kernel (if ephemeral child)."""
        return self._parent

    def spawn_child_kernel(
        self,
        config: "PhoenixConfig",
        ledger_path: str = ":memory:",
    ) -> "RealVibeKernel":
        """
        🌀 SPAWN EPHEMERAL CITY (4D Hypercube Operation)

        Creates a child kernel with custom configuration for specialized tasks.
        The child runs in isolation and results can be folded back to parent.

        Use cases:
        - Fast coding swarm (no democracy, just execution)
        - Sandboxed experimentation (throwaway environment)
        - Specialized agent configurations

        Args:
            config: Custom PhoenixConfig for the child kernel
            ledger_path: Ledger path (default ":memory:" for ephemeral)

        Returns:
            Child RealVibeKernel instance

        Example:
            # Agent generates a custom config for fast coding
            fast_config = PhoenixConfig(...)
            fast_config.city.governance.voting_threshold = 0  # No democracy

            # Spawn ephemeral city
            child = parent_kernel.spawn_child_kernel(fast_config)

            # Execute task in child
            result = await child.execute_circuit("build_app")

            # Child dies, result folds back
            parent_kernel.merge_child_result(child, result)
        """
        logger.info(f"🌀 Spawning ephemeral child kernel (parent: {id(self)})")

        child = RealVibeKernel(
            ledger_path=ledger_path,
            config=config,
            parent=self,
        )

        self._child_kernels.append(child)
        logger.info(f"🌀 Child kernel spawned (id: {id(child)}, ephemeral: {child.is_ephemeral})")

        return child

    def get_ledger_hash(self) -> str:
        """
        Get cryptographic hash of ledger state (for proof of work).

        Used when folding child kernel results back to parent.
        """
        import hashlib

        entries = self._ledger.get_all_entries() if hasattr(self._ledger, "get_all_entries") else []
        content = str(entries).encode()
        return hashlib.sha256(content).hexdigest()[:16]

    def merge_child_result(self, child: "RealVibeKernel", result: Any) -> Dict[str, Any]:
        """
        Fold child kernel result back into parent.

        Records the merge in parent's ledger with proof from child.

        Args:
            child: The ephemeral child kernel
            result: Result from child's execution

        Returns:
            Merge record with proof
        """
        if child not in self._child_kernels:
            raise ValueError("Cannot merge result from unknown child kernel")

        merge_record = {
            "child_id": id(child),
            "child_ledger_hash": child.get_ledger_hash(),
            "result": str(result)[:500],  # Truncate large results
            "timestamp": datetime.now().isoformat(),
        }

        # Record in parent ledger
        self._ledger.record_event(
            event_type="EPHEMERAL_CITY_MERGE",
            agent_id="KERNEL",
            details=merge_record,
        )
        logger.info(f"🌀 Merged child result (proof: {merge_record['child_ledger_hash']})")

        # Remove child from tracking
        self._child_kernels.remove(child)

        return {
            "type": "EPHEMERAL_CITY_MERGE",
            **merge_record,
        }

    def get_bank(self) -> "CivicBank":
        """
        Lazy-load the CivicBank.

        Phase 4c: Use VFS path for database to ensure it's in sandbox.
        Requires: cryptography package (see pyproject.toml)
        """
        if self._bank is None:
            from pathlib import Path

            from vibe_core.cartridges.system.civic.tools.economy import CivicBank

            # OPUS-025: Config-based path resolution for bank DB
            phoenix_config = _get_config()
            if phoenix_config and hasattr(phoenix_config, "paths"):
                kernel_data_path = phoenix_config.paths.data.resolve("economy_db")
            else:
                kernel_data_path = Path("/tmp") / "vibe_os" / "kernel" / "economy.db"
            kernel_data_path.parent.mkdir(parents=True, exist_ok=True)

            self._bank = CivicBank(db_path=str(kernel_data_path))
            logger.info("🏦 Kernel loaded CivicBank (VFS-isolated)")
        return self._bank

    def get_vault(self):
        """
        Get the CivicVault instance (Lazy Loaded).

        Requires: cryptography package (see pyproject.toml)
        """
        if self._vault is None:
            from vibe_core.cartridges.system.civic.tools.vault import CivicVault

            bank = self.get_bank()
            self._vault = CivicVault(bank.conn)
            logger.info("🔐 Kernel loaded CivicVault (Lazy)")
        return self._vault

    def _check_agent_capability(self, agent_id: str, capability: str) -> bool:
        """
        SECURITY (ARCH-HARDENING): Check if agent has a specific capability.

        This method is called by ToolRegistry to enforce capability-based
        access control. It uses the IMMUTABLE capability set stored at
        registration time - runtime modifications to agent.capabilities
        are ignored.

        Args:
            agent_id: The agent requesting the capability
            capability: The capability required (e.g., "read_file")

        Returns:
            True if agent has the capability, False otherwise

        Security:
            - Uses CapabilityRegistry with revocation support
            - Agent cannot self-escalate by modifying agent.capabilities
            - Unregistered agents have NO capabilities
            - Plugin CAPABILITY GATE: Any plugin can veto via on_capability_check
        """
        # Step 1: Check CapabilityRegistry (handles core capabilities)
        has_cap = self._capability_registry.has_capability(agent_id, capability)

        if not has_cap:
            return False

        # Step 2: CAPABILITY GATE - Ask ALL plugins (generic, eternal)
        # Any plugin returning False will VETO the capability access
        for plugin in self._plugins:
            result = plugin.on_capability_check(self, agent_id, capability)
            if result is False:
                logger.info(
                    f"🚫 Capability VETOED by plugin '{plugin.plugin_id}': agent '{agent_id}' denied '{capability}'"
                )
                return False
            if result is True:
                # Explicit allow - fast path (skip remaining plugins)
                return True

        # All plugins returned None (no opinion) - allow
        return True

    def _narasimha_destroy_agent(self, agent_id: str, trigger: "ThreatIndicator") -> None:
        """⚡ NARASIMHA DESTRUCTION HANDLER - Delegates to kernel_ops."""
        _narasimha_destroy_agent_impl(self, agent_id, trigger)

    # _register_core_tools: EXTRACTED TO ToolsPlugin (vibe_core/plugins/tools/plugin_main.py)

    # _discover_agent_tools: EXTRACTED TO ToolsPlugin (vibe_core/plugins/tools/plugin_main.py)

    @property
    def agent_registry(self) -> Dict[str, VibeAgent]:
        """Get all registered agents {agent_id: agent}

        SECURITY: Returns a READ-ONLY view to prevent registry poisoning.
        Agents cannot modify the registry directly.
        Use register_agent() for registration.
        """
        from types import MappingProxyType

        return MappingProxyType(self._agent_registry)

    @property
    def scheduler(self) -> VibeScheduler:
        """Get the task scheduler"""
        return self._scheduler

    @property
    def ledger(self) -> VibeLedger:
        """Get the immutable ledger

        WARNING: Direct ledger access allows identity spoofing.
        Prefer record_verified_event() for agent-attributed events.
        """
        return self._ledger

    def record_verified_event(
        self, event_type: str, agent_id: str, details: dict, caller_agent: "VibeAgent" = None
    ) -> str:
        """Record an event with identity verification.

        SECURITY: Prevents identity spoofing by validating:
        1. The agent_id exists in the registry
        2. If caller_agent is provided, it matches the agent_id

        Args:
            event_type: Type of event
            agent_id: ID of the agent this event is attributed to
            details: Event payload
            caller_agent: Optional - the agent object making the call

        Returns:
            event_id if successful

        Raises:
            PermissionError: If agent_id is not registered or doesn't match caller
        """
        # Validate agent exists
        if agent_id != "kernel" and agent_id not in self._agent_registry:
            raise PermissionError(
                f"IDENTITY_SPOOFING_BLOCKED: Agent '{agent_id}' not registered. "
                f"Cannot record events for unregistered agents."
            )

        # If caller provided, verify it matches
        if caller_agent is not None:
            if getattr(caller_agent, "agent_id", None) != agent_id:
                raise PermissionError(
                    f"IDENTITY_SPOOFING_BLOCKED: Caller '{getattr(caller_agent, 'agent_id', 'unknown')}' "
                    f"attempted to record event as '{agent_id}'."
                )

        # Record with verified identity
        return self._ledger.record_event(event_type, agent_id, details)

    @property
    def manifest_registry(self) -> ManifestRegistry:
        """Get the manifest registry"""
        return self._manifest_registry

    @property
    def status(self) -> KernelStatus:
        """Get kernel status"""
        return self._status

    def get_system_status(self) -> dict:
        """
        GAD-000 Test 2: AI-readable system state.

        Returns structured dict for AI operators to query:
        - Current kernel status
        - Queue statistics
        - Agent states
        - Recent errors (if any)

        See: docs/architecture/OPUS/006-GAD000-COMPLIANCE-AUDIT.md
        """
        import time

        # Get queue status
        queue_status = {}
        if hasattr(self, "_scheduler") and self._scheduler:
            queue_status = self._scheduler.get_queue_status()

        # Get agent states
        agents = {}
        for agent_id, agent in self._agent_registry.items():
            agent_info = {
                "capabilities": getattr(agent, "capabilities", []),
            }
            if hasattr(agent, "status"):
                agent_info["status"] = str(agent.status)
            agents[agent_id] = agent_info

        # Get circuit count from envoy if available
        circuit_count = 0
        if hasattr(self, "envoy") and self.envoy:
            circuits = getattr(self.envoy, "_circuits", {})
            circuit_count = len(circuits)

        # Get plugin count
        plugin_count = len(self._plugins) if hasattr(self, "_plugins") else 0

        return {
            "timestamp": time.time(),
            "kernel_status": self._status.value,
            "queue": {
                "pending": queue_status.get("pending", 0),
                "in_progress": queue_status.get("in_progress", 0),
            },
            "agents": agents,
            "agent_count": len(self._agent_registry),
            "circuit_count": circuit_count,
            "plugin_count": plugin_count,
            "uptime_seconds": time.time() - self._boot_time if hasattr(self, "_boot_time") else 0,
        }

    def get_capabilities(self) -> dict:
        """
        GAD-000 Test 1: Machine-readable capability discovery.

        Returns structured schema of what this kernel can do.
        """
        return {
            "version": "1.0",
            "kernel_status": self.status.value,
            "available_methods": [
                {
                    "name": "submit_task",
                    "purpose": "Queue a task for execution",
                    "parameters": [
                        {"name": "agent_id", "type": "string", "required": True},
                        {"name": "payload", "type": "dict", "required": True},
                        {"name": "idempotency_key", "type": "string", "required": False},
                    ],
                    "returns": {"success": "task_id", "failure": "StructuredError"},
                },
                {"name": "get_system_status", "purpose": "Get current system state"},
                {"name": "get_capabilities", "purpose": "Get this schema"},
                {"name": "register_agent", "purpose": "Register a new agent"},
            ],
            "registered_agents": list(self._agent_registry.keys()),
            "available_circuits": [r["name"] for r in self._playbook_router.list_available_routes()]
            if hasattr(self, "_playbook_router")
            else [],
            "plugins_loaded": [p.plugin_id for p in self._plugins],
        }

    def register_agent(self, agent: VibeAgent, spawn_process: bool = True) -> None:
        """
        Register an agent and inject kernel reference.

        🛡️  GOVERNANCE GATE: This kernel enforces Constitutional Oath.

        An agent is REFUSED ENTRY if it has not cryptographically bound itself
        to the Constitution via the Genesis Ceremony. This is not a warning.
        This is a hard architectural constraint.

        ARCHITECTURE: Church (Steward) + State (Vibe) = Fused Governance

        Args:
            agent: The VibeAgent to register
            spawn_process: If False, defer process spawning (used during discovery
                          to avoid spawning 13+ processes in tight loop which causes
                          import lock deadlocks). Processes are spawned later via
                          spawn_registered_agents().
        """
        # OPUS-015/020: Check if agent requests process isolation
        execution_mode = getattr(agent, "_execution_mode", "thread")
        if execution_mode == "process":
            spawn_process = True
            logger.info(f"🔒 Agent '{agent.agent_id}' forcing PROCESS isolation (manifest.execution.mode=process)")

        # GOVERNANCE GATE: Let plugins decide (e.g., steward_protocol)
        for plugin in self._plugins:
            if not plugin.on_agent_pre_register(self, agent):
                raise PermissionError(
                    f"PLUGIN_VETO: Agent '{agent.agent_id}' registration denied by {plugin.plugin_id}"
                )

        # Retrieve oath_event for lineage recording (if present)
        oath_event = getattr(agent, "oath_event", None)

        # STEP 4: THE REGISTRATION (Gate Opens - Agent Enters)
        self._agent_registry[agent.agent_id] = agent

        # STEP 4.5: SECURITY (ARCH-HARDENING) - Register capabilities
        # Uses CapabilityRegistry (supports revocation + audit trail)
        agent_caps = getattr(agent, "capabilities", [])
        self._capability_registry.register_agent(agent.agent_id, agent_caps)
        logger.debug(f"🔐 Agent '{agent.agent_id}' capabilities registered: {agent_caps}")

        # GOVERNANCE HOOK: Notify plugins about new agent
        # Plugins (e.g., VedicGovernancePlugin) handle classification/lifecycle
        for plugin in self._plugins:
            plugin.on_agent_registered(self, agent.agent_id)

        # STEP 4.6: INJECT KERNEL REFERENCE (Legacy Pattern)
        # Many agents use self.kernel directly. Keep backward compatibility.
        agent.set_kernel(self)
        logger.debug(f"🔗 Agent '{agent.agent_id}' received kernel reference")

        # PHASE 1.1: INJECT SYSTEM INTERFACE (The Bridge)
        # Give agent standardized access to:
        # - Dependency Management (replaces requirements.txt)
        # - VFS (replaces direct Path() access)
        # - Config (replaces hardcoded values)
        from vibe_core.agent_interface import AgentSystemInterface

        agent.system = AgentSystemInterface(self, agent.agent_id)
        logger.info(f"🔌 {agent.agent_id} received system interface (sandbox: {agent.system.get_sandbox_path()})")

        # OPUS-009: PRAKRITI - Load or create agent persona
        # This gives the agent persistent identity and system prompt
        persona = self.prakriti.personas.get(agent.agent_id)
        if not persona:
            # Create default persona from agent manifest
            manifest = agent.get_manifest()
            persona = self.prakriti.personas.create_default(
                agent_id=agent.agent_id,
                display_name=manifest.name,
                dharma=manifest.description,
            )
            # Set varna from manifest if available
            if hasattr(manifest, "varna"):
                persona.varna = manifest.varna
            logger.info(f"🧬 Created persona for {agent.agent_id}")
        else:
            logger.info(f"🧬 Loaded existing persona for {agent.agent_id}")

        # Attach persona to agent for system prompt access
        agent.persona = persona

        # Phase 2: Spawn Process (deferred if spawn_process=False)
        # LATE BINDING: Use cartridge_path/class_name instead of type(agent)
        if spawn_process:
            cartridge_path = getattr(agent, "_cartridge_path", None)
            cartridge_class_name = getattr(agent, "_cartridge_class_name", None)
            if cartridge_path and cartridge_class_name:
                self.process_manager.spawn_agent(
                    agent.agent_id,
                    cartridge_path,
                    cartridge_class_name,
                    config=getattr(agent, "config", None),
                )
            else:
                logger.info(f"📍 Agent '{agent.agent_id}' has no cartridge_path - running in-process (no isolation)")

        # Phase 3: Set initial resource quota (default: 100 credits)
        self.resource_manager.set_quota(agent.agent_id, credits=100)
        proc_info = self.process_manager.processes.get(agent.agent_id)
        if proc_info and proc_info.process.is_alive():
            import time

            time.sleep(0.1)  # Give process time to start
            self.resource_manager.enforce_quota(agent.agent_id, proc_info.process)

        # Phase 4b: Grant repo access to Scribe/Archivist
        if agent.agent_id in ["scribe", "archivist"]:
            self._grant_repo_access(agent.agent_id)

        # Phase 5: Record in Parampara Lineage
        manifest = agent.get_manifest()
        self.lineage.add_block(
            event_type=LineageEventType.AGENT_REGISTERED,
            agent_id=agent.agent_id,
            data={
                "name": manifest.name,
                "version": manifest.version,
                "author": manifest.author,
                "capabilities": manifest.capabilities,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        # Phase 5: Record Oath Sworn (The Sacred Moment)
        if oath_event:
            self.lineage.add_block(
                event_type=LineageEventType.OATH_SWORN,
                agent_id=agent.agent_id,
                data={
                    "oath_event": oath_event,
                    "constitution_hash": oath_event.get("constitution_hash", "unknown"),
                    "timestamp": datetime.utcnow().isoformat(),
                    "verified": True,
                },
            )
            logger.info(f"⛓️  Agent '{agent.agent_id}' oath recorded in Parampara")

        spawn_status = "spawned in isolated process" if spawn_process else "registered (process deferred)"
        logger.info(f"🛡️  ✅ GOVERNANCE GATE PASSED: Agent '{agent.agent_id}' {spawn_status}.")

    def spawn_deferred_agents(self) -> int:
        """
        Spawn processes for all registered agents that don't have running processes.

        Called after discovery to batch-spawn all agents at once, avoiding the
        import lock deadlock that occurs when spawning 13+ processes in a tight loop.

        Returns:
            Number of agents spawned
        """
        spawned = 0
        for agent_id, agent in self._agent_registry.items():
            # Skip if already has a running process
            if agent_id in self.process_manager.processes:
                proc_info = self.process_manager.processes[agent_id]
                if proc_info.process.is_alive():
                    continue

            # Spawn the process (LATE BINDING)
            cartridge_path = getattr(agent, "_cartridge_path", None)
            cartridge_class_name = getattr(agent, "_cartridge_class_name", None)
            if not cartridge_path or not cartridge_class_name:
                logger.info(f"📍 Agent '{agent_id}' has no cartridge_path - running in-process (no isolation)")
                continue

            try:
                self.process_manager.spawn_agent(
                    agent_id,
                    cartridge_path,
                    cartridge_class_name,
                    config=getattr(agent, "config", None),
                )
                spawned += 1
                logger.info(f"🌱 Spawned deferred process for {agent_id}")
            except Exception as e:
                logger.error(f"❌ Failed to spawn {agent_id}: {e}")

        logger.info(f"✅ Spawned {spawned} deferred agent processes")
        return spawned

    def boot(self, boot_mode: BootMode | None = None) -> None:
        """
        Boot the kernel - register all manifests and start scheduler.

        OPUS-031 Layer 4: Supports BootMode for different execution contexts.

        Args:
            boot_mode: Optional BootMode (FULL, HEADLESS, MINIMAL).
                       If None, defaults to FULL for backward compatibility.
        """
        from vibe_core.boot_mode import BootMode

        if boot_mode is None:
            boot_mode = BootMode.FULL

        self._status = KernelStatus.BOOTING
        logger.info(f"⚙️  KERNEL BOOTING... (mode: {boot_mode.value})")

        # Phase 5: Record Kernel Boot in Parampara
        self.lineage.add_block(
            event_type=LineageEventType.KERNEL_BOOT,
            agent_id=None,
            data={
                "version": "2.0.0",
                "timestamp": datetime.utcnow().isoformat(),
                "agents_registered": len(self._agent_registry),
                "boot_mode": boot_mode.value,
            },
        )

        # Register all agent manifests
        for agent_id, agent in self._agent_registry.items():
            try:
                # Handle both VibeAgent objects and dict entries (for tests)
                if hasattr(agent, "get_manifest"):
                    manifest = agent.get_manifest()
                    self._manifest_registry.register(manifest)
                    logger.info(f"   📜 {agent_id}: {manifest.description}")
                else:
                    # Skip dict entries (test mocks)
                    logger.debug(f"   ⏭️  Skipping manifest for {agent_id} (not a VibeAgent)")
            except Exception as e:
                logger.warning(f"   ⚠️  Failed to register manifest for {agent_id}: {e}")

        self._status = KernelStatus.RUNNING
        logger.info("✅ KERNEL RUNNING")

        # OPUS-009: Inject kernel reference into Prakriti for Layer 2 access
        self.prakriti.inject_kernel(self)

        # [OPUS-027] PRAKRITI ACTIVATION (The Awakening)
        try:
            # 1. Session Start (Ghost Lock Protocol)
            self.prakriti.begin_session()

            # 2. Consistency Check (Split-Brain Prevention)
            self.prakriti.sync_ledger_git(strategy="git_wins")

            # 3. Crash Recovery
            if self.prakriti.is_dirty:
                recovery = self.prakriti.recover_from_crash()
                if recovery:
                    logger.info(f"❤️‍🩹 Recovered state from previous crash: {recovery.git_sha[:7]}")
        except Exception as e:
            logger.error(f"❌ Prakriti Boot Failure: {e}")

        # PULSE: Write initial snapshot on boot
        self._pulse()

        # Phase 18: Start Network Gateway (Async Sidecar)
        # OPUS-031 Layer 4: Skip gateway in headless mode for faster boot
        if boot_mode.should_skip_gateway():
            logger.info("🚫 Network Gateway SKIPPED (headless mode)")
        elif not self._gateway_thread or not self._gateway_thread.is_alive():
            import threading

            self._gateway_thread = threading.Thread(target=self._run_gateway_sidecar, name="VibeGateway", daemon=True)
            self._gateway_thread.start()
            logger.info("🌐 Network Gateway sidecar thread started")

    def enforce_entropy_limits(self):
        """
        SAMSARA ENGINE: Enforces mortality on the ledger.
        Removes oldest events to make room for new creation.
        """
        # We only prune InMemoryLedger (SQLite handles its own disk space usually, or needs different logic)
        # But for 'Karmic Debt' (RAM), InMemory is the culprit.
        from vibe_core.ledger import InMemoryLedger
        
        if isinstance(self._ledger, InMemoryLedger):
            # Check internal events list directly (private access for kernel management)
            if hasattr(self._ledger, "events"):
                current_entropy = len(self._ledger.events)
                
                if current_entropy > self.MAX_ENTROPY_EVENTS:
                    excess = current_entropy - self.MAX_ENTROPY_EVENTS
                    # Sacrifice the oldest to save the universe
                    self._ledger.events = self._ledger.events[excess:]
                    
                    # Log to system (not ledger) to avoid feedback loop
                    logger.warning(f"🕉️ PRALAYA EXECUTED: Dissolved {excess} stale events. Entropy reduced to {len(self._ledger.events)}.")

    def tick(self) -> None:
        """Tick the kernel - process one task from the scheduler"""
        # 1. Enforce Mortality (Fixes Memory Leak)
        self.enforce_entropy_limits()

        if self._status != KernelStatus.RUNNING:
            logger.warning("⚠️  Kernel not running")
            return

        # Plugin Hook: Pre-Tick (Input Processing)
        for plugin in self._plugins:
            plugin.on_tick_pre(self)

        # Phase 2.5: UI Synchronization (Delegated to MarkdownUIManager)
        # Handles SETTINGS.md (Command Queue) and ENVOY.md (Terminal Interface)
        # self._ui_manager.sync_all()  # DEPRECATED: Handled by Plugins

        task = self._scheduler.next_task()
        if not task:
            # No tasks - but still pulse heartbeat every 5 seconds
            import time

            if time.time() - self._last_pulse_time >= 5.0:
                self._pulse()
                self._last_pulse_time = time.time()
            return

        # Get the target agent
        agent = self._agent_registry.get(task.agent_id)
        if not agent:
            error = f"Agent {task.agent_id} not found in registry"
            logger.error(f"❌ {error}")
            self._ledger.record_failure(task, error)
            return

        # GOVERNANCE HOOK: Ask plugins if task can be assigned
        # Any plugin returning False will VETO the task
        for plugin in self._plugins:
            if not plugin.on_task_pre_assign(self, task.agent_id, task):
                logger.info(f"🚫 Task vetoed by plugin '{plugin.plugin_id}' for agent '{task.agent_id}'")
                # Re-queue the task for later (bypasses Sarga validation)
                self._scheduler.requeue_task(task)
                return

        try:
            # Record start
            self._ledger.record_start(task)

            # Check if agent has a running process (Late Binding) or runs in-process
            has_process = (
                task.agent_id in self.process_manager.processes
                and self.process_manager.processes[task.agent_id].process.is_alive()
            )

            if has_process:
                # Execute task via Process Manager (IPC) - Agent runs in separate process
                logger.info(f"⚡ Dispatching task {task.task_id} to {task.agent_id} (IPC)")
                try:
                    self.process_manager.send_task(task.agent_id, task)
                except ValueError as e:
                    structured = kernel_fault("ipc_dispatch", str(e))
                    logger.error(f"❌ IPC Dispatch failed: {structured}")
                    self._ledger.record_failure(task, str(structured))
                    return
            else:
                # Execute task directly in-process (GenericAgent or failed process spawn)
                logger.info(f"⚡ Executing task {task.task_id} on {task.agent_id} (in-process)")
                try:
                    import asyncio

                    if asyncio.iscoroutinefunction(agent.process):
                        result = asyncio.run(agent.process(task))
                    else:
                        result = agent.process(task)
                    self._ledger.record_completion(task, result)
                    logger.info(f"✅ Task {task.task_id} completed (in-process)")

                    # Plugin Hook: Task Completed
                    for plugin in self._plugins:
                        plugin.on_task_completed(self, task.task_id, result)
                except Exception as e:
                    structured = kernel_fault("in_process_execution", str(e))
                    logger.error(f"❌ In-process execution failed: {structured}")
                    self._ledger.record_failure(task, str(structured))

                    # Plugin Hook: Task Failed
                    for plugin in self._plugins:
                        plugin.on_task_failed(self, task.task_id, str(structured))
                    return

            # Record completion (Optimistic for now, or move to callback)
            # In a real async kernel, we'd wait for the result event.
            # self._ledger.record_completion(task, result)
            # logger.info(f"✅ Task {task.task_id} completed")

            # PULSE: Update snapshot after task completion
            self._pulse()

            # 🛡️ IMMUNE SYSTEM CHECK: Run Auditor after task
            self._check_system_health()

            # Phase 2: Monitor Health & Process Events
            self.process_manager.check_health()
            self._process_ipc_events()

            # Phase 3: Sync resource quotas periodically
            self._sync_resource_quotas()

            # Plugin Hook: Post-Tick (Output/Status)
            for plugin in self._plugins:
                plugin.on_tick_post(self)

        except Exception as e:
            structured = kernel_fault("task_tick", str(e))
            error = str(structured)
            logger.exception(f"❌ Task {task.task_id} failed: {error}")
            self._ledger.record_failure(task, error)

            # Plugin Hook: Task Failed
            for plugin in self._plugins:
                plugin.on_task_failed(self, task.task_id, error)

    def get_status(self) -> Dict[str, Any]:
        """Get full kernel status"""
        try:
            bank_stats = self.get_bank().get_system_stats()
            total_credits = bank_stats["total_balance"]
        except Exception as e:
            logger.warning(f"CivicBank unavailable for status: {e}")
            total_credits = 0

        return {
            "status": self._status.value,
            "agents_registered": len(self._agent_registry),
            "scheduler": self._scheduler.get_queue_status(),
            "manifests": len(self._manifest_registry.list_all()),
            "ledger_events": len(self._ledger.get_all_events()),
            "total_credits": total_credits,
        }

    def _process_ipc_events(self) -> None:
        """
        Phase 2: Process IPC messages from agents (Task Results, Crashes, etc.)
        """
        messages = self.process_manager.get_pending_messages()
        for agent_id, msg in messages:
            msg_type = msg.get("type")

            if msg_type == "TASK_RESULT":
                task_id = msg.get("task_id")
                status = msg.get("status")

                if status == "success":
                    result = msg.get("result")
                    logger.info(f"✅ Task {task_id} completed (Async IPC)")
                    # Cache result for get_task_result() polling
                    self._completed_tasks[task_id] = result

                    # ENVOY.md: Update status if this was a terminal request
                    # self._ui_manager.update_envoy_task_status(task_id, "COMPLETED", str(result) if result else "Task completed successfully")
                    # logger.info(f"📬 ENVOY task {task_id} marked COMPLETED")

                    # Plugin Hook: Task Completed
                    for plugin in self._plugins:
                        plugin.on_task_completed(self, task_id, result)

                else:
                    error = msg.get("error")
                    logger.error(f"❌ Task {task_id} failed (Async IPC): {error}")

                    # ENVOY.md: Update status if this was a terminal request
                    # self._ui_manager.update_envoy_task_status(task_id, "FAILED", str(error))
                    # logger.info(f"📬 ENVOY task {task_id} marked FAILED")

                    # Plugin Hook: Task Failed
                    for plugin in self._plugins:
                        plugin.on_task_failed(self, task_id, error)

            elif msg_type == "CRASH":
                error = msg.get("error")
                logger.critical(f"💥 Agent {agent_id} CRASHED: {error}")
                # Narasimha handles restart in check_health

    def _sync_resource_quotas(self) -> None:
        """Phase 3: Sync resource quotas - Delegates to kernel_ops."""
        _sync_resource_quotas_impl(self)

    def _grant_repo_access(self, agent_id: str) -> None:
        """Phase 4b: Grant repo access - Delegates to kernel_ops."""
        _grant_repo_access_impl(self, agent_id)

    def _check_system_health(self) -> None:
        """🛡️ IMMUNE SYSTEM WATCHDOG - Delegates to kernel_ops."""
        _check_system_health_impl(self)

    def get_agent_manifest(self, agent_id: str) -> Optional[AgentManifest]:
        """Get manifest for an agent"""
        return self._manifest_registry.lookup(agent_id)

    def shutdown(self, reason: str = "User shutdown") -> None:
        """Gracefully shut down the kernel"""
        # Phase 5: Record Kernel Shutdown in Parampara (before changing status)
        if hasattr(self, "lineage"):
            self.lineage.add_block(
                event_type=LineageEventType.KERNEL_SHUTDOWN,
                agent_id=None,
                data={
                    "reason": reason,
                    "timestamp": datetime.utcnow().isoformat(),
                    "agents_active": len(self._agent_registry),
                },
            )
            # Close lineage chain
            self.lineage.close()

        # [OPUS-027] FINAL STATE PRESERVATION
        try:
            if hasattr(self, "prakriti") and self.prakriti:
                logger.info("💾 Preserving consciousness (Prakriti End Session)...")
                result = self.prakriti.end_session()
                if result:
                    logger.info(f"✅ Final State Committed: {result.git_sha[:7]}")
        except Exception as e:
            logger.critical(f"❌ Failed to save final state: {e}")

        # Plugin Hook: Shutdown
        for plugin in self._plugins:
            plugin.on_shutdown(self)

        self._status = KernelStatus.STOPPED
        logger.critical(f"🔴 KERNEL SHUTDOWN: {reason}")

        # Phase 2: Shutdown processes
        if hasattr(self, "process_manager"):
            self.process_manager.shutdown()

        if isinstance(self._ledger, SQLiteLedger):
            self._ledger.close()

        # Phase 18: Stop Gateway
        if self._gateway_loop:
            self._gateway_loop.call_soon_threadsafe(self._gateway_loop.stop)
            logger.info("🌐 Gateway loop stop signal sent")

    # =========================================================================
    # DURVASA PROTOCOL: Resource Triage (Emergency Response)
    # =========================================================================

    def terminate_agent(self, agent_id: str, reason: str = "Unknown") -> bool:
        """
        Terminate an agent and free its resources.
        
        DURVASA PROTOCOL: This is the knife. Use it wisely.
        
        Args:
            agent_id: The agent to terminate
            reason: Why we're killing it
            
        Returns:
            True if terminated, False if not found
        """
        if agent_id not in self._agent_registry:
            logger.warning(f"⚠️ Cannot terminate unknown agent: {agent_id}")
            return False
        
        logger.warning(f"🔪 TERMINATE_AGENT: {agent_id} (reason: {reason})")
        
        # 1. Stop the process if running
        if hasattr(self, "process_manager") and agent_id in self.process_manager.processes:
            try:
                proc_info = self.process_manager.processes[agent_id]
                if proc_info.process.is_alive():
                    proc_info.process.terminate()
                    proc_info.process.join(timeout=1)
                    if proc_info.process.is_alive():
                        proc_info.process.kill()  # Force kill if still alive
                del self.process_manager.processes[agent_id]
            except Exception as e:
                logger.error(f"❌ Failed to stop process for {agent_id}: {e}")
        
        # 2. Remove from registry
        del self._agent_registry[agent_id]
        
        # 3. Revoke capabilities
        self._capability_registry.revoke(
            agent_id=agent_id,
            capabilities=["*"],  # Revoke all
            revoker_id="KERNEL",
            reason=reason
        )
        
        # 4. Log the death
        self._ledger.record_event("AGENT_TERMINATED", "kernel", {
            "agent_id": agent_id,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        logger.info(f"💀 Agent {agent_id} terminated and resources freed")
        return True

    def enforce_prana_limits(self, pressure: float = None) -> int:
        """
        DURVASA PROTOCOL: The Prana Triage Engine.
        
        Sacrifices lower-dharma agents to preserve the system core during resource famine.
        
        Args:
            pressure: Optional override for system pressure (0.0-1.0).
                     If None, uses process_manager resource monitoring.
        
        Returns:
            Number of agents sacrificed
        """
        CRITICAL_THRESHOLD = 0.90  # Start triage at 90% pressure
        SAFE_LEVEL = 0.80          # Stop when we reach 80%
        
        # 1. Measure system pressure
        if pressure is None:
            # Use process_manager to estimate pressure (count-based for now)
            total_agents = len(self._agent_registry)
            running_processes = len(self.process_manager.processes) if hasattr(self, "process_manager") else 0
            # Simulate pressure based on process count
            pressure = min(running_processes / max(total_agents, 1), 1.0)
        
        if pressure < CRITICAL_THRESHOLD:
            return 0  # No action needed
        
        logger.critical(f"🚨 DURVASA ALERT: System pressure at {pressure:.0%}. Initiating triage...")
        
        self._ledger.record_event("PRANA_EMERGENCY", "kernel", {
            "pressure": pressure,
            "msg": "Durvasa Alert triggered",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # 2. Identify candidates
        candidates = []
        for agent_id, agent in list(self._agent_registry.items()):
            # Get metadata - handle both VibeAgent objects and dict entries
            if hasattr(agent, "__dict__"):
                meta = agent.__dict__
            elif isinstance(agent, dict):
                meta = agent
            else:
                meta = {}
            
            candidates.append({
                "id": agent_id,
                "dharma": str(meta.get("dharma", "tamas")).lower(),
                "priority": str(meta.get("priority", "low")).lower()
            })
        
        # 3. Sort by sacrifice priority (lowest value = first to die)
        dharma_rank = {"tamas": 0, "rajas": 1, "sattva": 2}
        priority_rank = {"disposable": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}
        
        candidates.sort(key=lambda x: (
            dharma_rank.get(x["dharma"], 0),
            priority_rank.get(x["priority"], 0)
        ))
        
        # 4. The Sacrifice
        sacrifices = 0
        
        for victim in candidates:
            # Never kill Critical/Sattva
            if priority_rank.get(victim["priority"], 0) >= 3:
                self._ledger.record_event("TRIAGE_LIMIT", "kernel", {
                    "msg": "Only High/Critical agents remain. Holding.",
                    "remaining": [c["id"] for c in candidates if priority_rank.get(c["priority"], 0) >= 3]
                })
                break
            
            if dharma_rank.get(victim["dharma"], 0) >= 2:
                self._ledger.record_event("TRIAGE_LIMIT", "kernel", {
                    "msg": "Only Sattva agents remain. Holding."
                })
                break
            
            # Execute termination
            success = self.terminate_agent(victim["id"], reason="PRANA_FAMINE_SACRIFICE")
            
            if success:
                sacrifices += 1
                self._ledger.record_event("AGENT_SACRIFICED", "kernel", {
                    "agent": victim["id"],
                    "dharma": victim["dharma"],
                    "priority": victim["priority"],
                    "reason": "Sacrificed to appease Durvasa"
                })
                
                # Simulate pressure reduction
                pressure -= 0.10
                
                if pressure <= SAFE_LEVEL:
                    break
        
        if sacrifices > 0:
            logger.warning(f"🔱 DURVASA APPEASED: {sacrifices} agent(s) sacrificed. System stabilized.")
        
        return sacrifices

    def find_agents_by_capability(self, capability: str) -> List[VibeAgent]:
        """Find agents with a specific capability"""
        manifests = self._manifest_registry.find_by_capability(capability)
        return [self._agent_registry[m.agent_id] for m in manifests]

    def revoke_capability(
        self, agent_id: str, capabilities: List[str], revoker_id: str, reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Revoke capabilities from an agent (REVOKE_MANDATE syscall).

        Permission Model:
            - KERNEL can revoke from anyone
            - CIVIC can revoke from anyone (governance)
            - Agents can revoke from themselves (voluntary)

        Args:
            agent_id: The agent to revoke from
            capabilities: List of capabilities to revoke
            revoker_id: The agent/system performing the revocation
            reason: Optional reason for revocation

        Returns:
            Dictionary with success, revoked list, and message
        """
        # Permission check
        if not self._can_revoke_capability(revoker_id, agent_id):
            return {
                "success": False,
                "revoked": [],
                "not_found": [],
                "message": f"Permission denied: '{revoker_id}' cannot revoke from '{agent_id}'",
            }

        # Delegate to capability registry
        result = self._capability_registry.revoke(
            agent_id=agent_id, capabilities=capabilities, revoker_id=revoker_id, reason=reason
        )

        return result

    def grant_capability(
        self, agent_id: str, capabilities: List[str], granter_id: str, reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Grant capabilities to an agent.

        Permission Model:
            - KERNEL can grant to anyone
            - CIVIC can grant to anyone (governance)

        Args:
            agent_id: The agent to grant to
            capabilities: List of capabilities to grant
            granter_id: The agent/system performing the grant
            reason: Optional reason for grant

        Returns:
            Dictionary with success, granted list, and message
        """
        # Permission check (stricter than revoke - no self-grant)
        if not self._can_grant_capability(granter_id):
            return {
                "success": False,
                "granted": [],
                "already_had": [],
                "message": f"Permission denied: '{granter_id}' cannot grant capabilities",
            }

        # Delegate to capability registry
        result = self._capability_registry.grant(
            agent_id=agent_id, capabilities=capabilities, granter_id=granter_id, reason=reason
        )

        return result

    def get_agent_capabilities(self, agent_id: str) -> List[str]:
        """
        Get current capabilities for an agent.

        Args:
            agent_id: The agent to query

        Returns:
            List of capabilities (empty if unregistered)
        """
        caps = self._capability_registry.get_capabilities(agent_id)
        return sorted(caps)

    def subscribe_to_events(
        self, callback: Callable, event_type: Optional[str] = None, subscriber_id: Optional[str] = None
    ) -> str:
        """
        Subscribe to system events via EventBus.

        Args:
            callback: Function to call on event (async or sync)
            event_type: Optional filter (None = all events)
            subscriber_id: Optional ID for logging (usually agent_id)

        Returns:
            Subscription ID

        Usage:
            def on_agent_born(event):
                print(f"New agent: {event.details['agent_id']}")

            kernel.subscribe_to_events(on_agent_born, "agent.born")
        """
        sub_id = self._event_bus.subscribe(callback, event_type)

        if subscriber_id:
            logger.debug(f"📡 Agent '{subscriber_id}' subscribed to events: {event_type or 'ALL'}")
        else:
            logger.debug(f"📡 Subscriber registered for events: {event_type or 'ALL'}")

        return sub_id

    def unsubscribe_from_events(self, callback: Callable, event_type: Optional[str] = None):
        """
        Unsubscribe from system events.

        Args:
            callback: The callback to remove
            event_type: Optional event type filter
        """
        self._event_bus.unsubscribe(callback, event_type)

    async def broadcast_event(
        self, event_type: str, broadcaster_id: str, data: Optional[Dict[str, Any]] = None, message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Broadcast an event to all subscribers via EventBus.

        Args:
            event_type: Type of event (e.g., "agent.born", "transaction.complete")
            broadcaster_id: ID of agent/system broadcasting
            data: Optional event data
            message: Optional human-readable message

        Returns:
            Dictionary with event_id and subscriber count

        Usage:
            await kernel.broadcast_event(
                event_type="agent.born",
                broadcaster_id="KERNEL",
                data={"agent_id": "new_agent", "capabilities": ["read", "write"]}
            )
        """
        from .event_bus import Event

        # Create event
        event = Event(
            event_type=event_type,
            agent_id=broadcaster_id,
            message=message or f"{event_type} from {broadcaster_id}",
            details=data or {},
        )

        # Emit via EventBus
        await self._event_bus.emit(event)

        # Get subscriber count for this event type
        status = self._event_bus.get_status()
        subscriber_count = status["subscribers"].get("by_type", {}).get(event_type, 0)
        subscriber_count += status["subscribers"]["global"]  # Add global subscribers

        logger.info(f"📢 BROADCAST: {event_type} from {broadcaster_id} → {subscriber_count} subscriber(s)")

        return {
            "event_id": event.event_id,
            "event_type": event_type,
            "broadcaster": broadcaster_id,
            "subscribers_notified": subscriber_count,
            "timestamp": event.timestamp,
        }

    async def execute_playbook(
        self,
        playbook_path: str,
        input_data: Dict[str, Any],
        user_input: str = "",
    ) -> Dict[str, Any]:
        """Execute a playbook - Delegates to kernel_ops."""
        return await _execute_playbook_impl(self, playbook_path, input_data, user_input)

    def get_event_history(self, limit: int = 100, event_type: Optional[str] = None):
        """
        Get recent event history from EventBus.

        Args:
            limit: Maximum number of events to return
            event_type: Optional filter by event type

        Returns:
            List of recent events
        """
        return self._event_bus.get_history(limit=limit, event_type=event_type)

    def get_event_bus_status(self) -> Dict[str, Any]:
        """
        Get the current status of the EventBus.

        Returns:
            Dict containing event bus statistics (total events, subscribers, etc.)
        """
        return self._event_bus.get_status()

    def get_trace(self, trace_id: str) -> List[Dict[str, Any]]:
        """
        GAD-000 Test 2: Observability.

        Get machine-readable execution history for a specific trace.
        """
        return self.trace.get_trace(trace_id)

    def _can_revoke_capability(self, revoker_id: str, target_id: str) -> bool:
        """
        Check if revoker_id has permission to revoke capabilities from target_id.

        Permission Model:
            - KERNEL can revoke from anyone
            - CIVIC can revoke from anyone (governance)
            - Agents can revoke from themselves (voluntary)
            - NARASIMHA can revoke from anyone (kill-switch)
        """
        # Kernel and system have full permissions
        if revoker_id in ["KERNEL", "NARASIMHA", "civic"]:
            return True

        # Self-revocation allowed (Principle of Least Privilege)
        if revoker_id == target_id:
            return True

        # All other cases denied
        return False

    def _can_grant_capability(self, granter_id: str) -> bool:
        """
        Check if granter_id has permission to grant capabilities.

        Permission Model:
            - KERNEL can grant to anyone
            - CIVIC can grant to anyone (governance)
            - No self-grant (prevents privilege escalation)
        """
        # Only kernel and civic can grant
        return granter_id in ["KERNEL", "civic"]

    def submit_task(self, task: Task) -> str:
        """Submit a task to the kernel.

        PLUGIN HOOK: Calls on_task_submit for all plugins before queue.
        Plugins can VETO by raising ValueError.
        """
        # COSMIC GATE: Ask plugins if task can be submitted
        # Any plugin can raise ValueError to reject the task
        for plugin in self._plugins:
            plugin.on_task_submit(self, task)

        return self._scheduler.submit_task(task)

    def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the result of a completed task"""
        # First check in-memory cache (for async IPC results)
        if task_id in self._completed_tasks:
            return self._completed_tasks[task_id]

        # Fallback to ledger (for sync results)
        event = self._ledger.get_task(task_id)
        if event and event.get("event_type") == "task_completed":
            return {
                "status": "COMPLETED",
                "task_id": task_id,
                "output_result": event.get("result"),
            }
        elif event and event.get("event_type") == "task_failed":
            return {
                "status": "FAILED",
                "task_id": task_id,
                "error": event.get("error"),
            }
        return None

    def dump_ledger(self) -> List[Dict[str, Any]]:
        """Dump full ledger for inspection"""
        return self._ledger.get_all_events()

    def _pulse(self) -> None:
        """💓 HEARTBEAT - Delegates to kernel_ops."""
        _pulse_impl(self)

    # ========================================================================
    # ENVOY.md: Terminal Interface (User Chat + Task Dispatch)
    # ========================================================================
    # ASYNC DISPATCH PATTERN:
    # 1. User writes request in ENVOY.md "Request" section
    # 2. Pulse detects change (fast mtime check)
    # 3. PlaybookRouter.route() - pattern match only, NO LLM
    # 4. Create Task, submit to scheduler (non-blocking)
    # 5. Write "QUEUED" status to ENVOY.md
    # 6. Scheduler executes task async (separate tick)
    # 7. Update ENVOY.md with result when complete
    # ========================================================================

    def _run_gateway_sidecar(self):
        """
        Phase 18: Async Sidecar Entry Point.
        Runs the NetworkGateway in a dedicated asyncio loop/thread.
        """
        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self._gateway_loop = loop

        try:
            loop.run_until_complete(self.gateway.start())
            loop.run_forever()
        except Exception as e:
            logger.error(f"🌐 Gateway Sidecar crashed: {e}")
        finally:
            loop.run_until_complete(self.gateway.stop())
            loop.close()
            logger.info("🌐 Gateway Sidecar shutdown complete")
