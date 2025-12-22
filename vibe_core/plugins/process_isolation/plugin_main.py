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

    def on_agent_registered(self, kernel: "RealVibeKernel", agent_id: str) -> None:
        """
        Spawn isolated process for newly registered agent.

        OPUS-209: This logic was extracted from kernel register_agent().
        The kernel only registers; the plugin handles process spawning.
        """
        if not self._manager:
            return

        agent = kernel.agent_registry.get(agent_id)
        if not agent:
            return

        # Check if agent requests process isolation
        execution_mode = getattr(agent, "_execution_mode", "thread")
        if execution_mode != "process":
            # Check cartridge path as fallback
            cartridge_path = getattr(agent, "_cartridge_path", None)
            if not cartridge_path:
                logger.debug(f"📍 Agent '{agent_id}' running in-process (no isolation)")
                return

        # Spawn the isolated process
        cartridge_path = getattr(agent, "_cartridge_path", None)
        cartridge_class_name = getattr(agent, "_cartridge_class_name", None)

        if cartridge_path and cartridge_class_name:
            try:
                self._manager.spawn_agent(
                    agent_id,
                    cartridge_path,
                    cartridge_class_name,
                    config=getattr(agent, "config", None),
                )
                logger.info(f"🔒 Agent '{agent_id}' spawned in isolated process")
            except Exception as e:
                logger.error(f"❌ Failed to spawn process for {agent_id}: {e}")

    def spawn_deferred_agents(self, kernel: "RealVibeKernel") -> int:
        """
        OPUS-209: Spawn processes for all registered agents without running processes.

        Called after discovery to batch-spawn agents, avoiding import lock deadlock.
        """
        if not self._manager:
            logger.warning("⚠️ ProcessManager not available")
            return 0

        spawned = 0
        for agent_id, agent in kernel._agent_registry.items():
            if agent_id in self._manager.processes:
                if self._manager.processes[agent_id].process.is_alive():
                    continue

            cartridge_path = getattr(agent, "_cartridge_path", None)
            cartridge_class_name = getattr(agent, "_cartridge_class_name", None)
            if not cartridge_path or not cartridge_class_name:
                continue

            try:
                self._manager.spawn_agent(agent_id, cartridge_path, cartridge_class_name, config=getattr(agent, "config", None))
                spawned += 1
                logger.info(f"🌱 Spawned deferred process for {agent_id}")
            except Exception as e:
                logger.error(f"❌ Failed to spawn {agent_id}: {e}")

        logger.info(f"✅ Spawned {spawned} deferred agent processes")
        return spawned

    def on_shutdown(self, kernel: "RealVibeKernel") -> HookResult:
        """Shutdown all agent processes on kernel shutdown."""
        if self._manager:
            try:
                self._manager.shutdown()
                logger.info("⚙️ Process Isolation Plugin shutdown complete")
            except Exception as e:
                logger.warning(f"⚠️ Process manager shutdown error: {e}")

        return HookResult.ok()

    def process_ipc_events(self, kernel: "RealVibeKernel") -> None:
        """OPUS-209: Process IPC messages from agents."""
        if not self._manager:
            return
        messages = self._manager.get_pending_messages()
        for agent_id, msg in messages:
            msg_type = msg.get("type")
            if msg_type == "TASK_RESULT":
                task_id = msg.get("task_id")
                status = msg.get("status")
                if status == "success":
                    result = msg.get("result")
                    logger.info(f"✅ Task {task_id} completed (Async IPC)")
                    kernel._completed_tasks[task_id] = result
                    for plugin in kernel._plugins:
                        plugin.on_task_completed(kernel, task_id, result)
                else:
                    error = msg.get("error")
                    logger.error(f"❌ Task {task_id} failed (Async IPC): {error}")
                    for plugin in kernel._plugins:
                        plugin.on_task_failed(kernel, task_id, error)
            elif msg_type == "CRASH":
                logger.critical(f"💥 Agent {agent_id} CRASHED: {msg.get('error')}")

    def get_api(self) -> Optional[ProcessManager]:
        """Return the process manager for direct access if needed."""
        return self._manager
