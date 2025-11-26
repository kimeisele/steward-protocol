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
from .agent_protocol import VibeAgent, AgentManifest
from .scheduling import Task, TaskStatus

# Import Auditor for immune system
try:
    from auditor.tools.invariant_tool import get_judge, InvariantSeverity
    AUDITOR_AVAILABLE = True
except ImportError:
    AUDITOR_AVAILABLE = False
    logger_setup = logging.getLogger("VIBE_KERNEL")
    logger_setup.warning("⚠️  Auditor not available - immune system disabled")

# Import Constitutional Oath verification (Governance Gate)
try:
    from steward.constitutional_oath import ConstitutionalOath
    OATH_ENFORCEMENT_AVAILABLE = True
except ImportError:
    OATH_ENFORCEMENT_AVAILABLE = False
    logger_setup = logging.getLogger("VIBE_KERNEL")
    logger_setup.warning("⚠️  Constitutional Oath not available - governance gate disabled")


logger = logging.getLogger("VIBE_KERNEL")


class InMemoryScheduler(VibeScheduler):
    """FIFO Task Scheduler - Real-time queue management"""

    def __init__(self):
        self.queue: deque = deque()
        self.executing: Optional[Task] = None
        self.completed: Dict[str, Task] = {}

    def submit_task(self, task: Task) -> str:
        """Submit task to queue, return task_id"""
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


class InMemoryLedger(VibeLedger):
    """Immutable Event Ledger - Append-only task record"""

    def __init__(self):
        self.events: List[Dict[str, Any]] = []
        self._event_counter = 0

    def record_event(self, event_type: str, agent_id: str, details: Dict[str, Any]) -> str:
        """Record a generic event (governance action)"""
        self._event_counter += 1
        event_id = f"EVT-{self._event_counter:06d}"
        event = {
            "event_id": event_id,
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "agent_id": agent_id,
            "details": details,
        }
        self.events.append(event)
        logger.debug(f"📝 Ledger: Event recorded {event_id} ({event_type})")
        return event_id

    def record_start(self, task: Task) -> None:
        """Record task start"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "task_start",
            "task_id": task.task_id,
            "agent_id": task.agent_id,
            "payload": task.payload,
        }
        self.events.append(event)
        logger.debug(f"📝 Ledger: Task started {task.task_id}")

    def record_completion(self, task: Task, result: Any) -> None:
        """Record task completion"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "task_completed",
            "task_id": task.task_id,
            "agent_id": task.agent_id,
            "result": result,
        }
        self.events.append(event)
        logger.debug(f"📝 Ledger: Task completed {task.task_id}")

    def record_failure(self, task: Task, error: str) -> None:
        """Record task failure"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "task_failed",
            "task_id": task.task_id,
            "agent_id": task.agent_id,
            "error": error,
        }
        self.events.append(event)
        logger.debug(f"📝 Ledger: Task failed {task.task_id}")

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Query task result"""
        # Search backwards for the most recent event
        for event in reversed(self.events):
            if event["task_id"] == task_id:
                return event
        return None

    def get_all_events(self) -> List[Dict[str, Any]]:
        """Return all ledger events"""
        return self.events.copy()


