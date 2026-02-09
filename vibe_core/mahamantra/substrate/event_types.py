"""
EVENT TYPES — Single Source of Truth
=====================================

Pure enum module with ZERO internal imports. This is the leaf node
of the dependency graph — importable by protocols, substrate, services,
and anything else without creating circular imports.

RULE: If you add a new EventType, you add it HERE. Nowhere else.
"""

from enum import Enum


class EventType(str, Enum):
    """Standard event types emitted by agents.

    This is the ONE AND ONLY EventType enum in the entire codebase.
    """

    # Core lifecycle events
    THOUGHT = "THOUGHT"  # Planning/reasoning
    ACTION = "ACTION"  # Executing task
    ERROR = "ERROR"  # Failure
    COMPLETED = "COMPLETED"  # Task completion

    # System events
    VIOLATION = "VIOLATION"  # Constitution breach
    MERCY = "MERCY"  # Supreme Court intervention
    PRAYER_RECEIVED = "PRAYER_RECEIVED"  # Request received
    CRITICAL_INTERRUPT = "CRITICAL_INTERRUPT"  # Emergency bypass (Gajendra)

    # Syscall events (OPUS-031 Layer 2)
    SYSCALL_EXECUTED = "SYSCALL_EXECUTED"  # Syscall completed (for experience replay)

    # OPUS-211: Pramana (Feedback Loop)
    INTENT_EXECUTED = "INTENT_EXECUTED"  # Action completed with verification proof

    # Agent-specific events
    BROADCAST = "BROADCAST"  # Content published
    PROPOSAL_CREATED = "PROPOSAL_CREATED"  # New proposal
    VOTE_CAST = "VOTE_CAST"  # Vote recorded
    AUDIT_CHECK = "AUDIT_CHECK"  # Invariant verified

    # Venu events (NaradaBridge — flute rhythm → agent events)
    PHASE_TRANSITION = "PHASE_TRANSITION"  # Quarter change (genesis→dharma→karma→moksha)

    # Circuit trigger events (NOT emitted from kernel - see OPUS-073)
    KERNEL_TICK = "KERNEL_TICK"  # For circuits, emitted by plugins if needed
    HOURLY_PULSE = "HOURLY_PULSE"  # For MANAS, emitted by heartbeat.py


class EventColor(str, Enum):
    """ANSI color codes for terminal visualization."""

    BLUE = "34"  # THOUGHT
    GREEN = "32"  # ACTION
    RED = "31"  # ERROR / CRITICAL_INTERRUPT
    PURPLE = "35"  # VIOLATION
    GOLD = "33"  # MERCY
    CYAN = "36"  # PRAYER_RECEIVED
    YELLOW = "33"  # AUDIT_CHECK
    WHITE = "37"  # COMPLETED


EVENT_COLOR_MAP = {
    EventType.THOUGHT: EventColor.BLUE,
    EventType.ACTION: EventColor.GREEN,
    EventType.ERROR: EventColor.RED,
    EventType.VIOLATION: EventColor.PURPLE,
    EventType.MERCY: EventColor.GOLD,
    EventType.PRAYER_RECEIVED: EventColor.CYAN,
    EventType.CRITICAL_INTERRUPT: EventColor.RED,
    EventType.BROADCAST: EventColor.GREEN,
    EventType.COMPLETED: EventColor.WHITE,
    EventType.AUDIT_CHECK: EventColor.YELLOW,
    EventType.SYSCALL_EXECUTED: EventColor.CYAN,
}


__all__ = [
    "EventType",
    "EventColor",
    "EVENT_COLOR_MAP",
]
