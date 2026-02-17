"""
NAVABHAKTI INSTRUCTION SET — The 12 VM Operations
===================================================

"nava-vidha bhakti" — Nine forms of devotion, extended to 12 (MAHAJANA_COUNT).

Each instruction maps to a VAMSI address at PARAMPARA(37) stride:
    addr = PARAMPARA * (index + KSETRAJNA)

Collision-free with THE_FLUTE_CYCLE (verified: 0 overlaps).

USAGE:
    from vibe_core.mahamantra.protocols._navabhakti import CYCLE, DISPATCH
    for op in CYCLE:
        DISPATCH[op](lotus, ctx)
"""

from __future__ import annotations

from enum import IntEnum
from typing import Callable, Dict, Final, Tuple

from vibe_core.mahamantra.protocols._seed import (
    KSETRAJNA,
    MAHAJANA_COUNT,
    PARAMPARA,
)


class NavaBhaktiOp(IntEnum):
    """12 VM instructions = MAHAJANA_COUNT."""
    SRAVANAM = 0
    NAMA = 1
    KIRTANAM = 2
    PADA_SEVANAM = 3
    ARCANAM = 4
    SMARANAM = 5
    VANDANAM = 6
    DASYAM = 7
    SAKHYAM = 8
    KIRTAN = 9
    YAJNA = 10
    ATMA_NIVEDANAM = 11


assert len(NavaBhaktiOp) == MAHAJANA_COUNT

# Gate index per instruction (TattvaGate.value)
GATE_INDEX: Final[Tuple[int, ...]] = (
    0, 0, 0,    # PARSE:    SRAVANAM, NAMA, KIRTANAM
    1, 1,       # VALIDATE: PADA_SEVANAM, ARCANAM
    2, 2,       # EXECUTE:  SMARANAM, VANDANAM
    3,          # RESULT:   DASYAM
    4, 4, 4, 4, # SYNC:     SAKHYAM, KIRTAN, YAJNA, ATMA_NIVEDANAM
)

assert len(GATE_INDEX) == MAHAJANA_COUNT

# VAMSI addresses: PARAMPARA * (i + KSETRAJNA) for i in range(12)
VAMSI_ADDR: Final[Tuple[int, ...]] = tuple(
    PARAMPARA * (i + KSETRAJNA) for i in range(MAHAJANA_COUNT)
)
# = (37, 74, 111, 148, 185, 222, 259, 296, 333, 370, 407, 444)

# The fixed execution cycle (Phase 1: static, like THE_FLUTE_CYCLE)
CYCLE: Final[Tuple[NavaBhaktiOp, ...]] = tuple(NavaBhaktiOp(i) for i in range(MAHAJANA_COUNT))


__all__ = [
    "NavaBhaktiOp",
    "GATE_INDEX",
    "VAMSI_ADDR",
    "CYCLE",
]
