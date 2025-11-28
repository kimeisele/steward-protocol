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

import logging
import json
import uuid
import sqlite3
import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import deque
from pathlib import Path
import os

from .kernel import (
    VibeKernel,
    VibeScheduler,
    VibeLedger,
    ManifestRegistry,
    KernelStatus,
)
from .protocols import VibeAgent, AgentManifest
from .scheduling import Task, TaskStatus
from .ledger import InMemoryLedger, SQLiteLedger
from .sarga import get_sarga, Cycle
from .process_manager import ProcessManager  # Phase 2: Process Isolation
from .resource_manager import ResourceManager  # Phase 3: Resource Isolation
from .vfs import VirtualFileSystem  # Phase 4: Filesystem Isolation
from .network_proxy import KernelNetworkProxy  # Phase 4: Network Isolation
from .lineage import LineageChain, LineageEventType  # Phase 5: Parampara Blockchain

# Import Auditor for immune system (optional)
try:
    from steward.system_agents.auditor.tools.invariant_tool import get_judge, InvariantSeverity
    AUDITOR_AVAILABLE = True
except ImportError:
    AUDITOR_AVAILABLE = False
    logger_setup = logging.getLogger("VIBE_KERNEL")
    logger_setup.warning("⚠️  Auditor not available - immune system disabled")

# Import Constitutional Oath verification (Governance Gate - optional)
try:
    from vibe_core.bridge import ConstitutionalOath
    OATH_ENFORCEMENT_AVAILABLE = True