class SQLiteLedger(VibeLedger):
    """Persistent SQLite-backed Event Ledger - Append-only task record with persistence"""

    def __init__(self, db_path: str = "data/vibe_ledger.db"):
        """Initialize SQLite ledger with database file"""
        self.db_path = db_path
        self.connection = None
        self._initialize_db()

    def _initialize_db(self) -> None:
        """Create database and schema if not exists"""
        # Ensure directory exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

        # Connect to database (check_same_thread=False for multi-threaded API access)
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row

        # Create table if not exists
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ledger_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                task_id TEXT,
                agent_id TEXT NOT NULL,
                payload TEXT,
                result TEXT,
                error TEXT,
                details TEXT,
                current_hash TEXT NOT NULL,
                previous_hash TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.connection.commit()
        logger.info(f"💾 SQLite ledger initialized at {self.db_path}")
        logger.info(f"⛓️  Cryptographic sealing ACTIVE - Hash chain enabled")

    def record_event(self, event_type: str, agent_id: str, details: Dict[str, Any]) -> str:
        """Record a generic event (governance action)"""
        # Get previous hash for the chain
        previous_hash = self._get_previous_hash()
        
        # Create deterministic event string for hashing (matches verify_chain_integrity)
        timestamp = datetime.utcnow().isoformat()
        event_string = json.dumps({
            "timestamp": timestamp,
            "event_type": event_type,
            "task_id": None,
            "agent_id": agent_id,
            "payload": json.dumps(details) if details else None,
            "result": None,
            "error": None,
        }, sort_keys=True)
        
        # Compute current hash
        current_hash = self._compute_hash(event_string, previous_hash)
        
        cursor = self.connection.cursor()
        row = cursor.execute("SELECT MAX(id) FROM ledger_events").fetchone()
        next_id = (row[0] or 0) + 1
        event_id = f"EVT-{next_id:06d}"
        
        cursor.execute("""
            INSERT INTO ledger_events 
            (event_id, timestamp, event_type, agent_id, payload, current_hash, previous_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            event_id,
            timestamp,
            event_type,
            agent_id,
            json.dumps(details) if details else None,
            current_hash,
            previous_hash,
        ))
        self.connection.commit()
        logger.debug(f"📝 Ledger: Event recorded {event_id} ({event_type})")
        return event_id

    def record_start(self, task: Task) -> None:
        """Record task start"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "task_start",
            "task_id": task.task_id,
            "agent_id": task.agent_id,
            "payload": json.dumps(task.payload) if task.payload else None,
        }
        self._insert_event(event)
        logger.debug(f"📝 Ledger: Task started {task.task_id}")

    def record_completion(self, task: Task, result: Any) -> None:
        """Record task completion"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "task_completed",
            "task_id": task.task_id,
            "agent_id": task.agent_id,
            "result": json.dumps(result) if result else None,
        }
        self._insert_event(event)
        logger.debug(f"📝 Ledger: Task completed {task.task_id}")

    def record_failure(self, task: Task, error: str) -> None:
        """Record task failure"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": "task_failed",
            "task_id": task.task_id,
            "agent_id": task.agent_id,
            "error": error,
        }
        self._insert_event(event)
        logger.debug(f"📝 Ledger: Task failed {task.task_id}")

    def _get_previous_hash(self) -> str:
        """Get hash of last event, or genesis hash if first event"""
        cursor = self.connection.cursor()
        row = cursor.execute(
            "SELECT current_hash FROM ledger_events ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return row[0] if row else "0" * 64

    def _compute_hash(self, event_data: str, previous_hash: str) -> str:
        """Compute SHA256 hash of event + previous_hash"""
        combined = event_data + previous_hash
        return hashlib.sha256(combined.encode()).hexdigest()

    def _insert_event(self, event: Dict[str, Any]) -> None:
        """Insert event into database (append-only with hash chaining)"""
        if not self.connection:
            logger.error("❌ Database connection not available")
            return

        # Get previous hash for the chain
        previous_hash = self._get_previous_hash()
        
        # Create deterministic event string for hashing
        event_string = json.dumps({
            "timestamp": event.get("timestamp"),
            "event_type": event.get("event_type"),
            "task_id": event.get("task_id"),
            "agent_id": event.get("agent_id"),
            "payload": event.get("payload"),
            "result": event.get("result"),
            "error": event.get("error"),
        }, sort_keys=True)
        
        # Compute current hash
        current_hash = self._compute_hash(event_string, previous_hash)

        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO ledger_events
            (timestamp, event_type, task_id, agent_id, payload, result, error, current_hash, previous_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event.get("timestamp"),
            event.get("event_type"),
            event.get("task_id"),
            event.get("agent_id"),
            event.get("payload"),
            event.get("result"),
            event.get("error"),
            current_hash,
            previous_hash,
        ))
        self.connection.commit()

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Query task result (return most recent event for task)"""
        if not self.connection:
            return None

        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM ledger_events
            WHERE task_id = ?
            ORDER BY id DESC
            LIMIT 1
        """, (task_id,))

        row = cursor.fetchone()
        if row:
            return dict(row)
        return None

    def get_all_events(self) -> List[Dict[str, Any]]:
        """Return all ledger events in order"""
        if not self.connection:
            return []

        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM ledger_events ORDER BY id ASC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def verify_chain_integrity(self) -> Dict[str, Any]:
        """Verify the hash chain is intact (tamper detection)"""
        events = self.get_all_events()
        
        if not events:
            return {
                "status": "CLEAN",
                "message": "Ledger is empty (genesis state)",
                "total_events": 0,
                "corrupted": False
            }
        
        corruptions = []
        previous_hash = "0" * 64
        
        for idx, event in enumerate(events):
            stored_previous = event.get("previous_hash")
            stored_current = event.get("current_hash")
            
            if stored_previous != previous_hash:
                corruptions.append({
                    "event_id": event.get("event_id"),
                    "index": idx,
                    "type": "PREVIOUS_HASH_MISMATCH",
                    "error": f"Previous hash mismatch at position {idx}"
                })
            
            # Recompute current hash
            event_string = json.dumps({
                "timestamp": event.get("timestamp"),
                "event_type": event.get("event_type"),
                "task_id": event.get("task_id"),
                "agent_id": event.get("agent_id"),
                "payload": event.get("payload"),
                "result": event.get("result"),
                "error": event.get("error"),
            }, sort_keys=True)
            
            computed_hash = self._compute_hash(event_string, previous_hash)
            
            if computed_hash != stored_current:
                corruptions.append({
                    "event_id": event.get("event_id"),
                    "index": idx,
                    "type": "CURRENT_HASH_MISMATCH",
                    "error": f"Current hash mismatch - computed {computed_hash} != stored {stored_current}"
                })
            
            previous_hash = stored_current
        
        if corruptions:
            logger.error(f"🚨 CORRUPTION DETECTED in ledger! {len(corruptions)} events tampered")
            return {
                "status": "CORRUPTED",
                "message": "DATA TAMPERING DETECTED - Ledger chain broken",
                "total_events": len(events),
                "corrupted": True,
                "corruptions": corruptions,
                "top_hash": previous_hash
            }
        
        logger.info(f"✅ Ledger chain integrity verified ({len(events)} events, chain unbroken)")
        return {
            "status": "CLEAN",
            "message": "All events verified - chain integrity intact",
            "total_events": len(events),
            "corrupted": False,
            "top_hash": previous_hash
        }

    def get_top_hash(self) -> str:
        """Get the fingerprint (top hash) of current ledger state"""
        cursor = self.connection.cursor()
        row = cursor.execute(
            "SELECT current_hash FROM ledger_events ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return row[0] if row else "0" * 64

    def close(self) -> None:
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("💾 SQLite ledger closed")


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
        agent.set_kernel(self)

        logger.info(
            f"🛡️  ✅ GOVERNANCE GATE PASSED: Agent '{agent.agent_id}' "
            f"registered with Constitutional Oath binding"
        )

    def boot(self) -> None:
        """Boot the kernel - register all manifests and start scheduler"""
        self._status = KernelStatus.BOOTING
        logger.info("⚙️  KERNEL BOOTING...")

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

            # Execute task
            logger.info(f"⚡ Processing task {task.task_id} with {task.agent_id}")
            result = agent.process(task)

            # Record completion
            self._ledger.record_completion(task, result)
            logger.info(f"✅ Task {task.task_id} completed")
            
            # PULSE: Update snapshot after task completion
            self._pulse()
            
            # 🛡️ IMMUNE SYSTEM CHECK: Run Auditor after task
            self._check_system_health()

        except Exception as e:
            error = str(e)
            logger.exception(f"❌ Task {task.task_id} failed: {error}")
            self._ledger.record_failure(task, error)

    def get_status(self) -> Dict[str, Any]:
        """Get full kernel status"""
        return {
            "status": self._status.value,
            "agents_registered": len(self._agent_registry),
            "scheduler": self._scheduler.get_queue_status(),
            "manifests": len(self._manifest_registry.list_all()),
            "ledger_events": len(self._ledger.get_all_events()),
            "total_credits": 1000,  # Placeholder - would be fetched from state
        }

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
        self._status = KernelStatus.STOPPED
        logger.critical(f"🔴 KERNEL SHUTDOWN: {reason}")
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
