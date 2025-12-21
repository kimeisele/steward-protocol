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

    # Syscall events (OPUS-031 Layer 2)
    SYSCALL_EXECUTED = "SYSCALL_EXECUTED"  # Syscall completed (for experience replay)

    # Agent-specific events
    BROADCAST = "BROADCAST"  # Content published
    PROPOSAL_CREATED = "PROPOSAL_CREATED"  # New proposal
    VOTE_CAST = "VOTE_CAST"  # Vote recorded
    AUDIT_CHECK = "AUDIT_CHECK"  # Invariant verified

    # Circuit trigger events (NOT emitted from kernel - see OPUS-073)
    KERNEL_TICK = "KERNEL_TICK"  # For circuits, emitted by plugins if needed
    HOURLY_PULSE = "HOURLY_PULSE"  # For MANAS, emitted by heartbeat.py


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
    EventType.SYSCALL_EXECUTED: EventColor.CYAN,  # OPUS-031: Experience Replay
}


# =============================================================================
# SUDARSHANA CHAKRA: Active Traffic Control (KALIYA FIX)
# =============================================================================

class SudarshanaGuard:
    """
    Active Traffic Control for the Event Bus.

    "The discus of Vishnu that cuts through all evil."

    Implements Token Bucket rate limiting per agent:
    - Each agent gets a bucket of tokens (default: 100)
    - Tokens refill at rate (default: 50/sec)
    - If bucket is empty, agent is BLOCKED
    - VIP agents (kernel, system) bypass all limits
    """

    # VIP agents that bypass rate limiting
    VIP_AGENTS = {"kernel", "system", "watchman", "narasimha", "test"}

    def __init__(
        self,
        bucket_size: float = 100.0,
        refill_rate: float = 50.0,
        enabled: bool = True,
    ):
        """
        Initialize the Sudarshana Guard.

        Args:
            bucket_size: Maximum tokens per agent (burst capacity)
            refill_rate: Tokens refilled per second
            enabled: If False, all traffic is allowed (for testing)
        """
        self._bucket_size = bucket_size
        self._refill_rate = refill_rate
        self._enabled = enabled

        # {agent_id: (tokens, last_update_time)}
        self._buckets: Dict[str, List[float]] = {}

        # Stats
        self._blocked_count = 0
        self._allowed_count = 0

        logger.info(
            f"🛡️ SUDARSHANA initialized (bucket={bucket_size}, rate={refill_rate}/s, enabled={enabled})"
        )

    def check_traffic(self, agent_id: str) -> bool:
        """
        Check if an agent is allowed to emit an event.

        Args:
            agent_id: The agent attempting to emit

        Returns:
            True if allowed

        Raises:
            PermissionError: If rate limit exceeded
        """
        if not self._enabled:
            return True

        # VIP bypass
        if agent_id in self.VIP_AGENTS:
            self._allowed_count += 1
            return True

        import time
        now = time.time()

        # Get or create bucket
        if agent_id not in self._buckets:
            self._buckets[agent_id] = [self._bucket_size, now]

        tokens, last_update = self._buckets[agent_id]

        # Refill tokens based on elapsed time
        elapsed = now - last_update
        tokens = min(self._bucket_size, tokens + elapsed * self._refill_rate)

        # Check if we have tokens
        if tokens < 1.0:
            # Update timestamp but don't deduct
            self._buckets[agent_id] = [tokens, now]
            self._blocked_count += 1
            logger.warning(
                f"🛑 SUDARSHANA: Rate limit exceeded for '{agent_id}' "
                f"(blocked={self._blocked_count})"
            )
            raise PermissionError(
                f"SUDARSHANA: Rate limit exceeded for '{agent_id}'. "
                f"Back off and try again."
            )

        # Deduct token and update
        self._buckets[agent_id] = [tokens - 1.0, now]
        self._allowed_count += 1
        return True

    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiting statistics."""
        return {
            "allowed": self._allowed_count,
            "blocked": self._blocked_count,
            "active_buckets": len(self._buckets),
            "enabled": self._enabled,
        }

    def reset_bucket(self, agent_id: str):
        """Reset an agent's bucket (after timeout/mercy)."""
        if agent_id in self._buckets:
            del self._buckets[agent_id]


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
    - SUDARSHANA: Rate limiting per agent (KALIYA FIX)
    """

    def __init__(
        self,
        max_history: int = 1000,
        rate_limit_enabled: bool = True,
        rate_limit_bucket: float = 100.0,
        rate_limit_rate: float = 50.0,
    ):
        self._subscribers: Dict[str, Set[Callable]] = {}  # event_type -> callbacks
        self._global_subscribers: Set[Callable] = set()  # All events
        self._event_history: List[Event] = []
        self._max_history = max_history
        self._event_count = 0
        self._dropped_count = 0  # Events dropped due to rate limiting

        # SUDARSHANA: Active Traffic Control
        self._guard = SudarshanaGuard(
            bucket_size=rate_limit_bucket,
            refill_rate=rate_limit_rate,
            enabled=rate_limit_enabled,
        )

        logger.info(f"🎵 EventBus initialized (max_history={max_history})")

    async def emit(self, event: Event):
        """
        Emit an event to all subscribers
        Non-blocking and fault-tolerant

        SUDARSHANA: Rate limits per agent. If limit exceeded,
        event is DROPPED (shadow ban) and not propagated.
        """
        # =====================================================================
        # SUDARSHANA GATE: Check rate limit BEFORE processing
        # =====================================================================
        try:
            self._guard.check_traffic(event.agent_id)
        except PermissionError:
            # Shadow ban - drop event silently
            self._dropped_count += 1
            return  # Event is NOT emitted

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
            logger.debug("📡 Global subscriber registered")

        return str(uuid4())

    def unsubscribe(self, callback: Callable, event_type: Optional[str] = None):
        """Unsubscribe from events"""
        if event_type and event_type in self._subscribers:
            self._subscribers[event_type].discard(callback)
        else:
            self._global_subscribers.discard(callback)

    def get_history(self, limit: int = 100, event_type: Optional[str] = None) -> List[Event]:
        """Get event history (most recent first)"""
        if event_type:
            history = [e for e in self._event_history if e.event_type == event_type]
        else:
            history = self._event_history

        return history[-limit:] if limit else history

    def get_status(self) -> Dict[str, Any]:
        """Get event bus status including rate limiting stats."""
        return {
            "total_events": self._event_count,
            "dropped_events": self._dropped_count,
            "history_size": len(self._event_history),
            "subscribers": {
                "global": len(self._global_subscribers),
                "by_type": {k: len(v) for k, v in self._subscribers.items() if v},
            },
            "rate_limiting": self._guard.get_stats(),
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
