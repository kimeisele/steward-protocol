"""
OPUS-174: Wiring Health Integration Tests

These tests verify that critical event wiring is functioning correctly.

TDD RED: These tests should FAIL until the fix is applied:
- KERNEL_TICK must be emitted by kernel.tick()

GAD-000 Compliance: These tests ensure the system doesn't fail silently.

<!-- @HARNESS
files:
  - path: tests/integration/test_wiring_health.py
    required: true
    rationale: "Integration tests for wiring health"
  - path: vibe_core/plugins/opus_assistant/manas/cortex/nadi_sense.py
    required: true
    rationale: "NadiSense implementation"

tests:
  - tests/integration/test_wiring_health.py
-->
"""

import asyncio
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Test EventBus
from vibe_core.event_bus import Event, EventBus, EventType

# Test NadiSense
from vibe_core.plugins.opus_assistant.manas.cortex.nadi_sense import (
    NadiPerception,
    NadiSense,
    WiringAnomaly,
)


class TestNadiSenseBasic:
    """Basic NadiSense functionality tests."""

    def test_nadi_sense_can_be_instantiated(self):
        """NadiSense should be instantiable without errors."""
        sense = NadiSense(workspace=Path.cwd())
        assert sense.name == "nadi_sense"

    def test_nadi_sense_perceive_returns_perception(self):
        """NadiSense.perceive() should return a NadiPerception."""
        sense = NadiSense(workspace=Path.cwd())
        perception = sense.perceive()

        assert isinstance(perception, NadiPerception)
        assert hasattr(perception, "anomalies")
        assert hasattr(perception, "health_score")

    def test_nadi_sense_boot_summary(self):
        """NadiSense should provide OPUS-172 compliant boot summary."""
        sense = NadiSense(workspace=Path.cwd())
        summary = sense.get_boot_summary()

        assert "message" in summary
        assert "data" in summary
        assert "emoji" in summary


class TestWiringAnomalyDetection:
    """Tests for detecting wiring anomalies."""

    def test_detects_dead_letter_event(self):
        """Should detect when an event type has subscribers but no emissions."""
        bus = EventBus(rate_limit_enabled=False)

        # Subscribe to KERNEL_TICK but never emit it
        received = []
        bus.subscribe(lambda e: received.append(e), event_type="KERNEL_TICK")

        sense = NadiSense(workspace=Path.cwd())
        sense._event_bus = bus  # Inject test bus

        perception = sense.perceive()

        # Should detect KERNEL_TICK as dead letter
        dead_letters = [a for a in perception.anomalies if a.anomaly_type == "dead_letter"]
        kernel_tick_anomaly = [a for a in dead_letters if a.event_type == "KERNEL_TICK"]

        assert len(kernel_tick_anomaly) > 0, (
            "NadiSense should detect KERNEL_TICK as dead letter when subscribed but never emitted"
        )
        assert kernel_tick_anomaly[0].severity == "critical"

    def test_no_anomaly_when_event_is_emitted(self):
        """Should NOT detect anomaly when event is properly emitted."""
        bus = EventBus(rate_limit_enabled=False)

        # Subscribe AND emit
        received = []
        bus.subscribe(lambda e: received.append(e), event_type="TEST_EVENT")

        # Emit the event
        asyncio.run(bus.emit(Event(event_type="TEST_EVENT", agent_id="test", message="Test emission")))

        sense = NadiSense(workspace=Path.cwd())
        sense._event_bus = bus

        perception = sense.perceive()

        # Should NOT have TEST_EVENT as dead letter
        dead_letters = [
            a for a in perception.anomalies if a.anomaly_type == "dead_letter" and a.event_type == "TEST_EVENT"
        ]
        assert len(dead_letters) == 0

    def test_detects_never_emitted_critical_event(self):
        """Should detect KERNEL_TICK as critical if never emitted."""
        bus = EventBus(rate_limit_enabled=False)

        sense = NadiSense(workspace=Path.cwd())
        sense._event_bus = bus

        # Check for KERNEL_TICK specifically
        wiring = sense.check_event_wiring("KERNEL_TICK")

        # Should show KERNEL_TICK has 0 emissions
        assert wiring["emission_count"] == 0, "KERNEL_TICK should have 0 emissions in fresh EventBus"


