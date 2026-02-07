"""
Tests for DIW Telemetry Subscriber and DIW Discovery.

Verifies:
1. DIWTelemetrySubscriber tracks events correctly
2. Phase distribution is accurate
3. Cycle detection works
4. Discovery finds and registers the subscriber
5. isinstance check against DIWSubscriberProtocol passes
"""

import pytest
from vibe_core.mahamantra.protocols._venu import DIWEvent, DIWSubscriberProtocol
from vibe_core.mahamantra.protocols._seed import WORDS, QUARTERS
from vibe_core.services.diw_telemetry import DIWTelemetrySubscriber
from vibe_core.services.diw_discovery import (
    discover_diw_subscriber_classes,
    discover_and_register_diw_subscribers,
)


def _make_event(position: int, phase: int = 0, mode: int = 0, diw: int = 0x1234) -> DIWEvent:
    return DIWEvent(
        diw=diw,
        tick=position,
        position=position,
        phase=phase,
        venu=0,
        vamsi=0,
        murali=phase,
        mode=mode,
    )


class TestDIWTelemetrySubscriber:
    def test_initial_state(self):
        sub = DIWTelemetrySubscriber()
        assert sub.total_events == 0
        assert sub.cycles_completed == 0
        assert sub.subscriber_name == "diw_telemetry"

    def test_counts_events(self):
        sub = DIWTelemetrySubscriber()
        for i in range(10):
            sub.on_diw(_make_event(i % WORDS))
        assert sub.total_events == 10

    def test_phase_distribution(self):
        sub = DIWTelemetrySubscriber()
        # Send 4 events per phase
        for phase in range(QUARTERS):
            for _ in range(4):
                sub.on_diw(_make_event(0, phase=phase))
        assert sub.phase_distribution == [4, 4, 4, 4]

    def test_cycle_detection(self):
        sub = DIWTelemetrySubscriber()
        # Cycle detection triggers on 15→0 wrap.
        # First loop: _last_position starts at -1, so 0 doesn't trigger.
        # Second loop: 15→0 triggers cycle 1.
        # Third loop: 15→0 triggers cycle 2.
        for cycle in range(3):
            for pos in range(WORDS):
                sub.on_diw(_make_event(pos, phase=pos // 4))
        assert sub.cycles_completed == 2

    def test_mode_distribution(self):
        sub = DIWTelemetrySubscriber()
        sub.on_diw(_make_event(0, mode=0))
        sub.on_diw(_make_event(1, mode=0))
        sub.on_diw(_make_event(2, mode=1))
        assert sub.mode_distribution == {0: 2, 1: 1}

    def test_summary(self):
        sub = DIWTelemetrySubscriber()
        sub.on_diw(_make_event(5, phase=1, mode=0, diw=0xABCD))
        s = sub.summary()
        assert s["total_events"] == 1
        assert s["last_position"] == 5
        assert s["last_diw"] == 0xABCD

    def test_isinstance_protocol(self):
        sub = DIWTelemetrySubscriber()
        assert isinstance(sub, DIWSubscriberProtocol)

    def test_orchestrator_integration(self):
        """Prove the subscriber works with VenuOrchestrator end-to-end."""
        from vibe_core.mahamantra.substrate.venu_orchestrator import VenuOrchestrator

        orch = VenuOrchestrator()
        sub = DIWTelemetrySubscriber()
        orch.subscribe(sub)

        # Run 2 full cycles + 1 step to trigger 2 wraps (15→0)
        # 16 steps = positions 0-15 (no wrap yet)
        # 17th step = position 0 again (1st wrap = cycle 1)
        # 33rd step = position 0 again (2nd wrap = cycle 2)
        for _ in range(WORDS * 2 + 1):
            orch.step()

        assert sub.total_events == WORDS * 2 + 1
        assert sub.cycles_completed == 2
        # All 4 phases should have events
        assert all(c > 0 for c in sub.phase_distribution)


class TestDIWDiscovery:
    def test_discovers_telemetry(self):
        classes = discover_diw_subscriber_classes()
        names = [cls.__name__ for cls in classes]
        assert "DIWTelemetrySubscriber" in names

    def test_register_populates_registry(self):
        from vibe_core.di import ServiceRegistry
        ServiceRegistry.reset()

        count = discover_and_register_diw_subscribers()
        assert count >= 1

        found = ServiceRegistry.get_all(DIWSubscriberProtocol)
        assert len(found) >= 1
        assert any(s.subscriber_name == "diw_telemetry" for s in found)

        ServiceRegistry.reset()
