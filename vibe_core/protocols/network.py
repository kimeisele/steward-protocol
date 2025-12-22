"""
NetworkGateway Protocol - OPUS-209 Phase 2

Defines the interface for network gateway implementations.
This allows the kernel to depend on the protocol, not the concrete implementation.
"""

from typing import Protocol, runtime_checkable


@runtime_checkable
class NetworkGatewayProtocol(Protocol):
    """
    Protocol for network gateway implementations.

    The gateway provides HTTP REST API access to the kernel.
    Implementations handle server lifecycle (start/stop).
    """

    async def start(self) -> None:
        """Start the API server."""
        ...

    async def stop(self) -> None:
        """Stop the API server."""
        ...
