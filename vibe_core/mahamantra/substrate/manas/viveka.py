"""
VIVEKA — Priority Scoring from BuddhiResult
=============================================

Sanskrit: Viveka = Discrimination, Discernment

Scores priority (0-100) from BuddhiResult cognitive fields:
- prana/COSMIC_FRAME → 0-60 base energy score
- integrity → 0-20 membrane health bonus
- function → 5-20 trinity function bonus (BRAHMA highest)

Also checks viability: is the cell alive?
"""

from __future__ import annotations

from vibe_core.mahamantra.protocols._buddhi import BuddhiResult
from vibe_core.mahamantra.protocols._seed import COSMIC_FRAME

# Function bonus map — BRAHMA (creation) gets highest priority
_FUNCTION_BONUS = {
    "BRAHMA": 20,
    "VISHNU": 10,
    "SHIVA": 5,
}

# Max scores per dimension
_PRANA_MAX = 60
_INTEGRITY_MAX = 20


def score_priority(cognition: BuddhiResult) -> float:
    """Score priority 0-100 from BuddhiResult fields.

    Components:
        prana_score (0-60): Energy normalized against COSMIC_FRAME
        integrity_score (0-20): Membrane integrity
        function_score (5-20): Trinity function bonus

    Returns:
        Priority score clamped to 0-100.
    """
    # Prana: 0-60 based on energy relative to cosmic frame
    prana_ratio = min(cognition.prana / COSMIC_FRAME, 1.0) if COSMIC_FRAME > 0 else 0.0
    prana_score = prana_ratio * _PRANA_MAX

    # Integrity: 0-20 from membrane health
    integrity_score = cognition.integrity * _INTEGRITY_MAX

    # Function: 5-20 from trinity role
    function_score = _FUNCTION_BONUS.get(cognition.function, 5)

    return min(prana_score + integrity_score + function_score, 100.0)


def is_viable(cognition: BuddhiResult) -> bool:
    """Check if the cognition represents a viable (alive) cell."""
    return cognition.is_alive
