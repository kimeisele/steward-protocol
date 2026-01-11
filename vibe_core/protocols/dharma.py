"""
DHARMA PROTOCOL - MIGRATED TO MAHAJANA OWNERSHIP
================================================

OWNER: Mahajana.MANU (The Lawgiver)
NEW LOCATION: vibe_core.protocols.mahajanas.manu.dharma

This file re-exports from the canonical location for backwards compatibility.
All new code should import from:
    from vibe_core.protocols.mahajanas.manu import ProtocolLayer, get_layer

"Manu is the LAWGIVER who defines WHAT Dharma IS.
 This is not abstract 'philosophy' - Manu the PERSON established these laws."
"""

# Re-export from canonical Mahajana location
from vibe_core.protocols.mahajanas.manu.dharma import (
    ProtocolLayer,
    PROTOCOL_MAP,
    get_layer,
    check_compliance,
    is_dharmic,
    OWNER,
    LOTUS_POSITION,
    LOTUS_QUARTER,
    OWNED_OPCODES,
)
