"""
VENU - Krishna's Flute (Pure Functions)
=======================================

"venum kvanantam aravinda-dalayataksham"
"Krishna plays His flute, with lotus-petal eyes"
— Brahma-samhita 5.30

DIES IST EINE BIBLIOTHEK, KEIN MOTOR.
=====================================

    Substrate = Die KARTE (stateless, pure math)
    Venu/     = Der REISENDE (hat state, Phase 2)

Diese Datei beantwortet NUR:
    "Welche Position bei Tick 25?" → 9 (25 % 16)
    "Welcher Cycle bei Tick 100?" → 6 (100 // 16)
    "Ist Tick 108 ein Mala-Ende?" → Nein (108 % 1728 != 0)

Diese Datei beantwortet NICHT:
    "Was ist der aktuelle Tick?" → Das ist Runtime's Job!

KEIN STATE. KEINE COUNTER. NUR PURE FUNCTIONS.
"""

from __future__ import annotations

from vibe_core.mahamantra.protocols._seed import KSETRAJNA, QUARTERS

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = QUARTERS
__genesis__ = "0xdb705f2f"  # GenesisByte: parampara % 37 == 0


from vibe_core.mahamantra.protocols._seed import (
    MALA,
    PRANA_DURATION_S,
    QUARTERS,
    TICK_INTERVAL_MS,
)
from vibe_core.mahamantra.protocols._venu import (
    VENU_POSITIONS,
    VENU_POSITIONS_PER_PHASE,
    VENU_TICKS_PER_MALA,
)

# =============================================================================
# TYPES
# =============================================================================
# TickState imported from seed/types.py (SSOT)
from vibe_core.mahamantra.seed.types import TickState
from vibe_core.mahamantra.substrate.seed import (
    MAHAMANTRA,
    QUARTER_NAMES,
    HolyName,
    Quarter,
)

# =============================================================================
# PURE FUNCTIONS - Tick Calculations
# =============================================================================


def tick_to_position(tick: int) -> int:
    """
    Convert tick count to position (0-15).

    PURE FUNCTION: No state, no side effects.

    Args:
        tick: The tick count (monotonically increasing)

    Returns:
        Position in the cycle (0-15)
    """
    return tick % VENU_POSITIONS


def tick_to_cycle(tick: int) -> int:
    """
    Convert tick count to cycle number.

    PURE FUNCTION: No state, no side effects.

    Args:
        tick: The tick count

    Returns:
        Cycle number (tick // 16)
    """
    return tick // VENU_POSITIONS


def tick_to_prana(tick: int) -> int:
    """
    Convert tick count to Prana number within current Mala.

    PURE FUNCTION: No state, no side effects.

    Args:
        tick: The tick count

    Returns:
        Prana number within Mala (0-107)
    """
    cycle = tick_to_cycle(tick)
    return cycle % MALA


def tick_to_mala(tick: int) -> int:
    """
    Convert tick count to Mala number.

    PURE FUNCTION: No state, no side effects.

    Args:
        tick: The tick count

    Returns:
        Mala number (tick // 1728)
    """
    return tick // VENU_TICKS_PER_MALA


