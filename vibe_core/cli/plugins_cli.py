"""
OPUS-307: Plugin CLI

CLI interface for PluginService.

Usage:
    steward plugins list              # List all plugins
    steward plugins info <name>       # Show plugin details
    steward plugins status            # Show loaded plugins
"""

import logging
from pathlib import Path
from typing import List, Optional

from vibe_core.plugin_service import PluginService
from vibe_core.protocols.cli import CLIMeta, register_cli

logger = logging.getLogger("PLUGINS_CLI")


@register_cli
class PluginsCLI:
    """
    CLI for Plugin management via PluginService.

    OPUS-307: Unified plugin access.
    """

    @property
    def meta(self) -> CLIMeta:
        """CLI metadata for registry discovery."""
        return CLIMeta(
            command="plugins",
            description="Plugin management (list, info, status)",
            domain="system",
            subcommands=["list", "info", "status"],
            tags=["plugins", "system"],
        )

    def __init__(self):
        """Initialize plugins CLI."""
        self._service: Optional[PluginService] = None

    def _get_service(self) -> PluginService:
        """Get PluginService instance."""
        if self._service is None:
            self._service = PluginService.get_instance(Path.cwd())
            self._service.scan()
        return self._service

    def run(self, args: List[str]) -> int:
        """Execute plugins command."""
        if not args:
            return self._cmd_list([])

        subcommand = args[0]
        sub_args = args[1:]

        commands = {
            "list": self._cmd_list,
            "info": self._cmd_info,
            "status": self._cmd_status,
            "--help": self._cmd_help,
            "-h": self._cmd_help,
        }

        handler = commands.get(subcommand)
        if handler:
            return handler(sub_args)

        # Unknown subcommand
        print(f"Unknown subcommand: {subcommand}")
        return self._cmd_help([])

    def _cmd_list(self, args: List[str]) -> int:
        """List all plugins."""
        svc = self._get_service()
        plugins = svc.list()

        print(f"\n{'=' * 60}")
        print(f"PLUGINS ({len(plugins)} total)")
        print(f"{'=' * 60}\n")

        # Group by priority ranges
        for plugin in plugins:
            enabled = "✓" if plugin.enabled else "✗"
            deps = f" (deps: {', '.join(plugin.depends_on)})" if plugin.depends_on else ""
            print(f"  [{enabled}] {plugin.plugin_id:<25} priority={plugin.priority:<3}{deps}")

        print(f"\n{'=' * 60}")
        return 0

    def _cmd_info(self, args: List[str]) -> int:
        """Show plugin details."""
        if not args:
            print("Usage: steward plugins info <plugin_id>")
            return 1

        plugin_id = args[0]
        svc = self._get_service()
        plugin = svc.get(plugin_id)

        if not plugin:
            print(f"Plugin not found: {plugin_id}")
            return 1

        print(f"\n{'=' * 60}")
        print(f"PLUGIN: {plugin.plugin_id}")
        print(f"{'=' * 60}\n")
        print(f"  Name:        {plugin.name}")
        print(f"  Description: {plugin.description}")
        print(f"  Version:     {plugin.version}")
        print(f"  Priority:    {plugin.priority}")
        print(f"  Path:        {plugin.path}")
        print(f"  Enabled:     {plugin.enabled}")
        print(f"  Exec Mode:   {plugin.execution_mode}")

        if plugin.capabilities:
            print(f"  Capabilities: {', '.join(plugin.capabilities)}")

        if plugin.depends_on:
            print(f"  Dependencies: {', '.join(plugin.depends_on)}")

        print(f"\n{'=' * 60}")
        return 0

    def _cmd_status(self, args: List[str]) -> int:
        """Show plugin status summary."""
        svc = self._get_service()
        plugins = svc.list()

        enabled = sum(1 for p in plugins if p.enabled)
        disabled = len(plugins) - enabled

        print(f"\n{'=' * 60}")
        print("PLUGIN STATUS")
        print(f"{'=' * 60}\n")
        print(f"  Total:    {len(plugins)}")
        print(f"  Enabled:  {enabled}")
        print(f"  Disabled: {disabled}")

        # Priority distribution
        early = sum(1 for p in plugins if p.priority < 10)
        mid = sum(1 for p in plugins if 10 <= p.priority < 50)
        late = sum(1 for p in plugins if p.priority >= 50)

        print("\n  Boot Order:")
        print(f"    Early (0-9):   {early}")
        print(f"    Mid (10-49):   {mid}")
        print(f"    Late (50+):    {late}")

        print(f"\n{'=' * 60}")
        return 0

    def _cmd_help(self, args: List[str]) -> int:
        """Show help."""
        print("""
Usage: steward plugins <command> [args]

Commands:
  list              List all discovered plugins
  info <plugin_id>  Show plugin details
  status            Show plugin status summary

Examples:
  steward plugins list
  steward plugins info opus_assistant
  steward plugins status
""")
        return 0
