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
__genesis__ = "0x25d36ba1"  # GenesisByte


def __getattr__(name: str) -> object:
    """
    Lazy load KapilaService and NullKapila.
    NO MANUAL WIRING - auto-discovery needs these exports.
    """
    if name == "KapilaService":
        from vibe_core.services.kapila_service import KapilaService

        return KapilaService

    if name == "NullKapila":
        from vibe_core.protocols.mahajanas.kapila import NullKapila

        return NullKapila

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