def tick_to_quarter(tick: int) -> Quarter:
    """
    Convert tick count to Quarter enum.

    PURE FUNCTION: No state, no side effects.

    Args:
        tick: The tick count

    Returns:
        Quarter (GENESIS, DHARMA, KARMA, MOKSHA)
    """
    position = tick_to_position(tick)
    return Quarter(position // VENU_POSITIONS_PER_PHASE)


def tick_to_word(tick: int) -> HolyName:
    """
    Convert tick count to the Holy Name at that position.

    PURE FUNCTION: No state, no side effects.

    Args:
        tick: The tick count

    Returns:
        HolyName (HARE, KRISHNA, RAMA)
    """
    position = tick_to_position(tick)
    return MAHAMANTRA[position]


def is_downbeat(tick: int) -> bool:
    """
    Check if tick is a downbeat (position 0).

    PURE FUNCTION: No state, no side effects.

    Args:
        tick: The tick count

    Returns:
        True if position == 0
    """
    return tick_to_position(tick) == 0


def is_mala_complete(tick: int) -> bool:
    """
    Check if a Mala just completed at this tick.

    PURE FUNCTION: No state, no side effects.

    Args:
        tick: The tick count

    Returns:
        True if tick is exactly at a Mala boundary (and tick > 0)
    """
    return tick > 0 and tick % VENU_TICKS_PER_MALA == 0


def get_tick_state(tick: int) -> TickState:
    """
    Get complete state for a tick.

    PURE FUNCTION: No state, no side effects.

    Args:
        tick: The tick count

    Returns:
        TickState with all derived values
    """
    position = tick_to_position(tick)
    quarter = tick_to_quarter(tick)
    word = tick_to_word(tick)

    return TickState(
        tick=tick,
        position=position,
        cycle=tick_to_cycle(tick),
        prana=tick_to_prana(tick),
        mala=tick_to_mala(tick),
        quarter=QUARTER_NAMES[quarter.value],
        word=word.name,
        is_downbeat=position == 0,
        is_mala_complete=is_mala_complete(tick),
    )


# =============================================================================
# PURE FUNCTIONS - Position Calculations
# =============================================================================


def position_to_quarter(position: int) -> Quarter:
    """
    Convert position to Quarter.

    Args:
        position: Position (0-15)

    Returns:
        Quarter enum
    """
    if not 0 <= position < VENU_POSITIONS:
        raise ValueError(f"Position must be 0-{VENU_POSITIONS - KSETRAJNA}, got {position}")
    return Quarter(position // VENU_POSITIONS_PER_PHASE)


def position_to_word(position: int) -> HolyName:
    """
    Convert position to Holy Name.

    Args:
        position: Position (0-15)

    Returns:
        HolyName at that position
    """
    if not 0 <= position < VENU_POSITIONS:
        raise ValueError(f"Position must be 0-{VENU_POSITIONS - KSETRAJNA}, got {position}")
    return MAHAMANTRA[position]


def next_position(position: int) -> int:
    """
    Get the next position (wraps at 16).

    Args:
        position: Current position (0-15)

    Returns:
        Next position (0-15)
    """
    return (position + KSETRAJNA) % VENU_POSITIONS


def previous_position(position: int) -> int:
    """
    Get the previous position (wraps at 0).

    Args:
        position: Current position (0-15)

    Returns:
        Previous position (0-15)
    """
    return (position - KSETRAJNA) % VENU_POSITIONS


# =============================================================================
# PURE FUNCTIONS - Timing Calculations
# =============================================================================


def tick_to_ms(tick: int) -> int:
    """
    Convert tick count to milliseconds.

    Args:
        tick: The tick count

    Returns:
        Elapsed milliseconds
    """
    return tick * TICK_INTERVAL_MS


def ms_to_tick(ms: int) -> int:
    """
    Convert milliseconds to tick count (floored).

    Args:
        ms: Milliseconds

    Returns:
        Tick count (floored to integer)
    """
    return ms // TICK_INTERVAL_MS


def tick_to_seconds(tick: int) -> float:
    """
    Convert tick count to seconds.

    Args:
        tick: The tick count

    Returns:
        Elapsed seconds
    """
    return tick * TICK_INTERVAL_MS / 1000


def mala_duration_seconds() -> int:
    """
    Get the duration of one Mala in seconds.

    Returns:
        432 seconds (JIVA_CYCLE)
    """
    return MALA * PRANA_DURATION_S  # 108 × 4 = 432


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Types
    "TickState",
    # Tick functions
    "tick_to_position",
    "tick_to_cycle",
    "tick_to_prana",
    "tick_to_mala",
    "tick_to_quarter",
    "tick_to_word",
    "is_downbeat",
    "is_mala_complete",
    "get_tick_state",
    # Position functions
    "position_to_quarter",
    "position_to_word",
    "next_position",
    "previous_position",
    # Timing functions
    "tick_to_ms",
    "ms_to_tick",
    "tick_to_seconds",
    "mala_duration_seconds",
]
