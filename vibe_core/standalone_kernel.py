"""
STANDALONE KERNEL — Lightweight VibeKernel for Cartridge-Outside-VibeOS
========================================================================

"yad yad ācarati śreṣṭhas tat tad evetaro janaḥ"
"Whatever action a great man performs, common men follow." (BG 3.21)

When cartridges need to run standalone (agent-city, CLI, tests),
they crash because VibeAgent.kernel is None and VibeAgent.system is None.

StandaloneKernel provides the FULL VibeKernel interface using MahaKernel's
existing InMemoryLedger/SQLiteLedger — no mocking, no skipping, real audit trail.

Usage:
    from vibe_core.standalone_kernel import get_standalone_kernel

    kernel = get_standalone_kernel()
    kernel.register_agent(forum_cartridge)
    # forum_cartridge.kernel.ledger.record_event() now works
    # forum_cartridge.system.get_sandbox_path() now works

    Hare Krishna Hare Krishna Krishna Krishna Hare Hare
    Hare Rama   Hare Rama   Rama   Rama   Hare Hare
"""

from __future__ import annotations

import logging
from collections import deque
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional
from uuid import uuid4

from vibe_core.protocols.agent import AgentManifest, VibeAgent
from vibe_core.protocols.ledger import (
    KernelStatus,
    QueueStatus,
    VibeLedger,
    VibeKernel,
    VibeScheduler,
)
from vibe_core.protocols.registry import ManifestRegistry

if TYPE_CHECKING:
    from vibe_core.scheduling import Task

logger = logging.getLogger("STANDALONE_KERNEL")


# =============================================================================
# STANDALONE SCHEDULER — Synchronous FIFO (no async, no threads)
# =============================================================================


class StandaloneScheduler(VibeScheduler):
    """Minimal synchronous task scheduler for standalone operation."""

    def __init__(self) -> None:
        self._queue: deque = deque()
        self._completed: int = 0

    def submit_task(self, task: "Task") -> str:
        task_id = getattr(task, "task_id", None) or f"TASK-{uuid4().hex[:8]}"
        self._queue.append(task)
        return task_id

    def next_task(self) -> Optional["Task"]:
        if self._queue:
            self._completed += 1
            return self._queue.popleft()
        return None

    def get_queue_status(self) -> QueueStatus:
        return QueueStatus(
            queue_length=len(self._queue),
            pending_count=len(self._queue),
            processing_count=0,
            completed_count=self._completed,
            failed_count=0,
        )


# =============================================================================
# STANDALONE MANIFEST REGISTRY — In-memory dict
# =============================================================================


class StandaloneManifestRegistry(ManifestRegistry):
    """In-memory manifest registry for standalone operation."""

    def __init__(self) -> None:
        self._manifests: Dict[str, AgentManifest] = {}

    def register(self, manifest: AgentManifest) -> None:
        self._manifests[manifest.agent_id] = manifest

    def lookup(self, agent_id: str) -> Optional[AgentManifest]:
        return self._manifests.get(agent_id)

    def find_by_capability(self, capability: str) -> List[AgentManifest]:
        return [
            m for m in self._manifests.values()
            if capability in (m.capabilities or [])
        ]

    def list_all(self) -> List[AgentManifest]:
        return list(self._manifests.values())


# =============================================================================
# STANDALONE KERNEL — The System-Wide Fix
# =============================================================================


