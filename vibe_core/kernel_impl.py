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
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.cartridges.system.civic.economy_agent import CivicBank
    from vibe_core.phoenix import PhoenixConfig

# Vedic Governance types (used for backward-compatible type hints)
# Actual governance logic is in vibe_core/plugins/vedic_governance.py
from steward.ashrama import Ashrama, AshramaTransition
from steward.varna import Varna

from .capability_registry import CapabilityRegistry  # Phase 2: Capability Revocation

# DocRenderer: Extracted markdown rendering logic
from .event_bus import get_event_bus  # Phase 2: Event Bus

# I/O Service: Central file operation controller (see docs/architecture/KERNEL_IO_ARCHITECTURE.md)
from .io_service import KernelIOService
from .kernel import (
    KernelStatus,
    ManifestRegistry,
    VibeKernel,
    VibeLedger,
    VibeScheduler,
)
from .ledger import InMemoryLedger, SQLiteLedger
from .lineage import LineageChain, LineageEventType  # Phase 5: Parampara Blockchain

# from .markdown_ui_manager import MarkdownUIManager  # DEPRECATED: UI Manager
from .narasimha import ThreatIndicator, get_narasimha  # Phase 7: Kill-Switch
from .network_proxy import KernelNetworkProxy  # Phase 4: Network Isolation
from .plugin_loader import PluginLoader  # Phase 1: Plugin System
from .process_manager import ProcessManager  # Phase 2: Process Isolation
from .protocols import AgentManifest, VibeAgent
from .resource_manager import ResourceManager  # Phase 3: Resource Isolation

# ENVOY.md: PlaybookRouter for intent routing (no LLM, pattern matching only)
from .runtime.playbook_router import PlaybookRouter
from .scheduling import Task

# Sync modules: Extracted bidirectional markdown interfaces
from .tool_discovery import ToolDiscovery  # Phase 6: Auto-Discovery
from .tools.tool_registry import ToolRegistry  # Phase 6: Universal Tool Registry

# Import Auditor for immune system (optional)
try:
    from vibe_core.cartridges.system.auditor.tools.invariant_tool import (
        InvariantSeverity,
        get_judge,
    )

    AUDITOR_AVAILABLE = True
except ImportError:
    AUDITOR_AVAILABLE = False
    logger_setup = logging.getLogger("VIBE_KERNEL")
    logger_setup.warning("⚠️  Auditor not available - immune system disabled")

# Import Constitutional Oath verification (Governance Gate - SECURITY FIX: P0.3)
try:
    from vibe_core.bridge import ConstitutionalOath

    OATH_ENFORCEMENT_AVAILABLE = True
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


class InMemoryScheduler(VibeScheduler):
    """FIFO Task Scheduler - Pure queue management.

    This is a PURE scheduler - no cosmic logic, no governance.
    Task filtering is handled by plugins via on_task_submit hook.

    The scheduler only knows how to:
    1. Accept tasks into the queue
    2. Return the next task (FIFO)
    3. Track completion status
    """

    def __init__(self):
        self.queue: deque = deque()
        self.executing: Optional[Task] = None
        self.completed: Dict[str, Task] = {}

    def submit_task(self, task: Task) -> str:
        """Submit task to queue, return task_id.

        NOTE: Task validation (Sarga cycle, governance, etc.) is handled
        by plugins via on_task_submit hook BEFORE this method is called.
        This method is a pure queue operation.
        """
        self.queue.append(task)
        logger.info(f"📨 Task queued: {task.task_id} for {task.agent_id}")
        return task.task_id

    def next_task(self) -> Optional[Task]:
        """Pop next task from queue"""
        if self.queue:
            task = self.queue.popleft()
            self.executing = task
            return task
        return None

    def get_queue_status(self) -> Dict[str, Any]:
        """Get queue statistics"""
        return {
            "queue_length": len(self.queue),
            "executing": self.executing.task_id if self.executing else None,
            "completed": len(self.completed),
        }

    def requeue_task(self, task: Task) -> None:
        """Re-queue a deferred task (bypasses Sarga validation)."""
        self.queue.append(task)
        logger.debug(f"📨 Task re-queued: {task.task_id} (deferred)")


