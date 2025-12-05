"""
Settings Renderer (Control Panel).
"""

import logging

from vibe_core.settings_sync import SettingsSync, SettingsSyncState

from .base import BaseRenderer

logger = logging.getLogger("RENDERER_SETTINGS")


class SettingsRenderer(BaseRenderer):
    """Renders SETTINGS.md and handles system configuration."""

    def __init__(self, kernel):
        super().__init__(kernel)
        self.sync = SettingsSync()
        self.state = SettingsSyncState()

    @property
    def name(self) -> str:
        return "settings"

    def render(self) -> None:
        # Update state from kernel
        if hasattr(self.kernel, "governance") and self.kernel.governance:
            self.state.paused_agents = set(self.kernel.governance.get_paused_agents())

        # Update known agents
        if hasattr(self.kernel, "agent_registry"):
            self.state.agent_ids = set(self.kernel.agent_registry.keys())

        # 1. Sync to reality (Process commands)
        try:
            # We need to pass a callback if we want ledger recording
            callback = getattr(self.kernel, "record_verified_event", None)

            result = self.sync.sync_to_reality(self.state, ledger_callback=callback)

            # Update state with result
            if result:
                self.state.last_modified = result.new_mtime
                self.state.execution_history.extend(result.history_entries)
                self.state.paused_agents = result.paused_agents

                # Handle side effects
                if result.refresh_topology:
                    logger.info("🔄 Topology refresh requested (handled by kernel)")

                if result.restart_agents:
                    for agent_id in result.restart_agents:
                        logger.info(f"🔄 Restart requested for {agent_id}")

        except Exception as e:
            logger.error(f"Error rendering SETTINGS.md: {e}")

        # 2. Generate and Write Document
        try:
            content = self._generate_content()
            self.sync.render_document(content)
        except Exception as e:
            logger.error(f"Error generating SETTINGS.md: {e}")

    def _generate_content(self) -> str:
        """Generate SETTINGS.md content."""
        lines = ["# ⚙️ SYSTEM SETTINGS", ""]

        # Kernel Config
        lines.extend(
            [
                "## 🔧 Kernel Configuration",
                "",
                "| Setting | Value | Description |",
                "| :--- | :--- | :--- |",
                "| `kernel.log_level` | `INFO` | Logging verbosity |",
                "| `kernel.verbose` | `False` | Verbose mode |",
                "| `provider` | `openai` | LLM Provider |",
                "| `mode` | `simulation` | Execution Mode |",
                "",
            ]
        )

        # Agent Registry
        agents = self.kernel.agent_registry if hasattr(self.kernel, "agent_registry") else {}
        lines.extend(
            [
                "## 🤖 Agent Registry",
                "",
                f"**Agents Registered:** {len(agents)}",
                "",
                "| Agent ID | Status | Tasks |",
                "| :--- | :--- | :--- |",
            ]
        )

        for agent_id, agent in agents.items():
            status = "ACTIVE"
            if agent_id in self.state.paused_agents:
                status = "PAUSED"

            # Try to get task count
            tasks = 0
            if hasattr(agent, "report_status"):
                try:
                    st = agent.report_status()
                    if isinstance(st, dict):
                        tasks = st.get("tasks_completed", 0)
                except Exception:
                    pass

            lines.append(f"| `{agent_id}` | {status} | {tasks} |")

        lines.append("")

        # Pending Commands (Placeholder for user input)
        lines.extend(
            [
                "## ⚡ Pending Commands",
                "",
                "> Add commands below (e.g. `- SET kernel.log_level=DEBUG`)",
                "",
                "_No pending commands. Add commands above this line._",
                "",
            ]
        )

        # Execution Ledger
        lines.extend(
            ["## 🏛️ Execution Ledger", "", "| Timestamp | Command | Status | Reason |", "| :--- | :--- | :--- | :--- |"]
        )

        # Show last 10 entries
        for entry in reversed(self.state.execution_history[-10:]):
            cmd_str = f"{entry['command'].get('action')} {entry['command'].get('key') or entry['command'].get('agent_id') or ''}"
            lines.append(f"| {entry['timestamp']} | `{cmd_str}` | {entry['status']} | {entry['reason']} |")

        return "\n".join(lines)
