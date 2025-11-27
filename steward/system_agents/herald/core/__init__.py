"""
HERALD Core Module - State Management and Event Sourcing.

This module implements the core infrastructure for HERALD:
- Event Sourcing: All actions are committed to an immutable event ledger
- Memory Reconstruction: Agent state is rebuilt by replaying events
- Cryptographic Proof: All events are signed with HERALD's identity
"""

from .memory import EventLog, Event

__all__ = [
    "EventLog",
    "Event",
]
