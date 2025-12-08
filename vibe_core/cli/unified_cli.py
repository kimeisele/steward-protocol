"""
UnifiedCLI - Single entry point for all CLI operations.
Combines Fractal CLI (Plugin-based) with Legacy StewardCLI (System commands).
"""

import argparse
import logging
import warnings
from typing import Any, Dict, List, Optional

from vibe_core.cli.executor import CLIExecutor
from vibe_core.cli.loader import CLILoader
from vibe_core.cli.protocol import CLICommand

# Import Legacy CLI for fallback/system commands
# Suppress deprecation warning during import if we add it later
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from vibe_core.cli.legacy import StewardCLI

logger = logging.getLogger("UNIFIED_CLI")


class UnifiedCLI:
    """
    GAD-000 compliant CLI that unifies:
    1. System commands (boot, stop, status) -> Legacy StewardCLI
    2. Plugin commands (verify, etc) -> Fractal CLIExecutor
    """

    def __init__(self):
        self._loader = CLILoader()
        self._executor = CLIExecutor()
        self._legacy = StewardCLI()

        # Define legacy commands that are handled by StewardCLI
        self._legacy_map = {
            "status": self._legacy.cmd_status,
            "verify": self._legacy.cmd_verify,  # Keep verify in legacy for now until Parampara plugin
            "lineage": self._legacy.cmd_lineage,
            "ps": self._legacy.cmd_ps,
            "boot": self._legacy.cmd_boot,
            "stop": self._legacy.cmd_stop,
            "init": self._legacy.cmd_init,
            "discover": self._legacy.cmd_discover,
            "introspect": self._legacy.cmd_introspect,
            "delegate": None,  # TODO: Migrate to plugin
        }

    def run(self, args: List[str]) -> int:
        """
        Execute CLI command.
        Returns exit code (0 = success, 1 = error).
        """
        parser = argparse.ArgumentParser(description="Steward Protocol Unified CLI")

        # We need to peek at the first argument to decide routing
        if not args:
            parser.print_help()
            return 1

        command_name = args[0]
        remaining_args = args[1:]

        # 1. Check Legacy/System Commands
        if command_name in self._legacy_map:
            handler = self._legacy_map[command_name]
            if handler:
                # Legacy handlers expect specific args or use their own parsing?
                # StewardCLI methods take specific typed args.
                # We need to bridge argparse to method args.
                return self._dispatch_legacy(command_name, handler, remaining_args)

        # 2. Check Plugin Commands
        commands = self._loader.discover_commands()
        if command_name in commands:
            cmd_def = commands[command_name]
            return self._dispatch_plugin(cmd_def, remaining_args)

        # 3. Help / Unknown
        if command_name in ("-h", "--help", "help"):
            self._print_help(commands)
            return 0

        print(f"❌ Unknown command: {command_name}")
        print("Try 'steward help' for available commands.")
        return 1

    def get_capabilities(self) -> Dict[str, Any]:
        """GAD-000 Test 1: Machine-readable capability discovery."""
        plugin_commands = self._loader.discover_commands()

        capabilities = {
            "version": "2.0.0 (Unified)",
            "system_commands": list(self._legacy_map.keys()),
            "plugin_commands": [
                {"name": cmd.name, "namespace": cmd.namespace, "help": cmd.help, "mode": cmd.execution_mode.name}
                for cmd in plugin_commands.values()
            ],
            "json_output_supported": True,
        }
        return capabilities

    def _dispatch_legacy(self, name: str, handler: Any, args: List[str]) -> int:
        """Dispatch to legacy StewardCLI methods."""
        # Simple argument parsing for legacy methods
        # Most legacy methods map 1:1 to args, but we need to match signatures.
        # For now, we'll implement a basic bridge.

        try:
            if name == "status":
                return handler()
            elif name == "ps":
                return handler()
            elif name == "boot":
                return handler()
            elif name == "stop":
                return handler()
            elif name == "discover":
                return handler()
            elif name == "introspect":
                return handler()
            elif name == "verify":
                if not args:
                    print("Usage: steward verify <agent_id>")
                    return 1
                return handler(args[0])
            elif name == "init":
                if not args:
                    print("Usage: steward init <agent_id>")
                    return 1
                return handler(args[0])
            elif name == "lineage":
                tail = None
                if "--tail" in args:
                    try:
                        idx = args.index("--tail")
                        tail = int(args[idx + 1])
                    except (ValueError, IndexError):
                        pass
                return handler(tail=tail)
            else:
                print(f"⚠️ Command '{name}' is known but dispatch is not implemented in UnifiedCLI.")
                return 1
        except Exception as e:
            print(f"❌ Error executing legacy command '{name}': {e}")
            return 1

    def _dispatch_plugin(self, cmd: CLICommand, args: List[str]) -> int:
        """Dispatch to Fractal CLIExecutor."""
        # Parse args based on cmd definition
        parsed_args = self._parse_plugin_args(cmd, args)
        if parsed_args is None:
            return 1

        response = self._executor.execute(cmd, parsed_args)

        if response.success:
            if response.data is not None:
                # formatting should be handled by a renderer, but for now print
                import json

                print(json.dumps(response.data, indent=2, default=str))
            return 0
        else:
            print(f"❌ Error: {response.error}")
            return 1

    def _parse_plugin_args(self, cmd: CLICommand, args: List[str]) -> Optional[Dict[str, Any]]:
        """Use argparse to parse arguments defined in manifest."""
        parser = argparse.ArgumentParser(prog=f"steward {cmd.name}", description=cmd.help)

        for arg in cmd.args:
            kwargs = {
                "help": arg.help,
                "type": arg.type,
                "default": arg.default,
            }
            if arg.required:
                kwargs["required"] = True
            if arg.nargs:
                kwargs["nargs"] = arg.nargs
            if arg.choices:
                kwargs["choices"] = arg.choices

            # If default is None and not required, it's optional
            # In argparse, positionals are required unless nargs='?' or default set

            name = arg.name
            if not arg.required and not name.startswith("-"):
                # Make it optional flag if not required? Or optional positional?
                # For CLI simplicity, let's assume manifest args are flags if optional
                pass

            # Simple mapping for now
            if not arg.required:
                name = f"--{arg.name}"

            parser.add_argument(name, **kwargs)

        try:
            # Only parse known args to check for help, but we isolated args already
            namespace = parser.parse_args(args)
            return vars(namespace)
        except SystemExit:
            return None

    def _print_help(self, plugin_commands: Dict[str, CLICommand]):
        print("🎛️  STEWARD UNIFIED CLI")
        print("=======================")
        print("\nSYSTEM COMMANDS:")
        for name in sorted(self._legacy_map.keys()):
            print(f"  {name:<15} (System)")

        print("\nPLUGIN COMMANDS:")
        for name, cmd in sorted(plugin_commands.items()):
            print(f"  {name:<15} {cmd.help}")
