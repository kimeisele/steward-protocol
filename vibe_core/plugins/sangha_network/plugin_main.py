"""
Sangha Network Plugin - Network Gateway as a Service

OPUS-209 Phase 2: Extracted from kernel_impl.py

This plugin encapsulates the NetworkGateway, removing the direct
instantiation from the kernel. The gateway is now a service that
can be accessed via ServiceRegistry.

The name "Sangha" comes from Sanskrit meaning "community/assembly" -
the network layer that connects the vibe ecosystem.
"""

import asyncio
import logging
import threading
from typing import TYPE_CHECKING, Any, Dict, Optional

from vibe_core.di import ServiceRegistry
from vibe_core.gateway.api import NetworkGateway
from vibe_core.plugin_protocol import HookResult, KernelPlugin
from vibe_core.protocols.network import NetworkGatewayProtocol

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("SANGHA_NETWORK")


class SanghaNetworkPlugin(KernelPlugin):
    """
    Network Gateway Plugin - Provides HTTP REST API for VibeOS.

    Responsibilities:
    - Create and manage NetworkGateway lifecycle
    - Register gateway in ServiceRegistry for DI
    - Handle async startup via gateway task
    - Clean shutdown of network services

    The kernel no longer instantiates NetworkGateway directly.
    Instead, it accesses the gateway via:
        gateway = ServiceRegistry.get(NetworkGatewayProtocol)
    """

    plugin_id = "sangha_network"

    def __init__(self):
        self._gateway: Optional[NetworkGateway] = None
        self._gateway_thread: Optional[threading.Thread] = None
        self._gateway_loop: Optional[asyncio.AbstractEventLoop] = None

    def on_boot(
        self,
        kernel: "RealVibeKernel",
        config: Optional[Dict[str, Any]] = None,
    ) -> HookResult:
        """
        Boot the network gateway.

        Creates the NetworkGateway instance and registers it
        in the ServiceRegistry for kernel access.
        """
        try:
            # Create gateway with Prakriti dependency
            self._gateway = NetworkGateway(kernel.prakriti)

            # Register in ServiceRegistry for DI
            ServiceRegistry.register(NetworkGatewayProtocol, self._gateway)

            # Also set on kernel for backward compatibility
            kernel.gateway = self._gateway
            kernel._gateway_thread = None
            kernel._gateway_loop = None

            logger.info("🌐 Sangha Network Plugin booted - Gateway registered")
            return HookResult.ok()

        except Exception as e:
            logger.error(f"❌ Sangha Network Plugin failed to boot: {e}")
            return HookResult.error(str(e))

    def on_shutdown(self, kernel: "RealVibeKernel") -> HookResult:
        """Stop the gateway on kernel shutdown."""
        if self._gateway:
            try:
                # Gateway stop is async, need to handle carefully
                loop = asyncio.new_event_loop()
                loop.run_until_complete(self._gateway.stop())
                loop.close()
                logger.info("🌐 Sangha Network Plugin shutdown complete")
            except Exception as e:
                logger.warning(f"⚠️ Gateway shutdown error: {e}")

        return HookResult.ok()

    async def start_gateway_async(self) -> None:
        """Start the gateway in async context."""
        if self._gateway:
            await self._gateway.start()

    async def stop_gateway_async(self) -> None:
        """Stop the gateway in async context."""
        if self._gateway:
            await self._gateway.stop()

    def get_api(self) -> Optional[NetworkGateway]:
        """Return the gateway for direct access if needed."""
        return self._gateway
