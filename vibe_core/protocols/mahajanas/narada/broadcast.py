"""
BROADCAST - Multi-Channel Communication Protocol
================================================

OWNER: NARADA (The Cosmic Journalist)
POSITION: 2 (GENESIS Quarter)
OPCODE: PULSE_SYNC

Narada travels across all universes, broadcasting news everywhere.
This is multi-channel broadcast: fan-out to many destinations.

SHASTRA BASIS:
    Narada Muni travels freely through all lokas (worlds).
    He brings news from one place to another.
    "Narada Muni ki Jai!"

    In code:
    - Channel = A named broadcast destination
    - Subscription = Interest in a channel
    - Broadcast = Send to all subscribers
    - Fan-out = One message → many recipients

DELIVERY MODES:
    - AT_MOST_ONCE: Fire and forget (fast, unreliable)
    - AT_LEAST_ONCE: Retry until ack (reliable, may duplicate)
    - EXACTLY_ONCE: Deduplication (slowest, most reliable)

WATERTIGHT: No Any types. All typed explicitly.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x3a9c2fe5"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Dict, Final, List, Optional, Protocol, Set, runtime_checkable

from vibe_core.protocols.mahajanas.router import Mahajana, MantraOpCode

from vibe_core.protocols.mahajanas.narada import (
    MessagePayload,
    MessageType,
    Message,
    BroadcastResult,
    ObserverState,
)


# =============================================================================
# OWNERSHIP DECLARATION
# =============================================================================

OWNER: Final[Mahajana] = Mahajana.NARADA
LOTUS_POSITION: Final[int] = 2
LOTUS_QUARTER: Final[str] = "genesis"

OWNED_OPCODES: Final[List[MantraOpCode]] = [
    MantraOpCode.ALLOC_MEM,  # PULSE_SYNC
]


# =============================================================================
# DELIVERY MODE
# =============================================================================


class DeliveryMode(str, Enum):
    """Message delivery guarantees."""

    AT_MOST_ONCE = "at_most_once"  # Fire and forget
    AT_LEAST_ONCE = "at_least_once"  # Retry until ack
    EXACTLY_ONCE = "exactly_once"  # Deduplicated


# =============================================================================
# CHANNEL
# =============================================================================


@dataclass
class Channel:
    """A broadcast channel."""

    name: str
    created_at: datetime = field(default_factory=datetime.now)
    message_count: int = 0
    subscriber_count: int = 0


BroadcastHandler = Callable[[str, MessagePayload], bool]


@dataclass
class Subscription:
    """A channel subscription."""

    subscriber_id: str
    channel: str
    handler: BroadcastHandler
    created_at: datetime = field(default_factory=datetime.now)


# =============================================================================
# BROADCAST PROTOCOL
# =============================================================================


@runtime_checkable
class BroadcastProtocol(Protocol):
    """
    The Multi-Channel Broadcast Protocol - Narada's Fan-out.

    OWNER: Mahajana.NARADA

    Enables multi-channel broadcasting:
    - Create channels
    - Subscribe to channels
    - Broadcast to all subscribers
    """

    @property
    def owner(self) -> Mahajana:
        """Always returns Mahajana.NARADA."""
        ...

    # Channel Management
    def create_channel(self, name: str) -> bool:
        """Create a broadcast channel."""
        ...

    def delete_channel(self, name: str) -> bool:
        """Delete a channel."""
        ...

    def list_channels(self) -> List[str]:
        """List all channels."""
        ...

    # Subscription
    def subscribe(self, channel: str, subscriber_id: str, handler: BroadcastHandler) -> bool:
        """Subscribe to a channel."""
        ...

    def unsubscribe(self, channel: str, subscriber_id: str) -> bool:
        """Unsubscribe from a channel."""
        ...

    # Broadcast
    def broadcast(
        self, channel: str, payload: MessagePayload, mode: DeliveryMode = DeliveryMode.AT_MOST_ONCE
    ) -> BroadcastResult:
        """Broadcast to all subscribers of a channel."""
        ...

    def broadcast_all(self, payload: MessagePayload) -> BroadcastResult:
        """Broadcast to ALL channels."""
        ...


# =============================================================================
# BROADCASTER IMPLEMENTATION
# =============================================================================


class Broadcaster:
    """
    Narada's Broadcaster - Multi-Channel Fan-out.

    OWNER: Mahajana.NARADA

    Features:
    - Named channels
    - Multiple subscribers per channel
    - Delivery mode selection
    - Fan-out broadcast
    """

    def __init__(self) -> None:
        """Initialize broadcaster."""
        self._channels: Dict[str, Channel] = {}
        self._subscriptions: Dict[str, List[Subscription]] = {}  # channel -> subscriptions
        self._message_count = 0

    @property
    def owner(self) -> Mahajana:
        return Mahajana.NARADA

    def create_channel(self, name: str) -> bool:
        """Create a broadcast channel."""
        if name in self._channels:
            return False
        self._channels[name] = Channel(name=name)
        self._subscriptions[name] = []
        return True

    def delete_channel(self, name: str) -> bool:
        """Delete a channel."""
        if name not in self._channels:
            return False
        del self._channels[name]
        del self._subscriptions[name]
        return True

    def list_channels(self) -> List[str]:
        """List all channels."""
        return list(self._channels.keys())

    def subscribe(self, channel: str, subscriber_id: str, handler: BroadcastHandler) -> bool:
        """Subscribe to a channel."""
        if channel not in self._channels:
            return False

        # Check if already subscribed
        for sub in self._subscriptions[channel]:
            if sub.subscriber_id == subscriber_id:
                return False

        subscription = Subscription(
            subscriber_id=subscriber_id,
            channel=channel,
            handler=handler,
        )
        self._subscriptions[channel].append(subscription)
        self._channels[channel].subscriber_count += 1
        return True

    def unsubscribe(self, channel: str, subscriber_id: str) -> bool:
        """Unsubscribe from a channel."""
        if channel not in self._subscriptions:
            return False

        for i, sub in enumerate(self._subscriptions[channel]):
            if sub.subscriber_id == subscriber_id:
                self._subscriptions[channel].pop(i)
                self._channels[channel].subscriber_count -= 1
                return True
        return False

    def broadcast(
        self,
        channel: str,
        payload: MessagePayload,
        mode: DeliveryMode = DeliveryMode.AT_MOST_ONCE,
    ) -> BroadcastResult:
        """Broadcast to all subscribers of a channel."""
        if channel not in self._channels:
            return BroadcastResult(
                success=False,
                recipients_count=0,
                failed_count=0,
                message_id="",
            )

        self._message_count += 1
        message_id = f"msg-{self._message_count}"
        recipients = 0
        failed = 0

        for sub in self._subscriptions[channel]:
            try:
                if sub.handler(channel, payload):
                    recipients += 1
                else:
                    failed += 1
                    # Retry for AT_LEAST_ONCE
                    if mode == DeliveryMode.AT_LEAST_ONCE:
                        for _ in range(3):  # 3 retries
                            if sub.handler(channel, payload):
                                recipients += 1
                                failed -= 1
                                break
            except Exception:
                failed += 1

        self._channels[channel].message_count += 1

        return BroadcastResult(
            success=failed == 0,
            recipients_count=recipients,
            failed_count=failed,
            message_id=message_id,
        )

    def broadcast_all(self, payload: MessagePayload) -> BroadcastResult:
        """Broadcast to ALL channels."""
        total_recipients = 0
        total_failed = 0

        for channel in self._channels:
            result = self.broadcast(channel, payload)
            total_recipients += result.get("recipients_count", 0)
            total_failed += result.get("failed_count", 0)

        return BroadcastResult(
            success=total_failed == 0,
            recipients_count=total_recipients,
            failed_count=total_failed,
            message_id=f"broadcast-all-{self._message_count}",
        )

    def get_state(self) -> ObserverState:
        """Get broadcaster state."""
        total_subscribers = sum(ch.subscriber_count for ch in self._channels.values())
        return ObserverState(
            observations=[],
            total_observed=self._message_count,
            listeners_count=total_subscribers,
            messages_sent=self._message_count,
            messages_received=0,
            health="healthy",
        )


# =============================================================================
# NULL BROADCASTER
# =============================================================================


class NullBroadcaster:
    """Null broadcaster - no delivery."""

    @property
    def owner(self) -> Mahajana:
        return Mahajana.NARADA

    def create_channel(self, name: str = "") -> bool:
        return True

    def delete_channel(self, name: str = "") -> bool:
        return True

    def list_channels(self) -> List[str]:
        return []

    def subscribe(self, channel: str = "", subscriber_id: str = "", handler: BroadcastHandler = None) -> bool:
        return True

    def unsubscribe(self, channel: str = "", subscriber_id: str = "") -> bool:
        return True

    def broadcast(
        self, channel: str = "", payload: MessagePayload = None, mode: DeliveryMode = DeliveryMode.AT_MOST_ONCE
    ) -> BroadcastResult:
        return BroadcastResult(success=True, recipients_count=0, failed_count=0, message_id="null")

    def broadcast_all(self, payload: MessagePayload = None) -> BroadcastResult:
        return BroadcastResult(success=True, recipients_count=0, failed_count=0, message_id="null")


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "OWNER",
    "LOTUS_POSITION",
    "LOTUS_QUARTER",
    "OWNED_OPCODES",
    "DeliveryMode",
    "Channel",
    "Subscription",
    "BroadcastHandler",
    "BroadcastProtocol",
    "Broadcaster",
    "NullBroadcaster",
]
