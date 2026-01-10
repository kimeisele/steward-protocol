"""
NARADA - The 2nd Mahajana (Devotion/Observation)
=================================================
OpCode: pulse_sync (Bit 3)
Opulence: Yashas (Fame/Glory)

"Narada Muni ki Jai!" - The Cosmic Journalist

Narada OWNS all observation protocols:
- Event Bus / Messaging
- Spy / Observer patterns
- Pulse synchronization
- Inter-system communication

Narada travels everywhere, knows everything, reports faithfully.
He does NOT act - he OBSERVES and TRANSMITS.

Existing: protocols/naga/narada.py (to be migrated)
"""

from typing import Protocol, runtime_checkable, Callable, TypeVar, ParamSpec, List, Any

P = ParamSpec("P")
R = TypeVar("R")


@runtime_checkable
class NaradaProtocol(Protocol):
    """
    The Observer Protocol.
    Any system that observes without modifying must implement this.
    """

    def spy(self, func: Callable[P, R]) -> Callable[P, R]:
        """
        Decorator to observe function calls.
        Must NOT modify behavior - pure observation.
        """
        ...

    def broadcast(self, message: Any) -> bool:
        """
        Broadcast a message to all listeners.
        Returns True if at least one listener received.
        """
        ...

    def get_observations(self) -> List[Any]:
        """Return collected observations."""
        ...


class NullNarada:
    """
    The Silent Witness.
    Observes nothing, reports nothing.
    """

    def spy(self, func: Callable[P, R]) -> Callable[P, R]:
        return func  # Pass-through

    def broadcast(self, message: Any) -> bool:
        return False

    def get_observations(self) -> List[Any]:
        return []


__all__ = ["NaradaProtocol", "NullNarada"]
