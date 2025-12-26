"""
OPUS-311 Sprint 2: Event Bus Protocol

The Flute that plays the Rasa Lila (Dance of Agents).

Protocol for inter-component messaging.
Replaces direct get_event_bus() singleton with DI.

Usage:
    # Via ServiceRegistry
    event_bus: EventBusProtocol = ServiceRegistry.get(EventBusProtocol)
    await event_bus.emit(event)

    # Fallback
    event_bus = event_bus or NullEventBus()
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Protocol, runtime_checkable
from uuid import uuid4


class EventType(str, Enum):
    """Standard event types emitted by agents."""

    # Core lifecycle events
    THOUGHT = "THOUGHT"  # Planning/reasoning
    ACTION = "ACTION"  # Executing task
    ERROR = "ERROR"  # Failure
    COMPLETED = "COMPLETED"  # Task completion

    # System events
    VIOLATION = "VIOLATION"  # Constitution breach
    MERCY = "MERCY"  # Supreme Court intervention
    PRAYER_RECEIVED = "PRAYER_RECEIVED"  # Request received
    CRITICAL_INTERRUPT = "CRITICAL_INTERRUPT"  # Emergency bypass

    # Syscall events
    SYSCALL_EXECUTED = "SYSCALL_EXECUTED"  # Syscall completed
    INTENT_EXECUTED = "INTENT_EXECUTED"  # OPUS-211: Pramana feedback

    # Agent-specific events
    BROADCAST = "BROADCAST"  # Content published
    PROPOSAL_CREATED = "PROPOSAL_CREATED"  # New proposal
    VOTE_CAST = "VOTE_CAST"  # Vote recorded
    AUDIT_CHECK = "AUDIT_CHECK"  # Invariant verified

    # Circuit trigger events
    KERNEL_TICK = "KERNEL_TICK"
    HOURLY_PULSE = "HOURLY_PULSE"

    # OPUS-311: Feedback events
    COMMAND_SUCCESS = "COMMAND_SUCCESS"  # Command executed successfully
    COMMAND_FAILURE = "COMMAND_FAILURE"  # Command failed


@dataclass
class Event:
    """Immutable event record."""

    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    event_type: str = ""
    agent_id: str = ""
    task_id: Optional[str] = None
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EventBusStatus:
    """Status of the event bus."""

    total_events: int = 0
    dropped_events: int = 0
    subscriber_count: int = 0
    history_size: int = 0
    type_counts: Dict[str, int] = field(default_factory=dict)


@runtime_checkable
class EventBusProtocol(Protocol):
    """
    OPUS-311: Protocol for event pub/sub.

    The Flute that plays the Rasa Lila (Dance of Agents).

    Features:
    - Async event emission
    - Type-specific and global subscribers
    - Event history
    - Rate limiting (implementation detail)
    """

    async def emit(self, event: Event) -> None:
        """
        Emit an event to all subscribers.

        Non-blocking and fault-tolerant.
        """
        ...

    def subscribe(
        self,
        callback: Callable[[Event], None],
        event_type: Optional[str] = None,
    ) -> str:
        """
        Subscribe to events.

        Args:
            callback: Function to call on event (async or sync)
            event_type: Optional filter (None = all events)

        Returns:
            Subscription ID
        """
        ...

    def unsubscribe(
        self,
        callback: Callable[[Event], None],
        event_type: Optional[str] = None,
    ) -> None:
        """Unsubscribe from events."""
        ...

    def get_history(
        self,
        limit: int = 100,
        event_type: Optional[str] = None,
    ) -> List[Event]:
        """Get event history (most recent first)."""
        ...

    def get_status(self) -> Dict[str, Any]:
        """Get event bus status."""
        ...


class NullEventBus:
    """
    Arjuna Pattern: No-op event bus.

    Events are silently dropped. No subscribers notified.
    Use when event bus is not available or not needed.
    """

    def __init__(self):
        self._event_count = 0

    async def emit(self, event: Event) -> None:
        """Silently drop event."""
        self._event_count += 1

    def subscribe(
        self,
        callback: Callable[[Event], None],
        event_type: Optional[str] = None,
    ) -> str:
        """No-op subscribe."""
        return "null-subscription"

    def unsubscribe(
        self,
        callback: Callable[[Event], None],
        event_type: Optional[str] = None,
    ) -> None:
        """No-op unsubscribe."""
        pass

    def get_history(
        self,
        limit: int = 100,
        event_type: Optional[str] = None,
    ) -> List[Event]:
        """Return empty history."""
        return []

    def get_status(self) -> Dict[str, Any]:
        """Return minimal status."""
        return {
            "total_events": self._event_count,
            "dropped_events": self._event_count,  # All dropped
            "subscriber_count": 0,
            "history_size": 0,
            "type_counts": {},
            "is_null": True,
        }


# Helper function for easy event creation
def create_event(
    event_type: EventType,
    agent_id: str,
    message: str = "",
    task_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
) -> Event:
    """Create an event with proper defaults."""
    return Event(
        event_type=event_type.value if isinstance(event_type, EventType) else event_type,
        agent_id=agent_id,
        message=message,
        task_id=task_id,
        details=details or {},
    )


def get_event_bus_safe() -> EventBusProtocol:
    """
    Get EventBus via ServiceRegistry with NullEventBus fallback.

    OPUS-311: Use this in new code for guaranteed non-None return.

    Usage:
        event_bus = get_event_bus_safe()
        await event_bus.emit(event)  # Always works, never None
    """
    try:
        from vibe_core.di import ServiceRegistry

        bus = ServiceRegistry.get(EventBusProtocol)
        if bus is not None:
            return bus
    except ImportError:
        pass

    # Arjuna Pattern: NullEventBus fallback
    return NullEventBus()