class InMemoryManifestRegistry(ManifestRegistry):
    """Agent Manifest Registry - Identity declarations"""

    def __init__(self):
        self.manifests: Dict[str, AgentManifest] = {}

    def register(self, manifest: AgentManifest) -> None:
        """Register an agent manifest"""
        self.manifests[manifest.agent_id] = manifest
        logger.info(f"📜 Manifest registered: {manifest.agent_id} ({manifest.name})")

    def lookup(self, agent_id: str) -> Optional[AgentManifest]:
        """Look up manifest by agent_id"""
        return self.manifests.get(agent_id)

    def find_by_capability(self, capability: str) -> List[AgentManifest]:
        """Find agents with a specific capability"""
        return [m for m in self.manifests.values() if capability in m.capabilities]

    def list_all(self) -> List[AgentManifest]:
        """List all registered manifests"""
        return list(self.manifests.values())


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

    def __init__(
        self,
        ledger_path: str = "data/vibe_ledger.db",
        config: "PhoenixConfig | None" = None,
        parent: "RealVibeKernel | None" = None,
    ):
        """
        Initialize the kernel.

        Args:
            ledger_path: Path to ledger database (":memory:" for in-memory)
            config: Optional PhoenixConfig for dependency injection.
                    If None, uses global get_config() singleton.
                    For ephemeral child kernels, pass custom config.
            parent: Optional parent kernel (for ephemeral cities).
                    Child kernels can access parent for result folding.
        """
        # 4D Hypercube: Store config and parent reference
        self._config = config
        self._parent = parent
        self._child_kernels: list["RealVibeKernel"] = []
        self._is_ephemeral = parent is not None

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

        # Markdown UI Manager (Centralized UI Coordination)
        # self._ui_manager = MarkdownUIManager(self)  # DEPRECATED: Handled by Plugins
        # logger.info("🖥️  Markdown UI Manager initialized")

        # Phase 4: Network Proxy
        self.network = KernelNetworkProxy(kernel=self)

        # Phase 5: Parampara Lineage Chain
        lineage_path = "/tmp/vibe_os/kernel/lineage.db"
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
        # Records all changes to Parampara Ledger for audit trail
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
        # Single source of truth for all agent tools
        # Tools are registered here and accessed via AgentSystemInterface
        # kernel=self enables on_tool_execute/on_tool_executed plugin hooks
        self.tool_registry = ToolRegistry(
            invariant_checker=self._auditor if AUDITOR_AVAILABLE else None,
            capability_checker=self._check_agent_capability,
            kernel=self,
        )
        self._register_core_tools()
        self._discover_agent_tools()
        logger.info(f"🔧 Tool Registry initialized ({len(self.tool_registry)} tools total)")

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

        # Playbook Router for Intent Routing (used by UI Manager)
        self._playbook_router = PlaybookRouter()

        # PLUGIN SYSTEM (The Avatars of Vishnu)
        # Phase 1: Load and boot all plugins
        self._plugins = PluginLoader.discover()
        for plugin in self._plugins:
            plugin.on_boot(self)

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

            # Phase 4c: Create bank with VFS-isolated database path
            kernel_data_path = Path("/tmp/vibe_os/kernel/economy.db")
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
        """
        NARASIMHA DESTRUCTION HANDLER - Called when Narasimha activates.

        This is the REAL kill-switch. When Narasimha detects an existential threat,
        this method executes total annihilation of the rogue agent:
        1. Kill process (if running)
        2. Revoke all capabilities
        3. Remove from registry
        4. Log to ledger (immutable record)
        5. Quarantine data

        Args:
            agent_id: The agent to destroy
            trigger: The threat that triggered destruction
        """
        logger.critical(f"⚡⚡⚡ NARASIMHA EXECUTING: Destroying agent '{agent_id}' ⚡⚡⚡")

        # 1. Kill process immediately
        if agent_id in self.process_manager.processes:
            proc_info = self.process_manager.processes[agent_id]
            try:
                if proc_info.process.is_alive():
                    proc_info.process.terminate()
                    proc_info.process.join(timeout=1)
                    if proc_info.process.is_alive():
                        proc_info.process.kill()  # SIGKILL if terminate fails
                logger.critical(f"🔥 Process killed: {agent_id}")
            except Exception as e:
                logger.error(f"Process kill failed: {e}")

        # 2. Revoke all capabilities (use CapabilityRegistry)
        if self._capability_registry.is_registered(agent_id):
            self._capability_registry.revoke_all(
                agent_id=agent_id, revoker_id="NARASIMHA", reason=f"Kill-switch activated: {trigger.threat_type.value}"
            )
            logger.critical(f"🔒 Capabilities revoked: {agent_id}")

        # 3. Remove from agent registry (internal - doesn't affect MappingProxyType view)
        if agent_id in self._agent_registry:
            del self._agent_registry[agent_id]
            logger.critical(f"🗑️  Removed from registry: {agent_id}")

            # PLUGIN HOOK: Notify plugins about agent removal
            for plugin in self._plugins:
                plugin.on_agent_unregistered(self, agent_id)

        # 4. Log to ledger (immutable record of destruction)
        self._ledger.record_event(
            event_type="NARASIMHA_DESTRUCTION",
            agent_id=agent_id,
            details={
                "trigger_type": trigger.indicator_type,
                "severity": trigger.severity.value,
                "description": trigger.description,
                "evidence": trigger.evidence,
                "timestamp": trigger.timestamp,
            },
        )
        logger.critical(f"📜 Destruction logged to ledger: {agent_id}")

        # 5. Mark in lineage (permanent blockchain record)
        self.lineage.add_block(
            event_type=LineageEventType.AGENT_DESTROYED,
            agent_id=agent_id,
            data={
                "reason": trigger.indicator_type,
                "description": trigger.description,
                "destroyer": "NARASIMHA",
            },
        )
        logger.critical(f"⛓️  Destruction recorded in Parampara: {agent_id}")
        logger.critical(f"✝️ NARASIMHA COMPLETE: Agent '{agent_id}' has been annihilated.")

    def _register_core_tools(self) -> None:
        """
        Register core tools that are available to all agents.

        Core tools are system-provided capabilities that don't belong to
        any specific agent. They're registered without namespace prefix
        (e.g., "read_file" not "core.read_file").

        Phase 6: These tools implement the Tool protocol and are registered
        at kernel boot time, before any agents are loaded.
        """
        from vibe_core.tools import (
            AddTaskTool,
            CompleteTaskTool,
            DelegateTool,
            ListTasksTool,
            ReadFileTool,
            WriteFileTool,
        )

        # File operations (VFS-aware tools will be added later)
        self.tool_registry.register(ReadFileTool())
        self.tool_registry.register(WriteFileTool())

        # Task management
        self.tool_registry.register(AddTaskTool())
        self.tool_registry.register(ListTasksTool())
        self.tool_registry.register(CompleteTaskTool())

        # Inter-agent delegation
        delegate_tool = DelegateTool()
        delegate_tool.set_kernel(self)  # Late binding to avoid circular dependency
        self.tool_registry.register(delegate_tool)

        tool_names = ", ".join(self.tool_registry.list_tools())
        logger.info(f"🔧 Registered {len(self.tool_registry)} core tools: {tool_names}")

    def _discover_agent_tools(self) -> None:
        """
        Auto-discover and register agent tools.

        Phase 6: Automatic tool discovery from agent directories.

        Scans:
        - steward/system_agents/{agent_id}/tools/*.py
        - agent_city/registry/{agent_id}/tools/*.py

        For each .py file:
        1. Dynamically import module
        2. Find classes implementing Tool protocol
        3. Register tools with namespace (agent_id.tool_name)

        Error Handling:
        - Import errors are logged but don't crash kernel
        - Invalid tools are skipped
        - Discovery continues even if some tools fail

        This allows developers to simply drop a .py file in {agent}/tools/
        and have it automatically available system-wide.
        """
        logger.info("🔍 Starting auto-discovery of agent tools...")

        # Initialize discovery scanner
        discovery = ToolDiscovery(root_path=Path("."))

        # Discover all tools
        discovered_tools = discovery.discover_all_tools()

        # Register discovered tools
        registered_count = 0
        failed_count = 0

        for tool in discovered_tools:
            try:
                self.tool_registry.register(tool)
                registered_count += 1

                # Inject I/O Service for tools that support it
                # This enables audited file writes through kernel.io
                if hasattr(tool, "set_io_service") and callable(tool.set_io_service):
                    tool.set_io_service(self.io)
                    logger.info(f"   ✅ Registered: {tool.name} (with I/O Service)")
                else:
                    logger.info(f"   ✅ Registered: {tool.name}")

            except ValueError as e:
                # Tool already registered (e.g., name collision)
                logger.warning(f"   ⚠️  Skipped {tool.name}: {e}")
                failed_count += 1

            except Exception as e:
                # Unexpected error during registration
                logger.error(f"   ❌ Failed to register {tool.name}: {e}")
                failed_count += 1

        # Get discovery stats
        stats = discovery.get_discovery_stats()

        logger.info(f"🔧 Auto-discovery complete: {registered_count} tools registered, {failed_count} failed")

        if stats["discovered_by_agent"]:
            logger.info("📊 Tools by agent:")
            for agent_id, tool_names in stats["discovered_by_agent"].items():
                logger.info(f"   {agent_id}: {', '.join(tool_names)}")

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

        # STEP 1: THE INSPECTION (Does the agent possess the Oath badge?)
        # Check for oath attributes that OathMixin provides
        has_oath_attribute = hasattr(agent, "oath_sworn") or hasattr(agent, "oath_event")

        if not has_oath_attribute:
            logger.critical(
                f"⛔ GOVERNANCE GATE VIOLATION: Agent '{agent.agent_id}' "
                f"attempted registration WITHOUT Constitutional Oath."
            )
            raise PermissionError(
                f"GOVERNANCE_GATE_DENIED: Agent '{agent.agent_id}' "
                f"has not sworn the Constitutional Oath. "
                f"Access to VibeOS kernel is refused."
            )

        # STEP 2: THE VERIFICATION (Is the Oath valid?)
        # Check if agent has actually sworn the oath (oath_sworn = True)
        oath_sworn = getattr(agent, "oath_sworn", False)
        oath_event = getattr(agent, "oath_event", None)

        if not oath_sworn:
            logger.critical(
                f"⛔ GOVERNANCE GATE VIOLATION: Agent '{agent.agent_id}' "
                f"has oath attributes but oath_sworn={oath_sworn}. "
                f"Agent has not executed Genesis Ceremony."
            )
            raise PermissionError(
                f"GOVERNANCE_GATE_DENIED: Agent '{agent.agent_id}' "
                f"has not sworn the Constitutional Oath (oath_sworn=False). "
                f"Kernel refuses entry."
            )

        # STEP 3: THE CRYPTOGRAPHIC VALIDATION (Is the oath genuine?)
        # Verify the oath signature against current Constitution
        if oath_event and OATH_ENFORCEMENT_AVAILABLE:
            try:
                is_valid, reason = ConstitutionalOath.verify_oath(oath_event, getattr(agent, "identity_tool", None))

                if not is_valid:
                    logger.critical(
                        f"⛔ GOVERNANCE GATE VIOLATION: Agent '{agent.agent_id}' oath verification FAILED: {reason}"
                    )
                    raise PermissionError(
                        f"GOVERNANCE_GATE_DENIED: Agent '{agent.agent_id}' "
                        f"oath is invalid. {reason} "
                        f"Kernel refuses entry."
                    )

                logger.info(f"✅ Governance Gate PASSED: Agent '{agent.agent_id}' oath verified ({reason})")

            except PermissionError:
                # Re-raise governance violations
                raise
            except Exception as e:
                logger.error(f"❌ Governance gate verification error for '{agent.agent_id}': {e}")
                raise PermissionError(
                    f"GOVERNANCE_GATE_ERROR: Agent '{agent.agent_id}' oath verification failed: {str(e)}"
                )

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

    def boot(self) -> None:
        """Boot the kernel - register all manifests and start scheduler"""
        self._status = KernelStatus.BOOTING
        logger.info("⚙️  KERNEL BOOTING...")

        # Phase 5: Record Kernel Boot in Parampara
        self.lineage.add_block(
            event_type=LineageEventType.KERNEL_BOOT,
            agent_id=None,
            data={
                "version": "2.0.0",
                "timestamp": datetime.utcnow().isoformat(),
                "agents_registered": len(self._agent_registry),
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

        # PULSE: Write initial snapshot on boot
        self._pulse()

    def tick(self) -> None:
        """Tick the kernel - process one task from the scheduler"""
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
            logger.debug("📭 No tasks in queue")
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
                    logger.error(f"❌ IPC Dispatch failed: {e}")
                    self._ledger.record_failure(task, str(e))
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
                    logger.error(f"❌ In-process execution failed: {e}")
                    self._ledger.record_failure(task, str(e))

                    # Plugin Hook: Task Failed
                    for plugin in self._plugins:
                        plugin.on_task_failed(self, task.task_id, str(e))
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
            error = str(e)
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
        """
        Phase 3: Sync resource quotas with CivicBank credits.

        This makes credits REAL by updating CPU/RAM limits based on balance.
        Runs every 60 seconds to avoid excessive bank queries.
        """
        import time

        current_time = time.time()
        if current_time - self._last_quota_sync < 60:  # Sync every 60 seconds
            return

        try:
            # Get CivicBank (lazy loaded)
            bank = self.get_bank()

            # Update quotas for all agents
            for agent_id in self._agent_registry.keys():
                try:
                    # Query credit balance
                    balance = bank.get_balance(agent_id)

                    # Update quota
                    self.resource_manager.set_quota(agent_id, credits=balance)

                    # Enforce on running process
                    proc_info = self.process_manager.processes.get(agent_id)
                    if proc_info and proc_info.process.is_alive():
                        self.resource_manager.enforce_quota(agent_id, proc_info.process)

                except Exception as e:
                    logger.debug(f"⚠️  Failed to sync quota for {agent_id}: {e}")

            self._last_quota_sync = current_time
            logger.debug("💰 Resource quotas synced with CivicBank")

        except Exception as e:
            logger.debug(f"⚠️  Quota sync failed: {e}")

    def _grant_repo_access(self, agent_id: str) -> None:
        """
        Phase 4b: Grant controlled repo access via symlink.

        Scribe and Archivist need to read the main repo.
        We create a symlink in their sandbox pointing to the repo.

        Security: This is a controlled escape. Only specific agents get it.
        """
        try:
            import os

            from vibe_core.vfs import VirtualFileSystem

            vfs = VirtualFileSystem(agent_id)
            repo_path = os.getcwd()  # /Users/ss/Downloads/steward-protocol

            # Create symlink: sandbox/repo -> actual repo
            vfs.create_symlink(repo_path, "repo")

            logger.info(f"🔗 {agent_id} granted repo access: {vfs.get_sandbox_path()}/repo -> {repo_path}")

        except Exception as e:
            logger.error(f"❌ Failed to grant repo access to {agent_id}: {e}")

    def _check_system_health(self) -> None:
        """
        🛡️ IMMUNE SYSTEM WATCHDOG

        Called after every task execution.
        If Auditor detects CRITICAL_VIOLATION -> Kernel shuts down.
        """
        if not AUDITOR_AVAILABLE or not self._auditor:
            return

        try:
            # Get current ledger events
            events = self._ledger.get_all_events()

            # Run verification (events-only for now, VOID checks need external context)
            report = self._auditor.verify_ledger(events)

            # If there's a CRITICAL violation, halt the kernel
            if not report.passed:
                for violation in report.violations:
                    if violation.severity == InvariantSeverity.CRITICAL.value:
                        # Don't halt on VOID violations in normal operation (they need context)
                        # Only halt on event-based violations (BROADCAST_LICENSE, DUPLICATES, etc)
                        if "VOID" not in violation.invariant_name:
                            logger.critical(f"🛡️  IMMUNE SYSTEM ALERT: {violation.invariant_name} - {violation.message}")
                            self.shutdown(reason=f"Immune system reaction: {violation.invariant_name}")
                            return
                        else:
                            logger.debug("⚠️  VOID check skipped (requires external context)")

            # Log health check (non-critical)
            if report.violations:
                logger.debug(f"⚠️  Auditor info: {len(report.violations)} issue(s) detected")
            else:
                logger.debug("✅ System health check passed")

        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")

    def get_agent_manifest(self, agent_id: str) -> Optional[AgentManifest]:
        """Get manifest for an agent"""
        return self._manifest_registry.lookup(agent_id)

    # =========================================================================
    # GOVERNANCE API (Delegates to governance plugin for backward compatibility)
    # =========================================================================

    def get_agent_varna(self, agent_id: str) -> Optional[Varna]:
        """Get the Varna (classification) of an agent. Delegates to governance plugin."""
        if self.governance and hasattr(self.governance, "get_agent_varna"):
            return self.governance.get_agent_varna(agent_id)
        return None

    def get_agent_ashrama(self, agent_id: str) -> Optional[AshramaTransition]:
        """Get the Ashrama (lifecycle stage) of an agent. Delegates to governance plugin."""
        if self.governance and hasattr(self.governance, "get_agent_ashrama"):
            return self.governance.get_agent_ashrama(agent_id)
        return None

    def get_agent_permissions(self, agent_id: str) -> List[str]:
        """Get the current permissions for an agent. Delegates to governance plugin."""
        if self.governance and hasattr(self.governance, "get_agent_permissions"):
            return self.governance.get_agent_permissions(agent_id)
        return []

    def check_agent_permission(self, agent_id: str, permission: str) -> bool:
        """Check if an agent has a specific permission. Delegates to governance plugin."""
        if self.governance and hasattr(self.governance, "check_agent_permission"):
            return self.governance.check_agent_permission(agent_id, permission)
        return True  # Default: allow if no governance plugin

    def transition_agent_ashrama(self, agent_id: str, new_ashrama: Ashrama, reason: str = "") -> bool:
        """Transition an agent to a new Ashrama. Delegates to governance plugin."""
        if self.governance and hasattr(self.governance, "transition_agent_ashrama"):
            return self.governance.transition_agent_ashrama(agent_id, new_ashrama, reason)
        logger.warning(f"No governance plugin loaded - cannot transition {agent_id}")
        return False

    def get_governance_status(self, agent_id: str) -> Dict[str, Any]:
        """Get full governance status for an agent. Delegates to governance plugin."""
        if self.governance and hasattr(self.governance, "get_governance_status"):
            return self.governance.get_governance_status(agent_id)
        return {"error": "No governance plugin loaded"}

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
        """
        Execute a playbook through the DeterministicExecutor.

        This method enables nested playbook execution, allowing playbooks to call
        other playbooks via the CALL_PLAYBOOK action type.

        Args:
            playbook_path: Path to the playbook YAML file (relative to knowledge/playbooks/)
            input_data: Input parameters for the playbook
            user_input: Optional user input string (defaults to empty string)

        Returns:
            Dictionary with execution results

        Example:
            result = await kernel.execute_playbook(
                playbook_path="vibe_core/playbook/circuits/wiring_audit.yaml",
                input_data={"scope": "full"},
                user_input="Run wiring audit"
            )
        """
        # Import here to avoid circular dependency
        from vibe_core.cartridges.system.envoy.deterministic_executor import DeterministicExecutor

        # Get or create executor instance
        if not hasattr(self, "_playbook_executor"):
            self._playbook_executor = DeterministicExecutor()

        # Extract playbook_id from path (e.g., "wiring_audit" from "circuits/wiring_audit.yaml")
        import os

        playbook_id = os.path.splitext(os.path.basename(playbook_path))[0]

        # Create a minimal intent vector (playbooks don't always need full intent analysis)
        class MinimalIntentVector:
            def __init__(self, user_input: str):
                self.raw_input = user_input
                self.concepts = set()
                self.target_agent = None

        intent_vector = MinimalIntentVector(user_input or "Nested playbook execution")

        # Execute the playbook
        logger.info(f"🎯 Kernel executing playbook: {playbook_id} from {playbook_path}")
        result = await self._playbook_executor.execute(
            playbook_id=playbook_id,
            user_input=user_input or str(input_data),
            intent_vector=intent_vector,
            kernel=self,
            emit_event=None,
        )

        return result

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
        """Get EventBus status (total events, subscribers, etc.)"""
        return self._event_bus.get_status()

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
        """
        💓 HEARTBEAT: Generate real-time snapshot of kernel state.

        Event Sourcing → State Projection:
        - Collects current state from all agents
        - Writes vibe_snapshot.json (immutable state view)
        - Renders OPERATIONS.md (human-readable dashboard)
        """
        try:
            snapshot = {
                "timestamp": datetime.utcnow().isoformat(),
                "kernel_status": self._status.value,
                "agents": {},
                "scheduler": self._scheduler.get_queue_status(),
                "ledger_stats": {
                    "total_events": len(self._ledger.get_all_events()),
                },
            }

            # Collect agent status
            for agent_id, agent in self._agent_registry.items():
                try:
                    agent_status = agent.report_status() if hasattr(agent, "report_status") else {}
                    # Mark paused agents (via governance plugin)
                    if self.governance and hasattr(self.governance, "is_agent_paused"):
                        if self.governance.is_agent_paused(agent_id):
                            agent_status["status"] = "PAUSED"
                    snapshot["agents"][agent_id] = agent_status
                except Exception as e:
                    logger.warning(f"⚠️  Could not get status from {agent_id}: {e}")
                    snapshot["agents"][agent_id] = {"error": str(e)}

            # Write snapshot through I/O Service (atomic + audited)
            result = self.io.write_snapshot("vibe_snapshot.json", snapshot, writer_id="KERNEL")
            if result.success:
                logger.info("💓 Pulse written: vibe_snapshot.json (via I/O Service)")
            else:
                logger.error(f"❌ Pulse snapshot write failed: {result.error}")

            # Render ALL UI files via Manager
            # self._ui_manager.render_all(snapshot)  # DEPRECATED: Handled by Plugins

        except Exception as e:
            logger.error(f"❌ Pulse failed: {e}")

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
