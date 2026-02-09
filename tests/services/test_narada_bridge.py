"""
Tests for NaradaBridge — the connection between VenuOrchestrator and EventBus.

Verifies:
1. Bridge implements DIWSubscriberProtocol correctly
2. Bridge tracks DIW context (tick, position, phase, quarter)
3. Bridge stamps event details with DIW context
4. Bridge detects phase transitions
5. Bridge degrades gracefully when unwired
6. Bridge is a singleton via get_narada_bridge()
"""

import pytest

from vibe_core.mahamantra.protocols._seed import QUARTERS, WORDS
from vibe_core.mahamantra.protocols._venu import DIWEvent, DIWSubscriberProtocol
from vibe_core.services.narada_bridge import (
    DIWContext,
    NaradaBridge,
    get_narada_bridge,
    _QUARTER_NAMES,
)


def _make_diw_event(
    diw: int = 0x1234,
    tick: int = 0,
    position: int = 0,
    phase: int = 0,
    venu: int = 0,
    vamsi: int = 0,
    murali: int = 0,
    mode: int = 0,
) -> DIWEvent:
    """Helper to create a DIWEvent for testing."""
    return DIWEvent(
        diw=diw,
        tick=tick,
        position=position,
        phase=phase,
        venu=venu,
        vamsi=vamsi,
        murali=murali,
        mode=mode,
    )


class TestNaradaBridgeProtocol:
    """Bridge must satisfy DIWSubscriberProtocol."""

    def test_implements_diw_subscriber_protocol(self):
        bridge = NaradaBridge()
        assert isinstance(bridge, DIWSubscriberProtocol)

    def test_subscriber_name(self):
        bridge = NaradaBridge()
        assert bridge.subscriber_name == "narada_bridge"

    def test_has_on_diw(self):
        bridge = NaradaBridge()
        assert callable(bridge.on_diw)


class TestNaradaBridgeContext:
    """Bridge must track DIW context correctly."""

    def test_unwired_context_is_none(self):
        bridge = NaradaBridge()
        assert bridge.context is None
        assert not bridge.is_wired

    def test_first_tick_wires_bridge(self):
        bridge = NaradaBridge()
        event = _make_diw_event(tick=0, position=0, murali=0, mode=0)
        bridge.on_diw(event)
        assert bridge.is_wired
        assert bridge.context is not None

    def test_context_tracks_position(self):
        bridge = NaradaBridge()
        for pos in range(WORDS):
            phase = pos // (WORDS // QUARTERS)
            event = _make_diw_event(tick=pos, position=pos, murali=phase)
            bridge.on_diw(event)
            assert bridge.context["position"] == pos
            assert bridge.context["phase"] == phase

    def test_context_tracks_quarter_names(self):
        bridge = NaradaBridge()
        for phase_idx in range(QUARTERS):
            event = _make_diw_event(tick=phase_idx, position=phase_idx * 4, murali=phase_idx)
            bridge.on_diw(event)
            assert bridge.context["quarter"] == _QUARTER_NAMES[phase_idx]

    def test_context_tracks_diw_and_mode(self):
        bridge = NaradaBridge()
        event = _make_diw_event(diw=0xABCD, mode=2)
        bridge.on_diw(event)
        assert bridge.context["diw"] == 0xABCD
        assert bridge.context["mode"] == 2

    def test_total_ticks_increments(self):
        bridge = NaradaBridge()
        for i in range(10):
            bridge.on_diw(_make_diw_event(tick=i))
        assert bridge.total_ticks == 10


class TestNaradaBridgePhaseTransitions:
    """Bridge must detect quarter transitions."""

    def test_no_transition_on_first_tick(self):
        bridge = NaradaBridge()
        bridge.on_diw(_make_diw_event(murali=0))
        assert bridge.phase_transitions == 0

    def test_detects_phase_transition(self):
        bridge = NaradaBridge()
        bridge.on_diw(_make_diw_event(tick=0, murali=0))
        bridge.on_diw(_make_diw_event(tick=1, murali=1))
        assert bridge.phase_transitions == 1

    def test_full_cycle_has_three_transitions(self):
        """genesis→dharma→karma→moksha = 3 transitions."""
        bridge = NaradaBridge()
        for pos in range(WORDS):
            phase = pos // (WORDS // QUARTERS)
            bridge.on_diw(_make_diw_event(tick=pos, position=pos, murali=phase))
        assert bridge.phase_transitions == 3

    def test_no_transition_within_same_phase(self):
        bridge = NaradaBridge()
        for i in range(4):
            bridge.on_diw(_make_diw_event(tick=i, murali=0))
        assert bridge.phase_transitions == 0


