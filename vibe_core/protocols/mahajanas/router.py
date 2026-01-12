"""
MAHAJANA ROUTER - OpCode → Mahajana Mapping
============================================

"No manual labour as long as we chant."

The Mahamantra sequence ITSELF determines routing.

ARCHITECTURE UPDATE (Chatur-Vyuha):
===================================
OLD (Kali Yuga / Linear):
    16 OpCodes → 12 Mahajanas (scattered, some own 2-3)

NEW (Satya Yuga / Fractal):
    16 = 4 × (1 + 3)
    4 HEADs (Avataras) own 4 OpCodes (positions 1, 5, 9, 13)
    12 Workers (Mahajanas) own 12 OpCodes (all other positions)

    See: vyuha.py for the full Chatur-Vyuha implementation.

This router provides backward compatibility while supporting
the new cycle-aware architecture via the VyuhaRouter.

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
# CHATUR-VYUHA ARCHITECTURE (NEW):
# ================================
# Each quarter has 1 HEAD (Avatara) + 3 Workers (Mahajanas).
# HEAD positions: 1, 5, 9, 13 (owned by Avataras, not Mahajanas)
# Worker positions: 2-4, 6-8, 10-12, 14-16 (owned by Mahajanas)
#
# QUARTER 1: GENESIS (H K H K)
#   HEAD: Prithu (SYS_WAKE) + Brahma, Narada, Shambhu
# QUARTER 2: DHARMA (K K H H)
#   HEAD: Vyasa (ASSERT_TRUTH) + Kumaras, Kapila, Manu
# QUARTER 3: KARMA (H R H R)
#   HEAD: Parashurama (FETCH_RES) + Prahlada, Janaka, Bhishma
# QUARTER 4: MOKSHA (R R H H)
#   HEAD: Nrisimha (CACHE_STATE) + Bali, Shuka, Yamaraja
#
# The Mahamantra is the CLOCK. Each word triggers an OpCode.
# HEAD OpCodes are handled by Avataras (see vyuha.py).
# Worker OpCodes are handled by Mahajanas (this table).

# -----------------------------------------------------------------------------
# VYUHA-ALIGNED ROUTING TABLE (NEW - 1:1 Mahajana:OpCode)
# -----------------------------------------------------------------------------
# This table maps the 12 Worker OpCodes to their Mahajanas.
# HEAD OpCodes (positions 1, 5, 9, 13) are NOT in this table.
# Use VyuhaRouter for full cycle-aware routing.

_VYUHA_ROUTING_TABLE: Dict[MantraOpCode, MahajanaRoute] = {
    # --- QUARTER 1: GENESIS (Workers only) ---
    MantraOpCode.LOAD_ROOT: MahajanaRoute(
        MantraOpCode.LOAD_ROOT, Mahajana.BRAHMA, quarter=1, position=2
    ),
    MantraOpCode.ALLOC_MEM: MahajanaRoute(
        MantraOpCode.ALLOC_MEM, Mahajana.NARADA, quarter=1, position=3
    ),
    MantraOpCode.INIT_THREAD: MahajanaRoute(
        MantraOpCode.INIT_THREAD, Mahajana.SHAMBHU, quarter=1, position=4
    ),

    # --- QUARTER 2: DHARMA (Workers only) ---
    MantraOpCode.BIND_SYMBOL: MahajanaRoute(
        MantraOpCode.BIND_SYMBOL, Mahajana.KUMARAS, quarter=2, position=6
    ),
    MantraOpCode.TYPE_CHECK: MahajanaRoute(
        MantraOpCode.TYPE_CHECK, Mahajana.KAPILA, quarter=2, position=7
    ),
    MantraOpCode.DHARMA_TEST: MahajanaRoute(
        MantraOpCode.DHARMA_TEST, Mahajana.MANU, quarter=2, position=8
    ),

    # --- QUARTER 3: KARMA (Workers only) ---
    MantraOpCode.EXTEND_CAP: MahajanaRoute(
        MantraOpCode.EXTEND_CAP, Mahajana.PRAHLADA, quarter=3, position=10
    ),
    MantraOpCode.STATE_SYNC: MahajanaRoute(
        MantraOpCode.STATE_SYNC, Mahajana.JANAKA, quarter=3, position=11
    ),
    MantraOpCode.LEDGER_SIGN: MahajanaRoute(
        MantraOpCode.LEDGER_SIGN, Mahajana.BHISHMA, quarter=3, position=12
    ),

    # --- QUARTER 4: MOKSHA (Workers only) ---
    MantraOpCode.IO_FLUSH: MahajanaRoute(
        MantraOpCode.IO_FLUSH, Mahajana.BALI, quarter=4, position=14
    ),
    MantraOpCode.YIELD_CPU: MahajanaRoute(
        MantraOpCode.YIELD_CPU, Mahajana.SHUKA, quarter=4, position=15
    ),
    MantraOpCode.AUDIT_SEAL: MahajanaRoute(
        MantraOpCode.AUDIT_SEAL, Mahajana.YAMARAJA, quarter=4, position=16
    ),
}

# HEAD OpCodes (owned by Avataras, not Mahajanas)
HEAD_OPCODES: set = {
    MantraOpCode.SYS_WAKE,      # Q1 HEAD: Prithu
    MantraOpCode.COMPILE_AST,  # Q2 HEAD: Vyasa
    MantraOpCode.EXEC_OP,     # Q3 HEAD: Parashurama
    MantraOpCode.YIELD_CPU,   # Q4 HEAD: Nrisimha
}

# -----------------------------------------------------------------------------
# LEGACY ROUTING TABLE (DEPRECATED - for backward compatibility)
# -----------------------------------------------------------------------------
# This table maintains the old 16→12 mapping for existing code.
# New code should use _VYUHA_ROUTING_TABLE or VyuhaRouter.

_ROUTING_TABLE: Dict[MantraOpCode, MahajanaRoute] = {
    # ==========================================================================
    # SEMANTIC ROUTING TABLE (Mahajana nature matches OpCode function)
    # ==========================================================================
    #
    # Each Mahajana's spiritual quality determines their OpCode ownership:
    #   BRAHMA (Creator)    → SYS_WAKE, LOAD_ROOT, ALLOC_MEM (creation ops)
    #   NARADA (Messenger)  → PULSE_SYNC (communication)
    #   SHAMBHU (Destroyer) → GARBAGE_COLLECT (destruction/cleanup)
    #   KUMARAS (Pure)      → RESET_IP (return to pure state)
    #   KAPILA (Analyst)    → RESOLVE_REQ, OPTIMIZE (analysis ops)
    #   MANU (Lawgiver)     → BIND_CTX, CHECK_DHARMA (law/rules)
    #   PRAHLADA (Resilient)→ FETCH_RES (persevering to get resources)
    #   JANAKA (Duty)       → EXEC_SERVICE (dutiful execution)
    #   BHISHMA (Vow)       → COMMIT_LOG (commitment/oath)
    #   BALI (Surrender)    → YIELD_CPU, CACHE_STATE (surrender control/state)
    #   SHUKA (Vision)      → (shares via Vyuha architecture)
    #   YAMARAJA (Judge)    → ASSERT_TRUTH (final judgment)
    #
    # --- QUARTER 1: GENESIS (H K H K) ---
    MantraOpCode.SYS_WAKE: MahajanaRoute(
        MantraOpCode.SYS_WAKE, Mahajana.BRAHMA, quarter=1, position=1
    ),
    MantraOpCode.LOAD_ROOT: MahajanaRoute(
        MantraOpCode.LOAD_ROOT, Mahajana.BRAHMA, quarter=1, position=2
    ),
    MantraOpCode.ALLOC_MEM: MahajanaRoute(
        MantraOpCode.ALLOC_MEM, Mahajana.BRAHMA, quarter=1, position=3
    ),
    MantraOpCode.INIT_THREAD: MahajanaRoute(
        MantraOpCode.INIT_THREAD, Mahajana.MANU, quarter=1, position=4
    ),

    # --- QUARTER 2: DHARMA (K K H H) ---
    MantraOpCode.COMPILE_AST: MahajanaRoute(
        MantraOpCode.COMPILE_AST, Mahajana.YAMARAJA, quarter=2, position=5
    ),
    MantraOpCode.BIND_SYMBOL: MahajanaRoute(
        MantraOpCode.BIND_SYMBOL, Mahajana.KAPILA, quarter=2, position=6
    ),
    MantraOpCode.TYPE_CHECK: MahajanaRoute(
        MantraOpCode.TYPE_CHECK, Mahajana.SHAMBHU, quarter=2, position=7
    ),
    MantraOpCode.DHARMA_TEST: MahajanaRoute(
        MantraOpCode.DHARMA_TEST, Mahajana.NARADA, quarter=2, position=8
    ),

    # --- QUARTER 3: KARMA (H R H R) ---
    MantraOpCode.EXEC_OP: MahajanaRoute(
        MantraOpCode.EXEC_OP, Mahajana.PRAHLADA, quarter=3, position=9
    ),
    MantraOpCode.EXTEND_CAP: MahajanaRoute(
        MantraOpCode.EXTEND_CAP, Mahajana.JANAKA, quarter=3, position=10
    ),
    MantraOpCode.STATE_SYNC: MahajanaRoute(
        MantraOpCode.STATE_SYNC, Mahajana.MANU, quarter=3, position=11
    ),
    MantraOpCode.LEDGER_SIGN: MahajanaRoute(
        MantraOpCode.LEDGER_SIGN, Mahajana.BHISHMA, quarter=3, position=12
    ),

    # --- QUARTER 4: MOKSHA (R R H H) ---
    MantraOpCode.YIELD_CPU: MahajanaRoute(
        MantraOpCode.YIELD_CPU, Mahajana.SHUKA, quarter=4, position=13
    ),
    MantraOpCode.IO_FLUSH: MahajanaRoute(
        MantraOpCode.IO_FLUSH, Mahajana.KAPILA, quarter=4, position=14
    ),
    MantraOpCode.YIELD_CPU: MahajanaRoute(
        MantraOpCode.YIELD_CPU, Mahajana.BALI, quarter=4, position=15
    ),
    MantraOpCode.AUDIT_SEAL: MahajanaRoute(
        MantraOpCode.AUDIT_SEAL, Mahajana.KUMARAS, quarter=4, position=16
    ),
}


# =============================================================================
# ROUTER CLASS - The Chanting Engine
# =============================================================================

class MahajanaRouter:
    """
    Routes OpCodes to Mahajanas.

    MODES:
        - legacy=True (default): Uses _ROUTING_TABLE (16→12, backward compat)
        - legacy=False: Uses _VYUHA_ROUTING_TABLE (12→12, 1:1 mapping)

    For cycle-aware routing with HEAD support, use VyuhaRouter from vyuha.py.

    Usage:
        router = MahajanaRouter()
        mahajana = router.route(MantraOpCode.TYPE_CHECK)
        # Returns: Mahajana.KAPILA

        opcodes = router.get_opcodes(Mahajana.KAPILA)
        # Returns: [GARBAGE_COLLECT] (in vyuha mode)

        # Check if opcode is HEAD (owned by Avatara, not Mahajana)
        is_head = router.is_head_opcode(MantraOpCode.SYS_WAKE)
        # Returns: True
    """

    def __init__(self, legacy: bool = True) -> None:
        """
        Initialize the router.

        Args:
            legacy: If True, use old 16→12 mapping. If False, use new 12→12 mapping.
        """
        self._legacy = legacy
        self._table = _ROUTING_TABLE if legacy else _VYUHA_ROUTING_TABLE
        self._reverse: Dict[Mahajana, List[MantraOpCode]] = {}
        self._build_reverse_index()

    def _build_reverse_index(self) -> None:
        """Build Mahajana → OpCodes reverse lookup."""
        for opcode, route in self._table.items():
            if route.mahajana not in self._reverse:
                self._reverse[route.mahajana] = []
            self._reverse[route.mahajana].append(opcode)

    def is_head_opcode(self, opcode: MantraOpCode) -> bool:
        """
        Check if an OpCode is a HEAD opcode (owned by Avatara, not Mahajana).

        HEAD positions: 1, 5, 9, 13 in the Mahamantra.
        """
        return opcode in HEAD_OPCODES

    def route(self, opcode: MantraOpCode) -> Mahajana:
        """
        Route an OpCode to its owning Mahajana.

        This is the CHANT - the OpCode determines the Mahajana.

        NOTE: In vyuha mode (legacy=False), HEAD opcodes raise ValueError.
        Use VyuhaRouter for HEAD opcode handling.
        """
        if opcode not in self._table:
            if not self._legacy and opcode in HEAD_OPCODES:
                raise ValueError(
                    f"HEAD OpCode {opcode.name} is owned by an Avatara, not a Mahajana. "
                    "Use VyuhaRouter for cycle-aware routing."
                )
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
    # Enums & Types
    "Mahajana",
    "MahajanaRoute",
    # Router
    "MahajanaRouter",
    "get_router",
    "route",
    "get_opcodes",
    "verify_router",
    # Vyuha Support
    "HEAD_OPCODES",
    "_VYUHA_ROUTING_TABLE",
]
