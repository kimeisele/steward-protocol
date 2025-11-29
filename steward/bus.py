"""
STEWARD Signal Bus - Async Communication Infrastructure for Agents.

The Signal Bus enables decoupled communication between agents:
- Agents don't call functions; they emit signals
- Listeners register for specific signal types
- Signals are propagated asynchronously (future: real async with asyncio)
- Enables multi-agent coordination and federation

Future roadmap:
- Support for Agent #2 (ARCHIVIST), Agent #3 (AUDITOR), Agent #4 (GUARDIAN)
- Redis-based distributed bus for multi-process communication
- Event persistence and replay
- Signal authentication and verification
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("STEWARD_BUS")


class SignalType(Enum):
    """Standard signal types for agent communication."""

    # Content signals
    CONTENT_GENERATED = "content_generated"
    CONTENT_PUBLISHED = "content_published"
    CONTENT_REJECTED = "content_rejected"

    # System signals
    AGENT_STARTUP = "agent_startup"
    AGENT_SHUTDOWN = "agent_shutdown"
    AGENT_ERROR = "agent_error"
    AGENT_STATUS_UPDATE = "agent_status_update"

    # Recruitment signals
    RECRUITMENT_NEEDED = "recruitment_needed"
    SKILL_AVAILABLE = "skill_available"

    # Governance signals
    POLICY_VIOLATION = "policy_violation"
    POLICY_UPDATE = "policy_update"

    # Audit signals
    AUDIT_REQUEST = "audit_request"
    AUDIT_COMPLETE = "audit_complete"

    # Custom signal (for user-defined types)
    CUSTOM = "custom"


@dataclass
class Signal:
    """
    A signal emitted by an agent.

    Attributes:
        signal_type: Type of signal (from SignalType enum)
        source_agent: Agent ID that emitted the signal
        timestamp: When the signal was emitted (ISO 8601)
        payload: Signal-specific data (dict)
        priority: Signal priority (0-10, higher = more urgent)
        requires_ack: Whether signal requires acknowledgment
        correlation_id: Optional ID linking related signals
    """

    signal_type: SignalType
    source_agent: str
    payload: Dict[str, Any]
    timestamp: Optional[str] = None
    priority: int = 5
    requires_ack: bool = False
    correlation_id: Optional[str] = None

    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Serialize signal to dict."""
        return {
            "signal_type": self.signal_type.value,
            "source_agent": self.source_agent,
            "timestamp": self.timestamp,
            "payload": self.payload,
            "priority": self.priority,
            "requires_ack": self.requires_ack,
            "correlation_id": self.correlation_id,
        }


