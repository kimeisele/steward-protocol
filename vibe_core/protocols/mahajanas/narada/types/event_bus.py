"""
CANTO 10: THE FLUTE (Event Bus - The Song of Agents)

The Event Bus is the mechanism through which agents communicate their state changes.
Instead of static logs, agents now "emit" events that are broadcast to all listeners.

DEPRECATED: Phase 4 Migration to Mahamantra (NARADA)
=====================================================
EventBus is being migrated to mahamantra.<quarter>.narada  # FIXME: specify correct quarter.

MIGRATION PATH:
- Events → mahamantra.<quarter>.narada  # FIXME: specify correct quarter (broadcast/events)
- Signals → mahajanas/narada/events.py
- Access: `from vibe_core.mahamantra import mahamantra; mahamantra.<quarter>.narada  # FIXME: specify correct quarter`

CURRENT STATUS: Deprecated but functional
- New event systems should use narada patterns
- Existing EventBus continues to work

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

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0xec02c0c4"  # GenesisByte: parampara % 37 == 0

import asyncio
import json
import logging
import time as time_module
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Dict, List, Optional, Set, TypedDict, Union
from uuid import uuid4

from vibe_core.mahamantra.substrate.mahajana import Mahajana
from vibe_core.protocols.mahajanas.narada.events import (
    EventBusProtocol,
    EventBusState,
    EventBusStats,
    SubscriberInfo,
)

logger = logging.getLogger("EVENT_BUS")


# =============================================================================
# WATERTIGHT TYPEDDICTS (NO ANY!)
# =============================================================================


class MetricsEntry(TypedDict):
    """Internal metrics for a single callback. WATERTIGHT - no Any!"""

    events_sent: int
    events_completed: int
    last_complete_time: float
    total_duration: float


class ZombieInfo(TypedDict):
    """Info about a zombie subscriber. WATERTIGHT - no Any!"""

    callback_id: str
    events_sent: int
    events_completed: int
    ack_rate: float
    status: str


class StalledInfo(TypedDict):
    """Info about a stalled handler. WATERTIGHT - no Any!"""

    callback_id: str
    seconds_since_complete: float
    events_pending: int
    status: str


class RateLimitStats(TypedDict):
    """Rate limiting statistics. WATERTIGHT - no Any!"""

    allowed: int
    blocked: int
    active_buckets: int
    enabled: bool


class EventDetails(TypedDict, total=False):
    """Event details dictionary. WATERTIGHT - no Any!"""

    message: str
    target_id: str
    syscall_type: str
    result_summary: str
    error_message: str


class SubscriberCounts(TypedDict):
    """Subscriber counts by category. WATERTIGHT - no Any!"""

    global_count: int
    by_type: Dict[str, int]


class SubscriberHealth(TypedDict):
    """Subscriber health metrics. WATERTIGHT - no Any!"""

    total_tracked: int
    zombies_detected: int
    stalled_detected: int


class EventBusStatus(TypedDict):
    """Full event bus status. WATERTIGHT - no Any!"""

    total_events: int
    dropped_events: int
    type_counts: Dict[str, int]
    history_size: int
    subscribers: SubscriberCounts
    rate_limiting: RateLimitStats
    zombie_subscribers: List[ZombieInfo]
    stalled_handlers: List[StalledInfo]
    subscriber_health: SubscriberHealth


# =============================================================================
# VRITRASURA DETECTION: Subscriber Health Metrics
# =============================================================================


class SubscriberMetrics:
    """
    Track subscriber health to detect "Healthy Zombies".

    A zombie subscriber receives events but never processes them,
    potentially hoarding resources and causing backpressure.

    VRITRASURA TEST: This enables detection of stalled handlers.
    """

    def __init__(self):
        # {callback_id: MetricsEntry}
        self._metrics: Dict[str, MetricsEntry] = {}
        self._zombie_threshold_events = 10  # Events sent without completion
        self._zombie_threshold_rate = 0.5  # ACK rate below this = zombie
        self._stall_threshold_seconds = 30  # No completion in this time = stalled

    def record_send(self, callback_id: str):
        """Record that an event was sent to a subscriber."""
        if callback_id not in self._metrics:
            self._metrics[callback_id] = {
                "events_sent": 0,
                "events_completed": 0,
                "last_complete_time": time_module.time(),
                "total_duration": 0.0,
            }
        self._metrics[callback_id]["events_sent"] += 1

    def record_complete(self, callback_id: str, duration: float):
        """Record that a subscriber completed processing an event."""
        if callback_id in self._metrics:
            self._metrics[callback_id]["events_completed"] += 1
            self._metrics[callback_id]["last_complete_time"] = time_module.time()
            self._metrics[callback_id]["total_duration"] += duration

    def get_zombie_subscribers(self) -> List[ZombieInfo]:
        """
        Identify subscribers exhibiting zombie behavior.

        A zombie subscriber:
        - Has received > threshold events
        - Has ACK rate < threshold (events_completed / events_sent)
        """
        zombies = []
        for callback_id, metrics in self._metrics.items():
            sent = metrics["events_sent"]
            completed = metrics["events_completed"]
            ack_rate = completed / sent if sent > 0 else 1.0

            if sent > self._zombie_threshold_events and ack_rate < self._zombie_threshold_rate:
                zombies.append(
                    {
                        "callback_id": callback_id,
                        "events_sent": sent,
                        "events_completed": completed,
                        "ack_rate": ack_rate,
                        "status": "ZOMBIE",
                    }
                )
        return zombies

    def get_stalled_handlers(self) -> List[StalledInfo]:
        """
        Identify handlers that haven't completed anything recently.
        """
        stalled = []
        now = time_module.time()
        for callback_id, metrics in self._metrics.items():
            if metrics["events_sent"] > 0:
                time_since_complete = now - metrics["last_complete_time"]
                if time_since_complete > self._stall_threshold_seconds:
                    stalled.append(
                        {
                            "callback_id": callback_id,
                            "seconds_since_complete": time_since_complete,
                            "events_pending": metrics["events_sent"] - metrics["events_completed"],
                            "status": "STALLED",
                        }
                    )
        return stalled

    def get_all_metrics(self) -> Dict[str, MetricsEntry]:
        """Get all subscriber metrics. WATERTIGHT - no Any!"""
        return dict(self._metrics)


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

    # OPUS-211: Pramana (Feedback Loop)
    INTENT_EXECUTED = "INTENT_EXECUTED"  # Action completed with verification proof

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

        logger.info(f"🛡️ SUDARSHANA initialized (bucket={bucket_size}, rate={refill_rate}/s, enabled={enabled})")

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
            logger.warning(f"🛑 SUDARSHANA: Rate limit exceeded for '{agent_id}' (blocked={self._blocked_count})")
            raise PermissionError(f"SUDARSHANA: Rate limit exceeded for '{agent_id}'. Back off and try again.")

        # Deduct token and update
        self._buckets[agent_id] = [tokens - 1.0, now]
        self._allowed_count += 1
        return True

    def get_stats(self) -> RateLimitStats:
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
    details: EventDetails = field(default_factory=dict)

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


class EventBus(EventBusProtocol):
    """
    Lightweight async Event Bus for agent communication

    Owner: NARADA (Position 2)
    Implements: EventBusProtocol

    Features:
    - Non-blocking event emission
    - Multiple subscriber types (filters, handlers, aggregators)
    - Fault-tolerant (error in one doesn't affect others)
    - Zero persistence (in-memory, real-time stream only)
    - SUDARSHANA: Rate limiting per agent (KALIYA FIX)
    - VRITRASURA DETECTION: Zombie subscriber tracking
    """

    @property
    def owner(self) -> Mahajana:
        """Always returns Mahajana.NARADA (Position 2)."""
        return Mahajana.NARADA

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
        self._type_counts: Dict[str, int] = {}  # event_type -> count

        # SUDARSHANA: Active Traffic Control
        self._guard = SudarshanaGuard(
            bucket_size=rate_limit_bucket,
            refill_rate=rate_limit_rate,
            enabled=rate_limit_enabled,
        )

        # VRITRASURA DETECTION: Subscriber health tracking
        self._subscriber_metrics = SubscriberMetrics()
        self._callback_ids: Dict[Callable, str] = {}  # callback -> unique id

        logger.info(f"🎵 EventBus initialized (max_history={max_history}, zombie_detection=enabled)")

    async def emit(self, event: Event) -> bool:
        """
        Emit an event to all subscribers
        Non-blocking and fault-tolerant

        SUDARSHANA: Rate limits per agent. If limit exceeded,
        event is DROPPED (shadow ban) and not propagated.

        Returns:
            True if emitted successfully, False if rate limited
        """
        # =====================================================================
        # SUDARSHANA GATE: Check rate limit BEFORE processing
        # =====================================================================
        try:
            self._guard.check_traffic(event.agent_id)
        except PermissionError:
            # Shadow ban - drop event silently
            self._dropped_count += 1
            return False  # Event is NOT emitted (rate limited)

        # Store in history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)  # FIFO removal

        self._event_count += 1

        # Increment per-type count
        etype = event.event_type
        self._type_counts[etype] = self._type_counts.get(etype, 0) + 1

        # Emit to type-specific subscribers
        type_subs = self._subscribers.get(event.event_type, set())
        tasks = [self._safe_call_with_metrics(sub, event) for sub in type_subs]

        # Emit to global subscribers
        tasks.extend([self._safe_call_with_metrics(sub, event) for sub in self._global_subscribers])

        # Execute all in parallel
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        return True  # Successfully emitted

    async def _safe_call_with_metrics(self, callback: Callable, event: Event):
        """
        Safely call a subscriber with metrics tracking.
        Supports both async and sync callbacks.

        VRITRASURA DETECTION: Tracks send/complete for zombie detection.
        """
        # Get or create callback ID
        if callback not in self._callback_ids:
            self._callback_ids[callback] = f"sub_{len(self._callback_ids)}"
        callback_id = self._callback_ids[callback]

        # Record send
        self._subscriber_metrics.record_send(callback_id)

        start_time = time_module.time()
        try:
            if asyncio.iscoroutinefunction(callback):
                await callback(event)
            else:
                callback(event)
            # Record successful completion
            duration = time_module.time() - start_time
            self._subscriber_metrics.record_complete(callback_id, duration)
        except Exception as e:
            logger.warning(f"⚠️  Event subscriber error: {e}")
            # Don't record completion on error - contributes to zombie score

    def subscribe(
        self,
        callback: Callable,
        event_types: Optional[List[EventType]] = None,
    ) -> str:
        """
        Subscribe to events

        Args:
            callback: Function to call on event (async or sync)
            event_types: Optional filter (None = all events, empty list = no events)

        Returns:
            Subscription ID
        """
        if event_types:
            # Subscribe to multiple event types
            for event_type in event_types:
                event_type_str = event_type.value if isinstance(event_type, EventType) else event_type
                if event_type_str not in self._subscribers:
                    self._subscribers[event_type_str] = set()
                self._subscribers[event_type_str].add(callback)
            logger.debug(f"📡 Subscriber registered for {len(event_types)} event types")
        else:
            # Subscribe to all events (global)
            self._global_subscribers.add(callback)
            logger.debug("📡 Global subscriber registered")

        return str(uuid4())

    def unsubscribe(self, subscriber_id: str) -> bool:
        """
        Unsubscribe from events.

        Args:
            subscriber_id: Subscriber ID returned by subscribe()

        Returns:
            True if was subscribed, False otherwise

        Note: Current implementation doesn't track subscriber IDs,
        so this always returns False. Legacy callback-based unsubscribe
        is still supported internally but not exposed in protocol.
        """
        # TODO: Implement proper subscriber ID tracking
        # For now, return False as we don't track subscriber IDs
        logger.warning("⚠️  Unsubscribe by ID not yet implemented")
        return False

    def emit_sync(
        self,
        event_type: EventType,
        agent_id: str,
        message: str,
        data: Optional[EventDetails] = None,
    ) -> str:
        """
        Emit an event synchronously.

        Args:
            event_type: Type of event
            agent_id: ID of agent emitting event
            message: Event message
            data: Optional event data

        Returns:
            Event ID
        """
        event_id = str(uuid4())
        event = Event(
            event_id=event_id,
            event_type=event_type.value if isinstance(event_type, EventType) else event_type,
            agent_id=agent_id,
            message=message,
            timestamp=datetime.now().isoformat() + "Z",
            details=data or {},
        )

        # Emit asynchronously if there's a running event loop
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.emit(event))
        except RuntimeError:
            # No event loop running - emit synchronously by directly adding to history
            # This is a simplified sync path that bypasses the full async emit logic
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history.pop(0)
            self._event_count += 1
            self._type_counts[event.event_type] = self._type_counts.get(event.event_type, 0) + 1

        return event_id

    def get_subscribers(self) -> List[SubscriberInfo]:
        """
        Get info about all subscribers.

        Returns:
            List of subscriber info dicts
        """
        # TODO: Implement proper SubscriberInfo tracking
        # For now, return basic info
        return []

    def get_zombie_subscribers(self) -> List[ZombieInfo]:
        """
        Get subscribers exhibiting zombie behavior.

        Returns:
            List of zombie subscriber info dicts
        """
        return self._subscriber_metrics.get_zombie_subscribers()

    def get_stalled_subscribers(self) -> List[StalledInfo]:
        """
        Get subscribers that haven't completed recently.

        Returns:
            List of stalled subscriber info dicts
        """
        return self._subscriber_metrics.get_stalled_handlers()

    def get_stats(self) -> EventBusStats:
        """
        Get event bus statistics.

        Returns:
            EventBusStats dict
        """
        zombie_subs = self.get_zombie_subscribers()
        stalled_subs = self.get_stalled_subscribers()

        return {
            "total_events_emitted": self._event_count,
            "total_subscribers": len(self._global_subscribers) + sum(len(subs) for subs in self._subscribers.values()),
            "active_subscribers": len(self._global_subscribers) + sum(len(subs) for subs in self._subscribers.values()),
            "zombie_count": len(zombie_subs),
            "stalled_count": len(stalled_subs),
            "rate_limited_count": self._dropped_count,
        }

    def get_state(self) -> EventBusState:
        """
        Get full event bus state.

        Returns:
            EventBusState dict
        """
        zombie_subs = self.get_zombie_subscribers()

        return {
            "protocol_name": "event_bus",
            "owner": "narada",
            "is_chanting": False,  # TODO: Integrate with OwnedProtocol
            "total_events": self._event_count,
            "total_subscribers": len(self._global_subscribers) + sum(len(subs) for subs in self._subscribers.values()),
            "zombie_subscribers": len(zombie_subs),
            "last_event_time": self._event_history[-1].timestamp if self._event_history else "",
            "health": "healthy" if len(zombie_subs) == 0 else "degraded",
        }

    def is_rate_limited(self, agent_id: str) -> bool:
        """
        Check if an agent is rate limited.

        Args:
            agent_id: Agent ID to check

        Returns:
            True if rate limited
        """
        try:
            self._guard.check_traffic(agent_id)
            return False
        except PermissionError:
            return True

    def reset_rate_limit(self, agent_id: str) -> None:
        """
        Reset rate limit for an agent.

        Args:
            agent_id: Agent ID to reset
        """
        if hasattr(self._guard, "_buckets") and agent_id in self._guard._buckets:
            self._guard._buckets[agent_id] = self._guard._bucket_size

    def get_history(
        self,
        limit: int = 100,
        event_type: Optional[str] = None,
        quarter: Optional[str] = None,
        tick_min: Optional[int] = None,
        tick_max: Optional[int] = None,
    ) -> List[Event]:
        """Get event history with optional DIW-aware filtering.

        Args:
            limit: Max events to return (0 = all). Most recent first.
            event_type: Filter by EventType value (e.g. "ACTION").
            quarter: Filter by DIW quarter name ("genesis", "dharma", "karma", "moksha").
            tick_min: Only events at or after this tick (inclusive).
            tick_max: Only events at or before this tick (inclusive).

        Returns:
            Filtered event list, most recent last, capped at *limit*.
        """
        history: List[Event] = self._event_history

        if event_type:
            history = [e for e in history if e.event_type == event_type]

        if quarter is not None:
            history = [
                e for e in history
                if e.diw_context is not None and e.diw_context.get("quarter") == quarter
            ]

        if tick_min is not None:
            history = [
                e for e in history
                if e.diw_context is not None and e.diw_context.get("tick", -1) >= tick_min
            ]

        if tick_max is not None:
            history = [
                e for e in history
                if e.diw_context is not None and e.diw_context.get("tick", -1) <= tick_max
            ]

        return history[-limit:] if limit else history

    def get_status(self) -> EventBusStatus:
        """Get event bus status including rate limiting and zombie detection stats."""
        zombie_subscribers = self._subscriber_metrics.get_zombie_subscribers()
        stalled_handlers = self._subscriber_metrics.get_stalled_handlers()

        return {
            "total_events": self._event_count,
            "dropped_events": self._dropped_count,
            "type_counts": self._type_counts,
            "history_size": len(self._event_history),
            "subscribers": {
                "global": len(self._global_subscribers),
                "by_type": {k: len(v) for k, v in self._subscribers.items() if v},
            },
            "rate_limiting": self._guard.get_stats(),
            # VRITRASURA DETECTION: Zombie and stalled handler tracking
            "zombie_subscribers": zombie_subscribers,
            "stalled_handlers": stalled_handlers,
            "subscriber_health": {
                "total_tracked": len(self._subscriber_metrics._metrics),
                "zombies_detected": len(zombie_subscribers),
                "stalled_detected": len(stalled_handlers),
            },
        }

    def clear_history(self):
        """Clear event history (debugging/memory cleanup)"""
        self._event_history.clear()
        logger.info("🗑️  Event history cleared")


# =============================================================================
# SERVICEREGISTRY FACTORY (NAGA-OBSERVED!)
# =============================================================================


def get_event_bus() -> EventBus:
    """
    Get EventBus through ServiceRegistry (WIRED + NAGA-wrapped).

    ARCHITECTURE:
        EventBus → ServiceRegistry.register() → NagaProxy wrapping

    This ensures:
    - Singleton pattern via ServiceRegistry
    - NAGA observation (Narada sees all events - meta!)
    - NAGA profiling (Chitragupta tracks event latency)
    - NAGA isolation (Kaliya handles event errors)

    Returns:
        EventBus wrapped with NagaProxy (if NAGA blessing enabled)
    """
    from vibe_core.di import ServiceRegistry

    # Check if already registered
    existing = ServiceRegistry.get(EventBusProtocol)
    if existing is not None:
        return existing  # type: ignore

    # Create new instance
    instance = EventBus()

    # Register with ServiceRegistry (applies NagaProxy wrapping!)
    ServiceRegistry.register(EventBusProtocol, instance)
    logger.info("✅ EventBus registered via ServiceRegistry (NAGA-observed)")

    return ServiceRegistry.get(EventBusProtocol)  # type: ignore


async def emit_event(
    event_type: str,
    agent_id: str,
    message: str = "",
    task_id: Optional[str] = None,
    details: Optional[EventDetails] = None,
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
