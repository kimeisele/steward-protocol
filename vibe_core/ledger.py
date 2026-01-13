"""
DEPRECATED: Use mahajana import.

VYASA OWNS (Position 13 - COMPILE_RECORD):
    from vibe_core.protocols.mahajanas.vyasa.types.ledger import SQLiteLedger, InMemoryLedger

This file is a BRIDGE for backward compatibility.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0x2a93739c"  # GenesisByte: parampara % 37 == 0

from vibe_core.protocols.mahajanas.vyasa.types.ledger import *
