"""
Activity Panel - Recent git commits and quick commands.

Provides context about recent changes and commonly used commands.
"""

import subprocess
from typing import Any, Dict

from .base_panel import OpusPanel


class ActivityPanel(OpusPanel):
    """
    Recent Activity Panel.

    Shows git commits for project context.
    """

    @property
    def panel_id(self) -> str:
        return "activity"

    @property
    def priority(self) -> int:
        return 30  # After main content

    def render(self, config: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Render recent activity section."""
        display = config.get("display", {})
        commit_count = display.get("show_recent_commits", 5)

        if commit_count <= 0:
            return ""

        commits = self._get_recent_commits(commit_count)

        return f"""## Recent Activity

```
{commits}
```

---
"""

    def _get_recent_commits(self, count: int) -> str:
        """Get recent git commits."""
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", f"-{count}"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.stdout.strip() if result.returncode == 0 else "Could not fetch commits"
        except Exception:
            return "Git not available"


class CommandsPanel(OpusPanel):
    """
    Quick Commands Panel.

    Displays commonly used commands from config.
    """

    @property
    def panel_id(self) -> str:
        return "commands"

    @property
    def priority(self) -> int:
        return 100  # Footer

    def render(self, config: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Render quick commands section."""
        quick_cmds = config.get("quick_commands", [])

        if not quick_cmds:
            return ""

        lines = ["| Command | Description |", "|---------|-------------|"]
        for cmd in quick_cmds:
            lines.append(f"| `{cmd.get('command', '')}` | {cmd.get('description', '')} |")

        return f"""## Quick Commands

{chr(10).join(lines)}

---
"""
