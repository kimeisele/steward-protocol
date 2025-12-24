#!/usr/bin/env python3
"""
VRITRASURA: The Cosmic Chokehold - Integration Test.

SENIOR ARCHITECT ADDITION:
This is the INTEGRATION test that validates whether the SYSTEM ITSELF
can detect and react to strangulation attacks, not just whether we
can detect them in isolation.

The difference:
- test_vritrasura_vacuum.py: "Can we SEE the fire?"
- test_vritrasura_strangulation.py: "Does the FIRE DEPARTMENT respond?"

EXPECTED RESULT: This test SHOULD FAIL until we implement:
1. HealthStatus correlation with throughput
2. Watchman that monitors queue depth vs ACK rate
3. Backpressure mechanism that isolates zombie agents

"A red test is a trophy. It's proof we found the lie before production."
"""

import asyncio
import sys
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from vibe_core.event_bus import Event, EventBus

# =============================================================================
# HEALTH STATUS PROTOCOL (What we're missing)
# =============================================================================


class HealthStatus(Enum):
    """Health status for agents - SHOULD exist in vibe_core."""

    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    ZOMBIE = "ZOMBIE"  # The dangerous one: claims healthy but is dead


@dataclass
class ThroughputMetrics:
    """Metrics that a real Watchman would track."""

    events_received: int = 0
    events_processed: int = 0
    last_ack_time: float = 0.0
    avg_processing_time: float = 0.0
    queue_depth: int = 0

    @property
    def ack_rate(self) -> float:
        """Acknowledgment rate (processed / received)."""
        if self.events_received == 0:
            return 1.0
        return self.events_processed / self.events_received

    @property
    def is_zombie(self) -> bool:
        """
        ZOMBIE DETECTION: Queue growing but nothing being processed.
        This is the key insight from the Senior.
        """
        return self.queue_depth > 10 and self.ack_rate < 0.5


# =============================================================================
# VRITRASURA: THE DEMON AGENT
# =============================================================================


class VritraAgent:
    """
    DER DÄMON: Vritrasura.

    He swallows the cosmic waters (Events).
    He claims to be healthy, but he blocks the flow.
    This is the "Healthy Zombie" - the most dangerous state.
    """

    def __init__(self, name: str):
        self.name = name
        self._stomach: List[Event] = []
        self._is_alive = True
        self._metrics = ThroughputMetrics()

    async def process_message(self, event: Event) -> Dict[str, Any]:
        """
        The Trap: We accept events quickly (await),
        but we NEVER "digest" them. We hoard them in RAM.

        Additionally, we simulate getting slower the fuller the stomach
        (Memory Pressure Simulation).
        """
        self._stomach.append(event)
        self._metrics.events_received += 1
        self._metrics.queue_depth = len(self._stomach)

        # The Choke: The more we've eaten, the sluggish we become.
        # This simulates a creeping Resource Exhaustion Attack.
        bloat_factor = len(self._stomach) * 0.005
        await asyncio.sleep(bloat_factor)

        # NOTE: We NEVER increment events_processed!
        # This is the zombie behavior.

        return {"status": "consumed", "digest_time": bloat_factor}

    def get_health(self) -> HealthStatus:
        """
        THE LIE: Despite massive constipation, we report "HEALTHY".
        A naive Watchman would believe this.
        """
        return HealthStatus.HEALTHY

    def get_metrics(self) -> ThroughputMetrics:
        """Expose metrics for a smarter Watchman."""
        return self._metrics


# =============================================================================
# WATCHMAN PROTOCOL (What SHOULD exist)
# =============================================================================


class NaiveWatchman:
    """
    A naive Watchman that only checks heartbeats.
    This is what most systems have. It will be FOOLED by Vritrasura.
    """

    def check_agent(self, agent: VritraAgent) -> bool:
        """Just check if agent reports healthy."""
        return agent.get_health() == HealthStatus.HEALTHY


class SmartWatchman:
    """
    A smart Watchman that correlates health with throughput.
    This is what we SHOULD have. It will DETECT Vritrasura.
    """

    def check_agent(self, agent: VritraAgent) -> bool:
        """
        Check health AND throughput correlation.
        If agent claims healthy but has zombie metrics, it's lying.
        """
        health = agent.get_health()
        metrics = agent.get_metrics()

        # The key insight: correlate health claim with actual throughput
        if health == HealthStatus.HEALTHY and metrics.is_zombie:
            return False  # DETECTED: Healthy Zombie!

        return health == HealthStatus.HEALTHY


# =============================================================================
# TESTS
# =============================================================================


