"""
EVENT BUS PROTOCOL - MIGRATED TO MAHAJANA OWNERSHIP
===================================================

OWNER: Mahajana.NARADA (The Cosmic Journalist)
NEW LOCATION: vibe_core.protocols.mahajanas.narada.events

This file re-exports from the canonical location for backwards compatibility.
All new code should import from:
    from vibe_core.protocols.mahajanas.narada import EventBusProtocol

"Narada travels everywhere, knows everything, reports faithfully.
 He does NOT act - he OBSERVES and TRANSMITS."
"""

# Re-export from canonical Mahajana location
from vibe_core.protocols.mahajanas.narada.events import (
    EventType,
    EventData,
    Event,
    SubscriberInfo,
    EventBusStats,
    EventBusState,
    EventBusProtocol,
    EventBusOwnedProtocol,
    NullEventBus,
    OWNER,
    LOTUS_POSITION,
    LOTUS_QUARTER,
    # Helper functions
    create_event,
    get_event_bus_safe,
    emit_event,
)

# Legacy compatibility - also export old names
EventBusStatus = EventBusStats  # Old name → new name

__all__ = [
    "EventType",
    "EventData",
    "Event",
    "SubscriberInfo",
    "EventBusStats",
    "EventBusStatus",  # Legacy name
    "EventBusState",
    "EventBusProtocol",
    "EventBusOwnedProtocol",
    "NullEventBus",
    "OWNER",
    "LOTUS_POSITION",
    "LOTUS_QUARTER",
    # Helper functions
    "create_event",
    "get_event_bus_safe",
    "emit_event",
]
