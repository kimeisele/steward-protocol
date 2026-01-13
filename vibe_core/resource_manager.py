"""
DEPRECATED: Use mahajana import.

BALI OWNS (Position 10 - ALLOC_RESOURCE):
    from vibe_core.protocols.mahajanas.bali.types.resource_manager import ResourceManager

This file is a BRIDGE for backward compatibility.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0x8bf8f877"  # GenesisByte: parampara % 37 == 0

from vibe_core.protocols.mahajanas.bali.types.resource_manager import *