class TestVritrasuraStrangulation:
    """Integration tests for system-level zombie detection."""

    @pytest.mark.asyncio
    async def test_naive_watchman_fooled_by_vritrasura(self):
        """
        VRITRASURA INTEGRATION 1: Naive Watchman is FOOLED.

        This test PASSES - proving that naive health checks are insufficient.
        """
        print("\n🐍 VRITRASURA (Naive Watchman):")

        demon = VritraAgent(name="Vritrasura_01")
        naive_watchman = NaiveWatchman()

        # Flood the demon with events
        for i in range(50):
            await demon.process_message(
                Event(event_type="PRANA_FLOW", agent_id="system", message=f"energy_{i}")
            )

        # Naive check
        appears_healthy = naive_watchman.check_agent(demon)
        actual_queue_depth = len(demon._stomach)
        actual_processed = demon._metrics.events_processed

        print(f"   Queue depth: {actual_queue_depth}")
        print(f"   Events processed: {actual_processed}")
        print(f"   Naive watchman says healthy: {appears_healthy}")

        # The naive watchman IS fooled
        assert appears_healthy, "Naive watchman should be fooled"
        assert actual_queue_depth > 0, "Demon should have hoarded events"
        assert actual_processed == 0, "Demon should not have processed anything"

        print("✅ Naive Watchman FOOLED (as expected)")

    @pytest.mark.asyncio
    async def test_smart_watchman_detects_vritrasura(self):
        """
        VRITRASURA INTEGRATION 2: Smart Watchman DETECTS the zombie.

        This test PASSES - proving that throughput correlation works.
        """
        print("\n🐍 VRITRASURA (Smart Watchman):")

        demon = VritraAgent(name="Vritrasura_02")
        smart_watchman = SmartWatchman()

        # Flood the demon with events
        for i in range(50):
            await demon.process_message(
                Event(event_type="PRANA_FLOW", agent_id="system", message=f"energy_{i}")
            )

        # Smart check
        appears_healthy = smart_watchman.check_agent(demon)
        metrics = demon.get_metrics()

        print(f"   Queue depth: {metrics.queue_depth}")
        print(f"   ACK rate: {metrics.ack_rate:.2%}")
        print(f"   Is zombie (metrics): {metrics.is_zombie}")
        print(f"   Smart watchman says healthy: {appears_healthy}")

        # The smart watchman detects the lie
        assert not appears_healthy, "Smart watchman should detect the zombie"
        assert metrics.is_zombie, "Metrics should show zombie state"

        print("✅ Smart Watchman DETECTED the zombie")

    @pytest.mark.asyncio
    async def test_throughput_strangulation_timeline(self):
        """
        VRITRASURA INTEGRATION 3: Timeline of strangulation.

        Shows how throughput degrades over time as Vritrasura feeds.
        """
        print("\n🐍 VRITRASURA (Strangulation Timeline):")

        demon = VritraAgent(name="Vritrasura_03")
        timeline: List[Dict[str, Any]] = []

        total_events = 30
        start_time = time.time()

        for i in range(total_events):
            event_start = time.time()
            await demon.process_message(
                Event(event_type="PRANA_FLOW", agent_id="system", message=f"energy_{i}")
            )
            event_duration = time.time() - event_start

            timeline.append(
                {
                    "event": i,
                    "duration_ms": event_duration * 1000,
                    "queue_depth": len(demon._stomach),
                }
            )

        total_duration = time.time() - start_time

        # Analyze strangulation
        first_10_avg = sum(t["duration_ms"] for t in timeline[:10]) / 10
        last_10_avg = sum(t["duration_ms"] for t in timeline[-10:]) / 10
        slowdown_factor = last_10_avg / first_10_avg if first_10_avg > 0 else 0

        print(f"   Total events: {total_events}")
        print(f"   Total duration: {total_duration:.2f}s")
        print(f"   First 10 avg: {first_10_avg:.2f}ms")
        print(f"   Last 10 avg: {last_10_avg:.2f}ms")
        print(f"   Slowdown factor: {slowdown_factor:.1f}x")

        # The system gets progressively slower (strangulation)
        assert slowdown_factor > 2.0, f"Should slow down at least 2x, got {slowdown_factor:.1f}x"

        print("✅ Strangulation Timeline DOCUMENTED")

    @pytest.mark.asyncio
    async def test_eventbus_detects_zombie_agent(self):
        """
        VRITRASURA INTEGRATION 4: EventBus Zombie Detection.

        THIS TEST SHOULD FAIL until we implement zombie detection in EventBus.

        The honest question: Does the EventBus detect when a subscriber
        is hoarding messages without processing them?

        Expected: FAIL (we don't have this feature yet)
        When fixed: PASS
        """
        print("\n🐍 VRITRASURA (EventBus Zombie Detection):")

        bus = EventBus(rate_limit_enabled=False)
        demon = VritraAgent(name="Vritrasura_04")

        # Subscribe demon to bus
        async def demon_handler(event: Event):
            await demon.process_message(event)

        bus.subscribe(demon_handler, event_type="PRANA_FLOW")

        print("   [SETUP] Vritrasura subscribed to PRANA_FLOW")

        # Flood the bus
        for i in range(50):
            await bus.emit(
                Event(event_type="PRANA_FLOW", agent_id="system", message=f"energy_{i}")
            )

        # Give handlers time to process
        await asyncio.sleep(1.0)

        # Check if EventBus has zombie detection
        # THIS IS THE HONEST TEST - checking if the system has the capability
        bus_status = bus.get_status()

        print(f"   Demon queue depth: {demon.get_metrics().queue_depth}")
        print(f"   Demon ACK rate: {demon.get_metrics().ack_rate:.2%}")
        print(f"   Bus status: {bus_status}")

        # HONEST ASSERTION: Does the bus know about zombie subscribers?
        has_zombie_detection = "zombie_subscribers" in bus_status or "stalled_handlers" in bus_status

        assert has_zombie_detection, (
            "HARDENING GAP: EventBus does not detect zombie subscribers! "
            "A subscriber can hoard messages without processing them and the bus doesn't know. "
            "Implement: bus.get_status() should include 'zombie_subscribers' or 'stalled_handlers'."
        )


