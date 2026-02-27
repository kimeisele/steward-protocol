"""
KALA SUBSTRATE - TimeKeeper Implementation
==========================================

"kāla-cakra" - The Wheel of Time.

Implements the Math of Time:
- 16 Ticks = 1 Mantra
- 48 Ticks = 1 Lila
- 1728 Ticks = 1 Mala

"""

from vibe_core.mahamantra.protocols._seed import KSETRAJNA, QUARTERS

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = QUARTERS
__genesis__ = "0x8dfd7ced"  # GenesisByte: parampara % 37 == 0

from typing import Final

from vibe_core.mahamantra.protocols._kala import KalaProtocol, KalaTime
from vibe_core.mahamantra.protocols._seed import MALA, TRINITY, WORDS  # SSOT

# --- CONSTANTS (DERIVED FROM _seed.py) ---
LILA_TICKS: Final[int] = WORDS * TRINITY  # 16 × 3 = 48
MALA_MANTRAS: Final[int] = MALA  # 108
MALA_TICKS: Final[int] = WORDS * MALA  # 16 × 108 = 1728


class TimeKeeper(KalaProtocol):
    """
    The Gearbox of Time.
    Tracks total ticks and converts to Cosmic Time.
    """

    def __init__(self, start_ticks: int = 0) -> None:
        self._total_ticks = start_ticks

    def advance(self) -> KalaTime:
        """Advance time by one tick and return new time."""
        self._total_ticks += KSETRAJNA
        return self.get_time()

    def get_time(self) -> KalaTime:
        """Calculate current Cosmic Time from total ticks."""
        t = self._total_ticks

        # 1. Tick in Mantra (0-15)
        tick_in_mantra = t % WORDS

        # 2. Mantra in Mala (0-107)
        # Total mantras elapsed
        total_mantras = t // WORDS
        mantra_in_mala = total_mantras % MALA_MANTRAS

        # 3. Lila Position (0-47)
        # Cycle of 3 Mantras
        lila_position = t % LILA_TICKS

        # 4. Mala Count
        mala_count = t // MALA_TICKS

        return KalaTime(
            total_ticks=t,
            tick_in_mantra=tick_in_mantra,
            mantra_in_mala=mantra_in_mala,
            lila_position=lila_position,
            mala_count=mala_count,
        )

    def set_ticks(self, ticks: int) -> None:
        """Force set time (e.g. from persistence)."""
        self._total_ticks = ticks
