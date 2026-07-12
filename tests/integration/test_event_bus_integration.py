#!/usr/bin/env python3
"""
Integration Test: Event Bus (BROADCAST_EVENT)
==============================================

Tests for Phase 2 implementation of Event Bus and BROADCAST_EVENT syscall.

Tests that:
1. Agents can subscribe to events
2. Agents can broadcast events
3. Subscribers receive events
4. Event history is maintained
5. BROADCAST_EVENT syscall works end-to-end
"""

import asyncio
import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from vibe_core.plugins.test_orchestration import TestKernel
from vibe_core.protocols import VibeAgent
from vibe_core.scheduling import Task
from vibe_core.steward import OathMixin


class MockAgent(VibeAgent, OathMixin):
    """Mock agent for event testing with Constitutional Oath.

    Note: Named MockAgent (not TestAgent) to avoid pytest collection conflict.
    Uses OathMixin.swear_oath_sync() - the canonical way to become compliant.
    """

    def __init__(self, agent_id: str):
        super().__init__(
            agent_id=agent_id,
            name=f"Mock Agent {agent_id}",
            capabilities=[],
        )
        self.received_events = []
        # Initialize OathMixin and swear oath properly (not manual oath_sworn=True)
        self.oath_mixin_init(agent_id)
        self.swear_oath_sync()

    def process(self, task: Task) -> dict:
        return {"status": "completed", "message": "test"}

    def on_event(self, event):
        """Callback for event subscription."""
        self.received_events.append(event)


def test_agent_can_subscribe_to_events():
    """Test that agents can subscribe to events via system interface."""
    kernel = TestKernel.minimal()

    # Register agent
    agent = MockAgent("test_agent_1")
    kernel.register_agent(agent, spawn_process=False)

    # Subscribe to events
    sub_id = agent.system.subscribe_to_events(callback=agent.on_event, event_type="test.event")

    assert sub_id is not None
    assert len(sub_id) > 0


def test_agent_can_broadcast_events():
    """Test that agents can broadcast events."""
    kernel = TestKernel.minimal()

    # Register agent
    agent = MockAgent("test_agent_2")
    kernel.register_agent(agent, spawn_process=False)

    # Broadcast event
    result = asyncio.run(
        agent.system.broadcast_event(
            event_type="test.broadcast", data={"message": "Hello World"}, message="Test broadcast"
        )
    )

    assert result is not None
    assert result["event_type"] == "test.broadcast"
    assert result["broadcaster"] == "test_agent_2"
    assert "event_id" in result


def test_subscriber_receives_event():
    """Test that subscribed agents receive broadcast events."""
    kernel = TestKernel.minimal()

    # Register two agents
    broadcaster = MockAgent("broadcaster")
    subscriber = MockAgent("subscriber")
    kernel.register_agent(broadcaster, spawn_process=False)
    kernel.register_agent(subscriber, spawn_process=False)

    # Subscriber subscribes to events
    subscriber.system.subscribe_to_events(callback=subscriber.on_event, event_type="test.message")

    # Broadcaster sends event
    asyncio.run(broadcaster.system.broadcast_event(event_type="test.message", data={"content": "Hello Subscriber!"}))

    # Give event loop time to deliver
    asyncio.run(asyncio.sleep(0.1))

    # Verify subscriber received event
    assert len(subscriber.received_events) == 1
    event = subscriber.received_events[0]
    assert event.event_type == "test.message"
    assert event.agent_id == "broadcaster"
    assert event.details["content"] == "Hello Subscriber!"


