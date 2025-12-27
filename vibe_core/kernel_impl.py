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
)
from .protocols.cognition import (
    IntentType as CognitiveIntentType,
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
            except Exception:
                pass

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
        self._completed_tasks: Dict[str, Any] = {}  # Temporary result cache for async IPC

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

        # Load immune system (Auditor)
        # OPUS-209: Auditor is now accessed via ServiceRegistry
        # If no auditor plugin loaded, use NullAuditor fallback
        from vibe_core.di import ServiceRegistry

        self._auditor = ServiceRegistry.get(AuditorProtocol) or NullAuditor()
        auditor_type = type(self._auditor).__name__
        if auditor_type == "NullAuditor":
            logger.warning("⚠️  No auditor plugin loaded - using NullAuditor")
        else:
            logger.info(f"🛡️  Immune system loaded (Auditor: {auditor_type})")

        # Phase 2: Process Manager
        # OPUS-209: Extracted to process_isolation plugin
        # ProcessManager is created and registered by ProcessIsolationPlugin.on_boot()
        # CRITICAL: Plugin MUST be loaded, or kernel cannot run agents
        self.process_manager = None  # Set by ProcessIsolationPlugin

        # Phase 3: Resource Manager
        # OPUS-209: Extracted to resource_limits plugin
        # ResourceManager is created and registered by ResourceLimitsPlugin.on_boot()
        # CRITICAL: Plugin MUST be loaded for quota enforcement
        self.resource_manager = None  # Set by ResourceLimitsPlugin
        self._last_quota_sync = 0  # Timestamp of last credit→quota sync
        self._last_pulse_time = 0  # Timestamp of last heartbeat pulse
        # OPUS-303: Agent health cache (TTL 30s) to reduce OS syscalls in pulse
        self._agent_health_cache: Dict[str, Dict[str, Any]] = {}

        # Phase 18: Network Gateway (Sangha)
        # OPUS-209: Extracted to sangha_network plugin
        # Gateway is created and registered by SanghaNetworkPlugin.on_boot()
        self.gateway = None  # Set by SanghaNetworkPlugin
        self._gateway_thread = None
        self._gateway_loop = None

        # Markdown UI Manager (Centralized UI Coordination)
        # self._ui_manager = MarkdownUIManager(self)  # DEPRECATED: Handled by Plugins
        # logger.info("🖥️  Markdown UI Manager initialized")

        # Phase 4: Network Proxy (OPUS-301: Lazy loaded)
        self._network = None  # Lazy: created on first access

        # Phase 5: Parampara Lineage Chain
        phoenix_config = _get_config()
        if phoenix_config and hasattr(phoenix_config, "paths"):
            lineage_path = str(phoenix_config.paths.system.resolve("lineage_db"))
        else:
            # OPUS-025: Fallback with Path pattern
            from pathlib import Path

            lineage_path = str(Path("/tmp") / "vibe_os" / "kernel" / "lineage.db")

        # OPUS-301: Lazy load LineageChain
        LazyLineageChain = lazy_class("vibe_core.lineage", "LineageChain")
        self.lineage = LazyLineageChain(db_path=lineage_path)
        logger.info("⛓️  Parampara chain initialized (lazy)")

        # Economic Substrate (Lazy Loaded)
        self._bank = None
        self._vault = None

        # OPUS-200/201: Quantum Resonance Engine (Core Primitive)
        # The reactor is the kernel's physics engine - how actions manifestation
        self._reactor = None
        self._akasha_field = ""  # Cumulative resonance field hash

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
        # OPUS-301: Lazy load Prakriti
        LazyPrakriti = lazy_class("vibe_core.state", "Prakriti")

        prakriti_db_path = None
        if phoenix_config and hasattr(phoenix_config, "paths"):
            try:
                prakriti_db_path = phoenix_config.paths.data.resolve("vibe_ledger")
            except Exception as e:
                logger.warning(f"⚠️  KERNEL: Could not resolve Prakriti DB path: {e}")

        self.prakriti = LazyPrakriti(db_path=prakriti_db_path)

        # OPUS-096: State Sync Holon Weaver (MetaData Orchestration)
        from vibe_core.state.weaver import get_state_sync_weaver

        get_state_sync_weaver()

        # 3. CAPABILITY REGISTRY (with blueprint)
        # Phase 2: Capability Registry (Must be before plugins)
        self._capability_registry_blueprint = lambda: CapabilityRegistry(ledger=self.ledger)
        self.__capability_registry = CapabilityRegistry(ledger=self.ledger)

        # I/O SERVICE: Central file operation controller
        # IMPORTANT: Must be initialized BEFORE tool discovery
        # Tools may inject io_service during registration via set_io_service()
        # All file writes MUST go through this service.
        # Plugins produce content, Kernel writes through self.io
        # See: docs/architecture/KERNEL_IO_ARCHITECTURE.md
        self.io = KernelIOService(self)
        logger.info("📁 Kernel I/O Service initialized (central file controller)")

        # MANIFESTATION SERVICE: High-level Markdown rendering engine
        # OPUS-308: The Rendering Engine of Reality
        # Plugins declare manifestation in manifest.json, implement get_manifestation_data()
        # This service handles: schema-based rendering, section ownership, atomic updates
        # See: docs/architecture/OPUS/308-MARKDOWN-MANIFESTATION-PROTOCOL.md
        self.manifestation = ManifestationService(self)
        logger.info("📄 ManifestationService initialized (OPUS-308 Core)")

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

        # OPUS-309: Cognitive Hook (Hot-Swap)
        # Plugins can register cognitive layer via register_cognitive()
        # Arjuna-Pattern: NullCognitive fallback if no plugin registers
        self._cognitive: OperatorCognitiveProtocol = NullCognitive()
        logger.info("🧠 Cognitive hook initialized (NullCognitive fallback)")

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

            from vibe_core.loaders.manifest_registry import ManifestRegistry

            # OPUS-307 Phase F: Ensure manifests are scanned (idempotent)
            ManifestRegistry.scan_all()

            # OPUS-020 Phase 3: Support custom plugin paths via env var
            # Usage: VIBE_PLUGIN_PATH=dist/plugins:custom/plugins python -m vibe_core.cli boot
            custom_paths_env = os.environ.get("VIBE_PLUGIN_PATH", "")
            if custom_paths_env:
                # Custom paths: Use legacy iterdir (env override)
                scan_paths = [Path(p.strip()) for p in custom_paths_env.split(":") if p.strip()]
                logger.info(f"🔌 Using custom plugin paths from VIBE_PLUGIN_PATH: {scan_paths}")
                self._plugins_map, self._plugin_metadata = PluginLoader.discover_and_load(scan_paths=scan_paths)
            else:
                # OPUS-307: Use ManifestRegistry (NO iterdir!)
                self._plugins_map, self._plugin_metadata = PluginLoader.discover_from_registry()
            # OPUS-FIX: Sort plugins by priority before on_boot (lower = earlier)
            self._plugins = sorted(
                self._plugins_map.values(),
                key=lambda p: getattr(p, "priority", 50),
            )

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

            # OPUS-308: Auto-register plugins for manifestation
            # Plugins with "manifestation" config in manifest.json get registered
            for plugin_id, meta in self._plugin_metadata.items():
                if meta.manifest and meta.manifest.get("manifestation"):
                    plugin_instance = self._plugins_map.get(plugin_id)
                    if plugin_instance:
                        self.manifestation.register_plugin(plugin_id, plugin_instance, meta.manifest)

            # OPUS-308: Register kernel-native SETTINGS.md
            # SETTINGS.md is a kernel feature, not a plugin
            self.manifestation.register_kernel_source(
                output="SETTINGS.md",
                schema="config_bidirectional",
                data_getter=self._get_settings_manifestation_data,
            )

            # OPUS-308: Register kernel-native OPERATIONS.md
            # OPERATIONS.md shows scheduler, agents, events - all kernel state
            self.manifestation.register_kernel_source(
                output="OPERATIONS.md",
                schema="dashboard_readonly",
                data_getter=self._get_operations_manifestation_data,
            )
        else:
            self._plugins = []
            self._plugins = []
            logger.info("🛡️ Vibe Kernel booted in Safe Mode (plugins disabled)")

        # =====================================================================

        # =====================================================================
        # VAJRA ARMOR: Seal the kernel DNA (PUTANA BLOCKED!)
        # After this, blueprints cannot be modified.
        # =====================================================================
        self.vajra_seal()

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
    def plugins(self) -> List[Any]:
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

    def _get_settings_manifestation_data(self) -> Dict[str, Any]:
        """
        OPUS-308: Kernel-native data source for SETTINGS.md.

        Returns data for the config_bidirectional schema sections:
        - current: Current kernel configuration
        - available: Available agents and their status
        - history: Recent command execution history
        """
        # Current configuration
        config = self._config or _get_config()
        log_level = logging.getLevelName(logging.getLogger("VIBE_KERNEL").getEffectiveLevel())
        verbose = getattr(self, "_verbose", False)
        provider = "unknown"
        mode = "simulation"

        if config:
            if hasattr(config, "llm"):
                provider = getattr(config.llm, "provider", provider)
            if hasattr(config, "runtime"):
                mode = getattr(config.runtime, "mode", mode)

        current = [
            {"Setting": "`kernel.log_level`", "Value": f"`{log_level}`", "Description": "Logging verbosity"},
            {"Setting": "`kernel.verbose`", "Value": f"`{verbose}`", "Description": "Verbose mode"},
            {"Setting": "`provider`", "Value": f"`{provider}`", "Description": "LLM Provider"},
            {"Setting": "`mode`", "Value": f"`{mode}`", "Description": "Execution Mode"},
            {"Setting": "`agents`", "Value": f"`{len(self._agent_registry)}`", "Description": "Registered agents"},
            {"Setting": "`plugins`", "Value": f"`{len(self._plugins)}`", "Description": "Loaded plugins"},
        ]

        # Available agents (from registry)
        available = []
        for agent_id in self._agent_registry.keys():
            status = "ACTIVE"
            # Check if paused via governance
            if self.governance and hasattr(self.governance, "get_paused_agents"):
                if agent_id in self.governance.get_paused_agents():
                    status = "PAUSED"
            available.append({"Agent": f"`{agent_id}`", "Status": status})

        # History - get from ledger (last 10 events)
        history = []
        try:
            events = self._ledger.get_all_events()[-10:]
            for event in events:
                history.append(
                    {
                        "Time": event.get("timestamp", "")[:19],
                        "Type": event.get("event_type", "")[:20],
                        "Agent": event.get("agent_id", "")[:15],
                    }
                )
        except Exception:
            pass

        return {
            "current": current,
            "available": available,
            "history": history,
        }

    def _get_operations_manifestation_data(self) -> Dict[str, Any]:
        """
        OPUS-308: Kernel-native data source for OPERATIONS.md.

        Returns data for the dashboard_readonly schema sections:
        - metrics: Key numbers (queue size, agent count, event count)
        - status: Current kernel and agent states
        - details: Scheduler queue details
        """
        # Metrics - key numbers
        queue_status = self._scheduler.get_queue_status() if hasattr(self, "_scheduler") else {}
        event_status = self._event_bus.get_status() if hasattr(self, "_event_bus") else {}

        metrics = {
            "Kernel Status": self._status.value,
            "Agents": len(self._agent_registry),
            "Queue Length": queue_status.get("queue_length", 0),
            "Pending Tasks": queue_status.get("pending", 0),
            "Total Events": event_status.get("total_emitted", 0),
            "Plugins": len(self._plugins),
        }

        # Status - agent states
        status = []
        for agent_id, agent in sorted(self._agent_registry.items()):
            name = getattr(agent, "name", agent_id)
            domain = getattr(agent, "domain", "UNKNOWN")
            status.append(
                {
                    "Agent": f"`{agent_id}`",
                    "Name": name,
                    "Domain": domain,
                    "Status": "ACTIVE",
                }
            )

        if not status:
            status = [{"Agent": "_No agents_", "Name": "-", "Domain": "-", "Status": "-"}]

        # Details - queue and events
        details = []
        tasks = queue_status.get("tasks", [])[:5]
        for t in tasks:
            details.append(
                {
                    "Item": f"Task: {t.get('id', '?')[:20]}",
                    "Info": f"Priority: {t.get('priority', '?')}",
                }
            )

        type_counts = event_status.get("type_counts", {})
        for event_type, count in sorted(type_counts.items(), key=lambda x: -x[1])[:5]:
            details.append(
                {
                    "Item": f"Event: {event_type[:20]}",
                    "Info": f"Count: {count}",
                }
            )

        if not details:
            details = [{"Item": "_No activity_", "Info": "-"}]

        return {
            "metrics": metrics,
            "status": status,
            "details": details,
        }

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

    async def process_operator_input(self, input_text: str, session_id: Optional[str] = None) -> CognitiveResult:
        """
        Process natural language input from operator (human or AI).

        OPUS-309: Main entry point for operator input.
        Routes through registered cognitive plugin.

        GAD-000: AI operates the system on behalf of human.
        The cognitive layer decides: chat, execute, query, or route.

        Args:
            input_text: Raw natural language input
            session_id: Optional session ID for conversation context

        Returns:
            CognitiveResult with intent_type and relevant data

        Usage:
            result = await kernel.process_operator_input("create a monitoring agent")
            if result.intent_type == CognitiveIntentType.EXECUTE:
                # Execute the syscall
                ...
        """
        # Build context
        context = CognitiveContext(
            kernel_status=self._status.value if hasattr(self._status, "value") else str(self._status),
            active_agents=list(self._agents.keys()) if hasattr(self, "_agents") else [],
            pending_tasks=len(self._scheduler.pending_tasks) if hasattr(self._scheduler, "pending_tasks") else 0,
            session_id=session_id,
            available_tools=list(self.tool_registry.list_tools()) if self.tool_registry else [],
            available_agents=list(self._agents.keys()) if hasattr(self, "_agents") else [],
        )

        # Process through cognitive layer
        try:
            result = await self._cognitive.process_intent(input_text, context)
            logger.debug(f"🧠 Cognitive result: {result.intent_type.value} (confidence: {result.confidence:.2f})")
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

    def boot(self, boot_mode: BootMode | None = None) -> None:
        """
        Boot the kernel synchronously (backward compatibility wrapper).

        OPUS-203 introduced boot_async(), but 30+ callers still use sync boot().
        This wrapper ensures backward compatibility while delegating to boot_async().

        For new code, prefer boot_async() in async contexts.

        Args:
            boot_mode: Optional BootMode (FULL, HEADLESS, MINIMAL).
                       If None, defaults to FULL for backward compatibility.
        """
        import asyncio

        from vibe_core.boot_mode import BootMode

        if boot_mode is None:
            boot_mode = BootMode.FULL

        # Check if we're already in an async context
        try:
            loop = asyncio.get_running_loop()
            # We're in an async context - schedule and wait
            import concurrent.futures

            future = concurrent.futures.Future()

            async def _boot_and_signal():
                try:
                    await self.boot_async(boot_mode)
                    future.set_result(None)
                except Exception as e:
                    future.set_exception(e)

            loop.create_task(_boot_and_signal())
            # Note: This will block the current thread waiting for boot
            # In pure async code, use boot_async() directly
            future.result(timeout=60)
        except RuntimeError:
            # No running event loop - use asyncio.run()
            asyncio.run(self.boot_async(boot_mode))

    async def boot_async(self, boot_mode: BootMode | None = None) -> None:
        """
        🚀 ASYNC BOOT (OPUS-203)
        Registers manifests, activates Prakriti, and starts Gateway task.
        """
        from vibe_core.boot_mode import BootMode

        if boot_mode is None:
            boot_mode = BootMode.FULL

        self._status = KernelStatus.BOOTING
        self._boot_time = time.time()
        logger.info(f"⚙️  KERNEL BOOTING ASYNC... (mode: {boot_mode.value})")

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
                if hasattr(agent, "get_manifest"):
                    manifest = agent.get_manifest()
                    self._manifest_registry.register(manifest)
                    logger.info(f"   📜 {agent_id}: {manifest.description}")
            except Exception as e:
                logger.warning(f"   ⚠️  Failed to register manifest for {agent_id}: {e}")

        self._status = KernelStatus.RUNNING
        logger.info("✅ KERNEL RUNNING (ASYNC)")

        # [OPUS-027] PRAKRITI ACTIVATION (The Awakening)
        try:
            self.prakriti.begin_session()
            self.prakriti.sync_ledger_git(strategy="git_wins")
            if self.prakriti.is_dirty:
                self.prakriti.recover_from_crash()
        except Exception as e:
            logger.error(f"❌ Prakriti Boot Failure: {e}")

        # 🍎 ASYNC PERSISTENCE (ADR-204)
        try:
            from vibe_core.state.state_service import get_state_service

            ss = get_state_service(self._workspace if hasattr(self, "_workspace") else None)
            ss.start_background_worker()
        except Exception as e:
            logger.warning(f"⚠️  Failed to start background persistence: {e}")

        # PULSE: Write initial snapshot on boot
        await self._pulse()

        # Phase 18: Gateway as Task (instead of Thread)
        if boot_mode.should_skip_gateway():
            logger.info("🚫 Network Gateway SKIPPED (headless mode)")
            self._gateway_task = None
        else:
            self._gateway_task = asyncio.create_task(self._run_gateway_async())
            logger.info("🌐 Network Gateway task started")

    async def run_forever(self) -> None:
        """
        🔄 MAIN KERNEL LOOP (OPUS-203)
        Runs tick_async() at 100ms intervals until shutdown.
        """
        logger.info("🔄 Entering Unified Async Kernel loop...")
        try:
            while self._status == KernelStatus.RUNNING:
                await self.tick_async()
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            logger.info("🛑 Kernel loop cancelled")
        finally:
            if self._status == KernelStatus.RUNNING:
                await self.shutdown_async("Loop terminated")

    async def tick_async(self) -> None:
        """
        💓 ASYNC TICK (OPUS-203)
        Drives the heartbeat, scheduler, and event emission natively.
        """
        self.enforce_entropy_limits()

        if self._status != KernelStatus.RUNNING:
            return

        # Plugin Hook: Pre-Tick
        for plugin in self._plugins:
            plugin.on_tick_pre(self)

        task = self._scheduler.next_task()

        if not task:
            # Idle Pulse
            if time.time() - self._last_pulse_time >= 5.0:
                await self._pulse()
                self._last_pulse_time = time.time()
        else:
            # Get target agent
            agent = self._agent_registry.get(task.agent_id)
            if not agent:
                error = f"Agent {task.agent_id} not found"
                logger.error(f"❌ {error}")
                self._ledger.record_failure(task, error)
                return

            # Task Execution
            try:
                self._ledger.record_start(task)

                # Execution (Process vs In-Process)
                has_process = (
                    self.process_manager
                    and task.agent_id in self.process_manager.processes
                    and self.process_manager.processes[task.agent_id].process.is_alive()
                )

                if has_process:
                    # Dispatch to isolated process
                    self.process_manager.send_task(task.agent_id, task)
                else:
                    # Execute natively (supports async agents!)
                    if asyncio.iscoroutinefunction(agent.process):
                        result = await agent.process(task)
                    else:
                        result = agent.process(task)

                    self._ledger.record_completion(task, result)

                    for plugin in self._plugins:
                        plugin.on_task_completed(self, task.task_id, result)

                # Maintenance
                await self._pulse()
                self._check_system_health()
                if self.process_manager:
                    self.process_manager.check_health()
                self._process_ipc_events()
                self._sync_resource_quotas()

                for plugin in self._plugins:
                    plugin.on_tick_post(self)

                # OPUS-308: Manifestation tick (render all registered plugin UIs)
                self.manifestation.tick()

            except Exception as e:
                error = str(kernel_fault("task_tick_async", str(e)))
                logger.exception(f"❌ Task {task.task_id} failed: {error}")
                self._ledger.record_failure(task, error)
                for plugin in self._plugins:
                    plugin.on_task_failed(self, task.task_id, error)

        # NATIVE HEARTBEAT (Direct await! Emitted every tick to drive circuits)
        await self._event_bus.emit(
            Event(event_type=EventType.KERNEL_TICK, agent_id="kernel", message="Kernel heartbeat tick")
        )

    async def _run_gateway_async(self) -> None:
        """Runs the NetworkGateway as an asyncio task."""
        if self.gateway is None:
            logger.warning("🌐 Gateway not available (sangha_network plugin not loaded)")
            return
        try:
            await self.gateway.start()
        except Exception as e:
            logger.error(f"🌐 Gateway task crashed: {e}")

    async def shutdown_async(self, reason: str = "User shutdown") -> None:
        """
        🛑 ASYNC SHUTDOWN (OPUS-203)
        Gracefully stops gateway task and preserves Prakriti state.
        """
        logger.critical(f"🛑 KERNEL SHUTTING DOWN ASYNC: {reason}")

        # Record shutdown
        if hasattr(self, "lineage"):
            self.lineage.add_block(event_type=LineageEventType.KERNEL_SHUTDOWN, agent_id=None, data={"reason": reason})
            self.lineage.close()

        # Preserve state
        try:
            if hasattr(self, "prakriti"):
                self.prakriti.end_session()
        except Exception as e:
            logger.error(f"❌ State preservation failed: {e}")

        # 🍎 ASYNC PERSISTENCE CLEANUP (ADR-204)
        try:
            from vibe_core.state.state_service import get_state_service

            ss = get_state_service(self._workspace if hasattr(self, "_workspace") else None)
            if ss._worker_task:
                ss._worker_task.cancel()
                logger.info("🛑 StateService: Background scribe stopped.")
        except Exception:
            pass

        # Plugin Hook
        for plugin in self._plugins:
            plugin.on_shutdown(self)

        self._status = KernelStatus.STOPPED

        # Cancel Gateway
        if hasattr(self, "_gateway_task") and self._gateway_task:
            self._gateway_task.cancel()
            try:
                await self._gateway_task
            except asyncio.CancelledError:
                pass
        # Cleanup processes
        if self.process_manager:
            self.process_manager.shutdown()
        if isinstance(self._ledger, SQLiteLedger):
            self._ledger.close()

    def shutdown(self, reason: str = "User shutdown") -> None:
        """
        🛑 SYNC SHUTDOWN (OPUS-314)
        Synchronous wrapper for shutdown_async. For use in tests and sync code.
        """
        import asyncio

        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.shutdown_async(reason))
        except RuntimeError:
            asyncio.run(self.shutdown_async(reason))
