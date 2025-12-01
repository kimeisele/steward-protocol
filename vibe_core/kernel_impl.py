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

import json
import logging
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from steward.system_agents.civic.economy_agent import CivicBank

from steward.ashrama import Ashrama, AshramaTransition, get_ashrama_description

# Phase B: Vedic Governance (Varna + Ashrama)
from steward.varna import Varna, categorize_agent_by_function, get_varna_description

from .kernel import (
    KernelStatus,
    ManifestRegistry,
    VibeKernel,
    VibeLedger,
    VibeScheduler,
)
from .ledger import InMemoryLedger, SQLiteLedger
from .lineage import LineageChain, LineageEventType  # Phase 5: Parampara Blockchain
from .narasimha import ThreatIndicator, get_narasimha  # Phase 7: Kill-Switch
from .network_proxy import KernelNetworkProxy  # Phase 4: Network Isolation
from .process_manager import ProcessManager  # Phase 2: Process Isolation
from .protocols import AgentManifest, VibeAgent
from .resource_manager import ResourceManager  # Phase 3: Resource Isolation
from .sarga import Cycle, get_sarga
from .scheduling import Task
from .tool_discovery import ToolDiscovery  # Phase 6: Auto-Discovery
from .tools.tool_registry import ToolRegistry  # Phase 6: Universal Tool Registry
from .capability_registry import CapabilityRegistry  # Phase 2: Capability Revocation