def test_multiple_subscribers_receive_event():
    """Test that multiple subscribers all receive the same event."""
    kernel = TestKernel.minimal()

    # Register broadcaster and 3 subscribers
    broadcaster = MockAgent("broadcaster")
    sub1 = MockAgent("sub1")
    sub2 = MockAgent("sub2")
    sub3 = MockAgent("sub3")

    kernel.register_agent(broadcaster, spawn_process=False)
    kernel.register_agent(sub1, spawn_process=False)
    kernel.register_agent(sub2, spawn_process=False)
    kernel.register_agent(sub3, spawn_process=False)

    # All subscribe to same event
    sub1.system.subscribe_to_events(sub1.on_event, "test.fanout")
    sub2.system.subscribe_to_events(sub2.on_event, "test.fanout")
    sub3.system.subscribe_to_events(sub3.on_event, "test.fanout")

    # Broadcast
    asyncio.run(broadcaster.system.broadcast_event(event_type="test.fanout", data={"value": 42}))

    # Wait for delivery
    asyncio.run(asyncio.sleep(0.1))

    # All 3 should have received it
    assert len(sub1.received_events) == 1
    assert len(sub2.received_events) == 1
    assert len(sub3.received_events) == 1

    # Verify content
    assert sub1.received_events[0].details["value"] == 42
    assert sub2.received_events[0].details["value"] == 42
    assert sub3.received_events[0].details["value"] == 42


def test_global_subscriber_receives_all_events():
    """Test that global subscribers (no event_type filter) receive all events."""
    kernel = TestKernel.minimal()

    # Register agents
    broadcaster = MockAgent("broadcaster")
    global_sub = MockAgent("global_sub")

    kernel.register_agent(broadcaster, spawn_process=False)
    kernel.register_agent(global_sub, spawn_process=False)

    # Subscribe globally (no event_type)
    global_sub.system.subscribe_to_events(
        callback=global_sub.on_event,
        event_type=None,  # All events
    )

    # Broadcast different event types
    asyncio.run(broadcaster.system.broadcast_event(event_type="event.a", data={"num": 1}))
    asyncio.run(broadcaster.system.broadcast_event(event_type="event.b", data={"num": 2}))
    asyncio.run(broadcaster.system.broadcast_event(event_type="event.c", data={"num": 3}))

    # Wait for delivery
    asyncio.run(asyncio.sleep(0.1))

    # Global subscriber should have received all 3
    assert len(global_sub.received_events) == 3
    assert global_sub.received_events[0].event_type == "event.a"
    assert global_sub.received_events[1].event_type == "event.b"
    assert global_sub.received_events[2].event_type == "event.c"


def test_event_type_filtering():
    """Test that event type filtering works correctly."""
    kernel = TestKernel.minimal()

    # Register agents
    broadcaster = MockAgent("broadcaster")
    specific_sub = MockAgent("specific_sub")

    kernel.register_agent(broadcaster, spawn_process=False)
    kernel.register_agent(specific_sub, spawn_process=False)

    # Subscribe only to "event.important"
    specific_sub.system.subscribe_to_events(callback=specific_sub.on_event, event_type="event.important")

    # Broadcast different types
    asyncio.run(broadcaster.system.broadcast_event(event_type="event.unimportant", data={}))
    asyncio.run(broadcaster.system.broadcast_event(event_type="event.important", data={"flag": True}))
    asyncio.run(broadcaster.system.broadcast_event(event_type="event.noise", data={}))

    # Wait for delivery
    asyncio.run(asyncio.sleep(0.1))

    # Subscriber should only have received "event.important"
    assert len(specific_sub.received_events) == 1
    assert specific_sub.received_events[0].event_type == "event.important"
    assert specific_sub.received_events[0].details["flag"] is True


def test_event_history_maintained():
    """Test that event history is maintained."""
    kernel = TestKernel.minimal()

    # Register agent
    agent = MockAgent("agent")
    kernel.register_agent(agent, spawn_process=False)

    # Broadcast several events
    for i in range(5):
        asyncio.run(agent.system.broadcast_event(event_type="test.history", data={"index": i}))

    # Wait for delivery
    asyncio.run(asyncio.sleep(0.1))

    # Check history
    history = agent.system.get_event_history(limit=10, event_type="test.history")

    assert len(history) >= 5  # At least our 5 events
    # Most recent should be index 4
    assert history[-1].details["index"] == 4


