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

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0xbeff6e39"  # GenesisByte: parampara % 37 == 0

from typing import Callable, Dict, List, ParamSpec, Protocol, TypeVar, runtime_checkable

from vibe_core.protocols.naga.types import EventDict, NagaStatus, NagaType, ObservationDict

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

    def receive_proxy_observation(self, observation: ObservationDict) -> None:
        """
        Receive a proxy observation.

        This is the ONE entry point from NagaProxy.
        Narada routes internally to:
        - Chitragupta (timing/profiling)
        - Sesha (audit trail)
        - Kaliya (if exception_type set)

        NagaProxy doesn't know about these - fractal separation.
        """
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

    def receive_proxy_observation(self, observation: ObservationDict) -> None:
        pass  # Silent drop - no observation target

    def export_observations(self) -> List[EventDict]:
        return []

    def get_status(self) -> NagaStatus:
        return NagaStatus(naga_type=NagaType.NARADA, healthy=False, message="Not initialized")
