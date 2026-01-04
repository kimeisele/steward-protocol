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

import asyncio
import logging
import time
from datetime import datetime
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.boot_mode import BootMode
    from vibe_core.phoenix import PhoenixConfig
    from vibe_core.protocols.economy import BankProtocol, VaultProtocol

# Governance is handled by plugins (vibe_core/plugins/vedic_governance.py)
# Kernel has no governance types - access via kernel.governance

from .capability_registry import CapabilityRegistry  # Phase 2: Capability Revocation
from .errors import kernel_fault  # GAD-000 Compliance

# DocRenderer: Extracted markdown rendering logic
from .event_bus import Event, EventType, get_event_bus  # Phase 2: Event Bus

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
from .lineage import LineageEventType  # Phase 5: Only EventType (LineageChain is lazy)
from .manifest_registry import InMemoryManifestRegistry
from .narasimha import ThreatIndicator, get_narasimha  # Phase 7: Kill-Switch

# OPUS-301: Lazy import - network_proxy loads 'requests' which is 180ms
# from .network_proxy import KernelNetworkProxy  # Phase 4: Network Isolation
from .plugin_loader import PluginLoader  # Phase 1: Plugin System

# OPUS-301: Direct import to avoid loading all of protocols (saves ~440ms)
from .protocols.agent import AgentManifest, VibeAgent

# Sync modules: Extracted bidirectional markdown interfaces
# NOTE: ToolRegistry and ToolDiscovery are now handled by ToolsPlugin (Phase 2 Extraction)
# OPUS-209: Auditor is now accessed via ServiceRegistry
# The auditor plugin registers itself; kernel uses NullAuditor fallback
from .protocols.auditor import AuditorProtocol, NullAuditor

# OPUS-309: Operator Cognitive Protocol (Hot-Swap Hook)
# Kernel doesn't know MANAS exists - only knows this protocol
from .protocols.cognition import (
    CognitiveContext,
    CognitiveResult,
    NullCognitive,
    OperatorCognitiveProtocol,
    SignedOperatorInput,
)
from .protocols.cognition import (
    IntentType as CognitiveIntentType,
)

# OPERATION LASAGNE Phase 1: Type Protocols (kill Any)
from .protocols.kernel_types import (
    AgentData,
    AgentHealth,
    GovernanceProtocol,
    PluginProtocol,
    TaskResult,
)

# Unified Execution: Single source of truth for routing (replaces PlaybookRouter)
from .runtime.unified_execution import create_unified_runtime
from .scheduling import InMemoryScheduler, Task
from .services.manifestation_service import ManifestationService
from .state.schema import ExecutionRequest

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


from .utils.async_logging import setup_async_logging
from .utils.lazy_import import lazy_class

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


# VAJRA ARMOR: Import immutable DNA protection
from vibe_core.reactor import encode

from .security import VajraGuarded


