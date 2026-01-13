"""
CLOCK - Der Mahamantra Taktgeber (LILA-AWARE)
=============================================

"kālo 'smi loka-kṣaya-kṛt pravṛddho"
"Ich bin die Zeit, der große Zerstörer der Welten."
— Bhagavad Gita 11.32

ZWEI MODI:
=========

    CPU MODE (tick):     0-15 (ein Mantra)
    LILA MODE (lila):    0-47 (Chaitanya Lila)

CHAITANYA LILA:
==============

    0-23:  NAVADVIP (Build, __init__, Compile)
    24-47: PURI (Runtime, yield, Execute)

    48 = 16 × 3 = Chaitanya's 48 Jahre

DIE MAP:
=======

    tick tick tick tick...

    NAVADVIP                      PURI
    ┌─────────────────────┐      ┌─────────────────────┐
    │ Cycle 1: 0-15       │      │ Cycle 2: 16-31      │ ← partially
    │ Cycle 2: 16-23      │      │ Cycle 3: 32-47      │
    └─────────────────────┘      └─────────────────────┘
           BUILD                       RUNTIME

WATERTIGHT: Keine externen Abhängigkeiten. Nur substrate/.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0xa7c3d2e1"  # GenesisByte: parampara % 37 == 0

from typing import TypedDict, Optional

from vibe_core.mahamantra.substrate.position import (
    MAHAMANTRA_POSITIONS,
    MantraPosition,
)
from vibe_core.mahamantra.substrate.protocol import ProtocolRegistry
from vibe_core.mahamantra.substrate.pancha_tattva import (
    CHAITANYA_LILA,      # 48
    NAVADVIPA_PHASE,     # 24
    get_lila_phase,      # tick → "navadvipa" / "puri"
    get_mantra_cycle,    # tick → 1, 2, 3
    get_mantra_position, # tick → 0-15
)


# =============================================================================
# TICK STATE - The output of each tick
# =============================================================================

class TickState(TypedDict):
    """What a tick returns. WATERTIGHT."""
    tick: int           # Current tick (0-15)
    position: int       # Same as tick
    quarter: str        # genesis/dharma/karma/moksha
    guardian: str       # The mahajana/avatara name
    word: str           # HARE/KRISHNA/RAMA
    opcode: Optional[int]  # The opcode value


class LilaTickState(TypedDict):
    """What a lila_tick returns. LILA-AWARE."""
    # Mantra level (0-15)
    tick: int           # Current mantra position (0-15)
    position: int       # Same as tick
    quarter: str        # genesis/dharma/karma/moksha
    guardian: str       # The mahajana/avatara name
    word: str           # HARE/KRISHNA/RAMA
    opcode: Optional[int]
    # Lila level (0-47)
    lila_tick: int      # Current lila position (0-47)
    phase: str          # "navadvipa" or "puri"
    cycle: int          # 1, 2, or 3
    is_navadvip: bool   # True if in build phase
    is_puri: bool       # True if in runtime phase


# =============================================================================
# THE CLOCK - Das Herz des Systems (LILA-AWARE)
# =============================================================================

class MahamantraClock:
    """
    Der Taktgeber. LILA-AWARE.

    ZWEI MODI:
        clock.tick()      → 0-15 (CPU Mode, ein Mantra)
        clock.lila_tick() → 0-47 (Lila Mode, Chaitanya's Leben)

    NAVIGATION:
        clock.goto_navadvip() → Springe zu Build-Phase (0)
        clock.goto_puri()     → Springe zu Runtime-Phase (24)

    PHASE-AWARE:
        clock.phase       → "navadvipa" oder "puri"
        clock.cycle       → 1, 2, oder 3
        clock.is_navadvip → True in Build-Phase
        clock.is_puri     → True in Runtime-Phase
    """

    __slots__ = ("_tick", "_lila_tick")

    def __init__(self) -> None:
        self._tick: int = 0       # Mantra position (0-15)
        self._lila_tick: int = 0  # Lila position (0-47)

    # =========================================================================
    # CPU MODE - Simple 16-position tick
    # =========================================================================

    def tick(self) -> TickState:
        """
        CPU Mode: Der einfache Herzschlag (0-15).

        Für Backward-Kompatibilität. Ignoriert Lila.
        """
        pos = MAHAMANTRA_POSITIONS[self._tick]

        state: TickState = {
            "tick": self._tick,
            "position": self._tick,
            "quarter": pos.quarter.name.lower(),
            "guardian": pos.guardian.value,
            "word": pos.word.name,
            "opcode": pos.opcode.value if pos.opcode else None,
        }

        # Dispatch to registered instance
        ProtocolRegistry.dispatch_tick(self._tick, state)

        # Advance mantra position only
        self._tick = (self._tick + 1) % 16

        return state

    # =========================================================================
    # LILA MODE - Full 48-position Chaitanya Lila
    # =========================================================================

    def lila_tick(self) -> LilaTickState:
        """
        Lila Mode: Der volle Chaitanya Herzschlag (0-47).

        NAVADVIP (0-23): Build-Phase, __init__, Compile
        PURI (24-47):    Runtime-Phase, yield, Execute

        Returns: LilaTickState mit Phase-Info
        """
        # Get mantra position from lila position
        mantra_pos = get_mantra_position(self._lila_tick)
        pos = MAHAMANTRA_POSITIONS[mantra_pos]

        # Build lila-aware state
        phase = get_lila_phase(self._lila_tick)
        cycle = get_mantra_cycle(self._lila_tick)

        state: LilaTickState = {
            # Mantra level
            "tick": mantra_pos,
            "position": mantra_pos,
            "quarter": pos.quarter.name.lower(),
            "guardian": pos.guardian.value,
            "word": pos.word.name,
            "opcode": pos.opcode.value if pos.opcode else None,
            # Lila level
            "lila_tick": self._lila_tick,
            "phase": phase,
            "cycle": cycle,
            "is_navadvip": phase == "navadvipa",
            "is_puri": phase == "puri",
        }

        # Dispatch to registered instance (uses mantra position)
        ProtocolRegistry.dispatch_tick(mantra_pos, state)

        # Advance BOTH counters
        self._lila_tick = (self._lila_tick + 1) % CHAITANYA_LILA
        self._tick = get_mantra_position(self._lila_tick)

        return state

    # =========================================================================
    # NAVIGATION - Springe zu Phase
    # =========================================================================

    def goto_navadvip(self) -> None:
        """Springe zu Navadvip (Build-Phase, Position 0)."""
        self._lila_tick = 0
        self._tick = 0

    def goto_puri(self) -> None:
        """Springe zu Puri (Runtime-Phase, Position 24)."""
        self._lila_tick = NAVADVIPA_PHASE  # 24
        self._tick = get_mantra_position(self._lila_tick)

    def goto_lila(self, lila_position: int) -> None:
        """Springe zu beliebiger Lila-Position (0-47)."""
        if not 0 <= lila_position < CHAITANYA_LILA:
            raise ValueError(f"Lila position must be 0-47, got {lila_position}")
        self._lila_tick = lila_position
        self._tick = get_mantra_position(self._lila_tick)

    def reset(self) -> None:
        """Reset zu Position 0 (Navadvip Start)."""
        self._tick = 0
        self._lila_tick = 0

    # =========================================================================
    # LILA PROPERTIES
    # =========================================================================

    @property
    def lila_position(self) -> int:
        """Current lila position (0-47)."""
        return self._lila_tick

    @property
    def phase(self) -> str:
        """Current phase: 'navadvipa' or 'puri'."""
        return get_lila_phase(self._lila_tick)

    @property
    def cycle(self) -> int:
        """Current cycle (1, 2, or 3)."""
        return get_mantra_cycle(self._lila_tick)

    @property
    def is_navadvip(self) -> bool:
        """True if in Navadvip (Build) phase."""
        return self._lila_tick < NAVADVIPA_PHASE

    @property
    def is_puri(self) -> bool:
        """True if in Puri (Runtime) phase."""
        return self._lila_tick >= NAVADVIPA_PHASE

    # =========================================================================
    # MANTRA PROPERTIES (backward compatible)
    # =========================================================================

    @property
    def position(self) -> int:
        """Current mantra position (0-15)."""
        return self._tick

    @property
    def quarter(self) -> str:
        """Current quarter name."""
        return MAHAMANTRA_POSITIONS[self._tick].quarter.name.lower()

    def get_position(self, index: int) -> MantraPosition:
        """Get position info by index."""
        if not 0 <= index <= 15:
            raise ValueError(f"Position must be 0-15, got {index}")
        return MAHAMANTRA_POSITIONS[index]

    def __getitem__(self, index: int) -> MantraPosition:
        """clock[5] → Position 5."""
        return self.get_position(index)

    def __len__(self) -> int:
        """16 mantra positions (or 48 lila positions via lila_len)."""
        return 16

    @property
    def lila_len(self) -> int:
        """48 lila positions."""
        return CHAITANYA_LILA

    def __iter__(self):
        """Iterate through all 16 mantra positions."""
        return iter(MAHAMANTRA_POSITIONS)

    def __contains__(self, item) -> bool:
        """Check if index or guardian name is valid."""
        if isinstance(item, int):
            return 0 <= item <= 15
        if isinstance(item, str):
            return any(pos.guardian.value == item for pos in MAHAMANTRA_POSITIONS)
        return False

    def by_guardian(self, guardian_name: str) -> MantraPosition:
        """Get position by guardian name."""
        for pos in MAHAMANTRA_POSITIONS:
            if pos.guardian.value == guardian_name:
                return pos
        raise ValueError(f"Unknown guardian: {guardian_name}")

    def __repr__(self) -> str:
        return (
            f"MahamantraClock(position={self._tick}, "
            f"lila={self._lila_tick}, phase={self.phase})"
        )

    # =========================================================================
    # THE CHANT
    # =========================================================================

    def chant(self, separator: str = " ") -> str:
        """The Holy Name as string."""
        words = [pos.word.name.capitalize() for pos in MAHAMANTRA_POSITIONS]
        return separator.join(words)

    # =========================================================================
    # VERIFICATION
    # =========================================================================

    def verify(self, parampara_vector: int) -> bool:
        """Verify Parampara connection (% 37 == 0)."""
        return parampara_vector % 37 == 0


# =============================================================================
# THE SINGLETON
# =============================================================================

clock = MahamantraClock()


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MahamantraClock",
    "TickState",
    "LilaTickState",
    "clock",
]
