"""
EVENT PROTOCOL BRIDGE - Level -1 (LOTUS/ONTOS)
===============================================

DEPRECATED: Use mahajana import.

This module is a DYNAMIC BRIDGE.
Position 2 (NARADA - Communication/Events) owns the Event Bus.

ONE IMPORT:
    from vibe_core.protocols.mahajanas.narada.events import *

Or via this bridge (for backward compatibility):
    from vibe_core.protocols.event import EventBusProtocol, Event

This file is a BRIDGE for backward compatibility.
The TRUTH lives in: vibe_core/protocols/mahajanas/narada/events.py

ARCHITECTURE:
    vibe_core.protocols.event (THIS BRIDGE)
        ↓
    vibe_core.protocols.mahajanas.narada.events (THE TRUTH)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x2967d08a"  # GenesisByte (Position 2 - Narada)

# =============================================================================
# RE-EXPORT FROM NARADA (THE TRUTH)
# =============================================================================

from vibe_core.protocols.mahajanas.narada.events import (
    # Protocol
    EventBusProtocol,
    EventBusState,
    EventBusStats,
    # Types
    EventType,
    SubscriberInfo,
    # Functions
    emit_event,
)

# Import Event from event_bus types if available
try:
    from vibe_core.protocols.mahajanas.narada.types.event_bus import Event
except ImportError:
    # Define minimal Event for compatibility if not in types
    from dataclasses import dataclass
    from datetime import datetime
    from typing import Any, Dict, Optional

    @dataclass
    class Event:
        """Legacy Event class for backward compatibility."""

        event_type: str
        source: str
        timestamp: datetime
        details: Optional[Dict[str, Any]] = None


__all__ = [
    "EventBusProtocol",
    "Event",
    "EventType",
    "EventBusStats",
    "EventBusState",
    "SubscriberInfo",
    "emit_event",
]
