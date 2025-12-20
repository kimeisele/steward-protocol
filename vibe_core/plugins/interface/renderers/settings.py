"""
Settings Renderer (Control Panel).

OPUS-152: Refactored to use render_sections() pattern.

Bidirectional: Processes user commands AND generates output.
Uses SettingsSync for INPUT parsing with WHITELIST security.

Architecture:
- INPUT: SettingsSync parses commands from "## Pending Commands" section
- OUTPUT: render_sections() uses config-driven sections from interface.yaml
- BIDIRECTIONAL: Preserves user sections on each render
"""

import logging
from typing import Any, Dict, List, Optional

from vibe_core.io_service import DocumentType
from vibe_core.settings_sync import SettingsSync, SettingsSyncState

from .base import BaseRenderer

logger = logging.getLogger("RENDERER_SETTINGS")


class SettingsRenderer(BaseRenderer):
    """Renders SETTINGS.md and handles system configuration.

    OPUS-152: Uses render_sections() for config-driven output.
    """

    def __init__(self, kernel):
        super().__init__(kernel)
        self.sync = SettingsSync()
        self.state = SettingsSyncState()
        self._register_data_sources()

    def _register_data_sources(self) -> None:
        """Register data sources for config-driven sections.

        Maps interface.yaml section sources to actual data.
        """
        self.register_data_source("config.current", self._get_current_config)
        self.register_data_source("settings.agents", self._get_agent_registry)
        self.register_data_source("settings.history", self._get_execution_history)

    @property
    def name(self) -> str:
        return "settings"

    @property
    def output_file(self) -> str:
        return "SETTINGS.md"

    @property
    def doc_type(self) -> DocumentType:
        return DocumentType.BIDIRECTIONAL

    # =========================================================================
    # DATA SOURCES (for render_sections)
    # =========================================================================

    def _get_current_config(self) -> List[Dict[str, Any]]:
        """Get current kernel configuration."""
        return [
            {"Setting": "`kernel.log_level`", "Value": "`INFO`", "Description": "Logging verbosity"},
            {"Setting": "`kernel.verbose`", "Value": "`False`", "Description": "Verbose mode"},
            {"Setting": "`provider`", "Value": "`openai`", "Description": "LLM Provider"},
            {"Setting": "`mode`", "Value": "`simulation`", "Description": "Execution Mode"},
        ]

    def _get_agent_registry(self) -> List[Dict[str, Any]]:
        """Get agent registry with status."""
        agents = self.kernel.agent_registry if hasattr(self.kernel, "agent_registry") else {}
        result = []

        for agent_id, agent in agents.items():
            status = "ACTIVE"
            if agent_id in self.state.paused_agents:
                status = "PAUSED"

            tasks = 0
            if hasattr(agent, "report_status"):
                try:
                    st = agent.report_status()
                    if isinstance(st, dict):
                        tasks = st.get("tasks_completed", 0)
                except Exception:
                    pass

            result.append(
                {
                    "Agent ID": f"`{agent_id}`",
                    "Status": status,
                    "Tasks": tasks,
                }
            )

        return result

    def _get_execution_history(self) -> List[Dict[str, Any]]:
        """Get execution history for ledger section."""
        history = []
        for entry in reversed(self.state.execution_history[-10:]):
            cmd = entry.get("command", {})
            cmd_str = f"{cmd.get('action', '')} {cmd.get('key') or cmd.get('agent_id') or ''}"
            history.append(
                {
                    "Timestamp": entry.get("timestamp", ""),
                    "Command": f"`{cmd_str}`",
                    "Status": entry.get("status", ""),
                    "Reason": entry.get("reason", ""),
                }
            )
        return history

    # =========================================================================
    # RENDER (OPUS-152: Config-driven with bidirectional support)
    # =========================================================================

    def render(self) -> None:
        """Render SETTINGS.md with bidirectional support.

        OPUS-152: Uses render_sections() for output when config available.

        Flow:
        1. Update state from kernel
        2. Process INPUT (user commands from file)
        3. Generate OUTPUT (config-driven or fallback)
        """
        # Update state from kernel
        self._update_state_from_kernel()

        # INPUT: Process user commands
        self._sync_from_file()

        # OUTPUT: Use config-driven sections if available
        config = self.get_config()
        if config and config.sections:
            content = self.render_sections()
            self.merge_and_write(content)
        else:
            # Fallback to hardcoded content
            content = self._generate_content()
            if content:
                self.merge_and_write(content)

    def generate_content(self) -> Optional[str]:
        """
        Legacy generate_content for compatibility.

        DEPRECATED: Use render() instead which calls render_sections().
        This method is kept for backwards compatibility only.
        """
        # Update state from kernel
        self._update_state_from_kernel()

        # Process user commands from SETTINGS.md
        self._sync_from_file()

        # Return content for KING to write
        return self._generate_content()

    def _update_state_from_kernel(self) -> None:
        """Update state from kernel."""
        if hasattr(self.kernel, "governance") and self.kernel.governance:
            self.state.paused_agents = set(self.kernel.governance.get_paused_agents())
        if hasattr(self.kernel, "agent_registry"):
            self.state.agent_ids = set(self.kernel.agent_registry.keys())

    def _sync_from_file(self) -> None:
        """Read and process user commands from SETTINGS.md."""
        try:
            callback = getattr(self.kernel, "record_verified_event", None)
            result = self.sync.sync_to_reality(self.state, ledger_callback=callback)

            if result:
                self.state.last_modified = result.new_mtime
                self.state.execution_history.extend(result.history_entries)
                self.state.paused_agents = result.paused_agents

                if result.refresh_topology:
                    logger.info("Topology refresh requested (handled by kernel)")
                if result.restart_agents:
                    for agent_id in result.restart_agents:
                        logger.info(f"Restart requested for {agent_id}")
        except Exception as e:
            logger.error(f"Error syncing from SETTINGS.md: {e}")

    def _generate_content(self) -> str:
        """Generate SETTINGS.md content (fallback if no config sections)."""
        lines = ["# SYSTEM SETTINGS", ""]

        # Kernel Config
        lines.extend(
            [
                "## Kernel Configuration",
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
                "## Agent Registry",
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
                "## Pending Commands",
                "",
                "> Add commands below (e.g. `- SET kernel.log_level=DEBUG`)",
                "",
                "_No pending commands. Add commands above this line._",
                "",
            ]
        )

        # Execution Ledger
        lines.extend(
            ["## Execution Ledger", "", "| Timestamp | Command | Status | Reason |", "| :--- | :--- | :--- | :--- |"]
        )

        # Show last 10 entries
        for entry in reversed(self.state.execution_history[-10:]):
            cmd = entry.get("command", {})
            cmd_str = f"{cmd.get('action', '')} {cmd.get('key') or cmd.get('agent_id') or ''}"
            lines.append(
                f"| {entry.get('timestamp', '')} | `{cmd_str}` | {entry.get('status', '')} | {entry.get('reason', '')} |"
            )

        return "\n".join(lines)
