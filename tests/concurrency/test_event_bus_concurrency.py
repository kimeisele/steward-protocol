"""
TEST: EventBus Concurrency - Thread Safety & Race Conditions
=============================================================
Target: vibe_core/event_bus.py
Standard: GAD-5000 (Concurrency Hardening)

Tests verify:
1. Concurrent emit operations don't corrupt state
2. Subscribe/unsubscribe during emit is safe
3. Rate limiting works under load
4. Zombie detection catches stalled handlers
5. No deadlocks under high contention
"""

import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List
from unittest.mock import MagicMock

import pytest

from vibe_core.event_bus import Event, EventBus, EventType, SubscriberMetrics, SudarshanaGuard


class TestEventBusConcurrentEmit:
    """Test concurrent event emission."""

    @pytest.mark.asyncio
    async def test_concurrent_emit_maintains_count(self):
        """Concurrent emits should all be counted correctly."""
        bus = EventBus(max_history=10000, rate_limit_enabled=False)
        num_events = 100

        async def emit_event(i: int):
            event = Event(
                event_type=EventType.ACTION.value,
                agent_id=f"agent_{i % 10}",
                message=f"Event {i}",
            )
            await bus.emit(event)

        # Emit 100 events concurrently
        await asyncio.gather(*[emit_event(i) for i in range(num_events)])

        assert bus._event_count == num_events

    @pytest.mark.asyncio
    async def test_concurrent_emit_history_integrity(self):
        """History should contain all events without corruption."""
        bus = EventBus(max_history=1000, rate_limit_enabled=False)
        num_events = 50

        async def emit_event(i: int):
            event = Event(
                event_type=EventType.THOUGHT.value,
                agent_id="test",
                message=f"unique_marker_{i}",
            )
            await bus.emit(event)

        await asyncio.gather(*[emit_event(i) for i in range(num_events)])

        # Verify all events are in history
        messages = [e.message for e in bus._event_history]
        for i in range(num_events):
            assert f"unique_marker_{i}" in messages

    @pytest.mark.asyncio
    async def test_concurrent_emit_with_slow_subscribers(self):
        """Slow subscribers shouldn't block other events."""
        bus = EventBus(rate_limit_enabled=False)
        received_events: List[str] = []
        lock = threading.Lock()

        async def slow_subscriber(event: Event):
            await asyncio.sleep(0.01)  # 10ms delay
            with lock:
                received_events.append(event.message)

        bus.subscribe(slow_subscriber)

        # Emit multiple events quickly
        events = [Event(event_type=EventType.ACTION.value, agent_id="test", message=f"msg_{i}") for i in range(10)]

        start = time.time()
        await asyncio.gather(*[bus.emit(e) for e in events])
        duration = time.time() - start

        # Should complete in parallel, not sequentially
        # 10 events * 10ms sequential = 100ms
        # Parallel should be ~10-20ms
        assert duration < 0.1  # Less than 100ms
        assert len(received_events) == 10


class TestEventBusConcurrentSubscribe:
    """Test subscribe/unsubscribe during emit."""

    @pytest.mark.asyncio
    async def test_subscribe_during_emit_is_safe(self):
        """Subscribing while emitting shouldn't cause errors."""
        bus = EventBus(rate_limit_enabled=False)
        received = []

        def handler(event: Event):
            received.append(event.message)
            # Subscribe a new handler during event processing
            bus.subscribe(lambda e: None, EventType.THOUGHT.value)

        bus.subscribe(handler)

        # Emit multiple events
        for i in range(10):
            event = Event(event_type=EventType.ACTION.value, agent_id="test", message=f"msg_{i}")
            await bus.emit(event)

        assert len(received) == 10

    @pytest.mark.asyncio
    async def test_unsubscribe_during_emit_is_safe(self):
        """Unsubscribing while emitting shouldn't cause errors."""
        bus = EventBus(rate_limit_enabled=False)
        received = []
        handler_ref = None

        def handler(event: Event):
            received.append(event.message)
            # Try to unsubscribe self (may or may not succeed depending on timing)
            if handler_ref:
                try:
                    bus.unsubscribe(handler_ref)
                except Exception:
                    pass

        handler_ref = handler
        bus.subscribe(handler)

        # Should not crash
        for i in range(5):
            event = Event(event_type=EventType.ACTION.value, agent_id="test", message=f"msg_{i}")
            await bus.emit(event)


class TestSudarshanaRateLimiting:
    """Test rate limiting under concurrent load."""

    def test_rate_limit_blocks_flood(self):
        """Rate limiter should block excessive events from same agent."""
        guard = SudarshanaGuard(bucket_size=10, refill_rate=1.0, enabled=True)

        # First 10 should pass
        for _ in range(10):
            assert guard.check_traffic("flood_agent") is True

        # 11th should be blocked
        with pytest.raises(PermissionError, match="Rate limit exceeded"):
            guard.check_traffic("flood_agent")

    def test_rate_limit_vip_bypass(self):
        """VIP agents should bypass rate limiting."""
        guard = SudarshanaGuard(bucket_size=1, refill_rate=0.0, enabled=True)

        # VIP agents should never be blocked
        for vip in ["kernel", "system", "watchman", "narasimha"]:
            for _ in range(100):
                assert guard.check_traffic(vip) is True

    def test_rate_limit_concurrent_access(self):
        """Rate limiter should be thread-safe."""
        guard = SudarshanaGuard(bucket_size=50, refill_rate=10.0, enabled=True)
        blocked_count = 0
        lock = threading.Lock()

        def attempt_traffic():
            nonlocal blocked_count
            try:
                guard.check_traffic("concurrent_agent")
            except PermissionError:
                with lock:
                    blocked_count += 1

        # 100 threads trying to emit from same agent
        with ThreadPoolExecutor(max_workers=50) as pool:
            list(pool.map(lambda _: attempt_traffic(), range(100)))

        # Should have blocked ~50 (100 attempts - 50 bucket)
        assert blocked_count >= 40  # Allow some tolerance

    def test_rate_limit_refill(self):
        """Bucket should refill over time."""
        guard = SudarshanaGuard(bucket_size=5, refill_rate=100.0, enabled=True)

        # Drain bucket
        for _ in range(5):
            guard.check_traffic("refill_agent")

        # Should be blocked
        with pytest.raises(PermissionError):
            guard.check_traffic("refill_agent")

        # Wait for refill (100 tokens/sec = 5 tokens in 0.05s)
        time.sleep(0.1)

        # Should work again
        assert guard.check_traffic("refill_agent") is True


