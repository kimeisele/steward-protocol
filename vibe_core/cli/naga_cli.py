"""
"Niemand darf es merken" - but YOU can command them.

FRACTAL NAGA CLI (Operation Kurukshetra):
    This CLI has been refactored to follow the Protocol-First architecture.
    All logic now resides in vibe_core/cli/naga_commands/ governed by the 12 Mahajanas.

"The Balarama Pattern: He becomes the bed, the throne, and the shoes."
"""

import logging
from pathlib import Path
from typing import List, Optional

from vibe_core.di import ServiceRegistry
from vibe_core.protocols.cli import CLIMeta, register_cli

logger = logging.getLogger("NAGA_CLI")


@register_cli
class NagaCLI:
    """
    NAGA Command Line Interface.

    THE EXECUTIVE LAYER IN YOUR TERMINAL.
    NAGAs don't just observe - they ACT.
    """

    @property
    def meta(self) -> CLIMeta:
        """CLI metadata for registry discovery."""
        return CLIMeta(
            command="naga",
            description="NAGA Federation CLI - The Invisible Guardians",
            domain="security",
            subcommands=[
                "status", "scan", "detect", "flood", "bite", "remediate", 
                "audit", "prahlad", "chaos", "chat", "intel", "commit",
                "validate", "gc", "reset", "optimize", "yield"
            ],
            tags=["naga", "security", "guardian", "fractal", "executive", "intelligence"],
        )

    def __init__(self):
        self._federation = None
        self._repo_root = Path.cwd()

    def run(self, args: List[str]) -> int:
        """
        Main entry point.

        BALARAMA DISPATCHER:
        Routes all commands through the NagaCommandRegistry.
        Legacy cmd_* methods have been surrendered to the Mahajanas.
        """
        if not args:
            self._print_usage()
            return 0

        cmd = args[0]

        if cmd == "help" or cmd == "--help":
            self._print_usage()
            return 0

        # =================================================================
        # PROTOCOL-FIRST: All commands now live in the registry
        # =================================================================
        result = self._try_protocol_command(cmd, args[1:])
        if result is not None:
            return result

        print(f"Unknown or unmigrated command: {cmd}")
        self._print_usage()
        return 1

    def _try_protocol_command(self, cmd: str, args: List[str]) -> Optional[int]:
        """
        Execute a command via NagaCommandRegistry.
        """
        try:
            from vibe_core.cli.naga_commands import discover_commands
            from vibe_core.protocols.naga.cli_command import NAGA_COMMAND_REGISTRY

            # Balarama discovers and injects life into commands
            discover_commands()

            protocol_cmd = NAGA_COMMAND_REGISTRY.get(cmd)
            if protocol_cmd is None:
                return None

            # Execute the command governed by its Mahajana
            result = protocol_cmd.execute(args)

            if result.output:
                print(result.output)
            if result.error:
                print(f"Error: {result.error}")

            return result.exit_code

        except Exception as e:
            logger.error(f"Protocol execution failure: {e}")
            return 1

    def _print_usage(self):
        """Print NAGA CLI usage via discovery."""
        print("\n    NAGA FEDERATION CLI (Protocol-First)")
        print("    " + "=" * 40)
        
        try:
            from vibe_core.cli.naga_commands import discover_commands
            from vibe_core.protocols.naga.cli_command import NAGA_COMMAND_REGISTRY
            discover_commands()
            
            print("\n    AVAILABLE COMMANDS:")
            for name in sorted(NAGA_COMMAND_REGISTRY.list_names()):
                cmd = NAGA_COMMAND_REGISTRY.get(name)
                print(f"        {name:<12} - {cmd.help_text}")
        except Exception:
            print("\n    (Discovery failed - check logs)")

        print("\n    Usage: steward naga <command> [options]")
        print("    " + "=" * 40 + "\n")