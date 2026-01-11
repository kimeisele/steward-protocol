"""
Tests for Narada Event Bus Protocol.

Owner: NARADA (Communication)
WATERTIGHT: All types explicit, no Any.
"""

import pytest
from typing import List

from vibe_core.protocols.mahajanas.narada import (
    EventType,
    EventData,
    Event,
    SubscriberInfo,
    EventBusStats,
    EventBusState,
    EventBusProtocol,
    EventBusOwnedProtocol,
    NullEventBus,
)
from vibe_core.protocols.mahajanas.router import Mahajana


class TestEventBusProtocol:
    """Test EventBusProtocol types and interfaces."""

    def test_owner_is_narada(self) -> None:
        """ANTI-MAYAVAD: EventBus is owned by NARADA (Position 2)."""
        from vibe_core.mahamantra import mahamantra
        assert mahamantra[2].guardian == Mahajana.NARADA

    def test_null_event_bus_implements_protocol(self) -> None:
        """NullEventBus should work as a drop-in replacement."""
        bus = NullEventBus()
        assert bus.owner == Mahajana.NARADA

    def test_null_event_bus_emit(self) -> None:
        """NullEventBus should accept emits."""
        bus = NullEventBus()
        event: Event = {
            "id": "test-123",
            "type": EventType.ACTION.value,
            "agent_id": "test-agent",
            "message": "Test message",
        }
        assert bus.emit(event) is True

    def test_null_event_bus_emit_sync(self) -> None:
        """NullEventBus should return event ID."""
        bus = NullEventBus()
        event_id = bus.emit_sync(
            event_type=EventType.THOUGHT,
            agent_id="test-agent",
            message="Thinking...",
        )
        assert event_id == "null-event-id"

    def test_null_event_bus_subscribe(self) -> None:
        """NullEventBus should accept subscriptions."""
        bus = NullEventBus()

        def callback(event: Event) -> None:
            pass

        subscriber_id = bus.subscribe(callback, [EventType.ACTION])
        assert subscriber_id == "null-subscriber-id"

    def test_null_event_bus_stats_watertight(self) -> None:
        """Stats should be WATERTIGHT TypedDict."""
        bus = NullEventBus()
        stats: EventBusStats = bus.get_stats()

        # All fields should be typed, no Any
        assert stats["total_events_emitted"] == 0
        assert stats["total_subscribers"] == 0
        assert stats["zombie_count"] == 0

    def test_null_event_bus_state_watertight(self) -> None:
        """State should be WATERTIGHT TypedDict."""
        bus = NullEventBus()
        state: EventBusState = bus.get_state()

        assert state["protocol_name"] == "event_bus"
        assert state["owner"] == "narada"
        assert state["health"] == "pristine"

    def test_event_types_enum(self) -> None:
        """All event types should be defined."""
        assert EventType.THOUGHT.value == "THOUGHT"
        assert EventType.ACTION.value == "ACTION"
        assert EventType.ERROR.value == "ERROR"
        assert EventType.VIOLATION.value == "VIOLATION"
        assert EventType.MERCY.value == "MERCY"

    def test_event_data_watertight(self) -> None:
        """EventData should be WATERTIGHT TypedDict."""
        data: EventData = {
            "message": "Test message",
            "agent_id": "test-agent",
            "error_message": "",
        }
        assert data["message"] == "Test message"

    def test_subscriber_info_watertight(self) -> None:
        """SubscriberInfo should be WATERTIGHT TypedDict."""
        info: SubscriberInfo = {
            "callback_id": "cb-123",
            "event_types": [EventType.ACTION.value, EventType.ERROR.value],
            "events_received": 10,
            "events_completed": 8,
            "ack_rate": 0.8,
            "is_zombie": False,
            "is_stalled": False,
        }
        assert info["ack_rate"] == 0.8
        assert info["is_zombie"] is False


class TestEventBusOwnedProtocol:
    """Test OwnedProtocol wrapper."""

    def test_owned_protocol_owner(self) -> None:
        """OwnedProtocol should have NARADA as owner."""
        bus = NullEventBus()
        owned = EventBusOwnedProtocol(bus)
        assert owned.OWNER == Mahajana.NARADA
        assert owned.owner == Mahajana.NARADA

    def test_owned_protocol_name(self) -> None:
        """Protocol name should be 'event_bus'."""
        bus = NullEventBus()
        owned = EventBusOwnedProtocol(bus)
        assert owned.PROTOCOL_NAME == "event_bus"

    def test_owned_protocol_chant(self) -> None:
        """OwnedProtocol should be able to chant."""
        bus = NullEventBus()
        owned = EventBusOwnedProtocol(bus)

        # Initial state
        assert owned.is_chanting is False

        # Chant and verify
        owned.chant()
        assert owned.is_chanting is True

    def test_owned_protocol_state_watertight(self) -> None:
        """get_state() should return WATERTIGHT ProtocolState."""
        bus = NullEventBus()
        owned = EventBusOwnedProtocol(bus)
        state = owned.get_state()

        assert state["protocol_name"] == "event_bus"
        assert state["owner"] == "narada"
        # No Any types allowed!

    def test_owned_protocol_gad_audit(self) -> None:
        """OwnedProtocol should pass GAD-000 audit."""
        bus = NullEventBus()
        owned = EventBusOwnedProtocol(bus)
        audit = owned.audit()

        # Basic checks should pass
        assert audit.discoverability is True  # Has name and description
        assert audit.sovereign_present is True  # Has owner


class TestVritrasuraDetection:
    """Test zombie/stalled subscriber detection."""

    def test_null_bus_no_zombies(self) -> None:
        """NullEventBus should have no zombies."""
        bus = NullEventBus()
        zombies: List[SubscriberInfo] = bus.get_zombie_subscribers()
        assert zombies == []

    def test_null_bus_no_stalled(self) -> None:
        """NullEventBus should have no stalled handlers."""
        bus = NullEventBus()
        stalled: List[SubscriberInfo] = bus.get_stalled_subscribers()
        assert stalled == []


class TestSudarshanaGuard:
    """Test rate limiting."""

    def test_null_bus_not_rate_limited(self) -> None:
        """NullEventBus should not rate limit anyone."""
        bus = NullEventBus()
        assert bus.is_rate_limited("any-agent") is False

    def test_null_bus_reset_rate_limit(self) -> None:
        """Reset should work without error."""
        bus = NullEventBus()
        bus.reset_rate_limit("any-agent")  # Should not raise