class TestSubscriberMetricsZombieDetection:
    """Test zombie subscriber detection."""

    def test_zombie_detection_identifies_stalled_handlers(self):
        """Handlers that receive but don't complete should be flagged."""
        metrics = SubscriberMetrics()
        metrics._zombie_threshold_events = 5
        metrics._zombie_threshold_rate = 0.5

        # Simulate a zombie: receives 10 events, completes 2
        for _ in range(10):
            metrics.record_send("zombie_handler")
        metrics.record_complete("zombie_handler", 0.001)
        metrics.record_complete("zombie_handler", 0.001)

        zombies = metrics.get_zombie_subscribers()
        assert len(zombies) == 1
        assert zombies[0]["callback_id"] == "zombie_handler"
        assert zombies[0]["ack_rate"] == 0.2  # 2/10

    def test_healthy_handler_not_flagged(self):
        """Handlers that complete events should not be flagged."""
        metrics = SubscriberMetrics()

        # Healthy handler: completes all events
        for _ in range(20):
            metrics.record_send("healthy_handler")
            metrics.record_complete("healthy_handler", 0.001)

        zombies = metrics.get_zombie_subscribers()
        assert len(zombies) == 0


class TestEventBusStressTest:
    """Stress tests for EventBus concurrency."""

    @pytest.mark.asyncio
    async def test_high_throughput_no_data_loss(self):
        """High event volume shouldn't lose data."""
        bus = EventBus(max_history=10000, rate_limit_enabled=False)
        received_count = 0
        lock = threading.Lock()

        def counter(event: Event):
            nonlocal received_count
            with lock:
                received_count += 1

        bus.subscribe(counter)

        num_events = 1000
        events = [
            Event(event_type=EventType.ACTION.value, agent_id="stress", message=f"e{i}") for i in range(num_events)
        ]

        await asyncio.gather(*[bus.emit(e) for e in events])

        assert received_count == num_events

    @pytest.mark.asyncio
    async def test_multiple_agents_concurrent_emit(self):
        """Multiple agents emitting simultaneously."""
        bus = EventBus(rate_limit_enabled=False)
        agent_counts: dict = {}
        lock = threading.Lock()

        def tracker(event: Event):
            with lock:
                agent_counts[event.agent_id] = agent_counts.get(event.agent_id, 0) + 1

        bus.subscribe(tracker)

        async def agent_emit(agent_id: str):
            for i in range(10):
                event = Event(
                    event_type=EventType.ACTION.value,
                    agent_id=agent_id,
                    message=f"msg_{i}",
                )
                await bus.emit(event)

        # 10 agents, 10 events each = 100 total
        await asyncio.gather(*[agent_emit(f"agent_{i}") for i in range(10)])

        assert sum(agent_counts.values()) == 100
        for agent_id, count in agent_counts.items():
            assert count == 10

    @pytest.mark.asyncio
    async def test_error_in_subscriber_doesnt_block_others(self):
        """One failing subscriber shouldn't affect others."""
        bus = EventBus(rate_limit_enabled=False)
        successful_receives: List[str] = []
        lock = threading.Lock()

        def failing_handler(event: Event):
            raise ValueError("Intentional failure")

        def successful_handler(event: Event):
            with lock:
                successful_receives.append(event.message)

        bus.subscribe(failing_handler)
        bus.subscribe(successful_handler)

        for i in range(5):
            event = Event(event_type=EventType.ACTION.value, agent_id="test", message=f"msg_{i}")
            await bus.emit(event)

        # Successful handler should have received all events
        assert len(successful_receives) == 5


class TestTypeCountIntegrity:
    """Test per-type event counting under concurrency."""

    @pytest.mark.asyncio
    async def test_type_counts_accurate_under_load(self):
        """Type counts should be accurate with concurrent emissions."""
        bus = EventBus(rate_limit_enabled=False)

        async def emit_type(event_type: str, count: int):
            for i in range(count):
                event = Event(event_type=event_type, agent_id="test", message=f"msg_{i}")
                await bus.emit(event)

        # Emit different types concurrently
        await asyncio.gather(
            emit_type(EventType.ACTION.value, 30),
            emit_type(EventType.THOUGHT.value, 20),
            emit_type(EventType.ERROR.value, 10),
        )

        assert bus._type_counts.get(EventType.ACTION.value) == 30
        assert bus._type_counts.get(EventType.THOUGHT.value) == 20
        assert bus._type_counts.get(EventType.ERROR.value) == 10
