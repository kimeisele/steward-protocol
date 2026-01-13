#!/usr/bin/env python3
"""
SettingsExecutor - Executes settings commands from SETTINGS.md

SEPARATED FROM kernel_impl.py to keep kernel clean.

This module handles the ACTUAL execution of settings commands:
- RESTART agent.<id> → Actually restarts the agent process
- REFRESH topology → Actually refreshes the topology
- SET kernel.verbose → Actually changes logging behavior

The kernel just calls: executor.execute(result)
No complex logic in kernel.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "manu"
__position__ = 7
__genesis__ = "0xe234a17b"  # GenesisByte: parampara % 37 == 0

import logging
from typing import TYPE_CHECKING, Set

from vibe_core.settings_sync import SettingsExecutionResult

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel

logger = logging.getLogger(__name__)


class SettingsExecutor:
    """
    Executes settings commands that require kernel access.

    Usage in kernel tick():
        result = settings_sync.sync_to_reality(state, ledger_callback)
        executor.execute(result, self)  # self = kernel
    """

    def execute(self, result: SettingsExecutionResult, kernel: "RealVibeKernel") -> None:
        """
        Execute all pending settings commands.

        Args:
            result: The result from SettingsSync.execute_commands()
            kernel: Reference to the kernel for process/topology access
        """
        # Handle RESTART commands
        if result.restart_agents:
            self._execute_restarts(result.restart_agents, kernel)

        # Handle REFRESH topology
        if result.refresh_topology:
            self._execute_refresh_topology(kernel)

        # Handle verbose mode
        if result.verbose_mode is not None:
            self._execute_verbose_mode(result.verbose_mode)

        # Handle provider change (UI Enhancement)
        if result.new_provider is not None:
            self._execute_provider_change(result.new_provider)

        # Handle execution mode change (UI Enhancement)
        if result.new_execution_mode is not None:
            self._execute_mode_change(result.new_execution_mode)

    def _execute_restarts(self, agent_ids: Set[str], kernel: "RealVibeKernel") -> None:
        """
        Restart specified agents via ProcessManager.

        Uses the same logic as crash recovery but triggered manually.
        """
        for agent_id in agent_ids:
            try:
                # Check if agent exists in process manager
                if agent_id not in kernel.process_manager.processes:
                    logger.warning(f"⚠️  Cannot restart '{agent_id}': not a process-isolated agent")
                    continue

                info = kernel.process_manager.processes[agent_id]

                # Terminate existing process gracefully
                if info.process.is_alive():
                    logger.info(f"🔄 Stopping agent '{agent_id}' for restart...")
                    info.parent_pipe.send({"type": "STOP"})
                    info.process.join(timeout=2)

                    if info.process.is_alive():
                        logger.warning(f"⚠️  Agent '{agent_id}' didn't stop gracefully, terminating...")
                        info.process.terminate()
                        info.process.join(timeout=1)

                # Use ProcessManager's internal restart logic
                # Set status to CRASHED to trigger _handle_crash logic
                from vibe_core.process_manager import ProcessStatus

                info.status = ProcessStatus.CRASHED
                kernel.process_manager._handle_crash(agent_id)

                logger.info(f"✅ Agent '{agent_id}' restarted successfully")

            except Exception as e:
                logger.error(f"❌ Failed to restart agent '{agent_id}': {e}")

    def _execute_refresh_topology(self, kernel: "RealVibeKernel") -> None:
        """
        Force refresh the agent topology.
        """
        try:
            from vibe_core.topology import refresh_topology

            logger.info("🔄 Refreshing topology...")
            topology = refresh_topology(kernel=kernel)

            agent_count = len(topology.agents) if hasattr(topology, "agents") else 0
            logger.info(f"✅ Topology refreshed ({agent_count} agents)")

        except Exception as e:
            logger.error(f"❌ Failed to refresh topology: {e}")

    def _execute_verbose_mode(self, enabled: bool) -> None:
        """
        Enable or disable verbose logging mode.

        When enabled: Sets root logger and VIBE_KERNEL to DEBUG
        When disabled: Restores to INFO level
        """
        try:
            level = logging.DEBUG if enabled else logging.INFO

            # Set root logger
            logging.getLogger().setLevel(level)

            # Set kernel-specific loggers
            for logger_name in ["VIBE_KERNEL", "PROCESS_MANAGER", "vibe_core"]:
                logging.getLogger(logger_name).setLevel(level)

            mode = "ENABLED" if enabled else "DISABLED"
            logger.info(f"📊 Verbose mode {mode} (log level: {logging.getLevelName(level)})")

        except Exception as e:
            logger.error(f"❌ Failed to set verbose mode: {e}")

    def _execute_provider_change(self, provider: str) -> None:
        """
        Change the LLM provider in phoenix config.

        Note: Requires kernel restart to take effect.
        """
        try:
            from vibe_core.phoenix import get_config

            config = get_config()

            # Map provider name to class path
            provider_map = {
                "anthropic": "vibe_core.runtime.providers.anthropic:AnthropicProvider",
                "openai": "vibe_core.runtime.providers.openai:OpenAIProvider",
                "openrouter": "vibe_core.runtime.providers.openrouter:OpenRouterProvider",
            }

            if provider not in provider_map:
                logger.error(f"❌ Unknown provider: {provider}")
                return

            config.kernel.providers.llm_provider = provider_map[provider]
            config.save()

            logger.info(f"🔌 Provider changed to '{provider}' - restart kernel to apply")

        except Exception as e:
            logger.error(f"❌ Failed to change provider: {e}")

    def _execute_mode_change(self, mode: str) -> None:
        """
        Change the execution mode (simulation/live_fire).

        Live Fire mode enables real API calls and file writes.
        """
        try:
            from vibe_core.phoenix import get_config

            config = get_config()

            is_live = mode == "live_fire"
            config.kernel.features.live_fire_enabled = is_live
            config.save()

            if is_live:
                logger.warning("⚠️  LIVE FIRE MODE ENABLED - Real API calls and writes are now active!")
            else:
                logger.info("🔒 Simulation mode enabled - API calls and writes are simulated")

        except Exception as e:
            logger.error(f"❌ Failed to change execution mode: {e}")


# Singleton instance for kernel to use
_executor: SettingsExecutor | None = None


def get_executor() -> SettingsExecutor:
    """Get the singleton SettingsExecutor instance."""
    global _executor
    if _executor is None:
        _executor = SettingsExecutor()
    return _executor
