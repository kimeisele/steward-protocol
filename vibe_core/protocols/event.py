"""
EVENT BUS PROTOCOL - USE MAHAMANTRA
===================================

DEPRECATED: This file is MAYA (illusion).

ONE IMPORT, KRISHNA ROUTES:
    from vibe_core.mahamantra import mahamantra

    # Position 2 = NARADA (Broadcast / Events)
    mahamantra[2]                    # -> MantraPosition
    mahamantra.protocols.narada      # -> NaradaProtocolBase

The canonical source is: vibe_core.protocols.mahajanas.narada
This file is a bridge for backward compatibility only.
"""

# Re-export from canonical Mahajana location
# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x9bec8331"  # GenesisByte: parampara % 37 == 0

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
    # Helper functions
    "create_event",
    "get_event_bus_safe",
    "emit_event",
]
