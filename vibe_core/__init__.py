"""
Vibe Core Interface Stubs

These are local interface definitions that allow steward-protocol cartridges
to be developed against the VibeAgent protocol. When steward-protocol runs
within vibe-agency, it will use the actual vibe_core.kernel implementation.

This stub allows standalone development and type checking.

LAZY IMPORTS: All imports are deferred until actually accessed.
This prevents 800ms+ import cascades when only accessing substrate modules.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0xaea5b029"  # GenesisByte: parampara % 37 == 0

from typing import TYPE_CHECKING

# Only import for type checking (no runtime cost)
if TYPE_CHECKING:
    from .event_bus import Event, EventBus, EventType
    from .protocols import (
        AgentManifest,
        Capability,
        ManifestRegistry,
        VibeAgent,
        VibeKernel,
        VibeLedger,
        VibeScheduler,
    )
    from .pulse import PulseFrequency, PulseManager, SystemState
    from .scheduling import Task, TaskStatus


__all__ = [
    "VibeAgent",
    "AgentManifest",
    "Capability",
    "VibeLedger",
    "VibeScheduler",
    "VibeKernel",
    "ManifestRegistry",
    "Task",
    "TaskStatus",
    "get_pulse_manager",
    "PulseManager",
    "PulseFrequency",
    "SystemState",
    "get_event_bus",
    "EventBus",
    "Event",
    "EventType",
    "emit_event",
]


# =============================================================================
# LAZY IMPORT MECHANISM (Python 3.7+)
# =============================================================================

_LAZY_IMPORTS = {
    # event_bus
    "Event": ".event_bus",
    "EventBus": ".event_bus",
    "EventType": ".event_bus",
    "emit_event": ".event_bus",
    "get_event_bus": ".event_bus",
    # protocols
    "AgentManifest": ".protocols",
    "Capability": ".protocols",
    "ManifestRegistry": ".protocols",
    "VibeAgent": ".protocols",
    "VibeKernel": ".protocols",
    "VibeLedger": ".protocols",
    "VibeScheduler": ".protocols",
    # pulse
    "PulseFrequency": ".pulse",
    "PulseManager": ".pulse",
    "SystemState": ".pulse",
    "get_pulse_manager": ".pulse",
    # scheduling
    "Task": ".scheduling",
    "TaskStatus": ".scheduling",
}


def __getattr__(name: str):
    """Lazy import on attribute access."""
    if name in _LAZY_IMPORTS:
        import importlib
        module = importlib.import_module(_LAZY_IMPORTS[name], __package__)
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
