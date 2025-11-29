"""
CANTO 10: THE FLUTE (Event Bus - The Song of Agents)

The Event Bus is the mechanism through which agents communicate their state changes.
Instead of static logs, agents now "emit" events that are broadcast to all listeners.

Event Types:
- THOUGHT: Agent is planning (Blue)
- ACTION: Agent acts (Green)
- ERROR: Agent fails (Red)
- VIOLATION: Constitution breach (Purple)
- MERCY: Supreme Court intervention (Gold)
- PRAYER_RECEIVED: Request processed (Cyan)
- CRITICAL_INTERRUPT: Emergency bypass triggered (Red + Flash)

This is the "Flute" that plays the Rasa Lila (Dance of Agents).
"""

import asyncio
import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set
from uuid import uuid4

logger = logging.getLogger("EVENT_BUS")


class EventType(str, Enum):
    """Standard event types emitted by agents"""

    # Core lifecycle events
    THOUGHT = "THOUGHT"  # Planning/reasoning
    ACTION = "ACTION"  # Executing task
    ERROR = "ERROR"  # Failure
    COMPLETED = "COMPLETED"  # Task completion

    # System events
    VIOLATION = "VIOLATION"  # Constitution breach
    MERCY = "MERCY"  # Supreme Court intervention
    PRAYER_RECEIVED = "PRAYER_RECEIVED"  # Request received
    CRITICAL_INTERRUPT = "CRITICAL_INTERRUPT"  # Emergency bypass (Gajendra)

    # Agent-specific events
    BROADCAST = "BROADCAST"  # Content published
    PROPOSAL_CREATED = "PROPOSAL_CREATED"  # New proposal
    VOTE_CAST = "VOTE_CAST"  # Vote recorded
    AUDIT_CHECK = "AUDIT_CHECK"  # Invariant verified


class EventColor(str, Enum):
    """ANSI color codes for terminal visualization"""

    BLUE = "34"  # THOUGHT
    GREEN = "32"  # ACTION
    RED = "31"  # ERROR / CRITICAL_INTERRUPT
    PURPLE = "35"  # VIOLATION
    GOLD = "33"  # MERCY
    CYAN = "36"  # PRAYER_RECEIVED
    YELLOW = "33"  # AUDIT_CHECK
    WHITE = "37"  # COMPLETED


EVENT_COLOR_MAP = {
    EventType.THOUGHT: EventColor.BLUE,
    EventType.ACTION: EventColor.GREEN,
    EventType.ERROR: EventColor.RED,
    EventType.VIOLATION: EventColor.PURPLE,
    EventType.MERCY: EventColor.GOLD,
    EventType.PRAYER_RECEIVED: EventColor.CYAN,
    EventType.CRITICAL_INTERRUPT: EventColor.RED,
    EventType.BROADCAST: EventColor.GREEN,
    EventType.COMPLETED: EventColor.WHITE,
    EventType.AUDIT_CHECK: EventColor.YELLOW,
}


@dataclass
class Event:
    """Immutable event record - the building block of the event stream"""

    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    event_type: str = ""  # EventType enum value
    agent_id: str = ""
    task_id: Optional[str] = None
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        """Serialize event to JSON"""
        return json.dumps(asdict(self), default=str, separators=(",", ":"))

    def get_color(self) -> str:
        """Get ANSI color code for this event"""
        try:
            event_type_enum = EventType(self.event_type)
            return EVENT_COLOR_MAP.get(event_type_enum, EventColor.WHITE).value
        except ValueError:
            return EventColor.WHITE.value


class EventBus:
    """
    Lightweight async Event Bus for agent communication

    Features:
    - Non-blocking event emission
    - Multiple subscriber types (filters, handlers, aggregators)
    - Fault-tolerant (error in one doesn't affect others)
    - Zero persistence (in-memory, real-time stream only)
    """

    def __init__(self, max_history: int = 1000):
        self._subscribers: Dict[str, Set[Callable]] = {}  # event_type -> callbacks
        self._global_subscribers: Set[Callable] = set()  # All events
        self._event_history: List[Event] = []
        self._max_history = max_history
        self._event_count = 0

        logger.info(f"🎵 EventBus initialized (max_history={max_history})")

    async def emit(self, event: Event):
        """
        Emit an event to all subscribers
        Non-blocking and fault-tolerant
        """
        # Store in history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)  # FIFO removal

        self._event_count += 1

        # Emit to type-specific subscribers
        type_subs = self._subscribers.get(event.event_type, set())
        tasks = [self._safe_call(sub, event) for sub in type_subs]

        # Emit to global subscribers
        tasks.extend([self._safe_call(sub, event) for sub in self._global_subscribers])

        # Execute all in parallel
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _safe_call(self, callback: Callable, event: Event):
        """
        Safely call a subscriber (catches exceptions)
        Supports both async and sync callbacks
        """
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(event)
            else:
                callback(event)
        except Exception as e:
            logger.warning(f"⚠️  Event subscriber error: {e}")

    def subscribe(self, callback: Callable, event_type: Optional[str] = None) -> str:
        """
        Subscribe to events

        Args:
            callback: Function to call on event (async or sync)
            event_type: Optional filter (None = all events)

        Returns:
            Subscription ID
        """
        if event_type:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = set()
            self._subscribers[event_type].add(callback)
            logger.debug(f"📡 Subscriber registered for {event_type}")
        else:
            self._global_subscribers.add(callback)
            logger.debug(f"📡 Global subscriber registered")

        return str(uuid4())

    def unsubscribe(self, callback: Callable, event_type: Optional[str] = None):
        """Unsubscribe from events"""
        if event_type and event_type in self._subscribers:
            self._subscribers[event_type].discard(callback)
        else:
            self._global_subscribers.discard(callback)

    def get_history(
        self, limit: int = 100, event_type: Optional[str] = None
    ) -> List[Event]:
        """Get event history (most recent first)"""
        if event_type:
            history = [e for e in self._event_history if e.event_type == event_type]
        else:
            history = self._event_history

        return history[-limit:] if limit else history

    def get_status(self) -> Dict[str, Any]:
        """Get event bus status"""
        return {
            "total_events": self._event_count,
            "history_size": len(self._event_history),
            "subscribers": {
                "global": len(self._global_subscribers),
                "by_type": {k: len(v) for k, v in self._subscribers.items() if v},
            },
        }

    def clear_history(self):
        """Clear event history (debugging/memory cleanup)"""
        self._event_history.clear()
        logger.info("🗑️  Event history cleared")


# Module-level singleton
_event_bus_instance: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get the global event bus singleton"""
    global _event_bus_instance
    if _event_bus_instance is None:
        _event_bus_instance = EventBus()
    return _event_bus_instance


async def emit_event(
    event_type: str,
    agent_id: str,
    message: str = "",
    task_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
):
    """
    Convenience function to emit an event from anywhere in the codebase

    Usage:
        await emit_event(EventType.ACTION, "herald", "Composing tweet", task_id="t123")
    """
    bus = get_event_bus()
    event = Event(
        event_type=event_type,
        agent_id=agent_id,
        task_id=task_id,
        message=message,
        details=details or {},
    )
    await bus.emit(event)
