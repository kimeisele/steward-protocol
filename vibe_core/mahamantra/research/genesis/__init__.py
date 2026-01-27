"""
GENESIS - Positions 1-4: Hare Krishna Hare Krishna
==================================================

The BEGINNING. Seed axioms, foundational constants, shabda (sound) foundations.

From _seed.py:
    QUARTER_SUM_GENESIS = 1 + 2 + 3 + 4 = 10 = TEN

Contents:
    - Axiom re-exports from protocols/_seed.py
    - Shabda (sound) translation foundations
    - Phoneme mappings
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0xa45d8a78"  # GenesisByte: parampara % 37 == 0

from vibe_core.mahamantra.protocols._seed import (
    HALVES,
    HARE_COUNT,
    KRISHNA_COUNT,
    KSETRAJNA,
    PANCHA,
    # Primary derivations
    QUARTERS,
    RAMA_COUNT,
    TRINITY,
    # The 7 Axioms
    WORDS,
)

__all__ = [
    "WORDS",
    "TRINITY",
    "HARE_COUNT",
    "KRISHNA_COUNT",
    "RAMA_COUNT",
    "PANCHA",
    "HALVES",
    "QUARTERS",
    "KSETRAJNA",
]
