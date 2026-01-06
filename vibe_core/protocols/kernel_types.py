"""
Kernel Type Protocols - Phase 1 of OPERATION LASAGNE

PROMPT.md: "Any ist verboten. Wenn du Any schreibst, hast du das Datenmodell nicht verstanden."

These types replace Dict[str, Any] patterns in kernel_impl.py and kernel_protocol.py.

VIMANA RANGE ROVER: Military-grade type safety for the Kernel heart.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Dict, List, Optional, Protocol, TypedDict, runtime_checkable

# =============================================================================
# KERNEL STATUS ENUM (replaces Any for kernel.status)
# =============================================================================


class KernelStatus(str, Enum):
    """Kernel lifecycle states - replaces Any."""

    STOPPED = "STOPPED"
    BOOTING = "BOOTING"
    RUNNING = "RUNNING"
    HALTED = "HALTED"
    SHUTTING_DOWN = "SHUTTING_DOWN"


# =============================================================================
# TYPED DICTS FOR KERNEL METHODS (replaces Dict[str, Any])
# =============================================================================


class CapabilityResult(TypedDict, total=False):
    """Result of capability grant/revoke operations."""

    success: bool
    agent_id: str
    capabilities: List[str]
    action: str  # "granted" | "revoked"
    reason: str
    granter_id: str
    timestamp: str


class KernelStatusReport(TypedDict, total=False):
    """Kernel status report - replaces get_status() -> Dict[str, Any]."""

    status: str  # KernelStatus value
    agents_registered: int
    agents_alive: int
    tasks_completed: int
    tasks_pending: int
    uptime_seconds: float
    ledger_hash: str


class SystemStatusReport(TypedDict, total=False):
    """GAD-000 compliant system status - replaces get_system_status() -> Dict[str, Any]."""

    kernel_status: str
    version: str
    agents: Dict[str, str]  # agent_id -> status
    plugins: List[str]
    capabilities: List[str]
    ledger_entries: int
    memory_mb: float
    timestamp: str


class CapabilitiesReport(TypedDict, total=False):
    """Capability discovery report - replaces get_capabilities() -> Dict[str, Any]."""

    available: List[str]
    agents: Dict[str, List[str]]  # agent_id -> capabilities
    plugins: List[str]
    tools: List[str]


if TYPE_CHECKING:
    from vibe_core.scheduling import Task


@dataclass
class TaskResult:
    """Replaces Dict[str, Any] for task results in _completed_tasks."""

    status: str  # "COMPLETED" | "FAILED" | "PENDING"
    task_id: str
    output: Optional[str] = None
    error: Optional[str] = None
    details: Dict[str, str] = field(default_factory=dict)


@dataclass
class AgentHealth:
    """Replaces Dict[str, Dict[str, Any]] for _agent_health_cache."""

    agent_id: str
    alive: bool
    memory_mb: float = 0.0
    cpu_percent: float = 0.0
    last_check: float = 0.0


@dataclass
class AgentData:
    """Replaces Dict[str, Dict[str, Any]] for _data_store."""

    agent_id: str
    data: Dict[str, str] = field(default_factory=dict)


@runtime_checkable
class GovernanceProtocol(Protocol):
    """
    Replaces Optional[Any] for kernel.governance.

    Governance plugins (e.g., VedicGovernancePlugin) implement this.
    """

    def get_paused_agents(self) -> List[str]:
        """Get list of currently paused agent IDs."""
        ...

    def pause_agent(self, agent_id: str) -> bool:
        """Pause an agent. Returns True if successful."""
        ...

    def resume_agent(self, agent_id: str) -> bool:
        """Resume a paused agent. Returns True if successful."""
        ...


@runtime_checkable
class PluginProtocol(Protocol):
    """
    Replaces List[Any] for kernel._plugins.

    All plugins must implement these hooks.
    See: vibe_core/plugin_base.py for base class.
    """

    plugin_id: str
    priority: int

    def on_boot(self, kernel) -> None:
        """Called when kernel boots. Initialize plugin state."""
        ...

    def on_shutdown(self, kernel) -> None:
        """Called when kernel shuts down. Cleanup resources."""
        ...

    def on_tick_pre(self, kernel) -> None:
        """Called before each kernel tick."""
        ...

    def on_tick_post(self, kernel) -> None:
        """Called after each kernel tick."""
        ...

    def on_pulse(self, kernel, transaction) -> Optional[Dict]:
        """Called during system pulse. Return status dict."""
        ...

    def on_agent_pre_register(self, kernel, agent) -> bool:
        """Called before agent registration. Return False to veto."""
        ...

    def on_agent_registered(self, kernel, agent_id: str) -> None:
        """Called after agent is registered."""
        ...

    def on_task_submit(self, kernel, task: "Task") -> None:
        """Called when task is submitted. Raise ValueError to veto."""
        ...

    def on_task_completed(self, kernel, task_id: str, result) -> None:
        """Called when task completes successfully."""
        ...

    def on_task_failed(self, kernel, task_id: str, error: str) -> None:
        """Called when task fails."""
        ...

    def on_capability_check(self, kernel, agent_id: str, capability: str) -> Optional[bool]:
        """Called to check capability. Return False to veto, True to allow, None for no opinion."""
        ...
