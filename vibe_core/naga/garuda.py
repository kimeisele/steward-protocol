"""
GARUDA - The Eagle. Controller of Nagas.

"Garuda is the carrier of Vishnu. When Garuda is present, the Nagas hide."

Implementation of GarudaProtocol using ContextVars.
"""

from contextlib import contextmanager
from contextvars import ContextVar
from typing import Generator

from vibe_core.protocols.naga import GarudaProtocol


class Garuda(GarudaProtocol):
    """
    The Eagle. Singleton-like recursion guard.

    Uses ContextVars to track recursion depth across async/sync boundaries.
    """

    def __init__(self):
        # flight_depth: 0 = Grounded, >0 = Flying
        self._flight_depth: ContextVar[int] = ContextVar("garuda_flight_depth", default=0)

    @property
    def is_flying(self) -> bool:
        """Check if Garuda is currently flying (recursion active)."""
        return self._flight_depth.get() > 0

    @contextmanager
    def fly(self) -> Generator[None, None, None]:
        """
        Spread wings. Suppress Naga governance for the duration.
        """
        token = self._flight_depth.set(self._flight_depth.get() + 1)
        try:
            yield
        finally:
            self._flight_depth.reset(token)


# Global Garuda Instance
garuda = Garuda()
