"""
DEPRECATED: Use vibe_core.mahamantra import.
SSOT PROXY: Redirects to vibe_core.mahamantra.substrate.event_bus
"""
from vibe_core.mahamantra import (
    EventBus,
    EventType,
    Event,
    EventBusProtocol,
    get_event_bus
)

__all__ = [
    "EventBus",
    "EventType",
    "Event",
    "EventBusProtocol",
    "get_event_bus",
]
