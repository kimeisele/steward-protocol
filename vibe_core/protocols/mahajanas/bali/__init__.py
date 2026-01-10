"""
BALI - The 10th Mahajana (Surrender/Yield)
==========================================
OpCode: yield_cpu (Bit 15)
Opulence: Vairagya (Renunciation)

King Bali - The Generous Demon King.
Gave everything to Vamana - even his own position.
"sarva-dharman parityajya mam ekam saranam vraja" (BG 18.66)

Bali OWNS all surrender protocols:
- CPU Yielding
- Graceful Shutdown
- Resource Release
- Cooperative Multitasking
- Prapatti (Surrender)

A system that cannot surrender = INFINITE LOOPS = HIRANYAKASHIPU.
Bali proves that even a demon can be liberated through surrender.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class BaliProtocol(Protocol):
    """
    The Surrender Protocol.
    Any system that can yield control must implement this.
    """

    def can_surrender(self) -> bool:
        """Check if surrender is possible."""
        ...

    def surrender(self) -> None:
        """
        Execute immediate cessation.
        After this, process() must return False.
        """
        ...

    def is_surrendered(self) -> bool:
        """Check if already surrendered."""
        ...


class NullBali:
    """
    The Hiranyakashipu Pattern.
    Cannot surrender (documents the anti-pattern).
    """

    def can_surrender(self) -> bool:
        return False

    def surrender(self) -> None:
        pass  # Refuses

    def is_surrendered(self) -> bool:
        return False  # Never


__all__ = ["BaliProtocol", "NullBali"]
