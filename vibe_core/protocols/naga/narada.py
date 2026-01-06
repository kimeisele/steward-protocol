"""
NARADA Protocol - Der Spion (Observer Protocol)

Narada - Der kosmische Journalist. Reist überall, weiß alles.
"Narada Muni ki Jai!" - The Messenger of the Gods.

Responsibilities:
- Intercept function calls via @spy decorator
- Observe without modifying (pure observation)
- Report to Cortex for pattern analysis
- Sign all observations (37th Principle)

Integration:
- Does NOT register as CorrectionHandler (pure observer)
- Reports patterns to other NAGAs
- Enables proactive drift detection
"""

from typing import Callable, Dict, List, ParamSpec, Protocol, TypeVar, runtime_checkable

from vibe_core.protocols.naga.types import EventDict, NagaStatus, NagaType

# ParamSpec for proper decorator typing (eliminates Any)
P = ParamSpec("P")
R = TypeVar("R")


@runtime_checkable
class NaradaProtocol(Protocol):
    """
    Narada - Der kosmische Journalist. Reist überall, weiß alles.

    "Narada Muni ki Jai!" - The Messenger of the Gods.

    Responsibilities:
    - Intercept function calls via @spy decorator
    - Observe without modifying (pure observation)
    - Report to Cortex for pattern analysis
    - Sign all observations (37th Principle)

    Integration:
    - Does NOT register as CorrectionHandler (pure observer)
    - Reports patterns to other NAGAs
    - Enables proactive drift detection

    Usage:
        narada = ServiceRegistry.get(NaradaProtocol)
        @narada.spy
        def my_function(x, y):
            return x + y
    """

    def spy(self, func: Callable[P, R]) -> Callable[P, R]:
        """Decorator to observe function calls."""
        ...

    def export_observations(self) -> List[EventDict]:
        """Export and clear observation buffer."""
        ...

    def get_status(self) -> NagaStatus:
        """Get NAGA health status."""
        ...


# =============================================================================
# NULL IMPLEMENTATION (Arjuna Pattern)
# =============================================================================


class NullNarada:
    """No-op Narada for when observation is unavailable."""

    def spy(self, func: Callable[P, R]) -> Callable[P, R]:
        return func  # Pass-through decorator

    def export_observations(self) -> List[EventDict]:
        return []

    def get_status(self) -> NagaStatus:
        return NagaStatus(naga_type=NagaType.NARADA, healthy=False, message="Not initialized")