"""
MahaManas — The Cognitive Mind Instance (Tattva #6)
====================================================

Singleton access to the MahaManas cognitive engine.

Usage:
    from vibe_core.mahamantra.substrate.manas import get_manas

    manas = get_manas()
    clean = manas.perceive(entries)
    verdicts = manas.decide(clean)
    manas.learn(verdicts[0], success=True)
"""

from typing import Optional

from vibe_core.mahamantra.substrate.manas.manas_core import MahaManas

_manas_instance: Optional[MahaManas] = None


def get_manas() -> MahaManas:
    """Get the singleton MahaManas instance."""
    global _manas_instance
    if _manas_instance is None:
        _manas_instance = MahaManas()
    return _manas_instance
