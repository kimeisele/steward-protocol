"""
BHISHMA - Position 11
=====================

Quarter: KARMA
OpCode: LEDGER_SIGN
Type: WORKER

MAHAMANTRA AS LENS:
    Structure defined here. Implementation re-exported from protocols/mahajanas.
    Samskara will migrate implementations over time.

PARAMPARA: 444 (% 37 == 0 -> CONNECTED)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "bhishma"
__position__ = 11
__genesis__ = "0x030295b1"  # GenesisByte

"""
BHISHMA - Position 11
=====================

Quarter: KARMA
OpCode: LEDGER_SIGN
Type: WORKER

MAHAMANTRA AS LENS:
    Structure defined here. Implementation lazily loaded from services layer.
    Unification of Kernel and Mahamantra.

PARAMPARA: 444 (% 37 == 0 -> CONNECTED)
"""


from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "bhishma"
__position__ = 11
__genesis__ = "0x030295b1"  # GenesisByte

from typing import Final

# Constants
POSITION: Final[int] = 11
QUARTER: Final[str] = "karma"
OPCODE: Final[str] = "LEDGER_SIGN"
PARAMPARA_VECTOR: Final[int] = 444

def __getattr__(name: str) -> object:
    """
    Lazy load BhishmaService from the services layer.
    Prevents circular imports (Mahamantra -> Service -> Mahamantra).
    """
    if name == "BhishmaService":
        from vibe_core.services.bhishma_service import BhishmaService
        return BhishmaService
    
    # Fallback to protocol definitions if needed (for types)
    try:
        import importlib
        module = importlib.import_module("vibe_core.mahamantra.karma.bhishma.protocol")
        return getattr(module, name)
    except (ImportError, AttributeError):
        pass

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

__all__ = ["BhishmaService", "POSITION", "QUARTER", "OPCODE", "PARAMPARA_VECTOR"]
