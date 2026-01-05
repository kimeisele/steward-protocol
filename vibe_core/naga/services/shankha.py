"""
SHANKHA SERVICE - Der Herold.

Shankha - The Conch Shell Naga that announces to all who listen.

From mythology: The Shankha (conch) is blown to announce important
events. Lord Vishnu holds the Panchajanya conch. Its sound reaches
all corners of the universe.

Responsibilities:
- Topic-based publish/subscribe messaging
- Pattern matching for topic subscriptions
- Message broadcasting to all listeners
- Pending message queue for offline subscribers

Integration:
- NagaFloodManager uses Shankha for event distribution
- All NAGAs can publish/subscribe to topics
"""

import fnmatch
import json
import logging
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from threading import Lock
from typing import Callable, Dict, List, Optional, Set

from vibe_core.naga.kulika import (
    NagaCapability,
    NagaLord,
    naga_service,
)
from vibe_core.naga.services.base import NagaBaseService, naga_governed
from vibe_core.protocols.naga import (
    BroadcastMessage,
    NagaStatus,
    NagaType,
    ShankhaProtocol,
)

logger = logging.getLogger("SHANKHA")


@dataclass
class Subscription:
    """A topic subscription."""

    subscription_id: str
    topic_pattern: str
    handler: Callable[[BroadcastMessage], None]
    subscriber_id: str
    created_at: float


