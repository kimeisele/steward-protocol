"""
DEPRECATED: Use mahajana import.

JANAKA OWNS (Position 9 - YIELD_CYCLE):
    from vibe_core.protocols.mahajanas.janaka.types.prana import PranaConfig, load_config

This file is a BRIDGE for backward compatibility.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0x25b81954"  # GenesisByte: parampara % 37 == 0

from vibe_core.protocols.mahajanas.janaka.types.prana import *
