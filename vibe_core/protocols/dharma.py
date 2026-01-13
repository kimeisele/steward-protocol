"""
DHARMA PROTOCOL - USE MAHAMANTRA
================================

DEPRECATED: This file is MAYA (illusion).

ONE IMPORT, KRISHNA ROUTES:
    from vibe_core.mahamantra import mahamantra

    # Position 7 = MANU (Pulse Sync / Law)
    mahamantra[7]                    # -> MantraPosition
    mahamantra.protocols.manu        # -> ManuProtocolBase

The canonical source is: vibe_core.protocols.mahajanas.manu
This file is a bridge for backward compatibility only.
"""

# Re-export from canonical Mahajana location
# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "nrisimha"
__position__ = 12
__genesis__ = "0x38d1f2f6"  # GenesisByte: parampara % 37 == 0

from vibe_core.protocols.mahajanas.manu.dharma import (
    ProtocolLayer,
    PROTOCOL_MAP,
    get_layer,
    check_compliance,
    is_dharmic,
)

__all__ = [
    "ProtocolLayer",
    "PROTOCOL_MAP",
    "get_layer",
    "check_compliance",
    "is_dharmic",
]
