"""
KAPILA - Position 6
===================

Quarter: DHARMA
OpCode: TYPE_CHECK
Type: WORKER

MAHAMANTRA AS LENS:
    Structure defined here. Implementation re-exported from protocols/mahajanas.
    Samskara will migrate implementations over time.

PARAMPARA: 259 (% 37 == 0 -> CONNECTED)
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"
__position__ = 6
__genesis__ = "0x348ce48e2986757649ef37ccd73ad6b0cad14a59f72a1733f9300f8d6673d28f"  # GenesisByte: parampara % 37 == 0

# =============================================================================
# FRACTAL DISCOVERY - Folder IS Wiring
# =============================================================================

_fractal_getattr_fn = None


def __getattr__(name: str):
    """Lazy fractal discovery to avoid circular imports."""
    # Explicit service loading (ExecutableMixin pattern)
    if name == "KapilaService":
        from vibe_core.protocols.mahajanas.kapila.service import KapilaService
        return KapilaService
    
    # Fallback to fractal discovery
    global _fractal_getattr_fn
    if _fractal_getattr_fn is None:
        from vibe_core.mahamantra.substrate.wiring import fractal_getattr

        _fractal_getattr_fn = fractal_getattr(__file__)
    return _fractal_getattr_fn(name)
