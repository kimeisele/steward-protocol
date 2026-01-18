"""
VibeKernel Interface Stub

This is a stub definition of the VibeKernel interface that steward-protocol
cartridges depend on. When cartridges run in vibe-agency, they will use the
actual implementation from vibe_core.kernel.

This stub allows cartridges to be type-checked and developed standalone.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0x3399c877"  # GenesisByte: parampara % 37 == 0

from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Dict, List, Optional, Protocol, TypedDict, runtime_checkable

# Import Layer -1 (Holy Name Maths) for Ternary Status
# SSOT: byte.py defines HolyName with VOID for binary encoding
from vibe_core.mahamantra.substrate.byte import HolyName

from .agent import AgentManifest, VibeAgent
from .registry import ManifestRegistry

if TYPE_CHECKING:
    from vibe_core.protocols.kernel_types import KernelStatusReport, PluginProtocol
    from vibe_core.scheduling import Task


# =============================================================================
# TYPED DICTS - VIMANA RANGE ROVER (replaces Dict[str, object])
# =============================================================================


class QueueStatus(TypedDict, total=False):
    """Scheduler queue statistics - replaces Dict[str, object]."""

    queue_length: int
    pending_count: int
    processing_count: int
    completed_count: int
    failed_count: int
    oldest_pending_age_ms: float


class TaskEvent(TypedDict, total=False):
    """Task event record - replaces Dict[str, object] for task queries."""

    task_id: str
    event_type: str  # "TASK_STARTED", "TASK_COMPLETED", "TASK_FAILED"
    agent_id: str
    status: str
    result: str
    error: str
    duration_ms: float
    timestamp: str


class LedgerEvent(TypedDict, total=False):
    """Generic ledger event - replaces Dict[str, object]."""

    event_id: str
    event_type: str
    agent_id: str
    timestamp: str
    details: Dict[str, object]  # Nested dict still typed
    prev_hash: str
    hash: str
    status: int  # HolyName value (0=HARE, 1=KRISHNA, 2=RAMA, 3=VOID)
    ttl: Optional[int]  # Time To Live in seconds (None = permanent)


class KernelStatus(str, Enum):
    """Kernel execution state"""

    STOPPED = "STOPPED"
    BOOTING = "BOOTING"
    RUNNING = "RUNNING"
    HALTED = "HALTED"


class VibeScheduler(ABC):
    """Task scheduler interface"""

    @abstractmethod
    def submit_task(self, task: "Task") -> str:
        """Submit a task to the queue, return task_id"""
        pass

    @abstractmethod
    def next_task(self) -> Optional["Task"]:
        """Pop next task from queue"""
        pass

    @abstractmethod
    def get_queue_status(self) -> QueueStatus:
        """Get queue statistics"""
        pass


class VibeLedger(ABC):
    """Immutable event ledger interface"""

    @abstractmethod
    def record_event(self, event_type: str, agent_id: str, details: Dict[str, object]) -> str:
        """Record a generic event (used by agents for governance actions)

        Args:
            event_type: Type of event (e.g., "proposal_created", "vote_cast", "credit_transfer")
            agent_id: ID of agent recording the event
            details: Event-specific details (typed as Dict[str, object])

        Returns:
            event_id: Unique identifier for this event
        """
        pass

    @abstractmethod
    def record_start(self, task: "Task") -> None:
        """Record task start"""
        pass

    @abstractmethod
    def record_completion(self, task: "Task", result: object, duration_ms: Optional[float] = None) -> None:
        """Record task completion"""
        pass

    @abstractmethod
    def record_failure(self, task: "Task", error: str, duration_ms: Optional[float] = None) -> None:
        """Record task failure"""
        pass

    @abstractmethod
    def get_task(self, task_id: str) -> Optional[TaskEvent]:
        """Query task result"""
        pass


# ManifestRegistry moved to protocols/registry.py (canonical source)
# Import via: from vibe_core.protocols import ManifestRegistry


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

    @property
    @abstractmethod
    def plugins(self) -> List["PluginProtocol"]:
        """Get list of loaded plugins"""
        pass

    @abstractmethod
    def register_agent(self, agent: VibeAgent) -> None:
        """Register an agent and inject kernel reference"""
        pass

    @abstractmethod
    def get_status(self) -> "KernelStatusReport":
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


# =============================================================================
# PHASE 2: Protocols for Hot-Swappable Services
# PROMPT.md: "Protocol statt konkrete Klassen (Dependency Inversion)"
#
# These protocols enable swapping implementations without modifying kernel code.
# Unlike ABCs, Protocols use structural subtyping (no inheritance required).
# =============================================================================


@runtime_checkable
class SchedulerProtocol(Protocol):
    """
    Protocol for task scheduler.

    GEMINI DIRECTIVE: "Use Protocols (structural subtyping, no inheritance)"

    Implementations:
        - PriorityScheduler (priority queue)
        - FIFOScheduler (simple queue)
        - RateLimitedScheduler (with throttling)

    Usage:
        scheduler = ServiceRegistry.get(SchedulerProtocol)
        task_id = scheduler.submit_task(task)
    """

    def submit_task(self, task: "Task") -> str:
        """
        Submit a task to the queue.

        Args:
            task: Task object to schedule

        Returns:
            task_id: Unique identifier for tracking
        """
        ...

    def next_task(self) -> Optional["Task"]:
        """
        Pop next task from queue.

        Returns:
            Task object or None if queue empty
        """
        ...

    def get_queue_status(self) -> QueueStatus:
        """
        Get queue statistics.

        Returns:
            QueueStatus with queue_length, pending_count, etc.
        """
        ...

    def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a pending task.

        Args:
            task_id: ID of task to cancel

        Returns:
            True if cancelled, False if not found/already running
        """
        ...

    def get_task_status(self, task_id: str) -> Optional[str]:
        """
        Get status of a specific task.

        Returns:
            Status string or None if not found
        """
        ...


