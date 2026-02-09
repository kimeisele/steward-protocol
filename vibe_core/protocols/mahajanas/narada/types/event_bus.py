"""
RE-EXPORT PROXY — SSOT is vibe_core.mahamantra.substrate.event_bus
==================================================================

This file re-exports all EventBus symbols from the Single Source of Truth.
Do NOT add implementations here. All code lives in substrate/event_bus.py.

History: This was an 870-line copy of the real EventBus that drifted out of sync.
Consolidated to a thin proxy to eliminate the parallel structure.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0xec02c0c4"  # GenesisByte: parampara % 37 == 0

# =============================================================================
# SSOT: vibe_core.mahamantra.substrate.event_bus
# =============================================================================

from vibe_core.mahamantra.substrate.event_bus import (  # noqa: F401
    Event,
    EventBus,
    EventBusStatus,
    EventColor,
    EventDetails,
    EventType,
    EVENT_COLOR_MAP,
    MetricsEntry,
    RateLimitStats,
    StalledInfo,
    SubscriberCounts,
    SubscriberHealth,
    SubscriberMetrics,
    SudarshanaGuard,
    ZombieInfo,
    get_event_bus,
)

from vibe_core.protocols.mahajanas.narada.events import (  # noqa: F401
    emit_event,
)

__all__ = [
    "Event",
    "EventBus",
    "EventBusStatus",
    "EventColor",
    "EventDetails",
    "EventType",
    "EVENT_COLOR_MAP",
    "MetricsEntry",
    "RateLimitStats",
    "StalledInfo",
    "SubscriberCounts",
    "SubscriberHealth",
    "SubscriberMetrics",
    "SudarshanaGuard",
    "ZombieInfo",
    "get_event_bus",
    "emit_event",
]
