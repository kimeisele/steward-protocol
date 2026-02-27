"""
GENESIS - Hare Krishna Hare Krishna
===================================

Quarter 0: Positionen 0-3
Sampradaya: Brahma
Funktion: Schöpfung / System Startup

"tene brahma hrda ya adi-kavaye"
"In the beginning, He imparted Vedic knowledge unto Brahma through the heart."
— Srimad Bhagavatam 1.1.1

POSITIONEN:
    0 - PRITHU (HEAD/Avatara): SYS_WAKE - System erwachen
    1 - BRAHMA: LOAD_ROOT - Wurzel laden
    2 - NARADA: ALLOC_MEM - Speicher allozieren
    3 - SHAMBHU: INIT_THREAD - Thread initialisieren

LEVEL: +5 (AVATARAS) für HEAD, +12 (MAHAJANAS) für Workers
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 4
__genesis__ = "0x0210f785"  # GenesisByte: parampara % 37 == 0

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

QUARTER: Final[Quarter] = Quarter.GENESIS
SAMPRADAYA: Final[Sampradaya] = Sampradaya.BRAHMA
SOUNDS: Final[str] = "Hare Krishna Hare Krishna"
POSITIONS: Final[tuple] = (0, 1, 2, 3)

# =============================================================================
# POSITION MAPPING
# =============================================================================

# Position 0: HEAD (Avatara)
HEAD: Final[Avatara] = Avatara.PRITHU
HEAD_POSITION: Final[int] = 0
HEAD_OPCODE: Final[str] = "SYS_WAKE"
HEAD_LEVEL: Final[ProtocolLevel] = ProtocolLevel.AVATARAS

# Position 1-3: Workers (Mahajanas)
WORKERS: Final[tuple] = (
    (1, Mahajana.BRAHMA, "LOAD_ROOT"),
    (2, Mahajana.NARADA, "ALLOC_MEM"),
    (3, Mahajana.SHAMBHU, "INIT_THREAD"),
)
WORKER_LEVEL: Final[ProtocolLevel] = ProtocolLevel.MAHAJANAS

# =============================================================================
# OPCODES
# =============================================================================


class GenesisOpCode:
    """Die OpCodes des Genesis Quarters."""

    SYS_WAKE = 0  # Prithu (HEAD)
    LOAD_ROOT = 1  # Brahma
    ALLOC_MEM = 2  # Narada
    INIT_THREAD = 3  # Shambhu


# =============================================================================
# FRACTAL DISCOVERY - Folder IS Wiring
# =============================================================================
# mahamantra.genesis.brahma → auto-discovered from genesis/brahma/ folder
# No manual imports. Drop a folder, it works.

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
    "GenesisOpCode",
]