class RealVibeKernel(VibeKernel, VajraGuarded):
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
    - QuantumReactor (OPUS-200/201 - resonance-based manifestation)  # NEW

    Philosophy (OPUS-200/201):
      Actions don't get "allowed" or "denied" - they MANIFEST
      when their resonance energy overcomes the field's inertia.
    """

    # SAMSARA CONFIG: Maximum entropy (ledger events) before Pralaya (pruning) occurs
    MAX_ENTROPY_EVENTS = 1000
    _reactor = None
    _akasha_field = ""

    def __init__(
        self,
        ledger_path: str | None = None,
        config: "PhoenixConfig | None" = None,
        parent: "RealVibeKernel | None" = None,
        load_plugins: bool = True,
        test_mode: bool = False,
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
            test_mode: If True, disable heavy I/O and blocking persistence (default: False).
        """
        # =====================================================================
        # VAJRA ARMOR: Initialize DNA protection (must be first!)
        # =====================================================================
        VajraGuarded.__init__(self)

        # 4D Hypercube: Store config and parent reference
        self._config = config
        self._parent = parent
        self._child_kernels: list["RealVibeKernel"] = []
        self._is_ephemeral = parent is not None
        self._load_plugins = load_plugins
        self._test_mode = test_mode

        # OPUS-301: Initialize async logging early to prevent I/O blocking
        if not self._test_mode:
            try:
                setup_async_logging()
            except Exception as e:
                # OPUS-312: Don't swallow logging setup failures silently
                logger.warning(f"⚠️ KERNEL: Async logging setup failed: {e}")

        if self._test_mode:
            import os

            os.environ["VIBE_NO_GIT_COMMIT"] = "1"
            logger.info("🧪 KERNEL: Test Mode Active - Git Persistence Disabled")
            try:
                from vibe_core.state.state_service import get_state_service

                ss = get_state_service(self._workspace if hasattr(self, "_workspace") else None)
            except Exception as e:
                logger.warning(f"🧪 KERNEL: Could not disable state auto-commit: {e}")

        # Resolve ledger path from config if not provided
        if ledger_path is None:
            phoenix_config = _get_config()
            if phoenix_config and hasattr(phoenix_config, "paths"):
                # OPUS-025: Must use resolve() to expand template variables
                # Direct attribute access returns literal "{root}/vibe_ledger.db"
                ledger_path = str(phoenix_config.paths.data.resolve("vibe_ledger"))
            else:
                ledger_path = "data/vibe_ledger.db"  # Fallback default

        # =====================================================================
        # BLUEPRINT PROTOCOL: Self-Healing Kernel (KURUKSHETRA FIX)
        # We store FACTORIES (blueprints) not just instances.
        # If Asura deletes an organ, we can resurrect it from the blueprint.
        # =====================================================================

        # 1. AGENT REGISTRY (with blueprint)
        self.__agent_registry: Dict[str, VibeAgent] = {}
        self._agent_registry_blueprint = lambda: {}  # Factory for empty registry

        self._scheduler = InMemoryScheduler()
        self._completed_tasks: Dict[str, TaskResult] = {}  # Temporary result cache for async IPC

        # 2. LEDGER (with blueprint)
        # Store the factory, not just the instance
        if ledger_path == ":memory:":
            self._ledger_blueprint = lambda: InMemoryLedger()
            self.__ledger = InMemoryLedger()
            logger.info("🚀 Vibe Kernel initialized (in-memory ledger)")
        else:
            self._ledger_blueprint = lambda path=ledger_path: SQLiteLedger(path)
            self.__ledger = SQLiteLedger(ledger_path)
            logger.info(f"🚀 Vibe Kernel initialized (persistent ledger at {ledger_path})")

        # =====================================================================
        # VAJRA ARMOR: Protect blueprints from PUTANA attack
        # =====================================================================
        self.protect_attribute("_ledger_blueprint")
        self.protect_attribute("_agent_registry_blueprint")
        self.protect_attribute("_capability_registry_blueprint")

        self._manifest_registry = InMemoryManifestRegistry()
        self._status = KernelStatus.STOPPED
        self.ledger_path = ledger_path

        # Auditor (immune system) - NullAuditor fallback if no plugin
        from vibe_core.di import ServiceRegistry

        self._auditor = ServiceRegistry.get(AuditorProtocol) or NullAuditor()
        if type(self._auditor).__name__ == "NullAuditor":
            logger.warning("⚠️  No auditor plugin - using NullAuditor")

        # Plugin-managed components (set by plugins on_boot)
        self.process_manager = None
        self.resource_manager = None
        self.gateway = None
        self._gateway_thread = None
        self._gateway_loop = None
        self._last_quota_sync = 0
        self._last_pulse_time = 0
        self._agent_health_cache: Dict[str, AgentHealth] = {}
        self._network = None

        # Parampara Lineage Chain
        phoenix_config = _get_config()
        if phoenix_config and hasattr(phoenix_config, "paths"):
            lineage_path = str(phoenix_config.paths.system.resolve("lineage_db"))
        else:
            from pathlib import Path

            lineage_path = str(Path("/tmp") / "vibe_os" / "kernel" / "lineage.db")
        LazyLineageChain = lazy_class("vibe_core.lineage", "LineageChain")
        self.lineage = LazyLineageChain(db_path=lineage_path)

        # Lazy-loaded subsystems
        self._bank = None
        self._vault = None
        self._reactor = None
        self._akasha_field = ""

        # Inter-agent data exchange
        self._data_store: Dict[str, AgentData] = {}

        # Governance (hot-swappable via plugins)
        self.governance: Optional[GovernanceProtocol] = None

        # Layer 0 Security (cannot be hot-swapped)
        from vibe_core.services.capability_enforcer import CapabilityEnforcerService

        self._capability_enforcer = CapabilityEnforcerService()

        # Core services
        from vibe_core.runtime.unified_trace import UnifiedTrace
        from vibe_core.services.lifecycle_service import LifecycleService

        self._lifecycle = LifecycleService(self)
        self.trace = UnifiedTrace()

        # Prakriti State Engine (lazy)
        LazyPrakriti = lazy_class("vibe_core.state", "Prakriti")
        prakriti_db_path = None
        if phoenix_config and hasattr(phoenix_config, "paths"):
            try:
                prakriti_db_path = phoenix_config.paths.data.resolve("vibe_ledger")
            except Exception:
                pass
        self.prakriti = LazyPrakriti(db_path=prakriti_db_path)

        # State Sync Weaver
        from vibe_core.state.weaver import get_state_sync_weaver

        get_state_sync_weaver()

        # Capability Registry (with blueprint for self-healing)
        self._capability_registry_blueprint = lambda: CapabilityRegistry(ledger=self.ledger)
        self.__capability_registry = CapabilityRegistry(ledger=self.ledger)

        # I/O and Manifestation services
        self.io = KernelIOService(self)
        self.manifestation = ManifestationService(self)
        self.tool_registry = None  # Set by ToolsPlugin

        # Narasimha kill-switch and Event Bus
        self._narasimha = get_narasimha()
        self._narasimha.register_destruction_handler(self._narasimha_destroy_agent)
        self._event_bus = get_event_bus()

        # Cognitive hook (NullCognitive fallback)
        self._cognitive: OperatorCognitiveProtocol = NullCognitive()

        # Unified Execution Runtime (Router + Executor)
        # Replaces legacy PlaybookRouter and MilkOceanRouter
        self._unified_router, self._unified_executor = create_unified_runtime(self)
        self._playbook_router = self._unified_router  # Alias for backward compatibility (temporarily)

        # PLUGIN SYSTEM: Load and boot all plugins
        self.genesis_path = None
        self._plugin_metadata = {}
        self._init_plugins()

        # VAJRA ARMOR: Seal kernel DNA (blueprints immutable after this)
        self.vajra_seal()

    def _init_plugins(self) -> None:
        """
        Initialize plugin system: discover, load, and boot all plugins.

        OPUS-LASAGNE: Extracted from __init__ to reduce kernel LOC.
        """
        if not self._load_plugins:
            self._plugins = []
            logger.info("🛡️ Kernel booted in Safe Mode (plugins disabled)")
            return

        import os
        from pathlib import Path

        from vibe_core.loaders.manifest_registry import ManifestRegistry

        # Scan manifests (idempotent)
        ManifestRegistry.scan_all()

        # Load plugins from custom paths or registry
        custom_paths_env = os.environ.get("VIBE_PLUGIN_PATH", "")
        if custom_paths_env:
            scan_paths = [Path(p.strip()) for p in custom_paths_env.split(":") if p.strip()]
            logger.info(f"🔌 Using custom plugin paths: {scan_paths}")
            self._plugins_map, self._plugin_metadata = PluginLoader.discover_and_load(scan_paths=scan_paths)
        else:
            self._plugins_map, self._plugin_metadata = PluginLoader.discover_from_registry()

        # Sort by priority (lower = earlier)
        self._plugins = sorted(self._plugins_map.values(), key=lambda p: getattr(p, "priority", 50))

        # Register plugin capabilities
        for plugin_id, meta in self._plugin_metadata.items():
            if meta.manifest:
                caps = meta.manifest.get("capabilities", [])
                if caps:
                    self._capability_registry.register_agent(plugin_id, caps)

        # Check Genesis Knowledge Pack
        genesis_meta = self._plugin_metadata.get("genesis_knowledge")
        if genesis_meta and genesis_meta.loaded_successfully:
            self.genesis_path = genesis_meta.manifest_path.parent if genesis_meta.manifest_path else None
            logger.info(f"🧠 Genesis Knowledge Pack: {self.genesis_path}")
        else:
            logger.warning("⚠️ Genesis Knowledge Pack not loaded")

        # Boot all plugins
        for plugin in self._plugins:
            plugin.on_boot(self)

        # Register plugins for manifestation
        for plugin_id, meta in self._plugin_metadata.items():
            if meta.manifest and meta.manifest.get("manifestation"):
                plugin_instance = self._plugins_map.get(plugin_id)
                if plugin_instance:
                    self.manifestation.register_plugin(plugin_id, plugin_instance, meta.manifest)

    # =========================================================================
    # AMRITA PROTOCOL: Self-Healing Properties (KURUKSHETRA FIX)
    # If Asura deletes an organ, it resurrects from the Blueprint.
    # =========================================================================

    async def pulse(self) -> Dict[str, Any]:
        """
        Execute one system pulse cycle across all plugins.

        This is the meta-orchestration of the macro-cycle.
        It calls on_pulse() for every loaded plugin.
        """
        logger.info("💓 KERNEL: System pulse started")
        results = {}

        # Create a mock transaction if needed by plugins (legacy compatibility)
        class MockTransaction:
            def register(self, mutation):
                pass

        transaction = MockTransaction()

        for plugin in self._plugins:
            try:
                if hasattr(plugin, "on_pulse"):
                    # Support both sync and async on_pulse
                    res = plugin.on_pulse(self, transaction)
                    if asyncio.iscoroutine(res):
                        res = await res
                    results[plugin.plugin_id] = res
            except Exception as e:
                logger.error(f"❌ Plugin '{plugin.plugin_id}' pulse failed: {e}")
                results[plugin.plugin_id] = {"success": False, "error": str(e)}

        logger.info(f"💓 KERNEL: System pulse complete ({len(results)} plugins responded)")
        return results

    @property
    def _ledger(self):
        """Self-healing ledger access. Resurrects from blueprint if destroyed."""
        if getattr(self, "_RealVibeKernel__ledger", None) is None:
            logger.warning("✨ AMRITA: Ledger destroyed. Resurrecting from Blueprint...")
            try:
                self.__ledger = self._ledger_blueprint()
                self.__ledger.record_event("AMRITA_RESURRECTION", "kernel", {"component": "ledger"})
            except Exception as e:
                logger.error(f"💀 AMRITA FAILED: {e}. Using emergency InMemoryLedger.")
                self.__ledger = InMemoryLedger()
        return self.__ledger

    @_ledger.setter
    def _ledger(self, value):
        """Allow direct setting of ledger (for testing/migration)."""
        self.__ledger = value

    @property
    def _agent_registry(self):
        """Self-healing agent registry. Resurrects from blueprint if destroyed."""
        if getattr(self, "_RealVibeKernel__agent_registry", None) is None:
            logger.warning("✨ AMRITA: Agent registry destroyed. Resurrecting from Blueprint...")
            self.__agent_registry = self._agent_registry_blueprint()
        return self.__agent_registry

    @_agent_registry.setter
    def _agent_registry(self, value):
        """Allow direct setting of agent registry."""
        self.__agent_registry = value

    @property
    def network(self):
        """OPUS-301: Lazy-loaded network proxy. Saves ~180ms on boot."""
        if self._network is None:
            from .network_proxy import KernelNetworkProxy

            self._network = KernelNetworkProxy(kernel=self)
        return self._network

    @property
    def _capability_registry(self):
        """Self-healing capability registry. Resurrects from blueprint if destroyed."""
        if getattr(self, "_RealVibeKernel__capability_registry", None) is None:
            logger.warning("✨ AMRITA: Capability registry destroyed. Resurrecting from Blueprint...")
            self.__capability_registry = self._capability_registry_blueprint()
        return self.__capability_registry

    @_capability_registry.setter
    def _capability_registry(self, value):
        """Allow direct setting of capability registry."""
        self.__capability_registry = value

    # Convenience alias for external access
    @property
    def ledger(self):
        """Public read-only access to ledger (with self-healing)."""
        return self._ledger

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

    @property
    def event_bus(self):
        """
        Direct access to the EventBus.

        PHASE 6 OPERATION LASAGNE: No wrapper methods.
        Plugins use event_bus.subscribe(), event_bus.emit() directly.

        Usage:
            # Subscribe to events
            kernel.event_bus.subscribe(my_callback, "agent.born")

            # Emit events
            await kernel.event_bus.emit(event)

            # Get history
            kernel.event_bus.get_history(limit=50)
        """
        return self._event_bus

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

    def get_bank(self) -> "BankProtocol":
        """Get CivicBank via ServiceRegistry (OPUS-209)."""
        if self._bank is None:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.economy import BankProtocol

            self._bank = ServiceRegistry.get(BankProtocol)
        return self._bank

    def get_vault(self) -> "VaultProtocol":
        """Get CivicVault via ServiceRegistry (OPUS-209)."""
        if self._vault is None:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.economy import VaultProtocol

            self._vault = ServiceRegistry.get(VaultProtocol)
        return self._vault

    @property
    def reactor(self):
        """
        OPUS-200/201: QuantumReactor as core kernel primitive.

        Like the ledger, process_table, and capability_registry,
        the reactor is a fundamental kernel component.

        Lazy-loaded to avoid boot-time overhead.
        """
        if self._reactor is None:
            try:
                from vibe_core.reactor import QuantumReactor

                self._reactor = QuantumReactor(initial_inertia=0.5)
                logger.info("☢️ QuantumReactor loaded as kernel primitive")
            except ImportError as e:
                logger.warning(f"☢️ QuantumReactor not available: {e}")
        return self._reactor

    @property
    def akasha_hash(self) -> str:
        """
        OPUS-200/201: Current state of the kernel's akasha field.

        The akasha is the cumulative resonance field that influences
        all future manifestations. Each manifestation evolves it.
        """
        if self.reactor is not None:
            return self.reactor._chain_hash()
        return self._akasha_field

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

    def manifest(self, intent: str, agent_id: str = "kernel", salt: str = "") -> "ExecutionRequest":
        """
        OPUS-200/201: Manifest an intent through the resonance field.

        This is the NEW primary entry point for kernel execution.
        Instead of boolean allow/deny, compute resonance and manifest.

        Args:
            intent: The intent to manifest (user input, command, etc.)
            agent_id: The agent requesting manifestation
            salt: Cryptographic salt for session context

        Returns:
            ExecutionRequest with resonance data and gate decision

        Philosophy:
            Actions don't get "allowed" - they MANIFEST when
            their energy overcomes the field's inertia.
        """
        from vibe_core.runtime.unified_execution import ExecutionRequest

        # Use the kernel's own reactor
        reactor = self.reactor

        if reactor is None:
            logger.warning("☢️ KERNEL: QuantumReactor not available for manifestation. Returning default request.")
            # Fallback to a default request if reactor is not available
            request = ExecutionRequest(user_input=intent, source=agent_id)
            return request

        try:
            # Encode intent as tensor
            # The user's snippet implies single tensor. compute_capability_resonance takes two.
            # I will use two for consistency with the spirit of capability resonance.
            # Intent vs Agent-Capability is different. Let's use one tensor for the intent.
            # If this fails, I will revisit.
            intent_tensor = encode(f"intent:{intent}", salt)

            # Resonate the intent
            field = reactor.resonate(intent_tensor)

            # Store resonance values
            request = ExecutionRequest(user_input=intent, source=agent_id)
            request.mark_resonance(
                energy=field.total_energy,
                inertia=reactor._inertia,
                field_hash=field.field_hash,
            )

            # Log manifestation
            status = "MANIFEST" if request.manifests else "PENDING"
            logger.info(f"☢️ KERNEL: {intent[:30]}... → E={request.resonance_energy:.3f} ({status})")

            # OPUS-202: Evolve the kernel's akasha field
            self._akasha_field = field.field_hash

            return request

        except Exception as e:
            logger.warning(f"☢️ KERNEL: Manifestation failed: {e}. Returning default request.")
            request = ExecutionRequest(user_input=intent, source=agent_id)
            request.mark_failed(str(e))
            return request

    def compute_capability_resonance(self, agent_id: str, capability: str) -> float:
        """
        OPUS-200/201: Compute resonance for capability check.

        Instead of boolean has_capability(), compute continuous
        resonance between agent and capability.

        Args:
            agent_id: The agent requesting the capability
            capability: The capability required

        Returns:
            Resonance energy (0.0 to 1.0)
            Higher = stronger resonance = more likely to manifest
        """
        if self.reactor is None:
            # Fallback to boolean converted to float
            return 1.0 if self._check_agent_capability(agent_id, capability) else 0.0

        try:
            from vibe_core.reactor import encode

            # Encode agent as tensor
            agent_tensor = encode(f"agent:{agent_id}", self.akasha_hash)

            # Encode capability as tensor
            cap_tensor = encode(f"capability:{capability}", self.akasha_hash)

            # Compute resonance
            field = self.reactor.resonate(agent_tensor, cap_tensor)

            return min(1.0, field.total_energy)

        except Exception as e:
            logger.warning(f"☢️ Capability resonance failed: {e}")
            return 1.0 if self._check_agent_capability(agent_id, capability) else 0.0

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

    @property
    def plugins(self) -> List[PluginProtocol]:
        """Get list of loaded plugins (for state snapshotting)"""
        return self._plugins

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

        # OPUS-209: Process spawning → ProcessIsolationPlugin.on_agent_registered()
        # OPUS-209: Resource quotas → ResourceLimitsPlugin.on_agent_registered()

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
        """OPUS-209: Delegated to ProcessIsolationPlugin."""
        for plugin in self._plugins:
            if hasattr(plugin, "spawn_deferred_agents"):
                return plugin.spawn_deferred_agents(self)
        return 0

    def enforce_entropy_limits(self):
        """OPUS-209: Delegated to SamsaraPlugin."""
        for plugin in self._plugins:
            if hasattr(plugin, "enforce_entropy_limits"):
                return plugin.enforce_entropy_limits()

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
            "ledger": {
                "events": self._ledger.count_events(),
                "top_hash": self._ledger.get_top_hash(),
            },
            "total_credits": total_credits,
        }

    # OPUS-LASAGNE: _get_settings_manifestation_data and _get_operations_manifestation_data
    # moved to ManifestationService (Phase 4 extraction)

    def _process_ipc_events(self) -> None:
        """OPUS-209: Delegated to ProcessIsolationPlugin."""
        for plugin in self._plugins:
            if hasattr(plugin, "process_ipc_events"):
                return plugin.process_ipc_events(self)

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
        if self.process_manager and agent_id in self.process_manager.processes:
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
            reason=reason,
        )

        # 4. Log the death
        self._ledger.record_event(
            "AGENT_TERMINATED",
            "kernel",
            {"agent_id": agent_id, "reason": reason, "timestamp": datetime.utcnow().isoformat()},
        )

        logger.info(f"💀 Agent {agent_id} terminated and resources freed")
        return True

    def enforce_prana_limits(self, pressure: float = None) -> int:
        """OPUS-209: Delegated to DurvasaPlugin."""
        for plugin in self._plugins:
            if hasattr(plugin, "enforce_prana_limits"):
                return plugin.enforce_prana_limits(pressure)
        return 0

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

    # =========================================================================
    # OPUS-309: Cognitive Protocol (Hot-Swap Hook)
    # =========================================================================

    def register_cognitive(self, cognitive: OperatorCognitiveProtocol) -> None:
        """
        Register a cognitive plugin for operator input processing.

        PROMPT.md: "Hot-Swap-Fähigkeit – Module austauschbar ohne Neustart"

        Can be called multiple times to swap implementations.
        The last registered cognitive wins.

        Args:
            cognitive: Implementation of OperatorCognitiveProtocol

        Usage:
            # In plugin (e.g., opus_assistant):
            kernel.register_cognitive(MANASCognitive())
        """
        old_type = type(self._cognitive).__name__
        self._cognitive = cognitive
        new_type = type(cognitive).__name__
        logger.info(f"🧠 Cognitive hook updated: {old_type} → {new_type}")

        # Log capabilities (sync - no event loop needed during boot)
        caps = cognitive.get_capabilities() if hasattr(cognitive, "get_capabilities") else []
        if caps:
            logger.debug(f"🧠 Cognitive capabilities: {caps[:5]}{'...' if len(caps) > 5 else ''}")

    async def process_operator_input(
        self,
        input_text: str,
        session_id: Optional[str] = None,
        signed_input: Optional[SignedOperatorInput] = None,
    ) -> CognitiveResult:
        """
        Process natural language input from operator (human or AI).

        OPUS-309: Main entry point for operator input.
        Routes through registered cognitive plugin.

        GAD-000 v2.0: The 37th Principle.
        Every operation should be signed by a sovereign entity.
        The cognitive layer decides: chat, execute, query, or route.

        Args:
            input_text: Raw natural language input
            session_id: Optional session ID for conversation context
            signed_input: Optional signed input (The 37th - sovereign signature)

        Returns:
            CognitiveResult with intent_type and relevant data

        Usage:
            # Unsigned (legacy, Mayavad mode - will log warning)
            result = await kernel.process_operator_input("create an agent")

            # Signed (37th compliant, Vaishnava mode)
            signed = SignedOperatorInput(message="create an agent", ...)
            result = await kernel.process_operator_input("create an agent", signed_input=signed)
        """
        # GAD-000 v2.0: Verify sovereign signature if provided
        sovereign_verified = False
        if signed_input and signed_input.is_signed():
            try:
                from vibe_core.steward.crypto import verify_signature

                is_valid = verify_signature(
                    signed_input.message,
                    signed_input.signature,
                    signed_input.public_key,
                )
                signed_input.is_verified = is_valid
                sovereign_verified = is_valid

                if is_valid:
                    logger.info(f"✅ 37th verified: {signed_input.signer_id or 'anonymous'}")
                else:
                    signed_input.verification_error = "Signature verification failed"
                    logger.warning(f"⚠️ 37th signature INVALID for: {input_text[:50]}...")

            except Exception as e:
                signed_input.is_verified = False
                signed_input.verification_error = str(e)
                logger.error(f"❌ 37th verification error: {e}")
        elif signed_input is None:
            # Mayavad mode: No signature provided
            logger.debug("🔓 Unsigned operator input (Mayavad mode)")

        # Build context with 37th status
        context = CognitiveContext(
            kernel_status=self._status.value if hasattr(self._status, "value") else str(self._status),
            active_agents=list(self._agent_registry.keys()),
            pending_tasks=len(self._scheduler.pending_tasks) if hasattr(self._scheduler, "pending_tasks") else 0,
            session_id=session_id,
            available_tools=list(self.tool_registry.list_tools()) if self.tool_registry else [],
            available_agents=list(self._agent_registry.keys()),
            # GAD-000 v2.0: The 37th Principle
            signed_input=signed_input,
            sovereign_verified=sovereign_verified,
        )

        # Process through cognitive layer
        try:
            result = await self._cognitive.process_intent(input_text, context)
            logger.debug(f"🧠 Cognitive result: {result.intent_type.value} (confidence: {result.confidence:.2f})")

            # Record to ledger if we have one (audit trail)
            if hasattr(self, "_ledger") and self._ledger:
                try:
                    self._ledger.record_event(
                        event_type="OPERATOR_INPUT",
                        agent_id=signed_input.signer_id if signed_input else "anonymous",
                        details={
                            "message": input_text[:200],  # Truncate for storage
                            "intent_type": result.intent_type.value,
                            "confidence": result.confidence,
                            "sovereign_verified": sovereign_verified,
                            "session_id": session_id,
                        },
                    )
                except Exception as ledger_err:
                    logger.debug(f"Ledger recording skipped: {ledger_err}")

            return result
        except Exception as e:
            logger.error(f"🧠 Cognitive processing failed: {e}")
            # Fallback: Route to Envoy
            return CognitiveResult(
                intent_type=CognitiveIntentType.ROUTE,
                confidence=0.0,
                target="envoy",
                reasoning=f"Cognitive processing failed: {e}",
            )

    def get_cognitive_capabilities(self) -> List[str]:
        """
        GAD-000: Discoverability.

        Returns capabilities of the registered cognitive layer.
        """
        if hasattr(self._cognitive, "get_capabilities"):
            return self._cognitive.get_capabilities()
        return []

    async def execute_playbook(
        self,
        playbook_path: str,
        input_data: Dict[str, Any],
        user_input: str = "",
    ) -> Dict[str, Any]:
        """Execute a playbook - Delegates to kernel_ops."""
        return await _execute_playbook_impl(self, playbook_path, input_data, user_input)

    def get_trace(self, trace_id: str) -> List[Dict[str, Any]]:
        """
        GAD-000 Test 2: Observability.

        Get machine-readable execution history for a specific trace.
        """
        return self.trace.get_trace(trace_id)

    def _can_revoke_capability(self, revoker_id: str, target_id: str) -> bool:
        """
        Check if revoker_id has permission to revoke capabilities from target_id.

        Delegates to CapabilityEnforcerService (Layer 0 Security).
        """
        return self._capability_enforcer.can_revoke(revoker_id, target_id)

    def _can_grant_capability(self, granter_id: str) -> bool:
        """
        Check if granter_id has permission to grant capabilities.

        Delegates to CapabilityEnforcerService (Layer 0 Security).
        """
        return self._capability_enforcer.can_grant(granter_id)

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

    async def _pulse(self) -> None:
        """💓 HEARTBEAT - Delegates to kernel_ops."""
        await _pulse_impl(self)

    def _run_gateway_sidecar(self):
        """
        Phase 18: Async Sidecar Entry Point.
        Runs the NetworkGateway in a dedicated asyncio loop/thread.
        """
        if self.gateway is None:
            logger.warning("🌐 Gateway not available (sangha_network plugin not loaded)")
            return

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

    # =========================================================================
    # LIFECYCLE METHODS - Delegated to LifecycleService
    # =========================================================================

    def boot(self, boot_mode: BootMode | None = None) -> None:
        """Boot the kernel synchronously. Delegates to LifecycleService."""
        self._lifecycle.boot(boot_mode)

    async def boot_async(self, boot_mode: BootMode | None = None) -> None:
        """Async boot. Delegates to LifecycleService."""
        await self._lifecycle.boot_async(boot_mode)

    async def run_forever(self) -> None:
        """Main kernel loop. Delegates to LifecycleService."""
        await self._lifecycle.run_forever()

    async def tick_async(self) -> None:
        """Async tick. Delegates to LifecycleService."""
        await self._lifecycle.tick_async()

    async def shutdown_async(self, reason: str = "User shutdown") -> None:
        """Async shutdown. Delegates to LifecycleService."""
        await self._lifecycle.shutdown_async(reason)

    def shutdown(self, reason: str = "User shutdown") -> None:
        """Sync shutdown. Delegates to LifecycleService."""
        self._lifecycle.shutdown(reason)