class StandaloneKernel(VibeKernel):
    """Lightweight VibeKernel for running cartridges without full VibeOS.

    Uses MahaKernel's existing ledger infrastructure (InMemoryLedger or
    SQLiteLedger). All governance events are recorded — no silent skips.

    This is NOT a toy stub. The ledger is real, the audit trail is real,
    the hash chain is real. The only thing missing is kernel-level scheduling
    and process isolation — which standalone cartridges don't need.
    """

    def __init__(
        self,
        ledger: Optional[VibeLedger] = None,
        sandbox_root: Optional[Path] = None,
    ) -> None:
        # Ledger: use provided or create from MahaKernel's infrastructure
        if ledger is not None:
            self._ledger = ledger
        else:
            from vibe_core.mahamantra.substrate.state.ledger import InMemoryLedger
            self._ledger = InMemoryLedger()

        self._agents: Dict[str, VibeAgent] = {}
        self._scheduler = StandaloneScheduler()
        self._manifest_registry = StandaloneManifestRegistry()
        self._sandbox_root = sandbox_root or Path("/tmp/vibe_os/standalone")
        self._status = KernelStatus.RUNNING

        logger.info(
            "StandaloneKernel initialized (ledger=%s, sandbox=%s)",
            type(self._ledger).__name__,
            self._sandbox_root,
        )

    # ── VibeKernel ABC implementation ─────────────────────────────────

    @property
    def agent_registry(self) -> Dict[str, VibeAgent]:
        return self._agents

    @property
    def scheduler(self) -> VibeScheduler:
        return self._scheduler

    @property
    def ledger(self) -> VibeLedger:
        return self._ledger

    @property
    def manifest_registry(self) -> ManifestRegistry:
        return self._manifest_registry

    @property
    def status(self) -> KernelStatus:
        return self._status

    @property
    def plugins(self) -> list:
        return []

    def register_agent(self, agent: VibeAgent) -> None:
        """Register an agent: inject kernel + system references.

        Sets agent.kernel = self (for ledger access).
        Sets agent.system to a SystemInterface that returns Path from
        get_sandbox_path() — cartridges do path / "subdir" which needs Path.
        """
        self._agents[agent.agent_id] = agent
        agent.kernel = self
        # Cartridges call self.system.get_sandbox_path() / "subdir"
        # VibeAgent.get_sandbox_path() returns str, but / operator needs Path.
        # Wrap with adapter that returns Path.
        agent.system = _StandaloneSystemInterface(agent.agent_id, self._sandbox_root)

        # Register manifest if agent provides one
        if hasattr(agent, "get_manifest"):
            try:
                manifest = agent.get_manifest()
                if manifest is not None:
                    self._manifest_registry.register(manifest)
            except Exception:
                pass  # Manifest generation is optional

        logger.info("Registered agent: %s", agent.agent_id)

    def get_status(self) -> dict:
        return {
            "status": self._status.value,
            "agents": len(self._agents),
            "ledger_events": (
                self._ledger.count_events()
                if hasattr(self._ledger, "count_events") else "N/A"
            ),
            "queue": self._scheduler.get_queue_status(),
        }

    def get_agent_manifest(self, agent_id: str) -> Optional[AgentManifest]:
        return self._manifest_registry.lookup(agent_id)

    def find_agents_by_capability(self, capability: str) -> List[VibeAgent]:
        manifests = self._manifest_registry.find_by_capability(capability)
        return [
            self._agents[m.agent_id]
            for m in manifests
            if m.agent_id in self._agents
        ]



# =============================================================================
# STANDALONE SYSTEM INTERFACE — Sandbox Path Provider
# =============================================================================


class _StandaloneSystemInterface:
    """Provides get_sandbox_path() → Path for standalone cartridges.

    Cartridges do: self.system.get_sandbox_path() / "governance" / "proposals"
    This requires Path, not str. Creates the sandbox dir on first access.
    """

    def __init__(self, agent_id: str, sandbox_root: Path) -> None:
        self._path = sandbox_root / agent_id

    def get_sandbox_path(self) -> Path:
        self._path.mkdir(parents=True, exist_ok=True)
        return self._path


# =============================================================================
# SINGLETON
# =============================================================================

_standalone_kernel: Optional[StandaloneKernel] = None


def get_standalone_kernel(
    ledger: Optional[VibeLedger] = None,
    sandbox_root: Optional[Path] = None,
) -> StandaloneKernel:
    """Get the singleton StandaloneKernel instance.

    First call creates the kernel. Subsequent calls return the same instance.
    Pass ledger/sandbox_root on first call to configure.
    """
    global _standalone_kernel
    if _standalone_kernel is None:
        _standalone_kernel = StandaloneKernel(
            ledger=ledger,
            sandbox_root=sandbox_root,
        )
    return _standalone_kernel


def reset_standalone_kernel() -> None:
    """Reset the singleton (for testing)."""
    global _standalone_kernel
    _standalone_kernel = None


__all__ = [
    "StandaloneKernel",
    "StandaloneScheduler",
    "StandaloneManifestRegistry",
    "get_standalone_kernel",
    "reset_standalone_kernel",
]
