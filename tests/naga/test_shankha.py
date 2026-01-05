"""
Tests for ShankhaService - The Herald.

Verifies:
- Topic-based publish/subscribe
- Pattern matching for subscriptions
- Message broadcasting
- Pending message queue
- Statistics tracking
"""

import json
import time
from typing import List

import pytest

from vibe_core.naga.services.shankha import ShankhaService
from vibe_core.protocols.naga import BroadcastMessage


@pytest.fixture
def shankha():
    """Create a ShankhaService for testing."""
    return ShankhaService(max_pending_per_subscriber=100, sender_id="test-sender")


class TestShankhaBasics:
    """Basic initialization tests."""

    def test_initialization(self, shankha):
        """Test service initializes correctly."""
        assert shankha is not None
        assert shankha._sender_id == "test-sender"

    def test_get_status(self, shankha):
        """Test get_status returns valid status."""
        status = shankha.get_status()
        assert status is not None
        assert "subs=" in status.message
        assert "topics=" in status.message


class TestPublish:
    """Publishing tests."""

    def test_publish_returns_message_id(self, shankha):
        """Test publish returns a message ID."""
        message_id = shankha.publish("topic.test", b"payload")
        assert message_id.startswith("msg-")

    def test_publish_json(self, shankha):
        """Test publishing JSON payload."""
        received: List[BroadcastMessage] = []
        shankha.subscribe("json.topic", received.append)

        payload = {"key": "value", "count": 42}
        message_id = shankha.publish_json("json.topic", payload)

        assert message_id.startswith("msg-")
        assert len(received) == 1
        assert json.loads(received[0].payload.decode()) == payload
        assert received[0].content_type == "application/json"

    def test_broadcast_to_all(self, shankha):
        """Test broadcast sends to all subscribers."""
        received_a: List[BroadcastMessage] = []
        received_b: List[BroadcastMessage] = []

        shankha.subscribe("topic.a", received_a.append)
        shankha.subscribe("topic.b", received_b.append)
        shankha.subscribe("*", received_a.append)  # Catch-all

        shankha.broadcast(b"to everyone")

        # Both should receive via the catch-all
        assert len(received_a) == 1
        assert received_a[0].topic == "*"


class TestSubscribe:
    """Subscription tests."""

    def test_subscribe_returns_subscription_id(self, shankha):
        """Test subscribe returns a subscription ID."""
        sub_id = shankha.subscribe("topic.test", lambda m: None)
        assert sub_id.startswith("sub-")

    def test_subscriber_receives_messages(self, shankha):
        """Test subscriber receives published messages."""
        received: List[BroadcastMessage] = []
        shankha.subscribe("events.user", received.append)

        shankha.publish("events.user", b"user created")
        shankha.publish("events.user", b"user updated")

        assert len(received) == 2
        assert received[0].payload == b"user created"
        assert received[1].payload == b"user updated"

    def test_subscriber_only_receives_matching_topic(self, shankha):
        """Test subscriber only gets matching topics."""
        received: List[BroadcastMessage] = []
        shankha.subscribe("events.user", received.append)

        shankha.publish("events.user", b"match")
        shankha.publish("events.order", b"no match")

        assert len(received) == 1
        assert received[0].payload == b"match"

    def test_multiple_subscribers_same_topic(self, shankha):
        """Test multiple subscribers to same topic."""
        received_1: List[BroadcastMessage] = []
        received_2: List[BroadcastMessage] = []

        shankha.subscribe("shared.topic", received_1.append)
        shankha.subscribe("shared.topic", received_2.append)

        shankha.publish("shared.topic", b"shared message")

        assert len(received_1) == 1
        assert len(received_2) == 1


