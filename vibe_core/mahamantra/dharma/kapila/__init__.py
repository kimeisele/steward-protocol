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
__genesis__ = "0x25d36ba1"  # GenesisByte: parampara % 37 == 0

# Backward-compat constants
from typing import Final

POSITION: Final[int] = 6
QUARTER: Final[str] = "dharma"
OPCODE: Final[str] = "TYPE_CHECK"
PARAMPARA_VECTOR: Final[int] = 259

# =============================================================================
# EXPORTS FOR RESONANCE (Auto-Wiring)
# =============================================================================
try:
    from vibe_core.protocols.mahajanas.kapila import on_event, __listening_for__
except ImportError:
    # Fallback if protocol not available yet
    on_event = None
    __listening_for__ = []


def execute(input_text: str, context: dict = None) -> dict:
    """KAPILA EXECUTION - Type Check (Position 6)"""
    return {
        "success": True,
        "mahajana": __mahajana__,
        "position": __position__,
        "quarter": QUARTER,
        "opcode": OPCODE,
        "input": input_text,
    }


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
