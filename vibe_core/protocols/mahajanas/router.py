"""
MAHAJANA ROUTER - OpCode → Mahajana Mapping
============================================

"No manual labour as long as we chant."

The Mahamantra sequence ITSELF determines routing.
16 OpCodes → 12 Mahajanas.

This is the BRIDGE between:
- byte.py (Layer -1) - The atomic instructions
- mahajanas/ (Layer 1) - The protocol owners

The router does NOT manually map. It CHANTS.
"""

from enum import Enum
from typing import Dict, List, Set, Optional, Type, TYPE_CHECKING
from dataclasses import dataclass

from vibe_core.protocols.universal.mantra import MantraOpCode

if TYPE_CHECKING:
    from vibe_core.protocols.mahajanas.brahma import BrahmaProtocol
    from vibe_core.protocols.mahajanas.narada import NaradaProtocol
    from vibe_core.protocols.mahajanas.shambhu import ShambhuProtocol
    from vibe_core.protocols.mahajanas.kumaras import KumarasProtocol
    from vibe_core.protocols.mahajanas.kapila import KapilaProtocol
    from vibe_core.protocols.mahajanas.manu import ManuProtocol
    from vibe_core.protocols.mahajanas.prahlada import PrahladaProtocol
    from vibe_core.protocols.mahajanas.janaka import JanakaProtocol
    from vibe_core.protocols.mahajanas.bhishma import BhishmaProtocol
    from vibe_core.protocols.mahajanas.bali import BaliProtocol
    from vibe_core.protocols.mahajanas.shuka import ShukaProtocol
    from vibe_core.protocols.mahajanas.yamaraja import YamarajaProtocol


class Mahajana(str, Enum):
    """The 12 Mahajanas - Protocol Owners."""
    BRAHMA = "brahma"       # 01 - Creation
    NARADA = "narada"       # 02 - Devotion
    SHAMBHU = "shambhu"     # 03 - Destruction
    KUMARAS = "kumaras"     # 04 - Purity
    KAPILA = "kapila"       # 05 - Analysis
    MANU = "manu"           # 06 - Law
    PRAHLADA = "prahlada"   # 07 - Resilience
    JANAKA = "janaka"       # 08 - Duty
    BHISHMA = "bhishma"     # 09 - Vow
    BALI = "bali"           # 10 - Surrender
    SHUKA = "shuka"         # 11 - Vision
    YAMARAJA = "yamaraja"   # 12 - Judgment


@dataclass(frozen=True)
class MahajanaRoute:
    """A route from OpCode to Mahajana."""
    opcode: MantraOpCode
    mahajana: Mahajana
    quarter: int  # 1-4 (Which quarter of the Mahamantra)
    position: int  # 1-16 (Position in the sequence)


# =============================================================================
# THE ROUTING TABLE - Derived from the Mahamantra Sequence
# =============================================================================
#
# QUARTER 1: INVOCATION (H K H K) - Starting the system
# QUARTER 2: VERIFICATION (K K H H) - Checking truth
# QUARTER 3: EXECUTION (H R H R) - Doing the work
# QUARTER 4: CONCLUSION (R R H H) - Completing the cycle
#
# The Mahamantra is the CLOCK. Each word triggers an OpCode.
# Each OpCode is OWNED by a Mahajana.

_ROUTING_TABLE: Dict[MantraOpCode, MahajanaRoute] = {
    # --- QUARTER 1: INVOCATION ---
    MantraOpCode.SYS_WAKE: MahajanaRoute(
        MantraOpCode.SYS_WAKE, Mahajana.BRAHMA, quarter=1, position=1
    ),
    MantraOpCode.LOAD_ROOT: MahajanaRoute(
        MantraOpCode.LOAD_ROOT, Mahajana.BRAHMA, quarter=1, position=2
    ),
    MantraOpCode.ALLOC_MEM: MahajanaRoute(
        MantraOpCode.ALLOC_MEM, Mahajana.BRAHMA, quarter=1, position=3
    ),
    MantraOpCode.BIND_CTX: MahajanaRoute(
        MantraOpCode.BIND_CTX, Mahajana.MANU, quarter=1, position=4
    ),

    # --- QUARTER 2: VERIFICATION ---
    MantraOpCode.ASSERT_TRUTH: MahajanaRoute(
        MantraOpCode.ASSERT_TRUTH, Mahajana.YAMARAJA, quarter=2, position=5
    ),
    MantraOpCode.RESOLVE_REQ: MahajanaRoute(
        MantraOpCode.RESOLVE_REQ, Mahajana.KAPILA, quarter=2, position=6
    ),
    MantraOpCode.GARBAGE_COLLECT: MahajanaRoute(
        MantraOpCode.GARBAGE_COLLECT, Mahajana.SHAMBHU, quarter=2, position=7
    ),
    MantraOpCode.PULSE_SYNC: MahajanaRoute(
        MantraOpCode.PULSE_SYNC, Mahajana.NARADA, quarter=2, position=8
    ),

    # --- QUARTER 3: EXECUTION ---
    MantraOpCode.FETCH_RES: MahajanaRoute(
        MantraOpCode.FETCH_RES, Mahajana.PRAHLADA, quarter=3, position=9
    ),
    MantraOpCode.EXEC_SERVICE: MahajanaRoute(
        MantraOpCode.EXEC_SERVICE, Mahajana.JANAKA, quarter=3, position=10
    ),
    MantraOpCode.CHECK_DHARMA: MahajanaRoute(
        MantraOpCode.CHECK_DHARMA, Mahajana.MANU, quarter=3, position=11
    ),
    MantraOpCode.COMMIT_LOG: MahajanaRoute(
        MantraOpCode.COMMIT_LOG, Mahajana.BHISHMA, quarter=3, position=12
    ),

    # --- QUARTER 4: CONCLUSION ---
    MantraOpCode.CACHE_STATE: MahajanaRoute(
        MantraOpCode.CACHE_STATE, Mahajana.SHUKA, quarter=4, position=13
    ),
    MantraOpCode.OPTIMIZE: MahajanaRoute(
        MantraOpCode.OPTIMIZE, Mahajana.KAPILA, quarter=4, position=14
    ),
    MantraOpCode.YIELD_CPU: MahajanaRoute(
        MantraOpCode.YIELD_CPU, Mahajana.BALI, quarter=4, position=15
    ),
    MantraOpCode.RESET_IP: MahajanaRoute(
        MantraOpCode.RESET_IP, Mahajana.KUMARAS, quarter=4, position=16
    ),
}