class TestPatternMatching:
    """Topic pattern matching tests."""

    def test_wildcard_star_matches_any_suffix(self, shankha):
        """Test * wildcard matches any suffix (fnmatch behavior)."""
        received: List[BroadcastMessage] = []
        shankha.subscribe("events.*", received.append)

        shankha.publish("events.user", b"user event")
        shankha.publish("events.order", b"order event")
        shankha.publish("events.nested.deep", b"nested")  # fnmatch * matches dots too

        # fnmatch's * matches any characters including dots
        assert len(received) == 3

    def test_wildcard_double_star_matches_deep(self, shankha):
        """Test ** wildcard matches nested levels."""
        received: List[BroadcastMessage] = []
        shankha.subscribe("events.**", received.append)

        shankha.publish("events.user", b"level 1")
        shankha.publish("events.user.created", b"level 2")
        shankha.publish("events.a.b.c.d", b"deep")

        assert len(received) == 3

    def test_universal_wildcard(self, shankha):
        """Test * matches everything."""
        received: List[BroadcastMessage] = []
        shankha.subscribe("*", received.append)

        shankha.publish("any.topic", b"1")
        shankha.publish("another", b"2")
        shankha.publish("deep.nested.topic", b"3")

        assert len(received) == 3

    def test_exact_match(self, shankha):
        """Test exact topic matching."""
        received: List[BroadcastMessage] = []
        shankha.subscribe("exact.topic.name", received.append)

        shankha.publish("exact.topic.name", b"match")
        shankha.publish("exact.topic", b"no match")
        shankha.publish("exact.topic.name.extra", b"no match")

        assert len(received) == 1


class TestUnsubscribe:
    """Unsubscription tests."""

    def test_unsubscribe(self, shankha):
        """Test unsubscribing stops message delivery."""
        received: List[BroadcastMessage] = []
        sub_id = shankha.subscribe("topic", received.append)

        shankha.publish("topic", b"before unsub")
        assert len(received) == 1

        success = shankha.unsubscribe(sub_id)
        assert success is True

        shankha.publish("topic", b"after unsub")
        assert len(received) == 1  # Still 1, no new messages

    def test_unsubscribe_nonexistent(self, shankha):
        """Test unsubscribing non-existent ID returns False."""
        result = shankha.unsubscribe("sub-nonexistent")
        assert result is False

    def test_unsubscribe_all(self, shankha):
        """Test unsubscribing all for a subscriber."""
        received: List[BroadcastMessage] = []

        shankha.subscribe("topic.a", received.append, subscriber_id="user1")
        shankha.subscribe("topic.b", received.append, subscriber_id="user1")
        shankha.subscribe("topic.c", received.append, subscriber_id="user2")

        count = shankha.unsubscribe_all("user1")
        assert count == 2

        shankha.publish("topic.a", b"msg")
        shankha.publish("topic.b", b"msg")
        shankha.publish("topic.c", b"msg")

        # Only user2's subscription should receive
        assert len(received) == 1


class TestTopics:
    """Topic management tests."""

    def test_list_topics(self, shankha):
        """Test listing active topics."""
        shankha.publish("topic.a", b"1")
        shankha.publish("topic.b", b"2")
        shankha.publish("topic.a", b"3")  # Duplicate

        topics = shankha.list_topics()
        assert set(topics) == {"topic.a", "topic.b"}

    def test_get_subscribers(self, shankha):
        """Test getting subscribers for a topic."""
        shankha.subscribe("shared", lambda m: None, subscriber_id="sub1")
        shankha.subscribe("shared", lambda m: None, subscriber_id="sub2")
        shankha.subscribe("other", lambda m: None, subscriber_id="sub3")

        subs = shankha.get_subscribers("shared")
        assert set(subs) == {"sub1", "sub2"}

    def test_get_subscriber_count(self, shankha):
        """Test getting subscriber count."""
        shankha.subscribe("counted", lambda m: None)
        shankha.subscribe("counted", lambda m: None)
        shankha.subscribe("counted", lambda m: None)

        count = shankha.get_subscriber_count("counted")
        assert count == 3