def test_syscall_broadcast_event():
    """Test BROADCAST_EVENT syscall end-to-end."""
    from vibe_core.semantic_syscalls import SemanticSyscallHandler, SyscallRequest, SyscallType

    kernel = TestKernel.minimal()
    handler = SemanticSyscallHandler(kernel)

    # Register subscriber
    subscriber = MockAgent("subscriber")
    kernel.register_agent(subscriber, spawn_process=False)
    subscriber.system.subscribe_to_events(subscriber.on_event, "syscall.test")

    # Create BROADCAST_EVENT syscall
    request = SyscallRequest(
        syscall_type=SyscallType.BROADCAST_EVENT,
        requester_id="test_broadcaster",
        params={
            "event_type": "syscall.test",
            "data": {"message": "Hello from syscall"},
            "message": "Test syscall broadcast",
        },
    )

    # Execute syscall
    result = handler.handle(request)

    # Wait for delivery
    asyncio.run(asyncio.sleep(0.1))

    # Verify syscall succeeded
    assert result.success is True
    assert result.output["event_type"] == "syscall.test"
    assert result.output["broadcaster"] == "test_broadcaster"

    # Verify subscriber received event
    assert len(subscriber.received_events) == 1
    assert subscriber.received_events[0].event_type == "syscall.test"
    assert subscriber.received_events[0].details["message"] == "Hello from syscall"


def test_subscriber_error_doesnt_crash_others():
    """Test that error in one subscriber doesn't affect others (fault tolerance)."""
    kernel = TestKernel.minimal()

    # Register broadcaster
    broadcaster = MockAgent("broadcaster")
    kernel.register_agent(broadcaster, spawn_process=False)

    # Subscribe with error-prone callback
    def bad_callback(event):
        raise RuntimeError("Intentional error")

    # Subscribe with good callback
    good_agent = MockAgent("good_agent")
    kernel.register_agent(good_agent, spawn_process=False)

    # Subscribe both
    kernel.event_bus.subscribe(bad_callback, "test.fault")
    good_agent.system.subscribe_to_events(good_agent.on_event, "test.fault")

    # Broadcast
    asyncio.run(broadcaster.system.broadcast_event(event_type="test.fault", data={"value": 123}))

    # Wait for delivery
    asyncio.run(asyncio.sleep(0.1))

    # Good agent should still have received event despite bad callback error
    assert len(good_agent.received_events) == 1
    assert good_agent.received_events[0].details["value"] == 123


def test_unsubscribe_works():
    """Test that unsubscribe removes subscription."""
    kernel = TestKernel.minimal()

    # Register agents
    broadcaster = MockAgent("broadcaster")
    subscriber = MockAgent("subscriber")

    kernel.register_agent(broadcaster, spawn_process=False)
    kernel.register_agent(subscriber, spawn_process=False)

    # Subscribe
    subscriber.system.subscribe_to_events(subscriber.on_event, "test.unsub")

    # Send event
    asyncio.run(broadcaster.system.broadcast_event(event_type="test.unsub", data={"num": 1}))
    asyncio.run(asyncio.sleep(0.1))

    # Should have received it
    assert len(subscriber.received_events) == 1

    # Unsubscribe
    subscriber.system.unsubscribe_from_events(subscriber.on_event, "test.unsub")

    # Send another event
    asyncio.run(broadcaster.system.broadcast_event(event_type="test.unsub", data={"num": 2}))
    asyncio.run(asyncio.sleep(0.1))

    # Should NOT have received second event
    assert len(subscriber.received_events) == 1  # Still only 1


def test_event_bus_status():
    """Test that event bus status is accurate."""
    kernel = TestKernel.minimal()

    # Register agents
    agent1 = MockAgent("agent1")
    agent2 = MockAgent("agent2")
    kernel.register_agent(agent1, spawn_process=False)
    kernel.register_agent(agent2, spawn_process=False)

    # Subscribe
    agent1.system.subscribe_to_events(agent1.on_event, "type.a")
    agent2.system.subscribe_to_events(agent2.on_event, "type.b")

    # Check status
    status = kernel.event_bus.get_status()

    assert "total_events" in status
    assert "subscribers" in status
    assert status["subscribers"]["by_type"]["type.a"] == 1
    assert status["subscribers"]["by_type"]["type.b"] == 1


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