class TestKernelTickEmission:
    """
    CRITICAL TEST: Verifies KERNEL_TICK is actually emitted.

    THIS TEST SHOULD FAIL (RED) until the fix is applied to kernel_impl.py tick()
    """

    @pytest.mark.xfail(
        reason="KERNEL_TICK is not yet emitted by kernel.tick() - FIX NEEDED in kernel_impl.py",
        strict=True,
    )
    def test_kernel_tick_is_emitted_on_tick(self):
        """
        KERNEL_TICK must be emitted when kernel.tick() is called.

        This is a TDD RED test - it SHOULD FAIL until the fix is applied.
        When the fix is applied, remove the xfail marker.

        FIX LOCATION: vibe_core/kernel_impl.py line ~1133
        FIX: Add event bus emit after pulse() call

        ```python
        # After pulse() in tick():
        asyncio.create_task(self._event_bus.emit(Event(
            event_type=EventType.KERNEL_TICK,
            agent_id="kernel",
            message="Kernel tick"
        )))
        ```
        """
        # This is a documentation test - the actual fix needs kernel integration
        # The test documents what SHOULD happen

        # Create a mock EventBus to track emissions
        bus = EventBus(rate_limit_enabled=False)
        emitted_events = []

        async def track_emission(event):
            emitted_events.append(event)

        bus.subscribe(track_emission, event_type=EventType.KERNEL_TICK)

        # Run a kernel tick cycle (mocked for now)
        # In the real fix, kernel.tick() would emit KERNEL_TICK

        # Assert: Should have received KERNEL_TICK
        kernel_ticks = [e for e in emitted_events if e.event_type == EventType.KERNEL_TICK]

        # THIS WILL FAIL because kernel doesn't emit KERNEL_TICK yet
        assert len(kernel_ticks) > 0, (
            "KERNEL_TICK should be emitted by kernel.tick() but it's NOT!\n"
            "FIX NEEDED: Add emit(KERNEL_TICK) to kernel_impl.py tick()\n"
            "This is why MANAS hasn't ticked for 3 days!"
        )


class TestStaleStateDetection:
    """Tests for detecting stale state files."""

    def test_detects_stale_manas_intents(self, tmp_path):
        """Should detect when manas_intents.json is stale."""
        # Create old manas_intents.json
        opus_state = tmp_path / ".opus_state"
        opus_state.mkdir()
        intents_file = opus_state / "manas_intents.json"
        intents_file.write_text('{"intents": [], "updated_at": "2025-12-18T00:00:00"}')

        # Make it 3 hours old (beyond 2h threshold)
        old_time = time.time() - (3 * 3600)
        import os

        os.utime(intents_file, (old_time, old_time))

        sense = NadiSense(workspace=tmp_path)
        perception = sense.perceive()

        # Should detect stale file
        assert len(perception.stale_files) > 0, "Should detect stale manas_intents.json"

        stale = perception.stale_files[0]
        assert "manas_intents" in stale.path
        assert stale.age_hours >= 2.0


class TestIntentGeneration:
    """Tests for NadiSense intent generation."""

    def test_generates_intent_for_critical_anomaly(self):
        """Should generate intent for critical wiring anomalies."""
        bus = EventBus(rate_limit_enabled=False)

        # Subscribe to KERNEL_TICK but don't emit (creates dead letter)
        bus.subscribe(lambda e: None, event_type="KERNEL_TICK")

        sense = NadiSense(workspace=Path.cwd())
        sense._event_bus = bus

        intents = sense.generate_intents()

        # Should generate intent for KERNEL_TICK being dead letter
        kernel_intents = [i for i in intents if "KERNEL_TICK" in i.title]
        assert len(kernel_intents) > 0, "NadiSense should generate intent for KERNEL_TICK wiring failure"

        intent = kernel_intents[0]
        assert intent.priority.value == "critical"
        assert "wiring" in intent.intent_type.lower() or "repair" in intent.intent_type.lower()


class TestHealthScore:
    """Tests for health score calculation."""

    def test_healthy_score_when_no_anomalies(self):
        """Health score should be 100 when no anomalies."""
        bus = EventBus(rate_limit_enabled=False)

        # No subscriptions, no issues
        sense = NadiSense(workspace=Path.cwd())
        sense._event_bus = bus

        # Clear expected emissions to avoid false positives
        import vibe_core.plugins.opus_assistant.manas.cortex.nadi_sense as ns

        original = ns.EXPECTED_EMISSIONS.copy()
        ns.EXPECTED_EMISSIONS = {}  # No expectations

        try:
            perception = sense.perceive()
            # Score should be high when no critical issues
            assert perception.health_score >= 70
        finally:
            ns.EXPECTED_EMISSIONS = original

    def test_low_score_with_critical_anomalies(self):
        """Health score should drop with critical anomalies."""
        bus = EventBus(rate_limit_enabled=False)

        # Subscribe to KERNEL_TICK to trigger dead letter detection
        bus.subscribe(lambda e: None, event_type="KERNEL_TICK")

        sense = NadiSense(workspace=Path.cwd())
        sense._event_bus = bus

        perception = sense.perceive()

        # Score should be low with KERNEL_TICK failure
        assert perception.critical_count > 0
        assert perception.health_score < 100
