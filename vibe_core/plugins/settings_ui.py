from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List

from vibe_core.doc_renderer import DocRenderer, SettingsRenderState
from vibe_core.plugin_protocol import KernelPlugin
from vibe_core.settings_sync import SettingsSync, SettingsSyncState

if TYPE_CHECKING:
    from vibe_core.kernel_impl import RealVibeKernel


class SettingsUIPlugin(KernelPlugin):
    """
    Plugin for SETTINGS.md synchronization.
    Handles the Command Queue and System Settings interface.
    """

    @property
    def plugin_id(self) -> str:
        return "settings_ui"

    @property
    def priority(self) -> int:
        return 50  # Early in tick cycle

    def __init__(self):
        self.sync = SettingsSync()
        self.last_modified = 0.0
        self.execution_history: List[Dict[str, Any]] = []
        self.doc_renderer = DocRenderer()

    def on_boot(self, kernel: "RealVibeKernel") -> None:
        """Initialize settings sync on boot."""
        pass

    def on_tick_pre(self, kernel: "RealVibeKernel") -> None:
        """Check for changes in SETTINGS.md and execute commands."""

        # Get paused agents from governance plugin (if available)
        paused_agents: set = set()
        if kernel.governance and hasattr(kernel.governance, "get_paused_agents"):
            paused_agents = kernel.governance.get_paused_agents()

        # 1. Check for changes
        if self.sync.check_file_changed(self.last_modified):
            # Prepare state
            state = SettingsSyncState(
                last_modified=self.last_modified,
                writing=False,
                paused_agents=paused_agents,
                agent_ids=set(kernel.agent_registry.keys()),
                execution_history=list(self.execution_history),
            )

            # Execute Sync
            result = self.sync.sync_to_reality(state, ledger_callback=kernel.record_verified_event)

            # Update Plugin State
            if result.new_mtime > 0:
                self.last_modified = result.new_mtime

            self.execution_history.extend(result.history_entries)

            # Update Governance Plugin State (Paused Agents)
            # Use public API instead of accessing private _paused_agents
            if kernel.governance:
                # Get current paused agents
                current_paused = kernel.governance.get_paused_agents()
                new_paused = result.paused_agents

                # Resume agents that are no longer paused
                for agent_id in current_paused - new_paused:
                    kernel.governance.resume_agent(agent_id)

                # Pause agents that should be paused
                for agent_id in new_paused - current_paused:
                    kernel.governance.pause_agent(agent_id)

            # Execute side effects (RESTART, REFRESH, verbose)
            from vibe_core.settings_executor import get_executor

            executor = get_executor()
            executor.execute(result, kernel)

    def on_tick_post(self, kernel: "RealVibeKernel") -> None:
        """Render SETTINGS.md."""
        snapshot = self._generate_snapshot(kernel)

        # Get config state from proper sources (not spaghetti)
        provider_info = None
        live_fire_enabled = False
        try:
            # Provider info from section's SINGLE SOURCE OF TRUTH
            from vibe_core.settings.sections.provider import get_provider_info_from_config

            provider_info = get_provider_info_from_config()

            # Live fire from phoenix config
            from vibe_core.phoenix import get_config

            live_fire_enabled = get_config().live_fire_enabled
        except Exception:
            pass  # Use defaults if not available

        # Get governance registries from plugin (if available)
        # Use public API instead of accessing private registries
        varna_registry = {}
        ashrama_registry = {}
        if kernel.governance:
            if hasattr(kernel.governance, "get_varna_registry"):
                varna_registry = kernel.governance.get_varna_registry()
            if hasattr(kernel.governance, "get_ashrama_registry"):
                ashrama_registry = kernel.governance.get_ashrama_registry()

        state = SettingsRenderState(
            ledger_path=str(kernel.ledger_path),
            varna_registry=varna_registry,
            ashrama_registry=ashrama_registry,
            execution_history=list(self.execution_history),
            provider_info=provider_info,
            live_fire_enabled=live_fire_enabled,
        )

        new_mtime = self.doc_renderer.render_settings(snapshot, state)
        if new_mtime:
            self.last_modified = new_mtime

    def _generate_snapshot(self, kernel: "RealVibeKernel") -> Dict[str, Any]:
        """Generate kernel snapshot for rendering."""
        snapshot = {
            "timestamp": datetime.utcnow().isoformat(),
            "kernel_status": kernel.status.value,
            "agents": {},
            "scheduler": kernel.scheduler.get_queue_status(),
            "ledger_stats": {
                "total_events": len(kernel.ledger.get_all_events()),
            },
        }

        for agent_id, agent in kernel.agent_registry.items():
            try:
                agent_status = agent.report_status() if hasattr(agent, "report_status") else {}
                # Check paused via governance plugin
                if kernel.governance and hasattr(kernel.governance, "is_agent_paused"):
                    if kernel.governance.is_agent_paused(agent_id):
                        agent_status["status"] = "PAUSED"
                snapshot["agents"][agent_id] = agent_status
            except Exception:
                snapshot["agents"][agent_id] = {"error": "Failed to get status"}

        return snapshot