class TestNaradaBridgeStamping:
    """Bridge must stamp event details with DIW context."""

    def test_stamp_returns_unchanged_when_unwired(self):
        bridge = NaradaBridge()
        details = {"message": "test"}
        result = bridge.stamp_event_details(details)
        assert result == {"message": "test"}
        assert "diw_context" not in result

    def test_stamp_adds_diw_context_when_wired(self):
        bridge = NaradaBridge()
        bridge.on_diw(_make_diw_event(diw=0x1234, tick=42, position=5, murali=1, mode=0))
        details = {"message": "test"}
        result = bridge.stamp_event_details(details)
        assert "diw_context" in result
        ctx = result["diw_context"]
        assert ctx["diw"] == 0x1234
        assert ctx["tick"] == 42
        assert ctx["position"] == 5
        assert ctx["phase"] == 1
        assert ctx["quarter"] == "dharma"

    def test_stamp_preserves_existing_details(self):
        bridge = NaradaBridge()
        bridge.on_diw(_make_diw_event())
        details = {"message": "hello", "target_id": "agent_1"}
        result = bridge.stamp_event_details(details)
        assert result["message"] == "hello"
        assert result["target_id"] == "agent_1"
        assert "diw_context" in result

    def test_stamp_does_not_mutate_original(self):
        bridge = NaradaBridge()
        bridge.on_diw(_make_diw_event())
        original = {"message": "test"}
        result = bridge.stamp_event_details(original)
        assert "diw_context" not in original
        assert "diw_context" in result

    def test_stamp_empty_details(self):
        bridge = NaradaBridge()
        bridge.on_diw(_make_diw_event())
        result = bridge.stamp_event_details({})
        assert "diw_context" in result


class TestNaradaBridgeSummary:
    """Bridge summary for telemetry."""

    def test_summary_unwired(self):
        bridge = NaradaBridge()
        s = bridge.summary()
        assert s["is_wired"] is False
        assert s["total_ticks"] == 0
        assert s["current_context"] is None

    def test_summary_wired(self):
        bridge = NaradaBridge()
        bridge.on_diw(_make_diw_event(tick=5, murali=1))
        s = bridge.summary()
        assert s["is_wired"] is True
        assert s["total_ticks"] == 1
        assert s["current_context"]["tick"] == 5


class TestNaradaBridgeSingleton:
    """get_narada_bridge() must return a singleton."""

    def test_singleton_returns_same_instance(self):
        # Reset the module-level singleton for this test
        import vibe_core.services.narada_bridge as mod
        mod._bridge_instance = None

        a = get_narada_bridge()
        b = get_narada_bridge()
        assert a is b

        # Clean up
        mod._bridge_instance = None

    def test_repr_unwired(self):
        bridge = NaradaBridge()
        assert "UNWIRED" in repr(bridge)

    def test_repr_wired(self):
        bridge = NaradaBridge()
        bridge.on_diw(_make_diw_event())
        assert "WIRED" in repr(bridge)


class TestEventDIWContext:
    """Phase 2: Event dataclass carries native diw_context field."""

    def test_event_has_diw_context_field(self):
        from vibe_core.mahamantra.substrate.event_bus import Event
        event = Event()
        assert hasattr(event, "diw_context")
        assert event.diw_context is None

    def test_event_diw_context_serializes(self):
        from vibe_core.mahamantra.substrate.event_bus import Event
        import json

        ctx = {"diw": 0x1234, "tick": 42, "position": 5, "phase": 1, "quarter": "dharma", "mode": 0}
        event = Event(diw_context=ctx)
        j = json.loads(event.to_json())
        assert j["diw_context"]["tick"] == 42
        assert j["diw_context"]["quarter"] == "dharma"

    def test_event_diw_context_none_serializes(self):
        from vibe_core.mahamantra.substrate.event_bus import Event
        import json

        event = Event()
        j = json.loads(event.to_json())
        assert j["diw_context"] is None

    def test_event_backward_compatible(self):
        """Existing code that creates Event without diw_context still works."""
        from vibe_core.mahamantra.substrate.event_bus import Event

        event = Event(
            event_type="ACTION",
            agent_id="test",
            message="hello",
        )
        assert event.diw_context is None
        assert event.agent_id == "test"

    def test_phase_transition_in_event_type_enum(self):
        from vibe_core.mahamantra.substrate.event_bus import EventType

        assert hasattr(EventType, "PHASE_TRANSITION")
        assert EventType.PHASE_TRANSITION.value == "PHASE_TRANSITION"


class TestEventBusDIWStamping:
    """EventBus.emit_sync stamps diw_context on Event when bridge is wired."""

    def test_emit_sync_without_bridge_has_none_context(self):
        """Before bridge is wired, diw_context is None."""
        from vibe_core.mahamantra.substrate.event_bus import EventBus, EventType

        bus = EventBus()
        # Reset class-level bridge state for isolation
        EventBus._narada_bridge = None
        EventBus._narada_bridge_failed = False

        captured = []
        bus.subscribe(lambda e: captured.append(e), [EventType.ACTION])
        bus.emit_sync(EventType.ACTION, "test", "hello")

        assert len(captured) == 1
        assert captured[0].diw_context is None

        # Clean up
        EventBus._narada_bridge = None
        EventBus._narada_bridge_failed = False

    def test_emit_sync_with_wired_bridge_has_context(self):
        """After bridge receives a DIW tick, events carry diw_context."""
        from vibe_core.mahamantra.substrate.event_bus import EventBus, EventType

        bus = EventBus()

        # Wire a bridge manually
        bridge = NaradaBridge()
        bridge.on_diw(_make_diw_event(diw=0xBEEF, tick=99, position=7, murali=1, mode=0))
        EventBus._narada_bridge = bridge
        EventBus._narada_bridge_failed = False

        captured = []
        bus.subscribe(lambda e: captured.append(e), [EventType.ACTION])
        bus.emit_sync(EventType.ACTION, "test", "hello")

        assert len(captured) == 1
        ctx = captured[0].diw_context
        assert ctx is not None
        assert ctx["diw"] == 0xBEEF
        assert ctx["tick"] == 99
        assert ctx["position"] == 7
        assert ctx["quarter"] == "dharma"

        # Clean up
        EventBus._narada_bridge = None
        EventBus._narada_bridge_failed = False
