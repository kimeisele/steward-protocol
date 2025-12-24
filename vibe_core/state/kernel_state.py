"""
KernelState - Layer 2 (PRANA) Kernel State Serialization

Captures kernel runtime state for the Prakriti state engine.
Allows snapshotting and restoring kernel state.

GAD-000 Compliant:
- All methods return dict/dataclass
- get_capabilities() for discoverability
"""

import logging
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.protocols import VibeKernel

logger = logging.getLogger("KERNEL_STATE")


@dataclass
class AgentSnapshot:
    """Snapshot of an agent's state."""

    agent_id: str
    status: str
    capabilities: List[str]
    varna: Optional[str] = None
    ashrama: Optional[str] = None


@dataclass
class QueueSnapshot:
    """Snapshot of scheduler queue state."""

    pending: int
    by_priority: Dict[int, int]
    executing: Optional[str] = None
    completed_count: int = 0


@dataclass
class KernelSnapshot:
    """Complete kernel state snapshot."""

    timestamp: float
    status: str
    uptime_seconds: float
    agents: List[AgentSnapshot]
    queue: QueueSnapshot
    plugins_loaded: List[str]


class KernelState:
    """Kernel state wrapper for Prakriti.

    Provides read-only access to kernel runtime state.
    Allows snapshotting for persistence and recovery.
    """

    def __init__(self, kernel: Optional["VibeKernel"] = None):
        self._kernel = kernel
        self._boot_time = None

    # =========================================================================
    # Kernel Injection
    # =========================================================================

    def inject_kernel(self, kernel: "VibeKernel") -> None:
        """Inject kernel reference after boot."""
        self._kernel = kernel
        self._boot_time = time.time()
        logger.debug("[KERNEL_STATE] Kernel injected")

    def has_kernel(self) -> bool:
        """Check if kernel is available."""
        return self._kernel is not None

    # =========================================================================
    # GAD-000: Discoverability
    # =========================================================================

    def get_capabilities(self) -> Dict[str, Any]:
        """GAD-000 Test 1: Machine-readable capability discovery."""
        return {
            "operations": ["snapshot", "status", "agents", "queue"],
            "has_kernel": self.has_kernel(),
            "read_only": True,
        }

    # =========================================================================
    # Core Operations
    # =========================================================================

    def snapshot(self) -> Optional[KernelSnapshot]:
        """Take a complete kernel state snapshot.

        Returns:
            KernelSnapshot or None if no kernel
        """
        if not self._kernel:
            return None

        kernel = self._kernel
        boot_time = self._boot_time or time.time()

        # Snapshot agents
        agents = []
        for agent_id, agent in kernel.agent_registry.items():
            agents.append(
                AgentSnapshot(
                    agent_id=agent_id,
                    status=getattr(agent, "status", "unknown"),
                    capabilities=list(getattr(agent, "capabilities", [])),
                    varna=getattr(agent, "varna", None),
                    ashrama=getattr(agent, "ashrama", None),
                )
            )

        # Snapshot queue
        queue_status = kernel.scheduler.get_queue_status()
        queue = QueueSnapshot(
            pending=queue_status.get("queue_length", 0),
            by_priority=queue_status.get("by_priority", {}),
            executing=queue_status.get("executing"),
            completed_count=queue_status.get("completed", 0),
        )

        # Snapshot plugins
        plugins = [p.plugin_id for p in kernel.plugins]

        return KernelSnapshot(
            timestamp=time.time(),
            status=kernel.status.value if hasattr(kernel.status, "value") else str(kernel.status),
            uptime_seconds=time.time() - boot_time,
            agents=agents,
            queue=queue,
            plugins_loaded=plugins,
        )

    def status(self) -> Dict[str, Any]:
        """Get kernel status as dict."""
        if not self._kernel:
            return {"available": False, "error": "No kernel injected"}

        snapshot = self.snapshot()
        if not snapshot:
            return {"available": False}

        return {
            "available": True,
            "status": snapshot.status,
            "uptime_seconds": snapshot.uptime_seconds,
            "agent_count": len(snapshot.agents),
            "queue_pending": snapshot.queue.pending,
            "plugins_loaded": len(snapshot.plugins_loaded),
        }

    def agents(self) -> List[AgentSnapshot]:
        """Get list of agent snapshots."""
        snapshot = self.snapshot()
        return snapshot.agents if snapshot else []

    def queue(self) -> Optional[QueueSnapshot]:
        """Get queue snapshot."""
        snapshot = self.snapshot()
        return snapshot.queue if snapshot else None
