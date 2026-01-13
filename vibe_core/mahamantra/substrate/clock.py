"""
CLOCK - Der Mahamantra Taktgeber
================================

"kālo 'smi loka-kṣaya-kṛt pravṛddho"
"Ich bin die Zeit, der große Zerstörer der Welten."
— Bhagavad Gita 11.32

DAS IST ALLES. EIN CLOCK. MEHR NICHT.

    16 ticks = 1 cycle
    4 ticks = 1 quarter
    1 tick = 1 position

Wie ein echter CPU Clock:
    tick tick tick tick...
    0 → 1 → 2 → ... → 15 → 0 → ...

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


# =============================================================================
# THE CLOCK - Das Herz des Systems
# =============================================================================

class MahamantraClock:
    """
    Der Taktgeber. 16 Positionen. Mehr nicht.

    Wie ein CPU Clock:
        clock.tick()  → Advance and return state
        clock.tick    → Current position (0-15)
        clock[5]      → Position 5 info

    KEINE Router. KEINE CLI. KEINE Spaghetti.
    NUR: tick tick tick tick...
    """

    __slots__ = ("_tick",)

    def __init__(self) -> None:
        self._tick: int = 0

    # =========================================================================
    # THE HEARTBEAT
    # =========================================================================

    def tick(self) -> TickState:
        """
        Der Herzschlag. Advance und return state.

        1. Get current position
        2. Dispatch to registered instances
        3. Advance counter
        4. Return state
        """
        # Get current position from truth table
        pos = MAHAMANTRA_POSITIONS[self._tick]

        # Build state
        state: TickState = {
            "tick": self._tick,
            "position": self._tick,
            "quarter": pos.quarter.name.lower(),
            "guardian": pos.guardian.value,
            "word": pos.word.name,
            "opcode": pos.opcode.value if pos.opcode else None,
        }

        # Dispatch to registered instance at this position
        ProtocolRegistry.dispatch_tick(self._tick, state)

        # Advance (wrap at 16)
        current = self._tick
        self._tick = (self._tick + 1) % 16

        return state

    def reset(self) -> None:
        """Reset to position 0."""
        self._tick = 0

    # =========================================================================
    # READ-ONLY ACCESS
    # =========================================================================

    @property
    def position(self) -> int:
        """Current position (0-15)."""
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
        """16 positions."""
        return 16

    def __iter__(self):
        """Iterate through all 16 positions."""
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
        return f"MahamantraClock(position={self._tick})"

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
    "clock",
]
