"""
ASHTASATTVIKA BHAVA - The 8 Transcendental Ecstasies
====================================================

"In the beginning, there may not be the presence of all transcendental ecstasies,
which are eight in number. These are:
(1) being stopped as though dumb,
(2) perspiration,
(3) standing up of hairs on the body,
(4) dislocation of voice,
(5) trembling,
(6) fading of the body,
(7) crying in ecstasy, and
(8) trance."
- Srila Prabhupada

These are OBSERVABLE STATES in the system.
They manifest as side-effects of chanting.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prithu"
__position__ = 0
__genesis__ = "0x1cf32409"  # GenesisByte: parampara % 37 == 0

from enum import IntEnum
from typing import List, Final


class SattvikaBhava(IntEnum):
    """
    The 8 transcendental ecstasies (Observable States).

    Sanskrit terms with computational mappings:
    """
    STAMBHA = 0      # 1. Being stopped as dumb (freeze/pause)
    SVEDA = 1        # 2. Perspiration (resource heat/load)
    ROMANCA = 2      # 3. Standing of hairs (alert state/interrupt)
    SVARA_BHEDA = 3  # 4. Dislocation of voice (output transformation)
    KAMPA = 4        # 5. Trembling (oscillation/instability)
    VAIVARNYA = 5    # 6. Fading of body (resource release/GC)
    ASHRU = 6        # 7. Crying in ecstasy (buffer overflow/emit)
    PRALAYA = 7      # 8. Trance (transcendental state/suspend)


# Sanskrit names with IAST transliteration
BHAVA_NAMES: Final[dict] = {
    SattvikaBhava.STAMBHA: ("stambha", "स्तम्भ"),
    SattvikaBhava.SVEDA: ("sveda", "स्वेद"),
    SattvikaBhava.ROMANCA: ("romāñca", "रोमाञ्च"),
    SattvikaBhava.SVARA_BHEDA: ("svara-bheda", "स्वर-भेद"),
    SattvikaBhava.KAMPA: ("kampa", "कम्प"),
    SattvikaBhava.VAIVARNYA: ("vaivarṇya", "वैवर्ण्य"),
    SattvikaBhava.ASHRU: ("aśru", "अश्रु"),
    SattvikaBhava.PRALAYA: ("pralaya", "प्रलय"),
}


class BhavaState:
    """
    Bitmask container for tracking active bhava states.

    Usage:
        state = BhavaState()
        state.set(SattvikaBhava.ROMANCA)
        state.set(SattvikaBhava.ASHRU)
        print(state.active)  # [ROMANCA, ASHRU]
    """
    __slots__ = ['_mask']

    def __init__(self, initial: int = 0) -> None:
        self._mask = initial

    def set(self, bhava: SattvikaBhava) -> None:
        """Activate an ecstatic state."""
        self._mask |= (1 << bhava.value)

    def clear(self, bhava: SattvikaBhava) -> None:
        """Deactivate an ecstatic state."""
        self._mask &= ~(1 << bhava.value)

    def has(self, bhava: SattvikaBhava) -> bool:
        """Check if ecstatic state is active."""
        return bool(self._mask & (1 << bhava.value))

    def reset(self) -> None:
        """Clear all bhava states."""
        self._mask = 0

    @property
    def active(self) -> List[SattvikaBhava]:
        """Get all currently active ecstatic states."""
        return [b for b in SattvikaBhava if self.has(b)]

    @property
    def count(self) -> int:
        """Number of active ecstatic states (0-8)."""
        return bin(self._mask).count('1')

    @property
    def is_in_trance(self) -> bool:
        """True if PRALAYA (trance) state is active."""
        return self.has(SattvikaBhava.PRALAYA)

    @property
    def mask(self) -> int:
        """Raw bitmask value."""
        return self._mask

    def __repr__(self) -> str:
        return f"BhavaState(mask=0b{self._mask:08b}, active={[b.name for b in self.active]})"


__all__ = [
    "SattvikaBhava",
    "BHAVA_NAMES",
    "BhavaState",
]
