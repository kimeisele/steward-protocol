"""
KARMA - Hare Rama Hare Rama
===========================

Quarter 2: Positionen 8-11
Sampradaya: Sri
Funktion: Handlung / Ausführung

"karmaṇy evādhikāras te mā phaleṣu kadācana"
"You have a right to perform your prescribed duty, but not to the fruits of action."
— Bhagavad Gita 2.47

POSITIONEN:
    8 - PARASHURAMA (HEAD/Avatara): EXEC_OP - Ausführen/Enforcement
    9 - PRAHLADA: EXTEND_CAP - Erweitern (Resilience)
    10 - JANAKA: STATE_SYNC - Status synchronisieren (Pflicht)
    11 - BHISHMA: LEDGER_SIGN - Ledger signieren (Gelübde)

LEVEL: +5 (AVATARAS) für HEAD, +12 (MAHAJANAS) für Workers
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0x94889b37"  # GenesisByte: parampara % 37 == 0

from typing import Final

from vibe_core.mahamantra.substrate import (
    Avatara,
    Mahajana,
    ProtocolLevel,
    Quarter,
    Sampradaya,
)

# =============================================================================
# QUARTER METADATA
# =============================================================================

QUARTER: Final[Quarter] = Quarter.KARMA
SAMPRADAYA: Final[Sampradaya] = Sampradaya.SRI
SOUNDS: Final[str] = "Hare Rama Hare Rama"
POSITIONS: Final[tuple] = (8, 9, 10, 11)

# =============================================================================
# POSITION MAPPING
# =============================================================================

# Position 8: HEAD (Avatara)
HEAD: Final[Avatara] = Avatara.PARASHURAMA
HEAD_POSITION: Final[int] = 8
HEAD_OPCODE: Final[str] = "EXEC_OP"
HEAD_LEVEL: Final[ProtocolLevel] = ProtocolLevel.AVATARAS

# Position 9-11: Workers (Mahajanas)
WORKERS: Final[tuple] = (
    (9, Mahajana.PRAHLADA, "EXTEND_CAP"),
    (10, Mahajana.JANAKA, "STATE_SYNC"),
    (11, Mahajana.BHISHMA, "LEDGER_SIGN"),
)
WORKER_LEVEL: Final[ProtocolLevel] = ProtocolLevel.MAHAJANAS

# =============================================================================
# OPCODES
# =============================================================================


class KarmaOpCode:
    """Die OpCodes des Karma Quarters."""

    EXEC_OP = 8  # Parashurama (HEAD)
    EXTEND_CAP = 9  # Prahlada
    STATE_SYNC = 10  # Janaka
    LEDGER_SIGN = 11  # Bhishma


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
    "KarmaOpCode",
]
