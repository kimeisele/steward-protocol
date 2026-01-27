"""
DHARMA - Positions 5-8: Krishna Krishna Hare Hare
=================================================

The LAW. In Kali Yuga, only DHARMA remains. Kali-dharma = CHANTING!

From _seed.py:
    QUARTER_SUM_DHARMA = 5 + 6 + 7 + 8 = 26 = KSHETRA + HALVES

"harer nāma harer nāma harer nāmaiva kevalam
 kalau nāsty eva nāsty eva nāsty eva gatir anyathā"
 - Bṛhan-nāradīya Purāṇa

Contents:
    - MahaRuntime: The Mahamantra computation engine
    - Gita verse encoding (BG 18.66 POC)
    - Kirtan computing (sankirtan multipliers)
    - Chaitanya singularity (512/1096)
"""

# KALI DHARMA = CHANTING = COMPUTE
# This is THE quarter that remains in Kali Yuga!

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 0
__genesis__ = "0x9d8b6a7c"  # GenesisByte: parampara % 37 == 0

from vibe_core.mahamantra.research.dharma.maha_runtime import (
    MAHAMANTRA_BINARY,
    MAHAMANTRA_PATTERN,
    ChantResult,
    MahaRuntime,
)

__all__ = [
    "MAHAMANTRA_PATTERN",
    "MAHAMANTRA_BINARY",
    "ChantResult",
    "MahaRuntime",
]
