"""
SUBSTRATE PROTOCOL - Layer 0 (Legacy Facade)
===========================================

"Yatha seed tatha fruit" - As the seed, so the fruit.
This file is a FACADE for the V2 SSOT.
It exists only for backward compatibility.

SSOT LOCATION: vibe_core/mahamantra/substrate/byte.py
"""

# =============================================================================
# SSOT REDIRECTION - NO LOCAL TRUTH
# =============================================================================
# "Wer am Seed vorbei importiert, stirbt." - MAHAPROMPT.md
# We import the V2 definitions and expose them as V1.

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 4
__genesis__ = "0x23129dff"  # GenesisByte: parampara % 37 == 0

from vibe_core.mahamantra.substrate.byte import (
    HolyName,
    MantraBit,
    MantraByte,
    GenesisByte,
    MANTRA_SEQUENCE,
    MAHAMANTRA_DIMENSION,
    LILA_CYCLES,
    LILA_LIMIT,
)

# MantraTrit is DEAD.
# Any legacy code referencing it will fail, as promised in the Audit.
# "Performance frisst" no more.

__all__ = [
    "HolyName",
    "MantraBit",
    "MantraByte",
    "GenesisByte",
    "MANTRA_SEQUENCE",
    "MAHAMANTRA_DIMENSION",
    "LILA_CYCLES",
    "LILA_LIMIT",
]
