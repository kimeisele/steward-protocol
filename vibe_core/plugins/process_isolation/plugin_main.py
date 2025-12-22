"""
Process Isolation Plugin - Agent Process Management as a Service

OPUS-209 Phase 2.2: Extracted from kernel_impl.py

This is a CRITICAL PLUGIN - the kernel cannot run agents without it.
It encapsulates the ProcessManager and provides process supervision
via the ServiceRegistry.

The name reflects its primary purpose: isolating agent execution
in separate processes so one crash doesn't kill the kernel.

Philosophy:
    "The Kernel is the Temple. Agents are the visitors.
    If a visitor collapses, the Temple stands."
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, Optional, Set

from vibe_core.di import ServiceRegistry
from vibe_core.plugin_protocol import HookResult, KernelPlugin
from vibe_core.process_manager import ProcessManager
from vibe_core.protocols.process import ProcessSupervisorProtocol

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger("PROCESS_ISOLATION")


class ProcessIsolationPlugin(KernelPlugin):
    """
    CRITICAL PLUGIN - Kernel cannot function without this.

    Manages agent process lifecycle:
    - Spawn isolated processes for agents
    - Route tasks between kernel and agents
    - Monitor health and restart crashed agents (Narasimha)
    - Clean shutdown of all processes

    The kernel no longer instantiates ProcessManager directly.
    Instead, it accesses the manager via:
        manager = ServiceRegistry.get(ProcessSupervisorProtocol)

    Or via backward-compatible:
        kernel.process_manager
    """

    plugin_id = "process_isolation"

    def __init__(self):
        self._manager: Optional[ProcessManager] = None

    @property
    def dependencies(self) -> Set[str]:
        """No dependencies - this is core infrastructure."""
        return set()

    @property
    def priority(self) -> int:
        """Very high priority - must boot early."""
        return 10

    def on_boot(
        self,
        kernel: "RealVibeKernel",
        config: Optional[Dict[str, Any]] = None,
    ) -> HookResult:
        """
        Boot the process manager.

        Creates the ProcessManager instance and registers it
        in the ServiceRegistry for kernel access.
        """
        try:
            # Create the process manager
            self._manager = ProcessManager()

            # Register in ServiceRegistry for DI
            ServiceRegistry.register(ProcessSupervisorProtocol, self._manager)

            # Also set on kernel for backward compatibility
            kernel.process_manager = self._manager

            logger.info("⚙️ Process Isolation Plugin booted - ProcessManager registered")
            return HookResult.ok()

        except Exception as e:
            logger.critical(f"❌ CRITICAL: Process Isolation Plugin failed to boot: {e}")
            return HookResult.fatal(str(e))

    def on_shutdown(self, kernel: "RealVibeKernel") -> HookResult:
        """Shutdown all agent processes on kernel shutdown."""
        if self._manager:
            try:
                self._manager.shutdown()
                logger.info("⚙️ Process Isolation Plugin shutdown complete")
            except Exception as e:
                logger.warning(f"⚠️ Process manager shutdown error: {e}")

        return HookResult.ok()

    def get_api(self) -> Optional[ProcessManager]:
        """Return the process manager for direct access if needed."""
        return self._manager
