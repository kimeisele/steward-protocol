"""
MODE AFFINITY — Graph-distance classification (no hardcoded keywords)
=====================================================================

Anchor phrases derived from protocol:
    HolyName.name + get_trinity_function(first_position_of_that_name)

WordNet graph distance determines which mode a word belongs to.
Pure semantic routing — no keyword lists.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Dict, Optional

from vibe_core.mahamantra.substrate.seed import (
    HolyName,
    HARE_POSITIONS,
    KRISHNA_POSITIONS,
    RAMA_POSITIONS,
)
from vibe_core.mahamantra.substrate.language.mantra_grid import get_holyname_mode
from vibe_core.mahamantra.protocols.seed._extended import get_trinity_function


@lru_cache(maxsize=1)
def mode_anchor_phrases() -> Dict[str, str]:
    """Build mode anchor phrases from protocol-derived trinity functions.

    Returns: {"DHARMA": "hare carrier", "GENESIS": "krishna source", "KARMA": "rama deliverer"}
    """
    holyname_mode = get_holyname_mode()
    return {
        holyname_mode[HolyName.HARE]: f"{HolyName.HARE.name.lower()} {get_trinity_function(HARE_POSITIONS[0])}",
        holyname_mode[
            HolyName.KRISHNA
        ]: f"{HolyName.KRISHNA.name.lower()} {get_trinity_function(KRISHNA_POSITIONS[0])}",
        holyname_mode[HolyName.RAMA]: f"{HolyName.RAMA.name.lower()} {get_trinity_function(RAMA_POSITIONS[0])}",
    }


def classify_by_graph(packed_hex: str, anchors: Optional[Dict[str, str]] = None) -> Optional[str]:
    """Classify a Gita word into a mode by WordNet graph distance to anchors.

    Returns the mode with highest semantic_score, or None if all scores are 0.
    """
    if anchors is None:
        anchors = mode_anchor_phrases()

    try:
        from vibe_core.mahamantra.substrate.wordnet_bridge import semantic_score
    except Exception:
        return None

    best_mode: Optional[str] = None
    best_score = 0.0
    for mode, anchor in anchors.items():
        score = semantic_score(anchor, packed_hex)
        if score > best_score:
            best_score = score
            best_mode = mode

    return best_mode
