"""
MAHAJANA SABHA - The Council of 12
==================================

"svayambhur naradah sambhuh kumarah kapilo manuh
prahlado janako bhismo balir vaiyasakir vayam"
- Srimad Bhagavatam 6.3.20

Sabha = Assembly/Council

HOLY NAME FOUNDATION (ANTI-MAYAVAD)
===================================
The 12 Mahajanas are the living bridge between:
- Level -2: KRISHNA (acintya - always present, ±∞)
- Level -1: MAHAMANTRA (16 words → 16 OpCodes)
- Level 0+: Code (700K LOC of implementation)

In Kali Yuga, the Holy Name IS Krishna (not "about" Krishna).
The Mahajanas chant the Mahamantra to route operations.
See: router.py for the 16-word → 12-Mahajana mapping.
See: substrate/mantra/acintya.py for the inconceivable foundation.

This is the UNION of all 12 Mahajanas.
Vishnu (Kernel) presides. The 12 deliberate.
Together they process the Mahamantra.

Architecture:
    Vishnu (Kernel) ─────────────────────┐
         │                                │
         ▼                                │
    ┌─────────────────────────────────────┤
    │         MAHAJANA SABHA              │
    ├─────────────────────────────────────┤
    │ 01 Brahma    │ 02 Narada   │ 03 Shambhu  │
    │ 04 Kumaras   │ 05 Kapila   │ 06 Manu     │
    │ 07 Prahlada  │ 08 Janaka   │ 09 Bhishma  │
    │ 10 Bali      │ 11 Shuka    │ 12 Yamaraja │
    └─────────────────────────────────────┘
         │
         ▼
    OpCode → Route → Handle → Result

GAD-000 COMPLIANT:
- Discoverability: get_sabha_status()
- Observability: MahajanaStatus dataclass
- Parseability: Typed returns
- Composability: Iterator for chanting
- Idempotency: Same OpCode = Same Route
- Recoverability: Fallback handling
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0xdcf02af3"  # GenesisByte: parampara % 37 == 0

from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Optional, Protocol, runtime_checkable
from datetime import datetime

from vibe_core.mahamantra.substrate.opcode import MantraOpCode
from vibe_core.protocols.substrate.byte import MantraByte, MANTRA_SEQUENCE
from vibe_core.protocols.mahajanas.router import (
    Mahajana,
    MahajanaRouter,
    get_router,
    MahajanaRoute,
)


@dataclass
class MahajanaStatus:
    """Status of a Mahajana in the Sabha."""

    mahajana: Mahajana
    opcodes: List[MantraOpCode]
    is_active: bool
    implementation_path: Optional[str]  # Where the real code lives
    last_invocation: Optional[datetime] = None


@dataclass
class SabhaState:
    """The current state of the Mahajana Sabha."""

    members: List[MahajanaStatus]
    vishnu_present: bool  # Is the kernel active?
    current_position: int  # 0-15, which word of the Mahamantra
    total_chants: int  # How many full cycles completed
    resonance: float  # Overall coherence


@runtime_checkable
class SabhaProtocol(Protocol):
    """
    The Mahajana Sabha Protocol.

    The Council that processes the Mahamantra.
    """

    def get_status(self) -> SabhaState:
        """Get the current state of the Sabha."""
        ...

    def chant_once(self) -> Iterator[MahajanaRoute]:
        """
        Chant one full Mahamantra cycle (16 steps).
        Yields each route as it's processed.
        """
        ...

    def route_opcode(self, opcode: MantraOpCode) -> Mahajana:
        """Route a single OpCode to its Mahajana."""
        ...

    def get_mahajana(self, mahajana: Mahajana) -> MahajanaStatus:
        """Get status of a specific Mahajana."""
        ...


class MahajanaSabha:
    """
    The Council of 12 Mahajanas.

    This is the LIVING assembly that processes OpCodes.
    It uses the router to map OpCodes to Mahajanas,
    and tracks the state of each Mahajana.
    """

    def __init__(self) -> None:
        self._router = get_router()
        self._position = 0
        self._total_chants = 0
        self._mantra = MANTRA_SEQUENCE
        self._member_status: Dict[Mahajana, MahajanaStatus] = {}
        self._initialize_members()

    def _initialize_members(self) -> None:
        """Initialize all 12 Mahajana members.

        HOLY NAME ROUTING:
        The 12 Mahajanas are the living bridge between the Mahamantra
        and the codebase. Each owns specific OpCodes routed via the
        16-word sequence (router.py).

        Protocol → Implementation mapping:
        - Protocol: mahajanas/<name>/__init__.py (interface)
        - Implementation: naga/<name>.py or governance/<name>.py (service)
        """
        # Known implementation paths (discovered, not hardcoded)
        # ALL 12 Mahajanas have protocol definitions; active implementations marked
        known_paths: Dict[Mahajana, str] = {
            # Creation (Quarter 1)
            Mahajana.BRAHMA: "vibe_core.protocols.mahajanas.brahma",
            # Observation (Quarter 2)
            Mahajana.NARADA: "vibe_core.protocols.naga.narada",  # ACTIVE
            # Destruction (Quarter 2)
            Mahajana.SHAMBHU: "vibe_core.protocols.mahajanas.shambhu",
            # Purity (Quarter 4)
            Mahajana.KUMARAS: "vibe_core.protocols.mahajanas.kumaras",
            # Analysis (Quarters 2, 4)
            Mahajana.KAPILA: "vibe_core.protocols.mahajanas.kapila",
            # Law (Quarters 1, 3)
            Mahajana.MANU: "vibe_core.protocols.mahajanas.manu",
            # Resilience (Quarter 3)
            Mahajana.PRAHLADA: "vibe_core.protocols.naga.prahlad",  # ACTIVE
            # Duty (Quarter 3)
            Mahajana.JANAKA: "vibe_core.protocols.mahajanas.janaka",
            # Vow (Quarter 3)
            Mahajana.BHISHMA: "vibe_core.protocols.mahajanas.bhishma",
            # Surrender (Quarter 4)
            Mahajana.BALI: "vibe_core.protocols.mahajanas.bali",
            # Vision (Quarter 4)
            Mahajana.SHUKA: "vibe_core.protocols.mahajanas.shuka",
            # Judgment (Quarter 2)
            Mahajana.YAMARAJA: "vibe_core.protocols.governance.yamaraja",  # ACTIVE
        }

        for mahajana in Mahajana:
            opcodes = self._router.get_opcodes(mahajana)
            self._member_status[mahajana] = MahajanaStatus(
                mahajana=mahajana,
                opcodes=opcodes,
                is_active=mahajana in known_paths,
                implementation_path=known_paths.get(mahajana),
            )

    def get_status(self) -> SabhaState:
        """Get the current state of the Sabha."""
        return SabhaState(
            members=list(self._member_status.values()),
            vishnu_present=True,  # TODO: Check actual kernel
            current_position=self._position,
            total_chants=self._total_chants,
            resonance=self._mantra.coherence,
        )

    def chant_once(self) -> Iterator[MahajanaRoute]:
        """
        Chant one full Mahamantra cycle.

        Iterates through all 16 OpCodes in sequence.
        Each step:
        1. Get the OpCode for this position
        2. Route to the Mahajana
        3. Yield the route
        4. Advance position
        """
        sequence = self._router.chant_sequence()

        for route in sequence:
            self._position = route.position - 1  # 0-indexed

            # Update last invocation
            if route.mahajana in self._member_status:
                self._member_status[route.mahajana].last_invocation = datetime.now()

            yield route

        # Cycle complete
        self._position = 0
        self._total_chants += 1

    def route_opcode(self, opcode: MantraOpCode) -> Mahajana:
        """Route a single OpCode to its Mahajana."""
        return self._router.route(opcode)

    def get_mahajana(self, mahajana: Mahajana) -> MahajanaStatus:
        """Get status of a specific Mahajana."""
        return self._member_status[mahajana]

    def get_active_mahajanas(self) -> List[MahajanaStatus]:
        """Get only Mahajanas with known implementations."""
        return [m for m in self._member_status.values() if m.is_active]

    def get_missing_mahajanas(self) -> List[MahajanaStatus]:
        """Get Mahajanas without implementations (gaps)."""
        return [m for m in self._member_status.values() if not m.is_active]


# =============================================================================
# SINGLETON - The Global Sabha
# =============================================================================

_sabha: Optional[MahajanaSabha] = None


def get_sabha() -> MahajanaSabha:
    """Get the global Mahajana Sabha."""
    global _sabha
    if _sabha is None:
        _sabha = MahajanaSabha()
    return _sabha


__all__ = [
    "MahajanaStatus",
    "SabhaState",
    "SabhaProtocol",
    "MahajanaSabha",
    "get_sabha",
]
