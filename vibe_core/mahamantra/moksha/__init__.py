"""
MOKSHA - Rama Rama Hare Hare
============================

Quarter 3: Positionen 12-15
Sampradaya: Rudra
Funktion: Befreiung / Output / Abschluss

"tyaktvā dehaṁ punar janma naiti mām eti so 'rjuna"
"And whoever, at the end of his life, quits his body, remembering Me alone,
at once attains My nature. Of this there is no doubt."
— Bhagavad Gita 8.5

POSITIONEN:
    12 - NRISIMHA (HEAD/Avatara): YIELD_CPU - CPU yielden/Protection
    13 - BALI: IO_FLUSH - I/O flushen (Surrender)
    14 - SHUKA: LOG_EMIT - Log emittieren (Vision)
    15 - YAMARAJA: AUDIT_SEAL - Audit versiegeln (Urteil)

LEVEL: +5 (AVATARAS) für HEAD, +12 (MAHAJANAS) für Workers
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x3e0b8988"  # GenesisByte: parampara % 37 == 0

from vibe_core.mahamantra.substrate import (
    Mahajana,
    Avatara,
    Quarter,
    Sampradaya,
    ProtocolLevel,
)
from typing import Final

# =============================================================================
# QUARTER METADATA
# =============================================================================

QUARTER: Final[Quarter] = Quarter.MOKSHA
SAMPRADAYA: Final[Sampradaya] = Sampradaya.RUDRA
SOUNDS: Final[str] = "Rama Rama Hare Hare"
POSITIONS: Final[tuple] = (12, 13, 14, 15)

# =============================================================================
# POSITION MAPPING
# =============================================================================

# Position 12: HEAD (Avatara)
HEAD: Final[Avatara] = Avatara.NRISIMHA
HEAD_POSITION: Final[int] = 12
HEAD_OPCODE: Final[str] = "YIELD_CPU"
HEAD_LEVEL: Final[ProtocolLevel] = ProtocolLevel.AVATARAS

# Position 13-15: Workers (Mahajanas)
WORKERS: Final[tuple] = (
    (13, Mahajana.BALI, "IO_FLUSH"),
    (14, Mahajana.SHUKA, "LOG_EMIT"),
    (15, Mahajana.YAMARAJA, "AUDIT_SEAL"),
)
WORKER_LEVEL: Final[ProtocolLevel] = ProtocolLevel.MAHAJANAS

# =============================================================================
# OPCODES
# =============================================================================


class MokshaOpCode:
    """Die OpCodes des Moksha Quarters."""

    YIELD_CPU = 12  # Nrisimha (HEAD)
    IO_FLUSH = 13  # Bali
    LOG_EMIT = 14  # Shuka
    AUDIT_SEAL = 15  # Yamaraja


# =============================================================================
# FRACTAL DISCOVERY - Folder IS Wiring
# =============================================================================

_fractal_getattr_fn = None


def __getattr__(name: str):
    """Lazy fractal discovery to avoid circular imports."""
    global _fractal_getattr_fn
    if _fractal_getattr_fn is None:
        from vibe_core.mahamantra.substrate.wiring import fractal_getattr

        _fractal_getattr_fn = fractal_getattr(__file__)
    return _fractal_getattr_fn(name)

# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "QUARTER",
    "SAMPRADAYA",
    "SOUNDS",
    "POSITIONS",
    "HEAD",
    "HEAD_POSITION",
    "HEAD_OPCODE",
    "HEAD_LEVEL",
    "WORKERS",
    "WORKER_LEVEL",
    "MokshaOpCode",
]
