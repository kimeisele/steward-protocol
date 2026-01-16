"""
FRACTAL TYPES - Die Fraktal-Hierarchie Ebenen
=============================================

"yathā nadīnāṁ bahavo 'mbu-vegāḥ
samudram evābhimukhā dravanti"

"As the many waves flow into the ocean,
so do all levels flow into the One."
— Bhagavad Gita 11.28

FRACTAL PRINCIPLE:
Zoom in → 37
Zoom out → 37
The pattern repeats at ALL levels.

SSOT: Diese Datei ist die Quelle für FractalLevel.
      protocols/substrate/mantra/routing.py IMPORTIERT von hier.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0x3a9e102f"  # GenesisByte: parampara % 37 == 0

from enum import IntEnum
from typing import Final

from vibe_core.mahamantra.substrate.seed import PARAMPARA


class FractalLevel(IntEnum):
    """
    Die Hierarchie-Ebenen des fraktalen Systems.
    
    COMPUTATIONAL MAPPING:
    - VARNA = Bit (smallest addressable unit)
    - AKSARA = Byte (pronounceable unit)
    - PADA = Word (semantic unit, 16 per mantra)
    - VAKYA = Instruction (16 words = 16 opcodes)
    - MALA = Round (108 mantras)
    - SADHANA = Session (16 rounds minimum)
    """
    VARNA = 0    # Letter (smallest)
    AKSARA = 1   # Syllable
    PADA = 2     # Word
    VAKYA = 3    # Sentence/Mantra (16 words)
    MALA = 4     # Round (108 mantras)
    SADHANA = 5  # Session (16 rounds)


# =============================================================================
# FRACTAL DIMENSIONS
# =============================================================================

DIMENSIONS: Final[dict[FractalLevel, int]] = {
    FractalLevel.VARNA: 50,      # ~50 varnas in Sanskrit alphabet
    FractalLevel.AKSARA: 6,      # 6 unique syllables in Mahamantra
    FractalLevel.PADA: 3,        # 3 unique words (Hare, Krishna, Rama)
    FractalLevel.VAKYA: 16,      # 16 words per mantra
    FractalLevel.MALA: 108,      # 108 mantras per round
    FractalLevel.SADHANA: 16,    # 16 rounds minimum
}

# Total counts in full Mahamantra
MAHAMANTRA_COUNTS: Final[dict[FractalLevel, int]] = {
    FractalLevel.PADA: 16,       # 16 words
    FractalLevel.AKSARA: 32,     # ~2 syllables per word
    FractalLevel.VARNA: 64,      # ~2 letters per syllable
}

# The 37 Formula at each level
FRACTAL_BASE: Final[int] = PARAMPARA  # 37


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "FractalLevel",
    "DIMENSIONS",
    "MAHAMANTRA_COUNTS",
    "FRACTAL_BASE",
]