@runtime_checkable
class LedgerProtocol(Protocol):
    """
    Protocol for immutable event ledger.

    Implementations:
        - SQLiteLedger (persistent)
        - InMemoryLedger (ephemeral)

    Usage:
        ledger = ServiceRegistry.get(LedgerProtocol)
        event_id = ledger.record_event("AGENT_BORN", "herald", {"role": "announcer"})
    """

    def record_event(self, event_type: str, agent_id: str, details: Dict[str, object]) -> str:
        """
        Record an immutable event.

        Args:
            event_type: Type of event (e.g., "AGENT_BORN", "TASK_COMPLETED")
            agent_id: ID of agent this event belongs to
            details: Event payload (typed Dict[str, object])

        Returns:
            event_id: Unique identifier for this event
        """
        ...

    def get_all_events(self) -> List[LedgerEvent]:
        """Get all events in chronological order."""
        ...

    def count_events(self) -> int:
        """Get total number of events."""
        ...

    def get_top_hash(self) -> str:
        """Get hash of latest event (blockchain-style)."""
        ...

    def get_task(self, task_id: str) -> Optional[TaskEvent]:
        """Get task event by task_id."""
        ...

    def record_start(self, task: "Task") -> None:
        """Record task start event."""
        ...

    def record_completion(self, task: "Task", result: object) -> None:
        """Record task completion event."""
        ...

    def record_failure(self, task: "Task", error: str) -> None:
        """Record task failure event."""
        ...

    def close(self) -> None:
        """Close any open resources (e.g., database connections)."""
        ...

    def get_all_entries(self) -> List[LedgerEvent]:
        """Alias for get_all_events (backward compatibility)."""
        ...

    # --- PHASE 29: DECAY INTEGRATION ---

    def record_event_with_status(
        self, event_type: str, agent_id: str, details: Dict[str, object], status: "HolyName"
    ) -> str:
        """
        Record an event with explicit Karmic Status.

        LOGIC (Decay):
        - KRISHNA (01): Store permanently (Merkle Tip Update).
        - RAMA (10):    Store with TTL (Time To Live = 24h).
        - VOID (11):    Reject immediately (Not recorded).
        - HARE (00):    Store as pending (TTL = 1h).
        """
        ...

    def purge_decayed(self) -> int:
        """
        Remove all entries that have exceeded their TTL.
        This is the 'Forgetting' mechanism (Kali Yuga Entropy).

        Returns:
            Number of entries purged.
        """
        ...

    def get_status(self, event_id: str) -> Optional["HolyName"]:
        """
        Get the Karmic Status of an entry.
        """
        ...
