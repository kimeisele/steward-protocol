"""
NARADA Types - Position 7 (DHARMA Quarter, BROADCAST_EVENT)
===========================================================

NARADA - The Divine Messenger.
Types for events, broadcast, and communication.

Enums are eager (zero-dep leaf). Heavy classes are lazy (breaks import cycle).
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0xfeda18e8"  # GenesisByte: parampara % 37 == 0

# Eager: zero-dep leaf module
from vibe_core.mahamantra.substrate.event_types import (  # noqa: F401
    EventType,
    EventColor,
)

# Lazy: heavy classes from substrate/event_bus.py
_LAZY = {"Event", "EventBus", "SubscriberMetrics", "SudarshanaGuard", "get_event_bus"}


def __getattr__(name):
    if name in _LAZY:
        from vibe_core.mahamantra.substrate import event_bus
        return getattr(event_bus, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "EventType",
    "EventColor",
    "Event",
    "EventBus",
    "SubscriberMetrics",
    "SudarshanaGuard",
    "get_event_bus",
]
