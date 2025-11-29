"""
VibeKernel Interface Stub

This is a stub definition of the VibeKernel interface that steward-protocol
cartridges depend on. When cartridges run in vibe-agency, they will use the
actual implementation from vibe_core.kernel.

This stub allows cartridges to be type-checked and developed standalone.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional

from .agent_protocol import AgentManifest, VibeAgent
from .scheduling import Task


class KernelStatus(str, Enum):
    """Kernel execution state"""

    STOPPED = "STOPPED"
    BOOTING = "BOOTING"
    RUNNING = "RUNNING"
    HALTED = "HALTED"


class VibeScheduler(ABC):
    """Task scheduler interface"""

    @abstractmethod
    def submit_task(self, task: Task) -> str:
        """Submit a task to the queue, return task_id"""
        pass

    @abstractmethod
    def next_task(self) -> Optional[Task]:
        """Pop next task from queue"""
        pass

    @abstractmethod
    def get_queue_status(self) -> Dict[str, Any]:
        """Get queue statistics"""
        pass


class VibeLedger(ABC):
    """Immutable event ledger interface"""

    @abstractmethod
    def record_event(self, event_type: str, agent_id: str, details: Dict[str, Any]) -> str:
        """Record a generic event (used by agents for governance actions)

        Args:
            event_type: Type of event (e.g., "proposal_created", "vote_cast", "credit_transfer")
            agent_id: ID of agent recording the event
            details: Event-specific details

        Returns:
            event_id: Unique identifier for this event
        """
        pass

    @abstractmethod
    def record_start(self, task: Task) -> None:
        """Record task start"""
        pass

    @abstractmethod
    def record_completion(self, task: Task, result: Any) -> None:
        """Record task completion"""
        pass

    @abstractmethod
    def record_failure(self, task: Task, error: str) -> None:
        """Record task failure"""
        pass

    @abstractmethod
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Query task result"""
        pass


class ManifestRegistry(ABC):
    """Agent manifest registry interface"""

    @abstractmethod
    def register(self, manifest: AgentManifest) -> None:
        """Register an agent manifest"""
        pass

    @abstractmethod
    def lookup(self, agent_id: str) -> Optional[AgentManifest]:
        """Look up manifest by agent_id"""
        pass

    @abstractmethod
    def find_by_capability(self, capability: str) -> List[AgentManifest]:
        """Find agents with a specific capability"""
        pass

    @abstractmethod
    def list_all(self) -> List[AgentManifest]:
        """List all registered manifests"""
        pass


class VibeKernel(ABC):
    """
    VibeOS Kernel Interface

    The kernel is the runtime host for all cartridges. It provides:
    - Agent registry (process table)
    - Task scheduler (FIFO queue)
    - Immutable ledger (SQLite)
    - Manifest registry (STEWARD protocol identity)

    When steward-protocol cartridges are loaded, the kernel calls:
    1. agent.set_kernel(self) - for dependency injection
    2. agent.process(task) - to execute tasks
    """

    @property
    @abstractmethod
    def agent_registry(self) -> Dict[str, VibeAgent]:
        """Get all registered agents {agent_id: agent}"""
        pass

    @property
    @abstractmethod
    def scheduler(self) -> VibeScheduler:
        """Get the task scheduler"""
        pass

    @property
    @abstractmethod
    def ledger(self) -> VibeLedger:
        """Get the immutable ledger"""
        pass

    @property
    @abstractmethod
    def manifest_registry(self) -> ManifestRegistry:
        """Get the manifest registry"""
        pass

    @property
    @abstractmethod
    def status(self) -> KernelStatus:
        """Get kernel status"""
        pass

    @abstractmethod
    def register_agent(self, agent: VibeAgent) -> None:
        """Register an agent and inject kernel reference"""
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get full kernel status"""
        pass

    @abstractmethod
    def get_agent_manifest(self, agent_id: str) -> Optional[AgentManifest]:
        """Get manifest for an agent"""
        pass

    @abstractmethod
    def find_agents_by_capability(self, capability: str) -> List[VibeAgent]:
        """Find agents with a specific capability"""
        pass