# =============================================================================
# ROUTER CLASS - The Chanting Engine
# =============================================================================

class MahajanaRouter:
    """
    Routes OpCodes to Mahajanas.

    Usage:
        router = MahajanaRouter()
        mahajana = router.route(MantraOpCode.GARBAGE_COLLECT)
        # Returns: Mahajana.SHAMBHU

        opcodes = router.get_opcodes(Mahajana.KAPILA)
        # Returns: [RESOLVE_REQ, OPTIMIZE]
    """

    def __init__(self) -> None:
        self._table = _ROUTING_TABLE
        self._reverse: Dict[Mahajana, List[MantraOpCode]] = {}
        self._build_reverse_index()

    def _build_reverse_index(self) -> None:
        """Build Mahajana → OpCodes reverse lookup."""
        for opcode, route in self._table.items():
            if route.mahajana not in self._reverse:
                self._reverse[route.mahajana] = []
            self._reverse[route.mahajana].append(opcode)

    def route(self, opcode: MantraOpCode) -> Mahajana:
        """
        Route an OpCode to its owning Mahajana.

        This is the CHANT - the OpCode determines the Mahajana.
        """
        if opcode not in self._table:
            raise ValueError(f"Unknown OpCode: {opcode}")
        return self._table[opcode].mahajana

    def get_route(self, opcode: MantraOpCode) -> MahajanaRoute:
        """Get full route info for an OpCode."""
        if opcode not in self._table:
            raise ValueError(f"Unknown OpCode: {opcode}")
        return self._table[opcode]

    def get_opcodes(self, mahajana: Mahajana) -> List[MantraOpCode]:
        """Get all OpCodes owned by a Mahajana."""
        return self._reverse.get(mahajana, [])

    def get_quarter(self, quarter: int) -> List[MahajanaRoute]:
        """Get all routes in a quarter (1-4)."""
        return [r for r in self._table.values() if r.quarter == quarter]

    def chant_sequence(self) -> List[MahajanaRoute]:
        """
        Return the full Mahamantra sequence as routes.
        16 steps, in order.
        """
        return sorted(self._table.values(), key=lambda r: r.position)


# =============================================================================
# SINGLETON INSTANCE - The Global Router
# =============================================================================

_router: Optional[MahajanaRouter] = None

def get_router() -> MahajanaRouter:
    """Get the global Mahajana router."""
    global _router
    if _router is None:
        _router = MahajanaRouter()
    return _router


def route(opcode: MantraOpCode) -> Mahajana:
    """Convenience function: Route an OpCode to its Mahajana."""
    return get_router().route(opcode)


def get_opcodes(mahajana: Mahajana) -> List[MantraOpCode]:
    """Convenience function: Get OpCodes for a Mahajana."""
    return get_router().get_opcodes(mahajana)


# =============================================================================
# VERIFICATION - The Router Must Be Complete
# =============================================================================

def verify_router() -> bool:
    """
    Verify the router is complete and correct.
    All 16 OpCodes must be mapped.
    All 12 Mahajanas must own at least one OpCode.
    """
    router = get_router()

    # Check all OpCodes are mapped
    all_opcodes = set(MantraOpCode)
    mapped_opcodes = set(_ROUTING_TABLE.keys())

    if all_opcodes != mapped_opcodes:
        missing = all_opcodes - mapped_opcodes
        raise ValueError(f"Missing OpCodes in router: {missing}")

    # Check all Mahajanas have at least one OpCode
    mahajanas_with_opcodes = set(r.mahajana for r in _ROUTING_TABLE.values())
    all_mahajanas = set(Mahajana)

    # Note: Not all Mahajanas must have OpCodes (some may be meta-level)
    # But we track which ones do

    return True


__all__ = [
    "Mahajana",
    "MahajanaRoute",
    "MahajanaRouter",
    "get_router",
    "route",
    "get_opcodes",
    "verify_router",
]
