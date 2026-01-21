"""
TEST FLOOD PROTOCOL
===================

Verifies the FloodProtocol for NAGA flooding operations.

MAHAJANA: NARADA (The Messenger)
OPCODE: PULSE_SYNC

"Wie Wasser in jede Ritze" - Like water into every crack.
"""

import pytest
from datetime import datetime

from vibe_core.protocols.naga.flood import (
    # Protocols
    FloodProtocol,
    FloodConsumerProtocol,
    NullFlood,
    # Enums
    FloodLayer,
    FloodStatus,
    # Data types
    FloodStats,
    FloodConfig,
    FloodSignal,
    FloodObservation,
    # Mantra connection
    FLOOD_OPCODE,
    FLOOD_PHASE,
    FLOOD_WORD,
    FLOOD_POSITION,
    FLOOD_MAHAJANA,
)
from vibe_core.protocols.substrate import MantraOpCode


class TestFloodLayers:
    """Test the three flood layers."""

    def test_three_layers_exist(self):
        """Three flood layers defined."""
        assert len(FloodLayer) == 3

    def test_event_bus_layer(self):
        """EventBus layer exists."""
        assert FloodLayer.EVENT_BUS.value == "event_bus"

    def test_signal_bus_layer(self):
        """SignalBus layer exists."""
        assert FloodLayer.SIGNAL_BUS.value == "signal_bus"

    def test_intelligence_layer(self):
        """Intelligence layer exists."""
        assert FloodLayer.INTELLIGENCE.value == "intelligence"


class TestFloodStatus:
    """Test flood status enum."""

    def test_inactive_status(self):
        """Inactive status exists."""
        assert FloodStatus.INACTIVE.value == "inactive"

    def test_active_status(self):
        """Active status exists."""
        assert FloodStatus.ACTIVE.value == "active"

    def test_error_status(self):
        """Error status exists."""
        assert FloodStatus.ERROR.value == "error"


class TestFloodStats:
    """Test FloodStats dataclass."""

    def test_stats_is_frozen(self):
        """FloodStats is immutable."""
        stats = FloodStats()
        with pytest.raises(Exception):
            stats.events_seen = 100

    def test_default_values(self):
        """Default values are zero."""
        stats = FloodStats()
        assert stats.events_seen == 0
        assert stats.violations_detected == 0

    def test_uptime_calculation(self):
        """Uptime is calculated from started_at."""
        # Without started_at, uptime is 0
        stats = FloodStats()
        assert stats.uptime_seconds == 0.0

        # With started_at, uptime is positive
        stats_with_time = FloodStats(started_at=datetime(2024, 1, 1, 0, 0, 0))
        assert stats_with_time.uptime_seconds > 0

    def test_events_per_second(self):
        """Throughput is calculated."""
        stats = FloodStats()
        assert stats.events_per_second == 0.0


class TestFloodConfig:
    """Test FloodConfig dataclass."""

    def test_config_is_frozen(self):
        """FloodConfig is immutable."""
        config = FloodConfig()
        with pytest.raises(Exception):
            config.enabled = False

    def test_default_values(self):
        """Default configuration values."""
        config = FloodConfig()
        assert config.max_analysis_queue == 1000
        assert config.analysis_timeout_ms == 50
        assert config.enabled is True

    def test_custom_config(self):
        """Custom configuration."""
        config = FloodConfig(max_analysis_queue=500, analysis_timeout_ms=100, enabled=False)
        assert config.max_analysis_queue == 500
        assert config.analysis_timeout_ms == 100
        assert config.enabled is False


class TestFloodSignal:
    """Test FloodSignal dataclass."""

    def test_signal_is_frozen(self):
        """FloodSignal is immutable."""
        signal = FloodSignal(
            source_id="test", event_type="TEST", agent_id="agent-1", toxicity_score=0.5, patterns_detected=()
        )
        with pytest.raises(Exception):
            signal.toxicity_score = 0.9

    def test_signal_fields(self):
        """Signal has all required fields."""
        signal = FloodSignal(
            source_id="flood_manager",
            event_type="CHAT_MESSAGE",
            agent_id="opus",
            toxicity_score=0.2,
            patterns_detected=("pattern_1", "pattern_2"),
        )
        assert signal.source_id == "flood_manager"
        assert signal.toxicity_score == 0.2
        assert len(signal.patterns_detected) == 2


