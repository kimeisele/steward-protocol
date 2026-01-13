"""
DEPRECATED: Use mahajana import.

NARADA OWNS (Position 7 - BROADCAST_EVENT):
    from vibe_core.protocols.mahajanas.narada.types.event_bus import EventBus, VibeEvent

This file is a BRIDGE for backward compatibility.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0xcac7584f"  # GenesisByte: parampara % 37 == 0

from vibe_core.protocols.mahajanas.narada.types.event_bus import *
