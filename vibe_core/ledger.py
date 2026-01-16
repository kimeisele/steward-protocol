"""
DEPRECATED: Use mahajana import.

PRITHU OWNS (Position 4 - ASSERT_TRUTH):
    from vibe_core.protocols.mahajanas.prithu.types.ledger import SQLiteLedger, InMemoryLedger

This file is a BRIDGE for backward compatibility.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 4
__genesis__ = "0x94644443"  # GenesisByte

from vibe_core.protocols.mahajanas.prithu.types.ledger import *