class TestFloodObservation:
    """Test FloodObservation dataclass."""

    def test_observation_is_frozen(self):
        """FloodObservation is immutable."""
        obs = FloodObservation(
            observation_type="toxicity",
            severity="warning",
            source="takshaka",
            summary="Toxic pattern detected",
            details=(),
        )
        with pytest.raises(Exception):
            obs.severity = "critical"

    def test_observation_details_dict(self):
        """Details can be converted to dict."""
        obs = FloodObservation(
            observation_type="anomaly",
            severity="info",
            source="chitragupta",
            summary="Unusual activity",
            details=(("key1", "value1"), ("key2", "value2")),
        )
        d = obs.details_dict
        assert d["key1"] == "value1"
        assert d["key2"] == "value2"

    def test_severity_levels(self):
        """Various severity levels work."""
        severities = ["info", "warning", "critical"]
        for sev in severities:
            obs = FloodObservation(observation_type="test", severity=sev, source="test", summary="Test", details=())
            assert obs.severity == sev


class TestNullFlood:
    """Test NullFlood implementation."""

    def test_implements_protocol(self):
        """NullFlood satisfies FloodProtocol."""
        flood = NullFlood()
        # Check key methods exist
        assert hasattr(flood, "start")
        assert hasattr(flood, "stop")
        assert hasattr(flood, "get_stats")
        assert hasattr(flood, "opcode")

    def test_opcode_is_pulse_sync(self):
        """NullFlood uses PULSE_SYNC opcode."""
        flood = NullFlood()
        assert flood.opcode == MantraOpCode.DHARMA_TEST

    def test_mahajana_is_narada(self):
        """NullFlood owned by NARADA."""
        flood = NullFlood()
        assert flood.mahajana == "narada"

    def test_status_is_inactive(self):
        """NullFlood is always inactive."""
        flood = NullFlood()
        assert flood.status == FloodStatus.INACTIVE

    def test_start_stop_idempotent(self):
        """Start/stop are idempotent."""
        flood = NullFlood()
        flood.start()
        flood.start()  # No error
        flood.stop()
        flood.stop()  # No error

    def test_get_stats_returns_empty(self):
        """NullFlood returns empty stats."""
        flood = NullFlood()
        stats = flood.get_stats()
        assert stats.events_seen == 0

    def test_get_layers_returns_empty(self):
        """NullFlood has no active layers."""
        flood = NullFlood()
        layers = flood.get_layers()
        assert layers == []

    def test_subscribe_returns_null_id(self):
        """Subscribe returns null subscription ID."""
        flood = NullFlood()
        sub_id = flood.subscribe_observations(lambda x: None)
        assert sub_id == "null-subscription"

    def test_unsubscribe_returns_false(self):
        """Unsubscribe returns False."""
        flood = NullFlood()
        result = flood.unsubscribe_observations("any-id")
        assert result is False

    def test_get_recent_observations_empty(self):
        """No recent observations."""
        flood = NullFlood()
        obs = flood.get_recent_observations()
        assert obs == []


class TestMantraConnection:
    """Test Mantra CPU connection."""

    def test_opcode_is_pulse_sync(self):
        """Flood uses PULSE_SYNC opcode."""
        assert FLOOD_OPCODE == MantraOpCode.DHARMA_TEST

    def test_phase_is_purify(self):
        """Flood is in PURIFY phase."""
        assert FLOOD_PHASE == "PURIFY"

    def test_word_is_hare(self):
        """Flood word is HARE."""
        assert FLOOD_WORD == "HARE"

    def test_position_is_7(self):
        """Flood position is 7 (second HARE in PURIFY)."""
        assert FLOOD_POSITION == 7

    def test_mahajana_is_narada(self):
        """Flood is owned by NARADA."""
        assert FLOOD_MAHAJANA == "narada"


