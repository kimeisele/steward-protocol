"""
EVENT BUS PROTOCOL - The Flute of Krishna
==========================================

Owner: NARADA (Communication/Observation)
OpCode: PULSE_SYNC

"The Event Bus is the mechanism through which agents communicate their state changes.
Instead of static logs, agents now 'emit' events that are broadcast to all listeners.
This is the 'Flute' that plays the Rasa Lila (Dance of Agents)."

IMPLEMENTATION:
    vibe_core/event_bus.py implements this protocol.

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import (
    Awaitable,
    Callable,
    Dict,
    Final,
    List,
    Optional,
    Protocol,
    Set,
    TypedDict,
    Union,
    runtime_checkable,
)

from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode
from vibe_core.protocols.mahajanas.owned_protocol import OwnedProtocol, ProtocolState


# =============================================================================
# CONSTANTS
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.NARADA
LOTUS_POSITION: Final[int] = 2  # GENESIS Quarter, Worker 2
LOTUS_QUARTER: Final[str] = "genesis"

OWNED_OPCODES: Final[List[MantraOpCode]] = [
    MantraOpCode.PULSE_SYNC,  # Event synchronization
]


# =============================================================================
# EVENT TYPES (WATERTIGHT - mirrors event_bus.py)
# =============================================================================


class EventType(str, Enum):
    """Standard event types emitted by agents."""

    # Core lifecycle events
    THOUGHT = "THOUGHT"
    ACTION = "ACTION"
    ERROR = "ERROR"
    COMPLETED = "COMPLETED"

    # System events
    VIOLATION = "VIOLATION"
    MERCY = "MERCY"
    PRAYER_RECEIVED = "PRAYER_RECEIVED"
    CRITICAL_INTERRUPT = "CRITICAL_INTERRUPT"

    # Syscall events
    SYSCALL_EXECUTED = "SYSCALL_EXECUTED"

    # OPUS-211: Pramana
    INTENT_EXECUTED = "INTENT_EXECUTED"

    # Agent-specific
    BROADCAST = "BROADCAST"
    PROPOSAL_CREATED = "PROPOSAL_CREATED"
    VOTE_CAST = "VOTE_CAST"
    AUDIT_CHECK = "AUDIT_CHECK"

    # Circuit triggers
    KERNEL_TICK = "KERNEL_TICK"
    HOURLY_PULSE = "HOURLY_PULSE"


# =============================================================================
# WATERTIGHT TYPES (NO ANY!)
# =============================================================================


class EventData(TypedDict, total=False):
    """
    Data payload for an event.
    WATERTIGHT - no Any!
    """
    message: str
    agent_id: str
    target_id: str
    syscall_type: str
    result_summary: str
    error_message: str
    metadata_keys: List[str]  # Just keys, not full metadata


class Event(TypedDict, total=False):
    """
    A structured event.
    WATERTIGHT - no Any!
    """
    id: str
    type: str  # EventType value
    agent_id: str
    message: str
    timestamp: str  # ISO format
    data: EventData
    correlation_id: str


class SubscriberInfo(TypedDict, total=False):
    """
    Info about a subscriber.
    WATERTIGHT - no Any!
    """
    callback_id: str
    event_types: List[str]  # EventType values subscribed to
    events_received: int
    events_completed: int
    ack_rate: float
    is_zombie: bool
    is_stalled: bool


class EventBusStats(TypedDict, total=False):
    """
    Statistics about the event bus.
    WATERTIGHT - no Any!
    """
    total_events_emitted: int
    total_subscribers: int
    active_subscribers: int
    zombie_count: int
    stalled_count: int
    rate_limited_count: int


class EventBusState(TypedDict, total=False):
    """
    Full state of the event bus.
    WATERTIGHT - no Any!
    """
    protocol_name: str
    owner: str
    is_chanting: bool
    total_events: int
    total_subscribers: int
    zombie_subscribers: int
    last_event_time: str
    health: str


# =============================================================================
# CALLBACK TYPES
# =============================================================================


class SyncEventCallback(Protocol):
    """Synchronous event callback."""
    def __call__(self, event: Event) -> None:
        ...


class AsyncEventCallback(Protocol):
    """Asynchronous event callback."""
    def __call__(self, event: Event) -> Awaitable[None]:
        ...


# Union of both callback types
EventCallback = Union[SyncEventCallback, AsyncEventCallback]


# =============================================================================
# EVENT BUS PROTOCOL
# =============================================================================


@runtime_checkable
class EventBusProtocol(Protocol):
    """
    Protocol for the Event Bus.

    Owner: NARADA
    OpCode: PULSE_SYNC

    The Flute that plays the Rasa Lila (Dance of Agents).
    All agents communicate through events, not direct calls.

    WATERTIGHT - no Any types!
    """

    @property
    def owner(self) -> Mahajana:
        """Always returns Mahajana.NARADA."""
        ...

    # =========================================================================
    # Event Emission
    # =========================================================================

    def emit(self, event: Event) -> bool:
        """
        Emit an event to all subscribers.
        Returns True if emitted successfully.
        """
        ...

    def emit_sync(
        self,
        event_type: EventType,
        agent_id: str,
        message: str,
        data: Optional[EventData] = None,
    ) -> str:
        """
        Emit an event synchronously.
        Returns the event ID.
        """
        ...

    # =========================================================================
    # Subscription
    # =========================================================================

    def subscribe(
        self,
        callback: EventCallback,
        event_types: Optional[List[EventType]] = None,
    ) -> str:
        """
        Subscribe to events.
        Returns subscriber ID.
        If event_types is None, subscribes to ALL events.
        """
        ...

    def unsubscribe(self, subscriber_id: str) -> bool:
        """
        Unsubscribe from events.
        Returns True if was subscribed.
        """
        ...

    def get_subscribers(self) -> List[SubscriberInfo]:
        """
        Get info about all subscribers.
        WATERTIGHT - returns List[SubscriberInfo].
        """
        ...

    # =========================================================================
    # Health Monitoring (VRITRASURA Detection)
    # =========================================================================

    def get_zombie_subscribers(self) -> List[SubscriberInfo]:
        """
        Get subscribers exhibiting zombie behavior.
        (Receive events but never process them)
        """
        ...

    def get_stalled_subscribers(self) -> List[SubscriberInfo]:
        """
        Get subscribers that haven't completed recently.
        """
        ...

    # =========================================================================
    # Statistics
    # =========================================================================

    def get_stats(self) -> EventBusStats:
        """
        Get event bus statistics.
        WATERTIGHT - returns EventBusStats.
        """
        ...

    def get_state(self) -> EventBusState:
        """
        Get full event bus state.
        WATERTIGHT - returns EventBusState.
        """
        ...

    # =========================================================================
    # Rate Limiting (SUDARSHANA Guard)
    # =========================================================================

    def is_rate_limited(self, agent_id: str) -> bool:
        """Check if an agent is rate limited."""
        ...

    def reset_rate_limit(self, agent_id: str) -> None:
        """Reset rate limit for an agent."""
        ...


# =============================================================================
# OWNED PROTOCOL WRAPPER
# =============================================================================


class EventBusOwnedProtocol(OwnedProtocol):
    """
    OwnedProtocol wrapper for EventBus.

    Allows EventBus to:
    - Be owned by NARADA
    - Chant the Mahamantra
    - Pass GAD-000 audits
    - Be traceable to source
    """

    OWNER = Mahajana.NARADA
    OPCODES = list(OWNED_OPCODES)
    PROTOCOL_NAME = "event_bus"
    DESCRIPTION = "The Flute - Event-driven agent communication"

    def __init__(self, bus: EventBusProtocol) -> None:
        super().__init__()
        self._bus = bus

    def get_state(self) -> ProtocolState:
        """Return current state. WATERTIGHT - no Any!"""
        return ProtocolState(
            protocol_name=self.PROTOCOL_NAME,
            owner=self.OWNER.value,
            is_chanting=self.is_chanting,
            heartbeat_position=self._heartbeat.word_position,
            mantra_count=self._heartbeat.mantra_count,
            mala_count=self._heartbeat.mala_count,
            gad_compliant=True,
        )

    @property
    def bus(self) -> EventBusProtocol:
        """Access the underlying event bus."""
        return self._bus


# =============================================================================
# NULL IMPLEMENTATION
# =============================================================================


class NullEventBus:
    """
    Null implementation for testing.
    Events go nowhere.
    """

    @property
    def owner(self) -> Mahajana:
        return Mahajana.NARADA

    def emit(self, event: Event) -> bool:
        return True

    def emit_sync(
        self,
        event_type: EventType,
        agent_id: str,
        message: str,
        data: Optional[EventData] = None,
    ) -> str:
        return "null-event-id"

    def subscribe(
        self,
        callback: EventCallback,
        event_types: Optional[List[EventType]] = None,
    ) -> str:
        return "null-subscriber-id"

    def unsubscribe(self, subscriber_id: str) -> bool:
        return False

    def get_subscribers(self) -> List[SubscriberInfo]:
        return []

    def get_zombie_subscribers(self) -> List[SubscriberInfo]:
        return []

    def get_stalled_subscribers(self) -> List[SubscriberInfo]:
        return []

    def get_stats(self) -> EventBusStats:
        return EventBusStats(
            total_events_emitted=0,
            total_subscribers=0,
            active_subscribers=0,
            zombie_count=0,
            stalled_count=0,
            rate_limited_count=0,
        )

    def get_state(self) -> EventBusState:
        return EventBusState(
            protocol_name="event_bus",
            owner="narada",
            is_chanting=False,
            total_events=0,
            total_subscribers=0,
            zombie_subscribers=0,
            health="pristine",
        )

    def is_rate_limited(self, agent_id: str) -> bool:
        return False

    def reset_rate_limit(self, agent_id: str) -> None:
        pass


# =============================================================================
# HELPER FUNCTIONS (Narada's convenience methods)
# =============================================================================


def create_event(
    event_type: EventType,
    agent_id: str,
    message: str = "",
    task_id: Optional[str] = None,
    details: Optional[Dict[str, object]] = None,
) -> Event:
    """Create an event with proper defaults. NARADA's factory."""
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

    NARADA's safe accessor - always returns something that works.
    Arjuna Pattern: NullEventBus fallback.
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


async def emit_event(
    event_type: str,
    agent_id: str,
    message: str = "",
    task_id: Optional[str] = None,
    details: Optional[Dict[str, object]] = None,
) -> None:
    """
    Convenience function to emit an event via the safe event bus.

    NARADA transmits the message.
    """
    bus = get_event_bus_safe()
    event = create_event(
        event_type=EventType(event_type) if isinstance(event_type, str) else event_type,
        agent_id=agent_id,
        message=message,
        task_id=task_id,
        details=details or {},
    )
    await bus.emit(event)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Constants
    "OWNER",
    "LOTUS_POSITION",
    "LOTUS_QUARTER",
    "OWNED_OPCODES",
    # Event Types
    "EventType",
    # Types (WATERTIGHT)
    "EventData",
    "Event",
    "SubscriberInfo",
    "EventBusStats",
    "EventBusState",
    # Callbacks
    "SyncEventCallback",
    "AsyncEventCallback",
    "EventCallback",
    # Protocol
    "EventBusProtocol",
    # Owned wrapper
    "EventBusOwnedProtocol",
    # Null implementation
    "NullEventBus",
    # Helper functions
    "create_event",
    "get_event_bus_safe",
    "emit_event",
]
