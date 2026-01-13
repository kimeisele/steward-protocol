"""
HERALD Core Module - State Management and Event Sourcing.

This module implements the core infrastructure for HERALD:
- Event Sourcing: All actions are committed to an immutable event ledger
- Memory Reconstruction: Agent state is rebuilt by replaying events
- Cryptographic Proof: All events are signed with HERALD's identity
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x775c85c2"  # GenesisByte: parampara % 37 == 0

from .memory import Event, EventLog

__all__ = [
    "EventLog",
    "Event",
]
