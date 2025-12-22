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

    def on_agent_registered(self, kernel: "RealVibeKernel", agent_id: str) -> None:
        """
        Set initial resource quota for newly registered agent.

        OPUS-209: This logic was extracted from kernel register_agent().
        The kernel only registers; the plugin handles quota management.
        """
        if not self._manager:
            return

        # Set initial resource quota (default: 100 credits)
        self._manager.set_quota(agent_id, credits=100)

        # Enforce quota if process is running
        if kernel.process_manager:
            proc_info = kernel.process_manager.processes.get(agent_id)
            if proc_info and proc_info.process.is_alive():
                self._manager.enforce_quota(agent_id, proc_info.process)
                logger.debug(f"📊 Quota enforced for {agent_id}")

    def get_api(self) -> Optional[ResourceManager]:
        """Return the resource manager for direct access if needed."""
        return self._manager
