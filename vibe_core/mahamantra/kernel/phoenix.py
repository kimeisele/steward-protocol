"""
PHOENIX - State Persistence (THE GUARANTEE)
===========================================

"ajo 'pi sann avyayātmā bhūtānām īśvaro 'pi san"
"Though unborn and eternal, the Lord of all beings..."
— Bhagavad Gita 4.6

THE PHOENIX GUARANTEE:
======================
Code assumes it can be killed ANYTIME.
On restart: Read state → Continue where stopped.

WATERTIGHT: All constants from SSOT (seed.py). NO MAGIC NUMBERS.
"""

from __future__ import annotations

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "nrisimha"
__position__ = 12
__genesis__ = "0x6c4ad0f5"  # GenesisByte: parampara % 37 == 0

import json
from pathlib import Path
from typing import Final, Optional, TypedDict

# IMPORT FROM SSOT - NO HARDCODED NUMBERS!
from vibe_core.mahamantra.protocols._seed import (
    PARAMPARA,  # 37
    WORDS,  # 16
    LILA,  # 48
)


# =============================================================================
# STATE SCHEMA
# =============================================================================


class PhoenixState(TypedDict):
    """The minimal state that must survive death."""

    tick: int  # Current position (0 to WORDS-1)
    lila_tick: int  # Current lila position (0 to LILA-1)
    parampara: int  # Verification constant (PARAMPARA)


# =============================================================================
# STATE LOCATION
# =============================================================================

# Store in .vibe_state/ (gitignored, local to repo)
STATE_DIR: Final[Path] = Path.cwd() / ".vibe_state"
STATE_FILE: Final[Path] = STATE_DIR / "mahamantra_tick.json"


# =============================================================================
# PERSISTENCE FUNCTIONS
# =============================================================================


def save_state(tick: int, lila_tick: int) -> None:
    """
    Save current state to disk.

    PHOENIX PATTERN: Called after every significant mutation.
    Failure to save = log error but continue (graceful degradation).

    Args:
        tick: Current tick position (0 to WORDS-1)
        lila_tick: Current lila position (0 to LILA-1)
    """
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)

        state: PhoenixState = {
            "tick": tick,
            "lila_tick": lila_tick,
            "parampara": PARAMPARA,  # From seed.py
        }

        # Atomic write: write to temp, then rename
        temp_file = STATE_FILE.with_suffix(".tmp")
        temp_file.write_text(json.dumps(state, indent=2))
        temp_file.replace(STATE_FILE)

    except Exception:
        # GRACEFUL DEGRADATION: Log would go here, but we continue
        # State loss is acceptable (resets to 0), death is not
        pass


def load_state() -> Optional[PhoenixState]:
    """
    Load state from disk.

    PHOENIX PATTERN: Called at module init BEFORE any ticks.

    Returns:
        PhoenixState if valid state exists, None otherwise
    """
    try:
        if not STATE_FILE.exists():
            return None

        data = json.loads(STATE_FILE.read_text())

        # Verify parampara (from seed.py, not hardcoded!)
        if data.get("parampara") != PARAMPARA:
            return None  # Corrupted state

        # Verify tick bounds (using WORDS and LILA from seed.py)
        tick = data.get("tick", 0)
        lila_tick = data.get("lila_tick", 0)

        if not (0 <= tick < WORDS and 0 <= lila_tick < LILA):
            return None  # Invalid positions

        return PhoenixState(
            tick=tick,
            lila_tick=lila_tick,
            parampara=PARAMPARA,
        )

    except Exception:
        # GRACEFUL DEGRADATION: Corrupted file → fresh start
        return None


def clear_state() -> None:
    """
    Clear persisted state.

    Used for testing or explicit reset.
    """
    try:
        if STATE_FILE.exists():
            STATE_FILE.unlink()
    except Exception:
        pass


# =============================================================================
# INITIALIZATION
# =============================================================================


def init_phoenix() -> tuple[int, int]:
    """
    Initialize Phoenix state on module load.

    THE RESURRECTION:
    -----------------
    1. Try to load state from disk
    2. If found and valid → restore positions
    3. If not → start from 0

    Returns:
        (tick, lila_tick) tuple - either restored or fresh (0, 0)
    """
    state = load_state()

    if state:
        # RESURRECTION: Continue where we stopped
        return state["tick"], state["lila_tick"]
    else:
        # FRESH START: No state or corrupted
        return 0, 0