@naga_service(
    name="Shankha",
    lord=NagaLord.SHANKHA,
    drift_source=None,  # Pure messaging, no drift handling
    priority=75,
    capabilities=[NagaCapability.BROADCAST],
    protocol_class="vibe_core.protocols.naga.ShankhaProtocol",
)
class ShankhaService(NagaBaseService, ShankhaProtocol):
    """
    Shankha - The Herald.

    Topic-based pubsub with pattern matching and message queuing.
    Thread-safe for concurrent publish/subscribe.


    OUROBOROS: Inherits NagaBaseService for self-monitoring."""

    def __init__(
        self,
        max_pending_per_subscriber: int = 1000,
        sender_id: Optional[str] = None,
    ) -> None:
        """
        Initialize Shankha.

        Args:
            max_pending_per_subscriber: Max pending messages per offline subscriber
            sender_id: Identifier for this node as message sender
        """
        super().__init__(service_name="Shankha")
        self._max_pending = max_pending_per_subscriber
        self._sender_id = sender_id or f"shankha-{uuid.uuid4().hex[:8]}"

        # Subscriptions
        self._subscriptions: Dict[str, Subscription] = {}  # subscription_id -> Subscription
        self._by_subscriber: Dict[str, Set[str]] = defaultdict(set)  # subscriber_id -> subscription_ids

        # Pending messages for offline subscribers
        self._pending: Dict[str, List[BroadcastMessage]] = defaultdict(list)

        # Active topics (for listing)
        self._active_topics: Set[str] = set()

        # Statistics
        self._messages_published = 0
        self._messages_delivered = 0
        self._lock = Lock()
        self._last_heartbeat = datetime.now()

        logger.info(f"SHANKHA initialized - Herald ready (sender={self._sender_id})")

    # =========================================================================
    # Publish
    # =========================================================================

    @naga_governed(operation="publish")
    def publish(self, topic: str, payload: bytes) -> str:
        """Publish a message to a topic."""
        self._last_heartbeat = datetime.now()

        message_id = f"msg-{uuid.uuid4().hex[:12]}"
        message = BroadcastMessage(
            topic=topic,
            payload=payload,
            sender_id=self._sender_id,
            timestamp=time.time(),
            message_id=message_id,
            content_type="application/octet-stream",
        )

        self._deliver(message)
        return message_id

    def publish_json(self, topic: str, payload: Dict[str, object]) -> str:
        """Publish a JSON message to a topic."""
        json_bytes = json.dumps(payload).encode("utf-8")
        self._last_heartbeat = datetime.now()

        message_id = f"msg-{uuid.uuid4().hex[:12]}"
        message = BroadcastMessage(
            topic=topic,
            payload=json_bytes,
            sender_id=self._sender_id,
            timestamp=time.time(),
            message_id=message_id,
            content_type="application/json",
        )

        self._deliver(message)
        return message_id

    def broadcast(self, payload: bytes) -> str:
        """Broadcast to ALL subscribers regardless of topic."""
        return self.publish("*", payload)

    def _deliver(self, message: BroadcastMessage) -> None:
        """Deliver message to matching subscribers."""
        with self._lock:
            self._messages_published += 1
            self._active_topics.add(message.topic)

            for sub in self._subscriptions.values():
                if self._matches_pattern(message.topic, sub.topic_pattern):
                    try:
                        sub.handler(message)
                        self._messages_delivered += 1
                    except Exception as e:
                        logger.warning(f"SHANKHA: Handler error for {sub.subscriber_id}: {e}")

    def _matches_pattern(self, topic: str, pattern: str) -> bool:
        """Check if topic matches subscription pattern."""
        # Handle wildcards
        if pattern == "*" or pattern == "**":
            return True

        # Convert pattern to fnmatch-compatible
        # "drift.*" matches "drift.state", "drift.config", etc.
        # "drift.**" matches "drift.state.deep.nested"
        fnmatch_pattern = pattern.replace(".**", ".*").replace("*", "*")

        # Simple wildcard matching
        if "*" in pattern:
            return fnmatch.fnmatch(topic, fnmatch_pattern)

        return topic == pattern

    # =========================================================================
    # Subscribe
    # =========================================================================

    @naga_governed(operation="subscribe")
    def subscribe(
        self,
        topic_pattern: str,
        handler: Callable[[BroadcastMessage], None],
        subscriber_id: Optional[str] = None,
    ) -> str:
        """Subscribe to topics matching pattern."""
        self._last_heartbeat = datetime.now()

        subscription_id = f"sub-{uuid.uuid4().hex[:12]}"
        actual_subscriber_id = subscriber_id or f"anon-{uuid.uuid4().hex[:8]}"

        subscription = Subscription(
            subscription_id=subscription_id,
            topic_pattern=topic_pattern,
            handler=handler,
            subscriber_id=actual_subscriber_id,
            created_at=time.time(),
        )

        with self._lock:
            self._subscriptions[subscription_id] = subscription
            self._by_subscriber[actual_subscriber_id].add(subscription_id)

        logger.debug(f"SHANKHA: Subscribed {actual_subscriber_id} to {topic_pattern}")
        return subscription_id

    def unsubscribe(self, subscription_id: str) -> bool:
        """Unsubscribe from a subscription."""
        self._last_heartbeat = datetime.now()

        with self._lock:
            if subscription_id not in self._subscriptions:
                return False

            sub = self._subscriptions[subscription_id]
            del self._subscriptions[subscription_id]
            self._by_subscriber[sub.subscriber_id].discard(subscription_id)

            logger.debug(f"SHANKHA: Unsubscribed {subscription_id}")
            return True

    def unsubscribe_all(self, subscriber_id: str) -> int:
        """Unsubscribe all subscriptions for a subscriber."""
        self._last_heartbeat = datetime.now()

        with self._lock:
            sub_ids = list(self._by_subscriber.get(subscriber_id, set()))
            count = 0
            for sub_id in sub_ids:
                if sub_id in self._subscriptions:
                    del self._subscriptions[sub_id]
                    count += 1

            if subscriber_id in self._by_subscriber:
                del self._by_subscriber[subscriber_id]

            return count

    # =========================================================================
    # Topics
    # =========================================================================

    def list_topics(self) -> List[str]:
        """Get all active topics."""
        with self._lock:
            return list(self._active_topics)

    def get_subscribers(self, topic: str) -> List[str]:
        """Get subscriber IDs for a topic."""
        with self._lock:
            subscribers: Set[str] = set()
            for sub in self._subscriptions.values():
                if self._matches_pattern(topic, sub.topic_pattern):
                    subscribers.add(sub.subscriber_id)
            return list(subscribers)

    def get_subscriber_count(self, topic: str) -> int:
        """Get number of subscribers for a topic."""
        return len(self.get_subscribers(topic))

    # =========================================================================
    # Pending Messages (for offline subscribers)
    # =========================================================================

    def queue_pending(self, subscriber_id: str, message: BroadcastMessage) -> bool:
        """Queue a message for an offline subscriber."""
        with self._lock:
            pending = self._pending[subscriber_id]
            if len(pending) >= self._max_pending:
                # Remove oldest
                pending.pop(0)

            pending.append(message)
            return True

    def get_pending_messages(self, subscriber_id: str, limit: int = 100) -> List[BroadcastMessage]:
        """Get pending messages for an offline subscriber."""
        self._last_heartbeat = datetime.now()

        with self._lock:
            pending = self._pending.get(subscriber_id, [])
            return pending[:limit]

    def acknowledge(self, subscriber_id: str, message_ids: List[str]) -> int:
        """Acknowledge messages as processed."""
        self._last_heartbeat = datetime.now()

        with self._lock:
            if subscriber_id not in self._pending:
                return 0

            original_count = len(self._pending[subscriber_id])
            self._pending[subscriber_id] = [m for m in self._pending[subscriber_id] if m.message_id not in message_ids]
            return original_count - len(self._pending[subscriber_id])

    # =========================================================================
    # Statistics
    # =========================================================================

    def get_stats(self) -> Dict[str, int]:
        """Get messaging statistics."""
        with self._lock:
            pending_total = sum(len(msgs) for msgs in self._pending.values())
            return {
                "messages_published": self._messages_published,
                "messages_delivered": self._messages_delivered,
                "subscribers_count": len(set(s.subscriber_id for s in self._subscriptions.values())),
                "subscriptions_count": len(self._subscriptions),
                "topics_count": len(self._active_topics),
                "pending_messages": pending_total,
            }

    def get_status(self) -> NagaStatus:
        """Get NAGA health status."""
        stats = self.get_stats()
        return NagaStatus(
            naga_type=NagaType.SESHA,  # No SHANKHA in NagaType
            healthy=True,
            last_heartbeat=self._last_heartbeat,
            events_processed=self._messages_published,
            errors=0,
            message=f"subs={stats['subscriptions_count']}, topics={stats['topics_count']}",
        )
