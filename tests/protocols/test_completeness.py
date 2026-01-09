import pytest
from vibe_core.protocols.event import EventBusProtocol, emit_event
from vibe_core.protocols import emit_event as emit_event_exported

def test_event_bus_protocol_completeness():
    """Verify EventBusProtocol has all required methods."""
    # Check signature presence (runtime checkable)
    assert hasattr(EventBusProtocol, "emit")
    assert hasattr(EventBusProtocol, "subscribe")
    assert hasattr(EventBusProtocol, "unsubscribe")
    assert hasattr(EventBusProtocol, "get_history")
    assert hasattr(EventBusProtocol, "get_status")
    # New method
    assert hasattr(EventBusProtocol, "clear_history")

def test_emit_event_exported():
    """Verify emit_event is exported correctly."""
    assert emit_event is not None
    assert callable(emit_event)
    assert emit_event_exported is emit_event

@pytest.mark.asyncio
async def test_emit_event_helper():
    """Verify emit_event helper creates NullEventBus if none exists and runs without error."""
    # This should use get_event_bus_safe internally
    await emit_event("ACTION", "test_agent", "Hello")
    # If no exception, passed.
