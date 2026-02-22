"""
Tests for BeatSubscriber auto-discovery.

Verifies:
1. All 4 subscribers are discoverable
2. All have zero-arg constructors
3. All implement BeatSubscriberProtocol shape
4. discover_and_register_beat_subscribers() registers them in ServiceRegistry
"""

import pytest

from vibe_core.mahamantra import BeatSubscriberProtocol
from vibe_core.services.beat_discovery import (
    discover_and_register_beat_subscribers,
    discover_beat_subscriber_classes,
)


class TestBeatDiscovery:
    def test_discovers_all_subscribers(self):
        classes = discover_beat_subscriber_classes()
        names = [cls.__name__ for cls in classes]
        assert "OuroborosSubscriber" in names
        assert "ShuddhiSubscriber" in names
        assert "KalaBridgeSubscriber" in names
        assert "JagannathSubscriber" in names
        assert "LotusBridgeSubscriber" in names

    def test_all_zero_arg_constructors(self):
        classes = discover_beat_subscriber_classes()
        for cls in classes:
            instance = cls()  # Must not raise
            assert instance is not None

    def test_all_have_protocol_shape(self):
        classes = discover_beat_subscriber_classes()
        for cls in classes:
            instance = cls()
            assert hasattr(instance, "beat_name")
            assert hasattr(instance, "beat_interval")
            assert hasattr(instance, "on_beat_tick")
            assert isinstance(instance.beat_name, str)
            assert isinstance(instance.beat_interval, int)
            assert instance.beat_interval > 0

    def test_all_are_runtime_checkable(self):
        classes = discover_beat_subscriber_classes()
        for cls in classes:
            instance = cls()
            assert isinstance(instance, BeatSubscriberProtocol), (
                f"{cls.__name__} does not pass isinstance check for BeatSubscriberProtocol"
            )

    def test_register_populates_service_registry(self):
        from vibe_core.di import ServiceRegistry

        ServiceRegistry.reset()

        count = discover_and_register_beat_subscribers()
        assert count == 5

        # Verify they are discoverable via protocol
        found = ServiceRegistry.get_all(BeatSubscriberProtocol)
        assert len(found) >= 5

        names = {sub.beat_name for sub in found}
        assert "ouroboros_ingestion" in names
        assert "shuddhi_healing" in names
        assert "kala_bridge" in names
        assert "jagannath_ratha_yatra" in names
        assert "lotus_bridge" in names

        ServiceRegistry.reset()

    def test_beat_intervals_are_harmonic(self):
        """All intervals must be derived from SSOT or be 1 (every-tick bridge)."""
        from vibe_core.mahamantra import VENU_FIELD_TICKS, VENU_NADI_TICKS

        classes = discover_beat_subscriber_classes()
        # 1 = every tick (LotusBridge), NADI=72, FIELD=144
        valid_intervals = {1, VENU_NADI_TICKS, VENU_FIELD_TICKS}

        for cls in classes:
            instance = cls()
            assert instance.beat_interval in valid_intervals, (
                f"{cls.__name__}.beat_interval={instance.beat_interval} not in {valid_intervals}"
            )
