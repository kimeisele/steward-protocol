"""
CLI Renderer - GAD-000 Compliant output rendering.

Handles:
- JSON output (--json flag) for machine consumption
- YAML output (--yaml flag) for human-readable structured data
- Rich rendering (default) for human consumption
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x07721959"  # GenesisByte: parampara % 37 == 0

import json
import sys
from dataclasses import asdict, is_dataclass
from typing import Any

from .protocol import CLIResponse, ProgressUpdate


class CLIRenderer:
    """
    Renders CLI responses in various formats.

    GAD-000: All output is structured, format is chosen at render time.
    """

    def __init__(self, output_format: str = "human"):
        """
        Initialize renderer.

        Args:
            output_format: "json", "yaml", or "human"
        """
        self.output_format = output_format

    def render(self, response: CLIResponse) -> None:
        """Render a CLI response."""
        if self.output_format == "json":
            self._render_json(response)
        elif self.output_format == "yaml":
            self._render_yaml(response)
        else:
            self._render_human(response)

    def render_progress(self, update: ProgressUpdate) -> None:
        """Render a progress update (for streaming commands)."""
        if self.output_format == "json":
            print(json.dumps(update.to_dict()), flush=True)
        elif self.output_format == "yaml":
            import yaml

            print(yaml.dump(update.to_dict()), flush=True)
        else:
            self._render_progress_human(update)

    def _render_json(self, response: CLIResponse) -> None:
        """Render response as JSON."""
        output = response.to_dict()
        print(json.dumps(output, indent=2, default=str))

    def _render_yaml(self, response: CLIResponse) -> None:
        """Render response as YAML."""
        try:
            import yaml

            output = response.to_dict()
            print(yaml.dump(output, default_flow_style=False, sort_keys=False))
        except ImportError:
            # Fallback to JSON if yaml not available
            print("# YAML not available, using JSON")
            self._render_json(response)

    def _render_human(self, response: CLIResponse) -> None:
        """Render response for human consumption."""
        if not response.success:
            self._print_error(response.error or "Unknown error")
            return

        data = response.data
        if data is None:
            print("OK")
            return

        # Try rich rendering first
        if self._try_rich_render(data):
            return

        # Fallback to pretty print
        self._pretty_print(data)

    def _try_rich_render(self, data: Any) -> bool:
        """Try to render using Rich library."""
        try:
            from rich.console import Console
            from rich.pretty import Pretty
            from rich.table import Table

            console = Console()

            # If data is a list of dicts, render as table
            if isinstance(data, list) and data and isinstance(data[0], dict):
                table = Table()
                keys = list(data[0].keys())
                for key in keys:
                    table.add_column(key.upper())
                for row in data:
                    table.add_row(*[str(row.get(k, "")) for k in keys])
                console.print(table)
                return True

            # If data is a dict, render as key-value pairs
            if isinstance(data, dict):
                for key, value in data.items():
                    console.print(f"[bold]{key}:[/bold] {value}")
                return True

            # Otherwise use Pretty
            console.print(Pretty(data))
            return True

        except ImportError:
            return False

    def _pretty_print(self, data: Any) -> None:
        """Simple pretty print without Rich."""
        if is_dataclass(data):
            data = asdict(data)

        if isinstance(data, dict):
            for key, value in data.items():
                print(f"{key}: {value}")
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    print("-", " ".join(f"{k}={v}" for k, v in item.items()))
                else:
                    print(f"- {item}")
        else:
            print(data)

    def _print_error(self, error: str) -> None:
        """Print error message."""
        try:
            from rich.console import Console

            Console().print(f"[red bold]ERROR:[/red bold] {error}")
        except ImportError:
            print(f"ERROR: {error}", file=sys.stderr)

    def _render_progress_human(self, update: ProgressUpdate) -> None:
        """Render progress update for humans."""
        status_icons = {
            "starting": "🚀",
            "running": "⏳",
            "progress": "📊",
            "done": "✅",
            "error": "❌",
        }
        icon = status_icons.get(update.status, "•")
        percent_str = f" {update.percent}%" if update.percent is not None else ""

        try:
            from rich.console import Console

            Console().print(f"{icon} {update.message}{percent_str}")
        except ImportError:
            print(f"{icon} {update.message}{percent_str}")


def get_renderer(output_format: str = "human") -> CLIRenderer:
    """Factory function to get a renderer."""
    return CLIRenderer(output_format)
