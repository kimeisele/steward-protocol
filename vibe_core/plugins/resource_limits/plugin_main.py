"""
Resource Limits Plugin - Resource Quota Management as a Service

OPUS-209 Phase 2.3: Extracted from kernel_impl.py

This is a CRITICAL PLUGIN - the kernel needs resource control to prevent
runaway agents from consuming all system resources.

Philosophy:
    "Credits are not numbers in a database. Credits are CPU cycles and memory bytes.
    The economy is the operating system."
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, Optional, Set

from vibe_core.di import ServiceRegistry
from vibe_core.plugin_protocol import HookResult, KernelPlugin
from vibe_core.protocols.resource import ResourceSupervisorProtocol
from vibe_core.resource_manager import ResourceManager

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("RESOURCE_LIMITS")


class ResourceLimitsPlugin(KernelPlugin):
    """
    CRITICAL PLUGIN - Kernel needs resource control.

    Manages agent resource quotas:
    - Set quotas based on credit balance
    - Enforce CPU/RAM limits via psutil
    - Monitor usage and detect violations

    The kernel no longer instantiates ResourceManager directly.
    Instead, it accesses the manager via:
        manager = ServiceRegistry.get(ResourceSupervisorProtocol)

    Or via backward-compatible:
        kernel.resource_manager
    """

    plugin_id = "resource_limits"

    def __init__(self):
        self._manager: Optional[ResourceManager] = None

    @property
    def dependencies(self) -> Set[str]:
        """No dependencies - core infrastructure."""
        return set()

    @property
    def priority(self) -> int:
        """High priority - must boot early."""
        return 15

    def on_boot(
        self,
        kernel: "RealVibeKernel",
        config: Optional[Dict[str, Any]] = None,
    ) -> HookResult:
        """
        Boot the resource manager.

        Creates the ResourceManager instance and registers it
        in the ServiceRegistry for kernel access.
        """
        try:
            # Create the resource manager
            self._manager = ResourceManager()

            # Register in ServiceRegistry for DI
            ServiceRegistry.register(ResourceSupervisorProtocol, self._manager)

            # Also set on kernel for backward compatibility
            kernel.resource_manager = self._manager

            logger.info("📊 Resource Limits Plugin booted - ResourceManager registered")
            return HookResult.ok()

        except Exception as e:
            logger.critical(f"❌ CRITICAL: Resource Limits Plugin failed to boot: {e}")
            return HookResult.fatal(str(e))

    def get_api(self) -> Optional[ResourceManager]:
        """Return the resource manager for direct access if needed."""
        return self._manager