class SignalListener:
    """
    A listener for signals of a specific type.

    Listeners are called when signals matching their criteria are emitted.
    """

    def __init__(
        self,
        listener_id: str,
        signal_type: SignalType,
        callback: Callable[[Signal], None],
    ):
        """
        Initialize a signal listener.

        Args:
            listener_id: Unique identifier for this listener
            signal_type: Type of signals to listen for
            callback: Function to call when signal is emitted
        """
        self.listener_id = listener_id
        self.signal_type = signal_type
        self.callback = callback
        self.signals_received = 0

    def handle(self, signal: Signal) -> bool:
        """
        Handle a signal (call the callback).

        Args:
            signal: Signal to handle

        Returns:
            True if handled successfully
        """
        try:
            self.callback(signal)
            self.signals_received += 1
            return True
        except Exception as e:
            logger.error(f"❌ Listener {self.listener_id} error: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get listener statistics."""
        return {
            "listener_id": self.listener_id,
            "signal_type": self.signal_type.value,
            "signals_received": self.signals_received,
        }


class SignalBus:
    """
    Central signal bus for agent communication.

    Implements a publish-subscribe pattern for inter-agent communication.
    All signal emissions and subscriptions are logged for auditing.
    """

    def __init__(self, bus_id: str = "steward.bus"):
        """
        Initialize the signal bus.

        Args:
            bus_id: Identifier for this bus instance
        """
        self.bus_id = bus_id
        self.listeners: Dict[SignalType, List[SignalListener]] = {}
        self.signal_history: List[Signal] = []
        self.max_history = 1000  # Keep last 1000 signals in memory
        self.total_signals_emitted = 0

        logger.info(f"📡 SignalBus initialized: {bus_id}")

    def subscribe(
        self,
        listener_id: str,
        signal_type: SignalType,
        callback: Callable[[Signal], None],
    ) -> SignalListener:
        """
        Subscribe a listener to signals of a specific type.

        Args:
            listener_id: Unique identifier for the listener
            signal_type: Type of signals to listen for
            callback: Callback function to invoke on signal

        Returns:
            SignalListener instance
        """
        listener = SignalListener(listener_id, signal_type, callback)

        if signal_type not in self.listeners:
            self.listeners[signal_type] = []

        self.listeners[signal_type].append(listener)

        logger.info(f"📡 Listener registered: {listener_id} -> {signal_type.value}")

        return listener

    def unsubscribe(
        self,
        listener_id: str,
        signal_type: Optional[SignalType] = None,
    ) -> bool:
        """
        Unsubscribe a listener.

        Args:
            listener_id: ID of listener to remove
            signal_type: Optional specific signal type to unsubscribe from

        Returns:
            True if successfully unsubscribed
        """
        if signal_type:
            if signal_type in self.listeners:
                before = len(self.listeners[signal_type])
                self.listeners[signal_type] = [
                    l
                    for l in self.listeners[signal_type]
                    if l.listener_id != listener_id
                ]
                after = len(self.listeners[signal_type])
                if before > after:
                    logger.info(
                        f"📡 Listener unregistered: {listener_id} from {signal_type.value}"
                    )
                    return True
        else:
            # Unsubscribe from all signal types
            found = False
            for st in list(self.listeners.keys()):
                before = len(self.listeners[st])
                self.listeners[st] = [
                    l for l in self.listeners[st] if l.listener_id != listener_id
                ]
                after = len(self.listeners[st])
                if before > after:
                    found = True
            if found:
                logger.info(f"📡 Listener unregistered from all signals: {listener_id}")
                return True

        return False

    def emit(self, signal: Signal) -> int:
        """
        Emit a signal and notify all registered listeners.

        Args:
            signal: Signal to emit

        Returns:
            Number of listeners successfully notified
        """
        # Record in history
        self.signal_history.append(signal)
        if len(self.signal_history) > self.max_history:
            self.signal_history = self.signal_history[-self.max_history :]

        self.total_signals_emitted += 1

        logger.debug(
            f"📡 Signal emitted: {signal.signal_type.value} from {signal.source_agent}"
        )

        # Notify listeners
        handled_count = 0
        if signal.signal_type in self.listeners:
            for listener in self.listeners[signal.signal_type]:
                if listener.handle(signal):
                    handled_count += 1

        logger.info(
            f"📡 Signal distributed: {signal.signal_type.value} to {handled_count} listener(s)"
        )

        return handled_count

    def get_listeners_for_type(
        self,
        signal_type: SignalType,
    ) -> List[SignalListener]:
        """
        Get all listeners for a specific signal type.

        Args:
            signal_type: Type of signal

        Returns:
            List of registered listeners
        """
        return self.listeners.get(signal_type, [])

    def get_signal_history(
        self,
        signal_type: Optional[SignalType] = None,
        limit: int = 100,
    ) -> List[Signal]:
        """
        Get recent signal history.

        Args:
            signal_type: Optional filter by signal type
            limit: Maximum number of signals to return

        Returns:
            List of signals (most recent first)
        """
        signals = (
            self.signal_history[-limit:]
            if len(self.signal_history) > limit
            else self.signal_history
        )

        if signal_type:
            signals = [s for s in signals if s.signal_type == signal_type]

        return list(reversed(signals))  # Most recent first

    def get_bus_stats(self) -> Dict[str, Any]:
        """
        Get signal bus statistics.

        Returns:
            Dict with bus statistics
        """
        total_listeners = sum(len(listeners) for listeners in self.listeners.values())

        return {
            "bus_id": self.bus_id,
            "total_signals_emitted": self.total_signals_emitted,
            "total_listeners": total_listeners,
            "listeners_by_type": {
                st.value: len(listeners) for st, listeners in self.listeners.items()
            },
            "history_size": len(self.signal_history),
        }

    def get_listener_stats(self) -> Dict[str, Any]:
        """
        Get statistics for all registered listeners.

        Returns:
            Dict with stats for each listener
        """
        stats = {}
        for signal_type, listeners in self.listeners.items():
            for listener in listeners:
                stats[listener.listener_id] = listener.get_stats()

        return stats


# Global singleton instance
_bus: Optional[SignalBus] = None


def get_bus(bus_id: str = "steward.bus") -> SignalBus:
    """
    Get the global signal bus instance (singleton pattern).

    Args:
        bus_id: Bus identifier (only used on first call)

    Returns:
        SignalBus instance
    """
    global _bus
    if _bus is None:
        _bus = SignalBus(bus_id)
    return _bus


def reset_bus() -> None:
    """Reset the global bus (for testing)."""
    global _bus
    _bus = None
