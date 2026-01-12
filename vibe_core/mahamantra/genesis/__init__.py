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
    SYS_WAKE = 0      # Prithu (HEAD)
    LOAD_ROOT = 1     # Brahma
    ALLOC_MEM = 2     # Narada
    INIT_THREAD = 3   # Shambhu


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
