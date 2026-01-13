"""
NRISIMHA Types - Position 12 (MOKSHA Quarter HEAD, CACHE_STATE)
===============================================================

NRISIMHA - The Half-Man Half-Lion Protector.
Types for security, protection, and threat handling.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "nrisimha"
__position__ = 12
__genesis__ = "0x2ba4a873"  # GenesisByte: parampara % 37 == 0

from vibe_core.protocols.mahajanas.nrisimha.types.narasimha import (
    ThreatLevel,
    ThreatIndicator,
    NarasimhaProtocol,
    get_narasimha,
    activate_emergency_protocol,
)

from vibe_core.protocols.mahajanas.nrisimha.types.security import (
    VajraGuarded,
    VajraViolation,
    IntentStatus,
    SecurityIntent,
    SecurityIntentManager,
)

__all__ = [
    # narasimha.py
    "ThreatLevel",
    "ThreatIndicator",
    "NarasimhaProtocol",
    "get_narasimha",
    "activate_emergency_protocol",
    # security.py
    "VajraGuarded",
    "VajraViolation",
    "IntentStatus",
    "SecurityIntent",
    "SecurityIntentManager",
]
