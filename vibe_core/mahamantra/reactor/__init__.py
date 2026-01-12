"""
REACTOR - Der Mahamantra Reaktor
================================

"yajñārthāt karmaṇo 'nyatra loko 'yaṁ karma-bandhanaḥ
tad-arthaṁ karma kaunteya mukta-saṅgaḥ samācara"

"Work done as a sacrifice for Vishnu has to be performed,
otherwise work causes bondage in this material world."
— Bhagavad Gita 3.9

THE BHOGA-PRASADAM YAJNA:
=========================

    Position 0-7:  BHOGA (Offering) - Krishna half
    Position 8:    THE SWITCH (Parashurama transforms)
    Position 8-15: PRASADAM (Grace) - Rama half

    The 8th position is where OFFERING becomes GRACE.
    No manual wiring - FOLDER = WIRING = REGISTRATION.

LEVEL: +2 (SERVICES) - Dies ist die Service-Schicht
"""

from typing import Final
from vibe_core.mahamantra.substrate import ProtocolLevel

REACTOR_LEVEL: Final[ProtocolLevel] = ProtocolLevel.SERVICES

# =============================================================================
# SHADOW REACTOR - The Bhoga-Prasadam Engine
# =============================================================================

from vibe_core.mahamantra.reactor.shadow import (
    # Phase
    YajnaPhase,
    SWITCH_POSITION,
    RETURN_POSITION,
    get_phase,
    # Types (WATERTIGHT)
    TickStateInput,
    ShadowState,
    # Protocol
    ShadowReactorProtocol,
    # Reactor
    ShadowReactor,
    get_shadow_reactor,
    shadow,
)

__all__ = [
    # Level
    "REACTOR_LEVEL",
    # Phase
    "YajnaPhase",
    "SWITCH_POSITION",
    "RETURN_POSITION",
    "get_phase",
    # Types (WATERTIGHT)
    "TickStateInput",
    "ShadowState",
    # Protocol
    "ShadowReactorProtocol",
    # Reactor
    "ShadowReactor",
    "get_shadow_reactor",
    "shadow",
]
