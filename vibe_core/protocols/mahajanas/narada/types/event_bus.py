"""
RE-EXPORT PROXY — Lazy to avoid circular imports
=================================================

Enums come from the zero-dep leaf module (event_types.py) — always safe.
Heavy classes (Event, EventBus, etc.) are resolved lazily via __getattr__
because this file is loaded during narada/__init__.py which is triggered
while substrate/event_bus.py is still initializing.

Do NOT add implementations here.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0xec02c0c4"  # GenesisByte: parampara % 37 == 0

# =============================================================================
# EAGER: Zero-dep leaf module (no cycles possible)
# =============================================================================

from vibe_core.mahamantra.substrate.event_types import (  # noqa: F401
    EventType,
    EventColor,
    EVENT_COLOR_MAP,
)

# =============================================================================
# LAZY: Heavy classes resolved on first access (breaks import cycle)
# =============================================================================

_LAZY_IMPORTS = {
    "Event", "EventBus", "EventBusStatus", "EventDetails",
    "MetricsEntry", "RateLimitStats", "StalledInfo",
    "SubscriberCounts", "SubscriberHealth", "SubscriberMetrics",
    "SudarshanaGuard", "ZombieInfo", "get_event_bus",
}

_LAZY_EVENTS = {
    "emit_event",
}


def __getattr__(name):
    if name in _LAZY_IMPORTS:
        from vibe_core.mahamantra.substrate import event_bus
        return getattr(event_bus, name)
    if name in _LAZY_EVENTS:
        from vibe_core.protocols.mahajanas.narada import events
        return getattr(events, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "EventType", "EventColor", "EVENT_COLOR_MAP",
    "Event", "EventBus", "EventBusStatus", "EventDetails",
    "MetricsEntry", "RateLimitStats", "StalledInfo",
    "SubscriberCounts", "SubscriberHealth", "SubscriberMetrics",
    "SudarshanaGuard", "ZombieInfo", "get_event_bus",
    "emit_event",
]
