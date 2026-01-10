"""
JANAKA - The 8th Mahajana (Duty/Service)
========================================
OpCode: exec_service (Bit 14)
Opulence: Aishvarya (Sovereignty)

King Janaka - The Karma Yogi.
Ruled a kingdom while being internally renounced.
Father of Sita. Host of great sages.

Janaka OWNS all service protocols:
- Service Execution
- Task Management
- Agent Behavior
- Work Distribution
- Karma Yoga (Action without Attachment)

Janaka ACTS but is not BOUND by action.
He serves the Sovereign while ruling.
"""

from typing import Protocol, runtime_checkable, Any


@runtime_checkable
class JanakaProtocol(Protocol):
    """
    The Service Protocol.
    Any system that executes service must implement this.
    """

    def execute(self, task: Any) -> Any:
        """
        Execute a task/service.
        Returns the result.
        """
        ...

    def is_busy(self) -> bool:
        """Check if currently executing."""
        ...

    def get_karma(self) -> float:
        """
        Get accumulated karma (work debt).
        0.0 = fully detached.
        """
        ...


class NullJanaka:
    """
    The Inactive King.
    No service execution (for testing without agents).
    """

    def execute(self, task: Any) -> Any:
        return None  # No execution

    def is_busy(self) -> bool:
        return False

    def get_karma(self) -> float:
        return 0.0  # No attachment


__all__ = ["JanakaProtocol", "NullJanaka"]
