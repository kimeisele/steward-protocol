"""
Tests for BeatSubscriber auto-discovery.

Verifies:
1. All 4 subscribers are discoverable
2. All have zero-arg constructors
3. All implement BeatSubscriberProtocol shape
4. discover_and_register_beat_subscribers() registers them in ServiceRegistry
"""

import pytest
from vibe_core.services.beat_discovery import (
    discover_beat_subscriber_classes,
    discover_and_register_beat_subscribers,
)
from vibe_core.mahamantra.protocols._venu import BeatSubscriberProtocol


class TestBeatDiscovery:
    def test_discovers_all_four_subscribers(self):
        classes = discover_beat_subscriber_classes()
        names = [cls.__name__ for cls in classes]
        assert "OuroborosSubscriber" in names
        assert "ShuddhiSubscriber" in names
        assert "KalaBridgeSubscriber" in names
        assert "JagannathSubscriber" in names

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
        assert count == 4

        # Verify they are discoverable via protocol
        found = ServiceRegistry.get_all(BeatSubscriberProtocol)
        assert len(found) >= 4

        names = {sub.beat_name for sub in found}
        assert "ouroboros_ingestion" in names
        assert "shuddhi_healing" in names
        assert "kala_bridge" in names
        assert "jagannath_ratha_yatra" in names

        ServiceRegistry.reset()

    def test_beat_intervals_are_harmonic(self):
        """All intervals must be derived from SSOT (NADI=72 or FIELD=144)."""
        from vibe_core.mahamantra.protocols._venu import VENU_NADI_TICKS, VENU_FIELD_TICKS

        classes = discover_beat_subscriber_classes()
        valid_intervals = {VENU_NADI_TICKS, VENU_FIELD_TICKS}

        for cls in classes:
            instance = cls()
            assert instance.beat_interval in valid_intervals, (
                f"{cls.__name__}.beat_interval={instance.beat_interval} "
                f"not in {valid_intervals}"
            )
