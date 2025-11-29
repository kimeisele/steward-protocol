"""
Vibe Core Interface Stubs

These are local interface definitions that allow steward-protocol cartridges
to be developed against the VibeAgent protocol. When steward-protocol runs
within vibe-agency, it will use the actual vibe_core.kernel implementation.

This stub allows standalone development and type checking.
"""

# BLOCKER #2: Import from canonical Layer 1 protocols location
from .protocols import (
    VibeAgent,
    AgentManifest,
    Capability,
    VibeLedger,
    VibeScheduler,
    VibeKernel,
    ManifestRegistry,
)
from .scheduling import Task, TaskStatus
from .pulse import get_pulse_manager, PulseManager, PulseFrequency, SystemState
from .event_bus import get_event_bus, EventBus, Event, EventType, emit_event

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
