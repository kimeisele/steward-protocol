"""
DHARMA - Krishna Krishna Hare Hare
==================================

Quarter 1: Positions 4-7
Sampradaya: Brahma
Function: Computation / Scientific Analysis

"dharmaṁ tu sākṣād bhagavat-praṇītam"
"Dharma is directly enacted by the Supreme Lord."
— Srimad Bhagavatam 6.3.19

POSITIONS:
    4 - PRITHU (HEAD/Avatara): ANALYZE - Scientific analysis
    5 - KUMARAS: CLASSIFY - Pattern recognition
    6 - KAPILA: COMPUTE - Core computation
    7 - MANU: VALIDATE - Verification

LEVEL: +5 (AVATARAS) for HEAD, +12 (MAHAJANAS) for Workers
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 4
__genesis__ = "0xf9a40bd3"  # GenesisByte: parampara % 37 == 0

from .engine import DharmaEngine, dharma

# =============================================================================
# FRACTAL DISCOVERY - Folder IS Wiring
# =============================================================================
# mahamantra.dharma.prithu → auto-discovered from dharma/prithu/ folder
# No manual imports. Drop a folder, it works.

_fractal_getattr_fn = None


def __getattr__(name: str):
    """Lazy fractal discovery to avoid circular imports."""
    global _fractal_getattr_fn
    if _fractal_getattr_fn is None:
        from vibe_core.mahamantra.substrate.wiring import fractal_getattr

        _fractal_getattr_fn = fractal_getattr(__file__)
    return _fractal_getattr_fn(name)