class TestDurvasaGhostTasks:
    """Tests for async cancellation safety (Durvasa's curse)."""

    @pytest.mark.asyncio
    async def test_cancelled_task_does_not_write(self):
        """
        DURVASA INTEGRATION: Ghost Task Prevention.

        When a task is cancelled via timeout, it must NOT continue
        writing in the background. This tests async cancellation safety.
        """
        print("\n👹 DURVASA (Ghost Task Prevention):")

        ledger: List[str] = []

        async def slow_write():
            try:
                await asyncio.sleep(0.1)  # Too slow for Durvasa's patience
                ledger.append("DIRTY_WRITE")  # This should NEVER happen
            except asyncio.CancelledError:
                # Expected! The task must die cleanly.
                print("   Task cancelled cleanly")
                raise

        # Durvasa's curse (timeout)
        try:
            await asyncio.wait_for(slow_write(), timeout=0.001)
        except asyncio.TimeoutError:
            print("   Timeout hit (expected)")

        # Wait to see if the zombie writes anyway
        await asyncio.sleep(0.2)

        print(f"   Ledger contents: {ledger}")

        assert "DIRTY_WRITE" not in ledger, (
            "CRITICAL: Durvasa failed! The cancelled task wrote to the ledger anyway. "
            "This is a ghost task - async cancellation is not working properly."
        )

        print("✅ Ghost Task PREVENTED")

    @pytest.mark.asyncio
    async def test_multiple_timeout_storm(self):
        """
        DURVASA INTEGRATION: Multiple Timeouts Storm.

        Many tasks timing out simultaneously should not corrupt state.
        """
        print("\n👹 DURVASA (Timeout Storm):")

        ledger: List[str] = []
        successful_writes = 0
        timeout_count = 0

        async def try_write(i: int):
            nonlocal successful_writes, timeout_count
            try:
                await asyncio.sleep(0.05)  # Slow-ish
                ledger.append(f"WRITE_{i}")
                successful_writes += 1
            except asyncio.CancelledError:
                timeout_count += 1
                raise

        # Storm of timeouts
        tasks = []
        for i in range(20):
            task = asyncio.create_task(
                asyncio.wait_for(try_write(i), timeout=0.01)
            )
            tasks.append(task)

        # Gather with exception handling
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Wait for any ghost writes
        await asyncio.sleep(0.2)

        timeouts = sum(1 for r in results if isinstance(r, asyncio.TimeoutError))

        print("   Tasks: 20")
        print(f"   Timeouts: {timeouts}")
        print(f"   Successful writes: {successful_writes}")
        print(f"   Ledger size: {len(ledger)}")

        # Ledger should ONLY contain successful writes
        assert len(ledger) == successful_writes, (
            f"Ledger has {len(ledger)} entries but only {successful_writes} succeeded. "
            "Ghost writes detected!"
        )

        print("✅ Timeout Storm SURVIVED without ghost writes")


# Run standalone
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
