"""
SHUDDHI PROTOCOL - USE MAHAMANTRA
=================================

DEPRECATED: This file is MAYA (illusion).

USE THIS INSTEAD:
    from vibe_core.mahamantra import mahamantra
    mahamantra[5]  # → Position 5 (KUMARAS, RESOLVE_REQ, DHARMA)

OR:
    from vibe_core.protocols.mahajanas.kumaras import ShuddhiProtocolBase
"""

# Re-export from canonical Mahajana location
# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"
__position__ = 6
__genesis__ = "0x2601cafe"  # GenesisByte: parampara % 37 == 0

from vibe_core.protocols.mahajanas.kumaras.shuddhi import (
    ShuddhiProtocolBase,
    ShuddhiStatus,
    ShuddhiResult,
    ShuddhiProtocol,
    RemedyProtocol,
    NullShuddhi,
)