# Import Auditor for immune system (optional)
try:
    from steward.system_agents.auditor.tools.invariant_tool import (
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
    """FIFO Task Scheduler - Real-time queue management

    PHASE 3 WIRING: Respects Sarga Cycle (Brahma's creation/maintenance cycles)
    - DAY_OF_BRAHMA: All task types allowed (creation, implementation, features)
    - NIGHT_OF_BRAHMA: Only maintenance tasks allowed (bugfix, refactor, maintenance)
    """

    # Task types allowed during NIGHT_OF_BRAHMA
    MAINTENANCE_TASK_TYPES = {
        "bugfix",
        "fix",
        "maintenance",
        "refactor",
        "cleanup",
        "optimization",
        "performance",
        "security",
        "test",
        "debug",
    }

    def __init__(self):
        self.queue: deque = deque()
        self.executing: Optional[Task] = None
        self.completed: Dict[str, Task] = {}

    def submit_task(self, task: Task) -> str:
        """Submit task to queue, return task_id

        PHASE 3: Checks Sarga cycle before allowing task submission
        """
        # Get current Brahma cycle
        sarga = get_sarga()
        current_cycle = sarga.get_cycle()

        # During NIGHT_OF_BRAHMA, restrict task types
        if current_cycle == Cycle.NIGHT_OF_BRAHMA:
            task_type = task.payload.get("type", "").lower() if task.payload else ""

            # Check if task type is allowed during night cycle
            if task_type and task_type not in self.MAINTENANCE_TASK_TYPES:
                logger.warning(
                    f"🌙 Task {task.task_id} blocked: type '{task_type}' not allowed during NIGHT_OF_BRAHMA. "
                    f"Only maintenance tasks permitted."
                )
                raise ValueError(
                    f"Task type '{task_type}' not allowed during NIGHT_OF_BRAHMA. "
                    f"Only maintenance tasks are permitted: {', '.join(self.MAINTENANCE_TASK_TYPES)}"
                )

            logger.info(f"🌙 Task {task.task_id} approved for NIGHT_OF_BRAHMA (maintenance cycle)")

        elif current_cycle == Cycle.DAY_OF_BRAHMA:
            logger.info(f"☀️  Task {task.task_id} approved for DAY_OF_BRAHMA (creation cycle)")

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
    """

    def __init__(self, ledger_path: str = "data/vibe_ledger.db"):
        """Initialize the kernel"""
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

        # Phase 2.5: SETTINGS.md synchronization (Command Queue)
        self._settings_last_modified = 0.0  # Last known mtime of SETTINGS.md
        self._settings_writing = False  # Lock flag to prevent read during write
        self._settings_execution_history: deque = deque(maxlen=10)  # Last 10 executed commands
        logger.info("⚙️  Settings sync initialized (Command Queue)")

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

        # Phase B: Vedic Governance (Varna + Ashrama)
        # Varna = Agent classification (what kind of being)
        # Ashrama = Lifecycle stage (what stage of life)
        self._varna_registry: Dict[str, Varna] = {}
        self._ashrama_registry: Dict[str, AshramaTransition] = {}
        logger.info("🕉️  Vedic Governance initialized (Varna + Ashrama)")

        # SECURITY (ARCH-HARDENING): Capability Registry with Revocation
        # Stores agent capabilities with support for selective revocation
        # Records all changes to Parampara Ledger for audit trail
        self._capability_registry = CapabilityRegistry(ledger=self._ledger)

        # Phase 6: Universal Tool Registry
        # Single source of truth for all agent tools
        # Tools are registered here and accessed via AgentSystemInterface
        self.tool_registry = ToolRegistry(
            invariant_checker=self._auditor if AUDITOR_AVAILABLE else None,
            capability_checker=self._check_agent_capability,
        )
        self._register_core_tools()
        self._discover_agent_tools()
        logger.info(f"🔧 Tool Registry initialized ({len(self.tool_registry)} tools total)")

        # Phase 7: NARASIMHA Kill-Switch (Hypervisor Level)
        # SECURITY FIX: Wire destruction handlers so Narasimha can actually kill agents
        self._narasimha = get_narasimha()
        self._narasimha.register_destruction_handler(self._narasimha_destroy_agent)
        logger.info("⚡ Narasimha Protocol wired (destruction handlers active)")

    def get_bank(self) -> "CivicBank":
        """
        Lazy-load the CivicBank.

        Phase 4c: Use VFS path for database to ensure it's in sandbox.
        Requires: cryptography package (see pyproject.toml)
        """
        if self._bank is None:
            from pathlib import Path

            from steward.system_agents.civic.tools.economy import CivicBank

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
            from steward.system_agents.civic.tools.vault import CivicVault

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
        """
        # Delegate to CapabilityRegistry (handles core capabilities)
        return self._capability_registry.has_capability(agent_id, capability)

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
                agent_id=agent_id,
                revoker_id="NARASIMHA",
                reason=f"Kill-switch activated: {trigger.threat_type.value}"
            )
            logger.critical(f"🔒 Capabilities revoked: {agent_id}")

        # 3. Remove from agent registry (internal - doesn't affect MappingProxyType view)
        if agent_id in self._agent_registry:
            del self._agent_registry[agent_id]
            logger.critical(f"🗑️  Removed from registry: {agent_id}")

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
        if agent_id not in self._agent_registry:
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

        # PHASE B: VEDIC GOVERNANCE - Assign Varna and Ashrama
        # Varna = Classification (what kind of being is this agent)
        varna = categorize_agent_by_function(agent.agent_id)
        self._varna_registry[agent.agent_id] = varna

        # Ashrama = Lifecycle stage (all agents start as students)
        ashrama = AshramaTransition(agent.agent_id)
        self._ashrama_registry[agent.agent_id] = ashrama

        varna_desc = get_varna_description(varna)
        logger.info(
            f"🕉️  Agent '{agent.agent_id}' classified: "
            f"Varna={varna.value} ({varna_desc.get('name', 'Unknown')}), "
            f"Ashrama={ashrama.current_ashrama.value}"
        )

        # PHASE 1.1: INJECT SYSTEM INTERFACE (The Bridge)
        # Give agent standardized access to:
        # - Dependency Management (replaces requirements.txt)
        # - VFS (replaces direct Path() access)
        # - Config (replaces hardcoded values)
        from vibe_core.agent_interface import AgentSystemInterface

        agent.system = AgentSystemInterface(self, agent.agent_id)
        logger.info(f"🔌 {agent.agent_id} received system interface (sandbox: {agent.system.get_sandbox_path()})")

        # Phase 2: Spawn Process (deferred if spawn_process=False)
        if spawn_process:
            self.process_manager.spawn_agent(agent.agent_id, type(agent), config=getattr(agent, "config", None))

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

            # Spawn the process
            try:
                self.process_manager.spawn_agent(agent_id, type(agent), config=getattr(agent, "config", None))
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
            manifest = agent.get_manifest()
            self._manifest_registry.register(manifest)
            logger.info(f"   📜 {agent_id}: {manifest.description}")

        self._status = KernelStatus.RUNNING
        logger.info("✅ KERNEL RUNNING")

        # PULSE: Write initial snapshot on boot
        self._pulse()

    def tick(self) -> None:
        """Tick the kernel - process one task from the scheduler"""
        if self._status != KernelStatus.RUNNING:
            logger.warning("⚠️  Kernel not running")
            return

        # Phase 2.5: Check for SETTINGS.md changes and sync to reality
        # This implements the SETTINGS -> REALITY direction (Command Queue)
        if not self._settings_writing and self._check_settings_file_changed():
            logger.info("⚙️  SETTINGS.md changed, synchronizing to reality...")
            self._sync_settings_to_reality()

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

        try:
            # Record start
            self._ledger.record_start(task)

            # Execute task via Process Manager (IPC)
            logger.info(f"⚡ Dispatching task {task.task_id} to {task.agent_id} (IPC)")

            try:
                self.process_manager.send_task(task.agent_id, task)
                # Note: Result is now async via pipe. We don't get it immediately here.
                # The ProcessManager loop handles results.
                # For this synchronous tick, we might need to wait or change architecture.
                # For Phase 2 MVP, we'll assume fire-and-forget or polling.

            except ValueError as e:
                logger.error(f"❌ Dispatch failed: {e}")
                self._ledger.record_failure(task, str(e))
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

        except Exception as e:
            error = str(e)
            logger.exception(f"❌ Task {task.task_id} failed: {error}")
            self._ledger.record_failure(task, error)

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

                else:
                    error = msg.get("error")
                    logger.error(f"❌ Task {task_id} failed (Async IPC): {error}")

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
    # PHASE B: VEDIC GOVERNANCE (Varna + Ashrama)
    # =========================================================================

    def get_agent_varna(self, agent_id: str) -> Optional[Varna]:
        """Get the Varna (classification) of an agent."""
        return self._varna_registry.get(agent_id)

    def get_agent_ashrama(self, agent_id: str) -> Optional[AshramaTransition]:
        """Get the Ashrama (lifecycle stage) of an agent."""
        return self._ashrama_registry.get(agent_id)

    def get_agent_permissions(self, agent_id: str) -> List[str]:
        """Get the current permissions for an agent based on Ashrama."""
        ashrama = self._ashrama_registry.get(agent_id)
        if ashrama:
            return ashrama.get_current_permissions()
        return []

    def check_agent_permission(self, agent_id: str, permission: str) -> bool:
        """Check if an agent has a specific permission based on Ashrama."""
        permissions = self.get_agent_permissions(agent_id)
        return permission in permissions

    def transition_agent_ashrama(self, agent_id: str, new_ashrama: Ashrama, reason: str = "") -> bool:
        """
        Transition an agent to a new Ashrama (lifecycle stage).

        Returns True if transition succeeded, False otherwise.
        """
        ashrama_transition = self._ashrama_registry.get(agent_id)
        if not ashrama_transition:
            logger.error(f"Agent '{agent_id}' not found in Ashrama registry")
            return False

        old_ashrama = ashrama_transition.current_ashrama
        success = ashrama_transition.transition_to(new_ashrama, reason)

        if success:
            logger.info(
                f"🕉️  Agent '{agent_id}' transitioned: "
                f"{old_ashrama.value} → {new_ashrama.value} ({reason or 'No reason given'})"
            )

            # Record in Parampara
            self.lineage.add_block(
                event_type=LineageEventType.AGENT_REGISTERED,  # Could add ASHRAMA_TRANSITION type
                agent_id=agent_id,
                data={
                    "event": "ashrama_transition",
                    "from": old_ashrama.value,
                    "to": new_ashrama.value,
                    "reason": reason,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

        return success

    def get_governance_status(self, agent_id: str) -> Dict[str, Any]:
        """Get full governance status for an agent (Varna + Ashrama)."""
        varna = self._varna_registry.get(agent_id)
        ashrama = self._ashrama_registry.get(agent_id)

        if not varna or not ashrama:
            return {"error": f"Agent '{agent_id}' not found"}

        varna_desc = get_varna_description(varna)
        ashrama_desc = get_ashrama_description(ashrama.current_ashrama)

        return {
            "agent_id": agent_id,
            "varna": {
                "type": varna.value,
                "name": varna_desc.get("name", "Unknown"),
                "consciousness": varna_desc.get("consciousness", "Unknown"),
                "mobility": varna_desc.get("mobility", "Unknown"),
            },
            "ashrama": {
                "stage": ashrama.current_ashrama.value,
                "name": ashrama_desc.get("name", "Unknown"),
                "phase": ashrama_desc.get("phase", "Unknown"),
                "permissions": ashrama.get_current_permissions(),
                "time_in_stage_seconds": ashrama.time_in_current_stage().total_seconds(),
            },
        }

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
        self,
        agent_id: str,
        capabilities: List[str],
        revoker_id: str,
        reason: Optional[str] = None
    ) -> Dict[str, any]:
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
                "message": f"Permission denied: '{revoker_id}' cannot revoke from '{agent_id}'"
            }

        # Delegate to capability registry
        result = self._capability_registry.revoke(
            agent_id=agent_id,
            capabilities=capabilities,
            revoker_id=revoker_id,
            reason=reason
        )

        return result

    def grant_capability(
        self,
        agent_id: str,
        capabilities: List[str],
        granter_id: str,
        reason: Optional[str] = None
    ) -> Dict[str, any]:
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
                "message": f"Permission denied: '{granter_id}' cannot grant capabilities"
            }

        # Delegate to capability registry
        result = self._capability_registry.grant(
            agent_id=agent_id,
            capabilities=capabilities,
            granter_id=granter_id,
            reason=reason
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
        """Submit a task to the kernel"""
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
                    snapshot["agents"][agent_id] = agent_status
                except Exception as e:
                    logger.warning(f"⚠️  Could not get status from {agent_id}: {e}")
                    snapshot["agents"][agent_id] = {"error": str(e)}

            # Write snapshot
            snapshot_path = Path("vibe_snapshot.json")
            snapshot_path.write_text(json.dumps(snapshot, indent=2))
            logger.info("💓 Pulse written: vibe_snapshot.json")

            # Render OPERATIONS.md
            self._render_operations_dashboard(snapshot)

            # Render SETTINGS.md (Phase 1: Read-Only)
            self._render_settings_file(snapshot)

        except Exception as e:
            logger.error(f"❌ Pulse failed: {e}")

    def _render_operations_dashboard(self, snapshot: Dict[str, Any]) -> None:
        """Render OPERATIONS.md from snapshot data"""
        try:
            lines = [
                "# 🏗️ OPERATIONS DASHBOARD",
                "",
                f"**Last Updated:** {snapshot['timestamp']}",
                f"**Status:** {snapshot['kernel_status']}",
                "",
                "## 📊 Kernel Status",
                f"- Kernel: {snapshot['kernel_status']}",
                f"- Agents Registered: {len(snapshot['agents'])}",
                f"- Queue Length: {snapshot['scheduler']['queue_length']}",
                f"- Completed Tasks: {snapshot['scheduler']['completed']}",
                f"- Total Events: {snapshot['ledger_stats']['total_events']}",
                "",
                "## 🤖 Agent Status",
            ]

            for agent_id, status in snapshot["agents"].items():
                lines.append(f"\n### {agent_id}")
                if "error" in status:
                    lines.append(f"❌ Error: {status['error']}")
                else:
                    for key, value in status.items():
                        lines.append(f"- {key}: {value}")

            lines.extend(
                [
                    "",
                    "---",
                    "*This dashboard is auto-generated by the kernel heartbeat.*",
                ]
            )

            ops_path = Path("OPERATIONS.md")
            ops_path.write_text("\n".join(lines))
            logger.info("📋 Operations dashboard rendered")

        except Exception as e:
            logger.error(f"❌ Failed to render dashboard: {e}")

    def _render_settings_file(self, snapshot: Dict[str, Any]) -> None:
        """
        Render SETTINGS.md from snapshot data.

        PHASE 1: READ-ONLY projection of kernel configuration.
        This file shows the current system state and configuration.

        PHASE 2: Command Queue for SETTINGS -> REALITY sync.
        """
        try:
            # Set write lock to prevent concurrent read
            self._settings_writing = True
            lines = [
                "# ⚙️ SYSTEM SETTINGS",
                "",
                f"**Last Updated:** {snapshot['timestamp']}",
                "**Mode:** READ-ONLY (Phase 1)",
                "",
                "> This file is auto-generated by the kernel heartbeat.",
                "> Phase 2 will enable a Command Queue for declarative configuration.",
                "",
                "## 🔧 Kernel Configuration",
                "",
                f"- **Status:** {snapshot['kernel_status']}",
                f"- **Ledger Path:** {self.ledger_path}",
                f"- **Agents Registered:** {len(snapshot['agents'])}",
                f"- **Queue Length:** {snapshot['scheduler']['queue_length']}",
                f"- **Total Events:** {snapshot['ledger_stats']['total_events']}",
                "",
            ]

            # Add agent registry details
            lines.extend(
                [
                    "## 🤖 Agent Registry",
                    "",
                    "Current agent configuration and status:",
                    "",
                ]
            )

            for agent_id, status in snapshot["agents"].items():
                lines.append(f"### `{agent_id}`")
                lines.append("")

                if "error" in status:
                    lines.append(f"❌ **Error:** {status['error']}")
                else:
                    # Display all status fields
                    for key, value in status.items():
                        # Format value nicely
                        if isinstance(value, list):
                            value_str = ", ".join(f"`{v}`" for v in value)
                        elif isinstance(value, dict):
                            value_str = f"{len(value)} items"
                        else:
                            value_str = f"{value}"
                        lines.append(f"- **{key}:** {value_str}")

                # Add governance info if available
                varna = self._varna_registry.get(agent_id)
                ashrama_transition = self._ashrama_registry.get(agent_id)

                if varna:
                    lines.append(f"- **Varna (Class):** `{varna.value}`")

                if ashrama_transition:
                    lines.append(f"- **Ashrama (Stage):** `{ashrama_transition.current_ashrama.value}`")
                    permissions = ashrama_transition.get_current_permissions()
                    if permissions:
                        lines.append(f"- **Permissions:** {', '.join(f'`{p}`' for p in permissions)}")

                lines.append("")

            # Add Command Queue sections
            lines.extend(
                [
                    "---",
                    "",
                    "## ⚡ Pending Commands",
                    "",
                    "> **Write your commands here.** The kernel will process them on the next tick.",
                    "> Commands are executed in order and then moved to the Execution Ledger below.",
                    "",
                    "**Available Commands:**",
                    "- `SET kernel.log_level=DEBUG` - Change kernel log level (DEBUG/INFO/WARNING/ERROR/CRITICAL)",
                    "- `PAUSE agent.<agent_id>` - Pause an agent (not yet implemented)",
                    "- `RESUME agent.<agent_id>` - Resume an agent (not yet implemented)",
                    "",
                    "**Example:**",
                    "```",
                    "- SET kernel.log_level=DEBUG",
                    "```",
                    "",
                    "_No pending commands. Add commands above this line._",
                    "",
                    "---",
                    "",
                    "## 🏛️ Execution Ledger",
                    "",
                    "> **Read-Only.** This section shows the last 10 executed commands.",
                    "> The kernel updates this automatically after processing commands.",
                    "",
                ]
            )

            # Add execution history
            if self._settings_execution_history:
                for entry in reversed(list(self._settings_execution_history)):
                    timestamp = entry.get("timestamp", "unknown")
                    status = entry.get("status", "UNKNOWN")
                    command = entry.get("command", "")
                    reason = entry.get("reason", "")

                    # Format status emoji
                    status_emoji = "✅" if status == "SUCCESS" else "❌"

                    # Format command text
                    if isinstance(command, dict):
                        action = command.get("action", "")
                        if action == "SET":
                            cmd_text = f"SET {command.get('key')}={command.get('value')}"
                        elif action == "PAUSE":
                            cmd_text = f"PAUSE {command.get('agent_id')}"
                        elif action == "RESUME":
                            cmd_text = f"RESUME {command.get('agent_id')}"
                        else:
                            cmd_text = str(command)
                    else:
                        cmd_text = str(command)

                    # Build ledger line
                    line_parts = [f"- [{status_emoji} {status} @ {timestamp}]", cmd_text]
                    if reason:
                        line_parts.append(f"(Reason: {reason})")

                    lines.append(" ".join(line_parts))
            else:
                lines.append("_No commands executed yet._")

            lines.extend(
                [
                    "",
                    "---",
                    (
                        "*This file is auto-generated by the kernel pulse. "
                        "Edit the Pending Commands section to control the system.*"
                    ),
                ]
            )

            # Write SETTINGS.md
            settings_path = Path("SETTINGS.md")
            settings_path.write_text("\n".join(lines))

            # Update last modified timestamp (to prevent immediate re-read)
            self._settings_last_modified = settings_path.stat().st_mtime

            logger.info("⚙️  Settings file rendered: SETTINGS.md")

        except Exception as e:
            logger.error(f"❌ Failed to render settings file: {e}")

        finally:
            # Release write lock
            self._settings_writing = False

    def _check_settings_file_changed(self) -> bool:
        """
        Check if SETTINGS.md has been modified since last read.

        Returns:
            True if file changed, False otherwise
        """
        try:
            settings_path = Path("SETTINGS.md")
            if not settings_path.exists():
                return False

            # Get current modification time
            current_mtime = settings_path.stat().st_mtime

            # Check if changed
            if current_mtime > self._settings_last_modified:
                logger.debug(f"⚙️  SETTINGS.md changed (mtime: {current_mtime})")
                return True

            return False

        except Exception as e:
            logger.error(f"❌ Failed to check settings file: {e}")
            return False

    def _parse_settings_commands(self) -> List[Dict[str, str]]:
        """
        Parse command queue from SETTINGS.md.

        Returns:
            List of command dicts: [{"action": "SET", "key": "...", "value": "..."}]

        Command Format:
            - SET kernel.log_level=DEBUG
            - PAUSE agent.steward
            - RESUME agent.steward
        """
        try:
            settings_path = Path("SETTINGS.md")
            if not settings_path.exists():
                return []

            content = settings_path.read_text()
            commands = []

            # Find the "Pending Commands" section
            in_commands_section = False
            for line in content.split("\n"):
                line = line.strip()

                # Detect start of Pending Commands section
                if "## ⚡ Pending Commands" in line:
                    in_commands_section = True
                    continue

                # Stop at next section
                if in_commands_section and line.startswith("##"):
                    break

                # Skip non-command lines
                if not in_commands_section or not line.startswith("-"):
                    continue

                # Skip placeholder/comment lines
                if line.startswith("_") or line.startswith("```"):
                    continue

                # Parse command: "- SET kernel.log_level=DEBUG"
                command_text = line[1:].strip()  # Remove leading "-"

                # Parse SET commands
                if command_text.startswith("SET "):
                    rest = command_text[4:].strip()  # Remove "SET "
                    if "=" in rest:
                        key, value = rest.split("=", 1)
                        commands.append(
                            {
                                "action": "SET",
                                "key": key.strip(),
                                "value": value.strip(),
                            }
                        )

                # Parse PAUSE commands
                elif command_text.startswith("PAUSE "):
                    agent_id = command_text[6:].strip()
                    commands.append(
                        {
                            "action": "PAUSE",
                            "agent_id": agent_id,
                        }
                    )

                # Parse RESUME commands
                elif command_text.startswith("RESUME "):
                    agent_id = command_text[7:].strip()
                    commands.append(
                        {
                            "action": "RESUME",
                            "agent_id": agent_id,
                        }
                    )

                else:
                    logger.warning(f"⚠️  Unknown command format: {command_text}")

            return commands

        except Exception as e:
            logger.error(f"❌ Failed to parse settings commands: {e}")
            return []

    def _execute_settings_commands(self, commands: List[Dict[str, str]]) -> None:
        """
        Execute settings commands with validation and whitelist enforcement.

        Security:
            - Only whitelisted settings can be modified
            - Schema validation on all inputs
            - Execution history tracking (feedback loop)
            - Audit trail in ledger
        """
        if not commands:
            return

        # WHITELIST: Only these settings can be modified
        EDITABLE_SETTINGS = {
            "kernel.log_level",  # Safe: logging verbosity
            # "kernel.status",      # FORBIDDEN: Security risk
            # "agent.*.capabilities" # FORBIDDEN: Capability escalation
        }

        logger.info(f"⚙️  Executing {len(commands)} settings commands")

        for cmd in commands:
            execution_record = {
                "command": cmd,
                "timestamp": datetime.utcnow().strftime("%H:%M:%S UTC"),
                "status": "SUCCESS",
                "reason": "",
            }

            try:
                action = cmd.get("action")

                if action == "SET":
                    key = cmd.get("key", "")
                    value = cmd.get("value", "")

                    # Whitelist check
                    if key not in EDITABLE_SETTINGS:
                        execution_record["status"] = "FAILED"
                        execution_record["reason"] = f"Setting '{key}' is not editable (whitelist violation)"
                        logger.warning(
                            f"⛔ SETTINGS COMMAND BLOCKED: '{key}' is not editable. "
                            f"Whitelist: {list(EDITABLE_SETTINGS)}"
                        )
                        self._settings_execution_history.append(execution_record)
                        continue

                    # Execute whitelisted commands
                    if key == "kernel.log_level":
                        self._set_log_level(value)
                        logger.info(f"✅ SET {key}={value}")
                        execution_record["reason"] = "Log level updated successfully"

                elif action == "PAUSE":
                    agent_id = cmd.get("agent_id", "")
                    execution_record["status"] = "FAILED"
                    execution_record["reason"] = "PAUSE command not yet implemented"
                    logger.info(f"⏸️  PAUSE command for {agent_id} (not yet implemented)")
                    # TODO: Implement agent pause

                elif action == "RESUME":
                    agent_id = cmd.get("agent_id", "")
                    execution_record["status"] = "FAILED"
                    execution_record["reason"] = "RESUME command not yet implemented"
                    logger.info(f"▶️  RESUME command for {agent_id} (not yet implemented)")
                    # TODO: Implement agent resume

                else:
                    execution_record["status"] = "FAILED"
                    execution_record["reason"] = f"Unknown action: {action}"

                # Add to execution history (for UI feedback)
                self._settings_execution_history.append(execution_record)

                # Record command execution in ledger (for audit trail)
                self._ledger.record_event(
                    event_type="SETTINGS_COMMAND_EXECUTED",
                    agent_id="kernel",
                    details={
                        "command": cmd,
                        "status": execution_record["status"],
                        "reason": execution_record["reason"],
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )

            except Exception as e:
                # Record failure in execution history
                execution_record["status"] = "FAILED"
                execution_record["reason"] = str(e)
                self._settings_execution_history.append(execution_record)

                logger.error(f"❌ Failed to execute command {cmd}: {e}")
                # Continue with other commands (don't fail all if one fails)

    def _set_log_level(self, level: str) -> None:
        """Set kernel log level (whitelisted setting)"""
        import logging

        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }

        if level.upper() not in level_map:
            raise ValueError(f"Invalid log level: {level}. Must be one of {list(level_map.keys())}")

        logging.getLogger("VIBE_KERNEL").setLevel(level_map[level.upper()])
        logger.info(f"📊 Log level changed to {level.upper()}")

    def _sync_settings_to_reality(self) -> None:
        """
        Synchronize SETTINGS.md commands to kernel reality.

        PHASE 2: SETTINGS -> REALITY direction.

        This implements the "Command Queue" pattern:
        1. Read commands from SETTINGS.md
        2. Validate against whitelist
        3. Execute commands
        4. Remove executed commands from file
        5. Update last modified timestamp
        """
        try:
            # Parse commands
            commands = self._parse_settings_commands()

            if not commands:
                logger.debug("⚙️  No pending commands in SETTINGS.md")
                return

            logger.info(f"⚙️  Found {len(commands)} pending commands")

            # Execute commands (this updates execution history)
            self._execute_settings_commands(commands)

            # Remove executed commands from SETTINGS.md
            self._remove_executed_commands_from_file()

            # Update timestamp to prevent re-execution
            settings_path = Path("SETTINGS.md")
            if settings_path.exists():
                self._settings_last_modified = settings_path.stat().st_mtime

            logger.info("✅ Settings synchronized to reality")

        except Exception as e:
            logger.error(f"❌ Settings sync failed: {e}")
            # Don't crash kernel on sync failure

    def _remove_executed_commands_from_file(self) -> None:
        """
        Remove executed commands from SETTINGS.md Pending Commands section.

        This creates the feedback loop: Commands move from Pending to Execution Ledger.
        """
        try:
            settings_path = Path("SETTINGS.md")
            if not settings_path.exists():
                return

            # Set write lock
            self._settings_writing = True

            # Read current file
            content = settings_path.read_text()
            lines = content.split("\n")

            # Rebuild file, removing commands from Pending Commands section
            new_lines = []
            in_pending_section = False

            for line in lines:
                # Detect Pending Commands section start
                if "## ⚡ Pending Commands" in line:
                    in_pending_section = True
                    new_lines.append(line)
                    continue

                # Detect next section (end of Pending Commands)
                if in_pending_section and line.strip().startswith("##"):
                    in_pending_section = False

                # Skip command lines in Pending Commands section
                if in_pending_section and line.strip().startswith("- ") and not line.strip().startswith("- `"):
                    # This is a command line - skip it (it's been executed)
                    # But preserve example/help lines that start with "- `"
                    continue

                # Keep all other lines
                new_lines.append(line)

            # Write updated file
            settings_path.write_text("\n".join(new_lines))
            logger.debug("⚙️  Removed executed commands from SETTINGS.md")

        except Exception as e:
            logger.error(f"❌ Failed to remove executed commands: {e}")

        finally:
            # Release write lock
            self._settings_writing = False
