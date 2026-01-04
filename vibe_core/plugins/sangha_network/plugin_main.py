"""
Sangha Network Plugin - Network Gateway as a Service

OPUS-209 Phase 2: Extracted from kernel_impl.py
OPUS-210: PluginStateContract compliant

This plugin encapsulates the NetworkGateway, removing the direct
instantiation from the kernel. The gateway is now a service that
can be accessed via ServiceRegistry.

The name "Sangha" comes from Sanskrit meaning "community/assembly" -
the network layer that connects the vibe ecosystem.
"""

import asyncio
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from vibe_core.di import ServiceRegistry
from vibe_core.gateway.api import NetworkGateway
from vibe_core.plugin_protocol import HookResult, KernelPlugin
from vibe_core.protocols.network import NetworkGatewayProtocol

if TYPE_CHECKING:
    from vibe_core.protocols.kernel_protocol import KernelProtocol

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

    OPUS-210: Implements PluginStateContract for Prakriti integration.
    """

    plugin_id = "sangha_network"

    # State paths for PluginStateContract
    STATE_DIR = Path(".vibe/state/plugins/sangha_network")

    def __init__(self):
        self._gateway: Optional[NetworkGateway] = None
        self._gateway_thread: Optional[threading.Thread] = None
        self._gateway_loop: Optional[asyncio.AbstractEventLoop] = None
        self._request_count: int = 0
        self._start_time: Optional[str] = None

    # =========================================================================
    # PluginStateContract Implementation (OPUS-210)
    # =========================================================================

    def get_state_paths(self) -> List[Path]:
        """Return paths where this plugin stores state."""
        return [self.STATE_DIR]

    def snapshot_state(self) -> Dict[str, Any]:
        """Return current runtime state for backup."""
        return {
            "version": 1,
            "gateway_active": self._gateway is not None,
            "request_count": self._request_count,
            "start_time": self._start_time,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def restore_state(self, snapshot: Dict[str, Any]) -> None:
        """Restore state from snapshot (crash recovery)."""
        if snapshot.get("version") == 1:
            self._request_count = snapshot.get("request_count", 0)
            # gateway is recreated on boot, not restored

    def on_boot(
        self,
        kernel: "KernelProtocol",
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

    def on_shutdown(self, kernel: "KernelProtocol") -> HookResult:
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
