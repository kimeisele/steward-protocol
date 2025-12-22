"""
ProcessSupervisor Protocol - OPUS-209 Phase 2.2

Defines the interface for process supervision implementations.
The kernel depends on this protocol, not the concrete ProcessManager.

This enables swappable execution backends:
- Default: ProcessManager (multiprocessing)
- Secure: DockerProcessManager (containerized)
- Test: MockProcessManager (no-op logging)
"""

from typing import TYPE_CHECKING, Any, Dict, List, Protocol, Tuple, runtime_checkable

if TYPE_CHECKING:
    from vibe_core.process_manager import AgentProcessInfo


@runtime_checkable
class ProcessSupervisorProtocol(Protocol):
    """
    Protocol for process supervision implementations.

    The supervisor manages agent process lifecycle:
    - Spawn isolated processes for agents
    - Route tasks between kernel and agents
    - Monitor health and restart crashed agents
    - Clean shutdown of all processes
    """

    # Dict mapping agent_id -> AgentProcessInfo
    processes: Dict[str, "AgentProcessInfo"]

    def spawn_agent(
        self,
        agent_id: str,
        cartridge_path: str,
        cartridge_class_name: str,
        config: Any = None,
    ) -> None:
        """
        Spawn a new agent process.

        Args:
            agent_id: Unique identifier for the agent
            cartridge_path: Path to the cartridge module
            cartridge_class_name: Name of the agent class
            config: Optional configuration for the agent
        """
        ...

    def send_task(self, agent_id: str, task: Any) -> bool:
        """
        Send a task to an agent process.

        Args:
            agent_id: Target agent
            task: Task to execute

        Returns:
            True if task was sent and acknowledged
        """
        ...

    def get_pending_messages(self) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Get all pending messages from agent processes.

        Returns:
            List of (agent_id, message) tuples
        """
        ...

    def check_health(self) -> None:
        """
        Check health of all agent processes.

        Restarts crashed agents up to MAX_RESTARTS limit.
        """
        ...

    def shutdown(self) -> None:
        """
        Shutdown all agent processes gracefully.
        """
        ...
