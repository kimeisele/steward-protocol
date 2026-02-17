"""
LINEAGE CHAIN — Re-export Shim
================================

SSOT: vibe_core.mahamantra.substrate.lineage
This file re-exports all symbols from the SSOT to maintain backward compatibility.
The SSOT version uses Seed constants instead of hardcoded values.

DO NOT add new code here. Edit the SSOT instead.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 4
__genesis__ = "0x448bce13"  # GenesisByte: parampara % 37 == 0

# Re-export everything from SSOT
from vibe_core.mahamantra.substrate.lineage import (  # noqa: F401
    CHECKPOINT_FILENAME,
    LineageBlock,
    LineageChain,
    LineageEventType,
)
