"""
Mini-ENVOY Terminal Panel - Quick Command Interface.

A simplified ENVOY terminal embedded in OPUS.md.
Allows quick commands without switching to ENVOY.md.

BIDIRECTIONAL: Users can write commands, system responds.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

from .base_panel import OpusPanel

logger = logging.getLogger("PANEL_TERMINAL")


class TerminalPanel(OpusPanel):
    """
    Mini command terminal for quick operations.

    Supports:
    - Quick status checks
    - Simple commands
    - Recent command history
    """

    def __init__(self):
        self._command_history: List[Dict[str, str]] = []
        self._max_history = 5

    @property
    def panel_id(self) -> str:
        return "terminal"

    @property
    def priority(self) -> int:
        return 90  # Near bottom, before commands

    def render(self, config: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Render the mini terminal panel."""
        lines = [
            "## Quick Terminal",
            "",
            "> **Mini-ENVOY** - Quick commands without leaving OPUS",
            "",
        ]

        # Command input area (bidirectional)
        lines.append("### Command")
        lines.append("")
        lines.append("```")
        lines.append("> _type command here_")
        lines.append("```")
        lines.append("")

        # Available quick commands
        lines.append("### Quick Commands")
        lines.append("")
        lines.append("| Command | Description |")
        lines.append("|---------|-------------|")
        lines.append("| `status` | Show kernel status |")
        lines.append("| `agents` | List active agents |")
        lines.append("| `debt` | Show technical debt summary |")
        lines.append("| `git` | Show recent commits |")
        lines.append("| `help` | Show available commands |")
        lines.append("")

        # Recent activity (from context or fallback)
        kernel = context.get("kernel")
        lines.append("### System Status")
        lines.append("")

        if kernel:
            status = getattr(kernel.status, "value", "UNKNOWN")
            agent_count = len(kernel.agent_registry) if hasattr(kernel, "agent_registry") else 0
            lines.append(f"- **Kernel:** `{status}`")
            lines.append(f"- **Agents:** {agent_count} registered")
        else:
            lines.append("- **Kernel:** Not connected")
            lines.append("- **Agents:** -")

        # Add timestamp
        lines.append(f"- **Updated:** {datetime.now().strftime('%H:%M:%S')}")
        lines.append("")

        # Command history (if any)
        if self._command_history:
            lines.append("### Recent Commands")
            lines.append("")
            lines.append("| Time | Command | Result |")
            lines.append("|------|---------|--------|")
            for entry in self._command_history[-5:]:
                lines.append(f"| {entry['time']} | `{entry['cmd']}` | {entry['result']} |")
            lines.append("")

        lines.append("---")
        lines.append("*For full terminal: see ENVOY.md*")

        return "\n".join(lines)

    def execute_command(self, command: str) -> str:
        """
        Execute a quick command.

        This can be called by the system when it detects
        a command in the terminal input area.
        """
        cmd = command.strip().lower()
        result = "Unknown command"
        timestamp = datetime.now().strftime("%H:%M")

        if cmd == "status":
            result = "OK - See OPUS header"
        elif cmd == "agents":
            result = "See AGENTS.md"
        elif cmd == "debt":
            result = "See Technical Debt panel above"
        elif cmd == "git":
            result = "See Activity panel"
        elif cmd == "help":
            result = "status|agents|debt|git|help"
        elif cmd.startswith("run "):
            circuit = cmd[4:].strip()
            result = f"Would execute: {circuit}"

        # Record in history
        self._command_history.append(
            {
                "time": timestamp,
                "cmd": command[:20],
                "result": result[:30],
            }
        )

        if len(self._command_history) > self._max_history:
            self._command_history = self._command_history[-self._max_history :]

        return result
