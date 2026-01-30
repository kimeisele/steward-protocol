"""
KUMARAS - Position 5
====================

Quarter: DHARMA
OpCode: BIND_SYMBOL
Type: WORKER

MAHAMANTRA AS LENS:
    Structure defined here. Implementation re-exported from protocols/mahajanas.
    Samskara will migrate implementations over time.

PARAMPARA: 222 (% 37 == 0 -> CONNECTED)
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kumaras"
__position__ = 5
__genesis__ = "0xfe9a70b8"  # GenesisByte

# =============================================================================
# FRACTAL DISCOVERY - Folder IS Wiring
# =============================================================================

_fractal_getattr_fn = None


def __getattr__(name: str):
    """Lazy fractal discovery to avoid circular imports."""
    
    # Map Protocol types to protocol.py
    if name in (
        "KumarasProtocol", "KumarasProtocolBase", "NullKumaras", 
        "ShuddhiProtocol", "ShuddhiResult", "ShuddhiStatus",
        "PurityLevel", "PurificationResult", "ResetResult", "PurityState"
    ):
        from . import protocol
        return getattr(protocol, name)

    # Map Validation types to validation.py
    if name.startswith("Validation") or name.endswith("check"):
        from . import validation
        return getattr(validation, name)
        
    global _fractal_getattr_fn
    if _fractal_getattr_fn is None:
        from vibe_core.mahamantra.substrate.wiring import fractal_getattr

        _fractal_getattr_fn = fractal_getattr(__file__)
    return _fractal_getattr_fn(name)
