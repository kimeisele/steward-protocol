"""
LEDGER MODULE — Re-export Shim
===============================

SSOT: vibe_core.mahamantra.substrate.ledger
This file re-exports all symbols from the SSOT to maintain backward compatibility.
The SSOT version uses Seed constants (KSETRAJNA, QUALITIES) instead of hardcoded values.

DO NOT add new code here. Edit the SSOT instead.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 4
__genesis__ = "0xf9a27e38"  # GenesisByte: parampara % 37 == 0

# Re-export everything from SSOT
from vibe_core.mahamantra.substrate.ledger import (  # noqa: F401
    ArchiveAttachment,
    InMemoryLedger,
    SQLiteLedger,
)
