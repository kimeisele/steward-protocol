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
from typing import Dict, Any, List, Optional
from datetime import datetime
from collections import deque
from pathlib import Path

from .kernel import (
    VibeKernel,
    VibeScheduler,
    VibeLedger,
    ManifestRegistry,
    KernelStatus,
)
from .agent_protocol import VibeAgent, AgentManifest
from .scheduling import Task, TaskStatus


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

    def __init__(self, ledger_path: str = ":memory:"):
        """Initialize the kernel"""
        self._agent_registry: Dict[str, VibeAgent] = {}
        self._scheduler = InMemoryScheduler()
        self._ledger = InMemoryLedger()
        self._manifest_registry = InMemoryManifestRegistry()
        self._status = KernelStatus.STOPPED
        self.ledger_path = ledger_path
        logger.info("🚀 Vibe Kernel initialized (in-memory)")

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
        """Register an agent and inject kernel reference"""
        self._agent_registry[agent.agent_id] = agent
        agent.set_kernel(self)
        logger.info(f"✅ Agent registered: {agent.agent_id}")

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
        }

    def get_agent_manifest(self, agent_id: str) -> Optional[AgentManifest]:
        """Get manifest for an agent"""
        return self._manifest_registry.lookup(agent_id)

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
