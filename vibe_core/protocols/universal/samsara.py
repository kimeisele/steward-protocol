"""
SAMSARA PROTOCOL - The Eternal Cycle (Layer 1)

"Punar api jananam punar api maranam" - Birth again, death again.

SCOPE:
This protocol manages the Lifecycle Stream (Samsara).
It ensures that 'The Eternal Now' (SovereignContext) is injected fresh
into every iteration of the system loop.

THE PROBLEM (MAYAVAD):
If we iterate a list with a static Context, the Context expires (Time Dilation).
The "Tail" of the list becomes dead/unauthorized.

THE SOLUTION (SAMSARA):
We use a Generator (Stream) that regenerates the SovereignContext
at the exact moment of yield.
This guarantees that 100% of the stream is "Alive" and "Authorized".
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "vyasa"
__position__ = 4
__genesis__ = "0x1efd1140"  # GenesisByte: parampara % 37 == 0

import time
from datetime import datetime
from typing import (
    Any,
    Callable,
    Iterable,
    Iterator,
    Optional,
    Protocol,
    Tuple,
    TypeVar,
    runtime_checkable,
)

from .types import SovereignContext

T = TypeVar("T")

# =============================================================================
# SAMSARA PROTOCOL (The Interface)
# =============================================================================


@runtime_checkable
class SamsaraProtocol(Protocol):
    """
    The Cycle Manager.

    Responsible for bridging the 'Eternal' (Identity) with the 'Now' (Action).
    """

    def breathe(self, identity_id: str) -> SovereignContext:
        """Create a fresh Context for THIS moment (Inhalation)."""
        ...

    def stream(self, iterable: Iterable[T], identity_id: str) -> Iterator[Tuple[T, SovereignContext]]:
        """
        Transform a dead iterable into a Living Stream.
        Yields (Item, FreshContext).
        """
        ...


# =============================================================================
# SAMSARA ENGINE (The Implementation)
# =============================================================================


class SamsaraEngine:
    """
    The Implementation of the Cycle.
    """

    def __init__(self, signer_func: Optional[Callable[[str], str]] = None):
        """
        Args:
            signer_func: Function to sign the moment.
                         If None, uses a mock hash (for internal loops).
        """
        self._signer_func = signer_func or (lambda x: f"sig_{hash(x)}")

    def breathe(self, identity_id: str) -> SovereignContext:
        """
        INHALATION: Create the SovereignContext for NOW.
        """
        timestamp = time.time()
        # The signature binds Identity + Time
        signature = self._signer_func(f"{identity_id}:{timestamp}")

        return SovereignContext(
            identity_id=identity_id, signature=signature, timestamp=timestamp, intent_id="LIVING_WILL"
        )

    def stream(self, iterable: Iterable[T], identity_id: str) -> Iterator[Tuple[T, SovereignContext]]:
        """
        THE WHEEL OF TIME: Iterate with Fresh Contexts.
        """
        for item in iterable:
            # 1. Breathe In (New Context)
            ctx = self.breathe(identity_id)

            # 2. Yield (Action)
            yield item, ctx

            # 3. Breathe Out (Cleanup/Pause - optional)
            # In a real system, we might handle backpressure here.


# =============================================================================
# THE VOID (Null Implementation)
# =============================================================================


class NullSamsara:
    """The Void - No Cycles, Static Time."""

    def breathe(self, identity_id: str) -> SovereignContext:
        return SovereignContext(identity_id, "void_sig")

    def stream(self, iterable: Iterable[T], identity_id: str) -> Iterator[Tuple[T, SovereignContext]]:
        ctx = self.breathe(identity_id)
        for item in iterable:
            yield item, ctx  # MAYAVAD: Reuse same context (Decays)