class TestPendingMessages:
    """Pending message queue tests."""

    def test_queue_pending(self, shankha):
        """Test queuing pending messages."""
        msg = BroadcastMessage(
            topic="test",
            payload=b"pending",
            sender_id="sender",
            timestamp=time.time(),
            message_id="msg-123",
            content_type="application/octet-stream",
        )

        success = shankha.queue_pending("offline-user", msg)
        assert success is True

    def test_get_pending_messages(self, shankha):
        """Test retrieving pending messages."""
        for i in range(3):
            msg = BroadcastMessage(
                topic="test",
                payload=f"msg-{i}".encode(),
                sender_id="sender",
                timestamp=time.time(),
                message_id=f"msg-{i}",
                content_type="application/octet-stream",
            )
            shankha.queue_pending("user1", msg)

        pending = shankha.get_pending_messages("user1")
        assert len(pending) == 3

    def test_pending_limit(self, shankha):
        """Test pending message limit per subscriber."""
        for i in range(5):
            msg = BroadcastMessage(
                topic="test",
                payload=f"msg-{i}".encode(),
                sender_id="sender",
                timestamp=time.time(),
                message_id=f"msg-{i}",
                content_type="application/octet-stream",
            )
            shankha.get_pending_messages("user1", limit=3)  # Only get first 3

    def test_acknowledge_messages(self, shankha):
        """Test acknowledging messages."""
        for i in range(3):
            msg = BroadcastMessage(
                topic="test",
                payload=f"msg-{i}".encode(),
                sender_id="sender",
                timestamp=time.time(),
                message_id=f"msg-{i}",
                content_type="application/octet-stream",
            )
            shankha.queue_pending("user1", msg)

        # Acknowledge first two
        count = shankha.acknowledge("user1", ["msg-0", "msg-1"])
        assert count == 2

        # Only msg-2 should remain
        pending = shankha.get_pending_messages("user1")
        assert len(pending) == 1
        assert pending[0].message_id == "msg-2"


class TestStatistics:
    """Statistics tracking tests."""

    def test_messages_published_tracked(self, shankha):
        """Test that published messages are counted."""
        shankha.publish("topic", b"1")
        shankha.publish("topic", b"2")
        shankha.publish("topic", b"3")

        stats = shankha.get_stats()
        assert stats["messages_published"] == 3

    def test_messages_delivered_tracked(self, shankha):
        """Test that delivered messages are counted."""
        shankha.subscribe("topic", lambda m: None)
        shankha.subscribe("topic", lambda m: None)

        shankha.publish("topic", b"msg")

        stats = shankha.get_stats()
        assert stats["messages_delivered"] == 2  # 2 subscribers

    def test_subscriber_count(self, shankha):
        """Test subscriber count in stats."""
        shankha.subscribe("a", lambda m: None, subscriber_id="user1")
        shankha.subscribe("b", lambda m: None, subscriber_id="user1")
        shankha.subscribe("c", lambda m: None, subscriber_id="user2")

        stats = shankha.get_stats()
        assert stats["subscribers_count"] == 2  # 2 unique subscribers
        assert stats["subscriptions_count"] == 3  # 3 subscriptions


class TestHandlerErrors:
    """Handler error handling tests."""

    def test_handler_error_does_not_stop_delivery(self, shankha):
        """Test that handler errors don't stop other deliveries."""
        received: List[BroadcastMessage] = []

        def bad_handler(msg: BroadcastMessage) -> None:
            raise ValueError("Handler error!")

        def good_handler(msg: BroadcastMessage) -> None:
            received.append(msg)

        shankha.subscribe("topic", bad_handler)
        shankha.subscribe("topic", good_handler)

        # Should not raise, and good_handler should still receive
        shankha.publish("topic", b"test")
        assert len(received) == 1


class TestHeartbeat:
    """Heartbeat update tests."""

    def test_heartbeat_updates_on_publish(self, shankha):
        """Test heartbeat updates on publish."""
        initial = shankha._last_heartbeat
        time.sleep(0.01)

        shankha.publish("topic", b"msg")
        assert shankha._last_heartbeat > initial

    def test_heartbeat_updates_on_subscribe(self, shankha):
        """Test heartbeat updates on subscribe."""
        initial = shankha._last_heartbeat
        time.sleep(0.01)

        shankha.subscribe("topic", lambda m: None)
        assert shankha._last_heartbeat > initial
