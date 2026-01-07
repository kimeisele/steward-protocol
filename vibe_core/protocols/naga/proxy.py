"""
NAGA PROXY PROTOCOL - The Balarama Pattern Interface

"Er wird zum Bett wenn Krishna schläft..."

Defines the contract for Dynamic Wrappers that inject Naga Intelligence.
Separated from implementation (vibe_core/naga/proxy.py).

Responsibilities:
- Intercept method calls
- Route to Nagas (Narada, Takshaka, etc.)
- Preserve type safety of wrapped object
"""

from typing import Protocol, TypeVar, runtime_checkable

T = TypeVar("T", covariant=True)


@runtime_checkable
class NagaProxyProtocol(Protocol[T]):
    """
    Protocol for NagaProxy.

    Ensures that any proxy implementation provides access to the
    underlying service and respects the Naga Governance contract.
    """

    @property
    def unwrap(self) -> T:
        """
        Get the unwrapped service.

        Use sparingly - prefer working through the proxy.
        """
        ...

    @property
    def _service_name(self) -> str:
        """Name of the wrapped service for logging/metrics."""
        ...

    def clear_observations(self) -> int:
        """Clear local observation buffer."""
        ...
