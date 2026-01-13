"""
DEPRECATED: Use mahajana import.

MANU OWNS (Position 5 - SYNC_PULSE):
    from vibe_core.protocols.mahajanas.manu.types.pulse import PulseManager, get_pulse_manager

This file is a BRIDGE for backward compatibility.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0xfce97926"  # GenesisByte: parampara % 37 == 0

from vibe_core.protocols.mahajanas.manu.types.pulse import *