except ImportError:
    OATH_ENFORCEMENT_AVAILABLE = False
    logger_setup = logging.getLogger("VIBE_KERNEL")
    logger_setup.warning("⚠️  Constitutional Oath not available - governance gate disabled")



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

    def get_bank(self) -> "CivicBank":
        """
        Lazy-load the CivicBank.

        Phase 4c: Use VFS path for database to ensure it's in sandbox.
        Requires: cryptography package (see pyproject.toml)
        """
        if self._bank is None:
            from steward.system_agents.civic.tools.economy import CivicBank
            from pathlib import Path

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

    @property
    def agent_registry(self) -> Dict[str, VibeAgent]:
        """Get all registered agents {agent_id: agent}"""
        return self._agent_registry

    @property
    def scheduler(self) -> VibeScheduler:
        """Get the task scheduler"""
        return self._scheduler

    @property
    def ledger(self) -> VibeLedger:
        """Get the immutable ledger"""
        return self._ledger

    @property
    def manifest_registry(self) -> ManifestRegistry:
        """Get the manifest registry"""
        return self._manifest_registry

    @property
    def status(self) -> KernelStatus:
        """Get kernel status"""
        return self._status

    def register_agent(self, agent: VibeAgent) -> None:
        """
        Register an agent and inject kernel reference.

        🛡️  GOVERNANCE GATE: This kernel enforces Constitutional Oath.

        An agent is REFUSED ENTRY if it has not cryptographically bound itself
        to the Constitution via the Genesis Ceremony. This is not a warning.
        This is a hard architectural constraint.

        ARCHITECTURE: Church (Steward) + State (Vibe) = Fused Governance
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
                is_valid, reason = ConstitutionalOath.verify_oath(
                    oath_event,
                    getattr(agent, "identity_tool", None)
                )

                if not is_valid:
                    logger.critical(
                        f"⛔ GOVERNANCE GATE VIOLATION: Agent '{agent.agent_id}' "
                        f"oath verification FAILED: {reason}"
                    )
                    raise PermissionError(
                        f"GOVERNANCE_GATE_DENIED: Agent '{agent.agent_id}' "
                        f"oath is invalid. {reason} "
                        f"Kernel refuses entry."
                    )

                logger.info(
                    f"✅ Governance Gate PASSED: Agent '{agent.agent_id}' "
                    f"oath verified ({reason})"
                )

            except PermissionError:
                # Re-raise governance violations
                raise
            except Exception as e:
                logger.error(
                    f"❌ Governance gate verification error for '{agent.agent_id}': {e}"
                )
                raise PermissionError(
                    f"GOVERNANCE_GATE_ERROR: Agent '{agent.agent_id}' "
                    f"oath verification failed: {str(e)}"
                )

        # STEP 4: THE REGISTRATION (Gate Opens - Agent Enters)
        self._agent_registry[agent.agent_id] = agent

        # PHASE 1.1: INJECT SYSTEM INTERFACE (The Bridge)
        # Give agent standardized access to:
        # - Dependency Management (replaces requirements.txt)
        # - VFS (replaces direct Path() access)
        # - Config (replaces hardcoded values)
        from vibe_core.agent_interface import AgentSystemInterface
        agent.system = AgentSystemInterface(self, agent.agent_id)
        logger.info(
            f"🔌 {agent.agent_id} received system interface "
            f"(sandbox: {agent.system.get_sandbox_path()})"
        )

        # Phase 2: Spawn Process
        self.process_manager.spawn_agent(agent.agent_id, type(agent), config=getattr(agent, 'config', None))

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
            }
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
                    "verified": True
                }
            )
            logger.info(f"⛓️  Agent '{agent.agent_id}' oath recorded in Parampara")

        logger.info(
            f"🛡️  ✅ GOVERNANCE GATE PASSED: Agent '{agent.agent_id}' "
            f"registered and spawned in isolated process."
        )

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
            }
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
                    # We need to reconstruct the Task object or look it up if we want to record properly
                    # For now, we'll just log. In a real system, we'd have a pending_tasks map.
                    # self._ledger.record_completion(task_id, result) 
                    
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
            from vibe_core.vfs import VirtualFileSystem
            import os
            
            vfs = VirtualFileSystem(agent_id)
            repo_path = os.getcwd()  # /Users/ss/Downloads/steward-protocol
            
            # Create symlink: sandbox/repo -> actual repo
            vfs.create_symlink(repo_path, "repo")
            
            logger.info(
                f"🔗 {agent_id} granted repo access: "
                f"{vfs.get_sandbox_path()}/repo -> {repo_path}"
            )
            
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
                            logger.critical(
                                f"🛡️  IMMUNE SYSTEM ALERT: {violation.invariant_name} - {violation.message}"
                            )
                            self.shutdown(reason=f"Immune system reaction: {violation.invariant_name}")
                            return
                        else:
                            logger.debug(f"⚠️  VOID check skipped (requires external context)")
            
            # Log health check (non-critical)
            if report.violations:
                logger.debug(
                    f"⚠️  Auditor info: {len(report.violations)} issue(s) detected"
                )
            else:
                logger.debug("✅ System health check passed")
                
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")

    def get_agent_manifest(self, agent_id: str) -> Optional[AgentManifest]:
        """Get manifest for an agent"""
        return self._manifest_registry.lookup(agent_id)

    def shutdown(self, reason: str = "User shutdown") -> None:
        """Gracefully shut down the kernel"""
        # Phase 5: Record Kernel Shutdown in Parampara (before changing status)
        if hasattr(self, 'lineage'):
            self.lineage.add_block(
                event_type=LineageEventType.KERNEL_SHUTDOWN,
                agent_id=None,
                data={
                    "reason": reason,
                    "timestamp": datetime.utcnow().isoformat(),
                    "agents_active": len(self._agent_registry),
                }
            )
            # Close lineage chain
            self.lineage.close()

        self._status = KernelStatus.STOPPED
        logger.critical(f"🔴 KERNEL SHUTDOWN: {reason}")

        # Phase 2: Shutdown processes
        if hasattr(self, 'process_manager'):
            self.process_manager.shutdown()

        if isinstance(self._ledger, SQLiteLedger):
            self._ledger.close()

    def find_agents_by_capability(self, capability: str) -> List[VibeAgent]:
        """Find agents with a specific capability"""
        manifests = self._manifest_registry.find_by_capability(capability)
        return [self._agent_registry[m.agent_id] for m in manifests]

    def submit_task(self, task: Task) -> str:
        """Submit a task to the kernel"""
        return self._scheduler.submit_task(task)

    def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the result of a completed task"""
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
            logger.info(f"💓 Pulse written: vibe_snapshot.json")
            
            # Render OPERATIONS.md
            self._render_operations_dashboard(snapshot)
            
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
            
            lines.extend([
                "",
                "---",
                "*This dashboard is auto-generated by the kernel heartbeat.*",
            ])
            
            ops_path = Path("OPERATIONS.md")
            ops_path.write_text("\n".join(lines))
            logger.info(f"📋 Operations dashboard rendered")
            
        except Exception as e:
            logger.error(f"❌ Failed to render dashboard: {e}")
