"""
ResourceSupervisor Protocol - OPUS-209 Phase 2.3

Defines the interface for resource supervision implementations.
The kernel depends on this protocol, not the concrete ResourceManager.

This enables swappable resource management backends:
- Default: ResourceManager (psutil-based)
- Economy: EconomyResourceManager (credit-based billing)
- Mock: MockResourceManager (no enforcement)
"""

from dataclasses import dataclass
from multiprocessing import Process
from typing import Any, Dict, Protocol, runtime_checkable


@dataclass
class ResourceQuota:
    """Resource quota for an agent."""

    cpu_percent: int  # Max CPU% (0-100)
    memory_mb: int  # Max RAM in MB


@runtime_checkable
class ResourceSupervisorProtocol(Protocol):
    """
    Protocol for resource supervision implementations.

    The supervisor manages agent resource quotas:
    - Set quotas based on credit balance
    - Enforce CPU/RAM limits on processes
    - Monitor usage and detect violations
    """

    quotas: Dict[str, ResourceQuota]

    def set_quota(self, agent_id: str, credits: int) -> None:
        """
        Set resource quota for an agent based on credits.

        Args:
            agent_id: Agent identifier
            credits: Current credit balance
        """
        ...

    def enforce_quota(self, agent_id: str, process: Process) -> None:
        """
        Apply resource quota to a running process.

        Args:
            agent_id: Agent identifier
            process: multiprocessing.Process object
        """
        ...

    def get_usage(self, agent_id: str, process: Process) -> Dict[str, Any]:
        """
        Get current resource usage for an agent.

        Returns:
            Dict with cpu_percent, memory_mb, and quota info
        """
        ...

    def check_violations(self, process_manager: Any) -> list:
        """
        Check for agents exceeding their quotas.

        Returns:
            List of violation dicts
        """
        ...
