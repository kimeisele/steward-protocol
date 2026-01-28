"""
CLOCK - Mahamantra Rhythmus Bibliothek (STATELESS)
==================================================

"kālo 'smi loka-kṣaya-kṛt pravṛddho"
"Ich bin die Zeit, der große Zerstörer der Welten."
— Bhagavad Gita 11.32

DIES IST EINE BIBLIOTHEK, KEIN MOTOR.
=====================================

    Substrate = Die KARTE (stateless, pure math)
    Reactor   = Der REISENDE (hat state, woanders!)

Diese Datei beantwortet NUR:
    "Was WÄRE bei Tick 25?"  → Puri, Cycle 2, Position 9
    "Was WÄRE bei Tick 0?"   → Navadvip, Cycle 1, Position 0

Diese Datei beantwortet NICHT:
    "Wo bin ich GERADE?"     → Das ist Reactor's Job!

KEIN STATE. KEINE COUNTER. NUR PURE FUNCTIONS.

WATERTIGHT: Keine externen Abhängigkeiten. Nur substrate/.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0xd8198ee0"  # GenesisByte: parampara % 37 == 0

from typing import Optional, Tuple, TypedDict

from vibe_core.mahamantra.substrate.pancha_tattva import (
    CHAITANYA_LILA,  # 48
    MAHAMANTRA_WORDS,  # 16
    NAVADVIPA_PHASE,  # 24
    get_lila_phase,  # tick → "navadvipa" / "puri"
    get_mantra_cycle,  # tick → 1, 2, 3
    get_mantra_position,  # tick → 0-15
)
from vibe_core.mahamantra.substrate.position import (
    MAHAMANTRA_POSITIONS,
    MantraPosition,
)

# =============================================================================
# WATERTIGHT TYPES
# =============================================================================


class TickInfo(TypedDict):
    """Info about a mantra position (0-15). STATELESS."""

    position: int  # 0-15
    quarter: str  # genesis/dharma/karma/moksha
    guardian: str  # The mahajana/avatara name
    word: str  # HARE/KRISHNA/RAMA
    opcode: Optional[int]


class LilaInfo(TypedDict):
    """Info about a lila position (0-47). STATELESS."""

    # Mantra level
    position: int  # 0-15 (derived from lila)
    quarter: str  # genesis/dharma/karma/moksha
    guardian: str
    word: str
    opcode: Optional[int]
    # Lila level
    lila_position: int  # 0-47
    phase: str  # "navadvipa" or "puri"
    cycle: int  # 1, 2, or 3
    is_navadvip: bool
    is_puri: bool


# =============================================================================
# PURE FUNCTIONS - Mantra (0-15)
# =============================================================================


def get_tick_info(position: int) -> TickInfo:
    """
    Get info for a mantra position (0-15).

    PURE FUNCTION: No state, no side effects.

    Args:
        position: Mantra position (0-15)

    Returns:
        TickInfo with all position details
    """
    if not 0 <= position <= 15:
        raise ValueError(f"Position must be 0-15, got {position}")

    pos = MAHAMANTRA_POSITIONS[position]
    return TickInfo(
        position=position,
        quarter=pos.quarter.name.lower(),
        guardian=pos.guardian.value,
        word=pos.word.name,
        opcode=pos.opcode.value if pos.opcode is not None else None,  # BOMBENFEST: 0 is valid!
    )


def get_position_by_index(index: int) -> MantraPosition:
    """Get MantraPosition by index (0-15)."""
    if not 0 <= index <= 15:
        raise ValueError(f"Index must be 0-15, got {index}")
    return MAHAMANTRA_POSITIONS[index]


def get_position_by_guardian(guardian_name: str) -> MantraPosition:
    """Get MantraPosition by guardian name."""
    for pos in MAHAMANTRA_POSITIONS:
        if pos.guardian.value == guardian_name:
            return pos
    raise ValueError(f"Unknown guardian: {guardian_name}")


def next_position(position: int) -> int:
    """Calculate next position (wraps at 16). PURE."""
    return (position + 1) % MAHAMANTRA_WORDS


def previous_position(position: int) -> int:
    """Calculate previous position (wraps at 0). PURE."""
    return (position - 1) % MAHAMANTRA_WORDS


# =============================================================================
# PURE FUNCTIONS - Lila (0-47)
# =============================================================================


def get_lila_info(lila_position: int) -> LilaInfo:
    """
    Get info for a lila position (0-47).

    PURE FUNCTION: No state, no side effects.

    Args:
        lila_position: Chaitanya Lila position (0-47)

    Returns:
        LilaInfo with mantra and lila details
    """
    if not 0 <= lila_position < CHAITANYA_LILA:
        raise ValueError(f"Lila position must be 0-47, got {lila_position}")

    # Derive mantra position from lila
    mantra_pos = get_mantra_position(lila_position)
    pos = MAHAMANTRA_POSITIONS[mantra_pos]

    phase = get_lila_phase(lila_position)
    cycle = get_mantra_cycle(lila_position)

    return LilaInfo(
        # Mantra level
        position=mantra_pos,
        quarter=pos.quarter.name.lower(),
        guardian=pos.guardian.value,
        word=pos.word.name,
        opcode=pos.opcode.value if pos.opcode is not None else None,  # BOMBENFEST: 0 is valid!
        # Lila level
        lila_position=lila_position,
        phase=phase,
        cycle=cycle,
        is_navadvip=phase == "navadvipa",
        is_puri=phase == "puri",
    )


def next_lila_position(lila_position: int) -> int:
    """Calculate next lila position (wraps at 48). PURE."""
    return (lila_position + 1) % CHAITANYA_LILA


def previous_lila_position(lila_position: int) -> int:
    """Calculate previous lila position (wraps at 0). PURE."""
    return (lila_position - 1) % CHAITANYA_LILA


def lila_to_mantra(lila_position: int) -> Tuple[int, int, str]:
    """
    Convert lila position to mantra position + context.

    Returns:
        (mantra_position, cycle, phase)
    """
    if not 0 <= lila_position < CHAITANYA_LILA:
        raise ValueError(f"Lila position must be 0-47, got {lila_position}")

    mantra_pos = get_mantra_position(lila_position)
    cycle = get_mantra_cycle(lila_position)
    phase = get_lila_phase(lila_position)

    return (mantra_pos, cycle, phase)


# =============================================================================
# CONSTANTS
# =============================================================================

MANTRA_LENGTH = MAHAMANTRA_WORDS  # 16
LILA_LENGTH = CHAITANYA_LILA  # 48
NAVADVIP_END = NAVADVIPA_PHASE  # 24 (exclusive)
PURI_START = NAVADVIPA_PHASE  # 24 (inclusive)


# =============================================================================
# CHANT - The Holy Name
# =============================================================================


def get_chant(separator: str = " ") -> str:
    """Get the complete Mahamantra as string. PURE."""
    words = [pos.word.name.capitalize() for pos in MAHAMANTRA_POSITIONS]
    return separator.join(words)


# =============================================================================
# VERIFICATION
# =============================================================================


def verify_parampara(value: int) -> bool:
    """Verify Parampara connection (% 37 == 0). PURE."""
    return value % 37 == 0


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Types
    "TickInfo",
    "LilaInfo",
    # Mantra functions (0-15)
    "get_tick_info",
    "get_position_by_index",
    "get_position_by_guardian",
    "next_position",
    "previous_position",
    # Lila functions (0-47)
    "get_lila_info",
    "next_lila_position",
    "previous_lila_position",
    "lila_to_mantra",
    # Constants
    "MANTRA_LENGTH",
    "LILA_LENGTH",
    "NAVADVIP_END",
    "PURI_START",
    # Utilities
    "get_chant",
    "verify_parampara",
]
