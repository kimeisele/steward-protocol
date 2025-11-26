"""
Vibe Core Interface Stubs

These are local interface definitions that allow steward-protocol cartridges
to be developed against the VibeAgent protocol. When steward-protocol runs
within vibe-agency, it will use the actual vibe_core.kernel implementation.

This stub allows standalone development and type checking.
"""

from .agent_protocol import VibeAgent, AgentManifest, Capability
from .scheduling import Task, TaskStatus
from .kernel import VibeKernel
from .pulse import get_pulse_manager, PulseManager, PulseFrequency, SystemState
from .event_bus import get_event_bus, EventBus, Event, EventType, emit_event

__all__ = [
    "VibeAgent",
    "AgentManifest",
    "Capability",
    "Task",
    "TaskStatus",
    "VibeKernel",
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