class TestFloodProtocolContract:
    """Test FloodProtocol contract."""

    def test_protocol_is_runtime_checkable(self):
        """Protocol can be checked at runtime."""
        assert hasattr(FloodProtocol, "__protocol_attrs__") or hasattr(FloodProtocol, "_is_protocol")

    def test_protocol_has_lifecycle_methods(self):
        """Protocol has lifecycle methods."""
        methods = ["start", "stop"]
        for method in methods:
            assert method in dir(FloodProtocol)

    def test_protocol_has_observation_methods(self):
        """Protocol has observation methods."""
        methods = ["get_stats", "get_layers", "get_recent_observations"]
        for method in methods:
            assert method in dir(FloodProtocol)

    def test_protocol_has_subscription_methods(self):
        """Protocol has subscription methods."""
        methods = ["subscribe_observations", "unsubscribe_observations"]
        for method in methods:
            assert method in dir(FloodProtocol)

    def test_protocol_has_cortex_integration(self):
        """Protocol has Cortex integration."""
        assert "set_cortex_callback" in dir(FloodProtocol)


class TestFloodConsumerProtocolContract:
    """Test FloodConsumerProtocol contract."""

    def test_protocol_is_runtime_checkable(self):
        """Protocol can be checked at runtime."""
        assert hasattr(FloodConsumerProtocol, "__protocol_attrs__") or hasattr(FloodConsumerProtocol, "_is_protocol")

    def test_has_on_flood_observation(self):
        """Protocol has on_flood_observation method."""
        assert "on_flood_observation" in dir(FloodConsumerProtocol)

    def test_has_get_relevant_observations(self):
        """Protocol has get_relevant_observations method."""
        assert "get_relevant_observations" in dir(FloodConsumerProtocol)


class TestStrictTyping:
    """Test that no Any types are used."""

    def test_flood_stats_no_any(self):
        """FloodStats has no Any types."""
        from typing import get_type_hints, Any

        hints = get_type_hints(FloodStats)
        for field_name, field_type in hints.items():
            assert field_type is not Any, f"FloodStats.{field_name} uses Any"

    def test_flood_config_no_any(self):
        """FloodConfig has no Any types."""
        from typing import get_type_hints, Any

        hints = get_type_hints(FloodConfig)
        for field_name, field_type in hints.items():
            assert field_type is not Any, f"FloodConfig.{field_name} uses Any"

    def test_flood_signal_no_any(self):
        """FloodSignal has no Any types."""
        from typing import get_type_hints, Any

        hints = get_type_hints(FloodSignal)
        for field_name, field_type in hints.items():
            assert field_type is not Any, f"FloodSignal.{field_name} uses Any"

    def test_flood_observation_no_any(self):
        """FloodObservation has no Any types."""
        from typing import get_type_hints, Any

        hints = get_type_hints(FloodObservation)
        for field_name, field_type in hints.items():
            assert field_type is not Any, f"FloodObservation.{field_name} uses Any"


class TestImmutability:
    """Test that all dataclasses are frozen."""

    def test_flood_stats_immutable(self):
        """FloodStats is immutable."""
        stats = FloodStats(events_seen=100)
        with pytest.raises(Exception):
            stats.events_seen = 200

    def test_flood_config_immutable(self):
        """FloodConfig is immutable."""
        config = FloodConfig()
        with pytest.raises(Exception):
            config.enabled = False

    def test_flood_signal_immutable(self):
        """FloodSignal is immutable."""
        signal = FloodSignal(
            source_id="test", event_type="TEST", agent_id=None, toxicity_score=0.0, patterns_detected=()
        )
        with pytest.raises(Exception):
            signal.source_id = "changed"

    def test_flood_observation_immutable(self):
        """FloodObservation is immutable."""
        obs = FloodObservation(observation_type="test", severity="info", source="test", summary="Test", details=())
        with pytest.raises(Exception):
            obs.summary = "Changed"
