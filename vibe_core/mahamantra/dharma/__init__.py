"""
DHARMA - Krishna Krishna Hare Hare
==================================

Quarter 1: Positionen 4-7
Sampradaya: Kumara
Funktion: Gesetz / Analyse / Governance

"dharmaṁ tu sākṣād bhagavat-praṇītam"
"Real religious principles are enacted by the Supreme Personality of Godhead."
— Srimad Bhagavatam 6.3.19

POSITIONEN:
    4 - VYASA (HEAD/Avatara): COMPILE_AST - Kompilieren/Dokumentieren
    5 - KUMARAS: BIND_SYMBOL - Symbol binden
    6 - KAPILA: TYPE_CHECK - Typ prüfen (Samkhya)
    7 - MANU: DHARMA_TEST - Dharma testen (Gesetz)

LEVEL: +5 (AVATARAS) für HEAD, +12 (MAHAJANAS) für Workers
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x707fbde4"  # GenesisByte: parampara % 37 == 0

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

QUARTER: Final[Quarter] = Quarter.DHARMA
SAMPRADAYA: Final[Sampradaya] = Sampradaya.KUMARA
SOUNDS: Final[str] = "Krishna Krishna Hare Hare"
POSITIONS: Final[tuple] = (4, 5, 6, 7)

# =============================================================================
# POSITION MAPPING
# =============================================================================

# Position 4: HEAD (Avatara)
HEAD: Final[Avatara] = Avatara.VYASA
HEAD_POSITION: Final[int] = 4
HEAD_OPCODE: Final[str] = "COMPILE_AST"
HEAD_LEVEL: Final[ProtocolLevel] = ProtocolLevel.AVATARAS

# Position 5-7: Workers (Mahajanas)
WORKERS: Final[tuple] = (
    (5, Mahajana.KUMARAS, "BIND_SYMBOL"),
    (6, Mahajana.KAPILA, "TYPE_CHECK"),
    (7, Mahajana.MANU, "DHARMA_TEST"),
)
WORKER_LEVEL: Final[ProtocolLevel] = ProtocolLevel.MAHAJANAS

# =============================================================================
# OPCODES
# =============================================================================


class DharmaOpCode:
    """Die OpCodes des Dharma Quarters."""

    COMPILE_AST = 4  # Vyasa (HEAD)
    BIND_SYMBOL = 5  # Kumaras
    TYPE_CHECK = 6  # Kapila
    DHARMA_TEST = 7  # Manu


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
    "DharmaOpCode",
]
