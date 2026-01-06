"""
SHANKHA Protocol - Der Herold (Broadcast/Pubsub Protocol)

Shankha (Conch Shell) - The Herald that announces.
From mythology: Its sound travels far and wide, reaching all who listen.

Responsibilities:
- Topic-based publish/subscribe
- Event broadcasting to all listeners
- Message queuing for offline subscribers
- Integration with existing EventBus
"""

from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Protocol, runtime_checkable

from vibe_core.protocols.naga.types import NagaStatus, NagaType


@dataclass
class BroadcastMessage:
    """A message for broadcasting."""

    topic: str
    payload: bytes
    sender_id: str
    timestamp: float
    message_id: str = ""
    content_type: str = "application/json"


@runtime_checkable
class ShankhaProtocol(Protocol):
    """
    Shankha - Der Herold. The Conch Shell that announces.

    Usage:
        shankha = ServiceRegistry.get(ShankhaProtocol)
        shankha.subscribe("drift.*", handler)
        shankha.publish("drift.detected", payload)
    """

    # === Publish ===

    def publish(self, topic: str, payload: bytes) -> str:
        """Publish a message to a topic."""
        ...

    def publish_json(self, topic: str, payload: Dict[str, object]) -> str:
        """Publish a JSON message to a topic."""
        ...

    def broadcast(self, payload: bytes) -> str:
        """Broadcast to ALL subscribers regardless of topic."""
        ...

    # === Subscribe ===

    def subscribe(
        self,
        topic_pattern: str,
        handler: Callable[[BroadcastMessage], None],
        subscriber_id: Optional[str] = None,
    ) -> str:
        """Subscribe to topics matching pattern."""
        ...

    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from a subscription."""
        ...

    def unsubscribe_all(self, subscriber_id: str) -> int:
        """Unsubscribe all subscriptions for a subscriber."""
        ...

    # === Topics ===

    def list_topics(self) -> List[str]:
        """Get all active topics."""
        ...

    def get_subscribers(self, topic: str) -> List[str]:
        """Get subscriber IDs for a topic."""
        ...

    def get_subscriber_count(self, topic: str) -> int:
        """Get number of subscribers for a topic."""
        ...

    # === Queue ===

    def get_pending_messages(self, subscriber_id: str, limit: int = 100) -> List[BroadcastMessage]:
        """Get pending messages for an offline subscriber."""
        ...

    def acknowledge(self, subscriber_id: str, message_ids: List[str]) -> int:
        """Acknowledge messages as processed."""
        ...

    # === Statistics ===

    def get_stats(self) -> Dict[str, int]:
        """Get messaging statistics."""
        ...

    def get_status(self) -> NagaStatus:
        """Get NAGA health status."""
        ...


# =============================================================================
# NULL IMPLEMENTATION (Arjuna Pattern)
# =============================================================================


class NullShankha:
    """No-op Shankha for when pubsub is unavailable."""

    def publish(self, topic: str, payload: bytes) -> str:
        return ""

    def publish_json(self, topic: str, payload: Dict[str, object]) -> str:
        return ""

    def broadcast(self, payload: bytes) -> str:
        return ""

    def subscribe(
        self,
        topic_pattern: str,
        handler: Callable[[BroadcastMessage], None],
        subscriber_id: Optional[str] = None,
    ) -> str:
        return ""

    def unsubscribe(self, subscription_id: str) -> bool:
        return False

    def unsubscribe_all(self, subscriber_id: str) -> int:
        return 0

    def list_topics(self) -> List[str]:
        return []

    def get_subscribers(self, topic: str) -> List[str]:
        return []

    def get_subscriber_count(self, topic: str) -> int:
        return 0

    def get_pending_messages(self, subscriber_id: str, limit: int = 100) -> List[BroadcastMessage]:
        return []

    def acknowledge(self, subscriber_id: str, message_ids: List[str]) -> int:
        return 0

    def get_stats(self) -> Dict[str, int]:
        return {"messages_published": 0, "subscribers_count": 0}

    def get_status(self) -> NagaStatus:
        return NagaStatus(naga_type=NagaType.SESHA, healthy=False, message="Pubsub not available")
