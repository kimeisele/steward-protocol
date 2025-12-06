"""
CLI Main Entry Point - Fractal CLI System.

Dynamically discovers commands from plugin manifests and executes them.
VEDA-4 Pattern:
  SHABDA   → Parse command line
  ARTHA    → Discover available commands
  PRATYAYA → Validate and match command
  KARMA    → Execute and render result
"""

import argparse
import logging
import sys
from typing import Dict, List, Optional

from .executor import CLIExecutor
from .loader import CLILoader
from .protocol import CLICommand, ExecutionMode
from .renderer import get_renderer

logger = logging.getLogger("CLI")


def _add_builtin_commands(subparsers: argparse._SubParsersAction) -> None:
    """Add built-in CLI commands (observe, status) that don't come from plugins."""
    # observe - Glass Box introspection
    observe = subparsers.add_parser(
        "observe",
        help="Observe system state (Glass Box introspection)",
        description="List or query system monitors from all plugins.",
    )
    observe.add_argument(
        "monitor_id",
        nargs="?",
        help="Monitor to observe (e.g., 'scheduler:queue'). Omit to list all.",
    )

    # status - Overall system status
    subparsers.add_parser(
        "status",
        help="Show overall system status",
        description="Aggregated status from all monitors.",
    )


def _get_default_db_path() -> str:
    """Get the default database path for the system."""
    from pathlib import Path

    # Check common locations in order of priority
    candidates = [
        Path("data/vibe_ledger.db"),  # Project default
        Path(".vibe/state/vibe_agency.db"),  # Agent state
        Path("/tmp/vibe_os/kernel/lineage.db"),  # Lineage DB
    ]

    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    # Fallback to default (may not exist)
    return "data/vibe_ledger.db"


def _execute_builtin(command: str, args: argparse.Namespace) -> dict:
    """
    Execute a built-in command (observe, status).

    IMPORTANT: Uses persistent DB, NOT ephemeral kernel.
    This ensures we see REAL system state, not a ghost kernel.
    """
    from datetime import datetime
    from pathlib import Path

    from vibe_core.kernel_impl import RealVibeKernel

    from .monitor_loader import MonitorLoader

    # Use persistent DB path - NOT :memory:!
    db_path = _get_default_db_path()
    db_exists = Path(db_path).exists()

    # Boot kernel with real DB (read-only introspection)
    kernel = RealVibeKernel(db_path)
    kernel.boot()

    try:
        if command == "observe":
            monitor_id = getattr(args, "monitor_id", None)
            registry = MonitorLoader.discover_monitors(kernel)

            if not monitor_id:
                # List all monitors
                monitors = [m.to_dict() for m in registry.values()]
                return {
                    "monitors": monitors,
                    "total": len(monitors),
                    "db_path": db_path,
                    "db_exists": db_exists,
                    "hint": "Use 'steward observe <monitor_id>' to view a specific monitor",
                }

            # Get specific monitor snapshot
            snapshot = MonitorLoader.get_snapshot(monitor_id, kernel)
            if not snapshot:
                return {"error": f"Monitor not found: {monitor_id}"}
            return snapshot.to_dict()

        elif command == "status":
            # Aggregate status from all monitors + real kernel state
            status = {
                "timestamp": datetime.now().isoformat(),
                "db_path": db_path,
                "db_exists": db_exists,
                "kernel": {
                    "agents": len(kernel.agent_registry) if hasattr(kernel, "agent_registry") else 0,
                    "plugins": len(kernel.plugin_manager.plugins) if hasattr(kernel, "plugin_manager") else 0,
                },
                "monitors": {},
            }

            # Add ledger stats if available
            if hasattr(kernel, "ledger") and kernel.ledger:
                try:
                    # Try to get ledger stats
                    ledger = kernel.ledger
                    if hasattr(ledger, "get_all_events"):
                        events = ledger.get_all_events()
                        status["ledger"] = {
                            "total_events": len(events) if events else 0,
                        }
                except Exception:
                    pass

            snapshots = MonitorLoader.get_all_snapshots(kernel)
            for monitor_id, snapshot in snapshots.items():
                status["monitors"][monitor_id] = {
                    "values": {v.name: v.value for v in snapshot.values},
                }

            return status

    finally:
        try:
            kernel.shutdown()
        except Exception:
            pass

    return {"error": f"Unknown builtin command: {command}"}


def build_parser(commands: Dict[str, CLICommand]) -> argparse.ArgumentParser:
    """
    Build argparse parser dynamically from discovered commands.

    Groups commands by namespace for cleaner help output.
    """
    parser = argparse.ArgumentParser(
        prog="steward",
        description="Steward Protocol CLI - Fractal Command System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Global options
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format (GAD-000 compliant)",
    )
    parser.add_argument(
        "--yaml",
        action="store_true",
        help="Output in YAML format",
    )
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Force offline mode (no kernel)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Verbose output",
    )

    # Build subparsers for commands
    subparsers = parser.add_subparsers(
        dest="command",
        title="commands",
        metavar="COMMAND",
    )

    # Group commands by namespace
    namespaces: Dict[str, List[CLICommand]] = {}
    for cmd in commands.values():
        ns = cmd.namespace or "core"
        if ns not in namespaces:
            namespaces[ns] = []
        namespaces[ns].append(cmd)

    # Add built-in commands first
    _add_builtin_commands(subparsers)

    # Add each plugin command as subparser
    for cmd in commands.values():
        # Use shell-friendly name (: -> -)
        sub = subparsers.add_parser(
            cmd.to_argparse_name(),
            help=cmd.help,
            description=cmd.help,
        )

        # Add command-specific args
        for arg in cmd.args:
            arg_name = f"--{arg.name}" if not arg.required else arg.name
            sub.add_argument(arg_name, **arg.to_argparse_kwargs())

        # Store command reference
        sub.set_defaults(_cli_command=cmd)

    return parser


# Built-in command names (not from plugins)
BUILTIN_COMMANDS = {"observe", "status"}


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main CLI entry point.

    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    # Discover commands
    try:
        commands = CLILoader.discover_commands()
    except Exception as e:
        print(f"ERROR: Failed to discover commands: {e}", file=sys.stderr)
        return 1

    # Build parser
    parser = build_parser(commands)

    # Parse args
    args = parser.parse_args(argv)

    # Configure logging
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    elif args.verbose:
        logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.WARNING)

    # No command specified
    if not args.command:
        parser.print_help()
        return 0

    # Determine output format
    if args.json:
        output_format = "json"
    elif args.yaml:
        output_format = "yaml"
    else:
        output_format = "human"

    renderer = get_renderer(output_format)

    # Handle built-in commands (observe, status)
    if args.command in BUILTIN_COMMANDS:
        from .protocol import CLIResponse

        try:
            result = _execute_builtin(args.command, args)
            response = CLIResponse(
                success="error" not in result,
                data=result,
                error=result.get("error"),
                execution_mode=ExecutionMode.BOOT,
            )
        except Exception as e:
            response = CLIResponse(
                success=False,
                data=None,
                error=str(e),
                execution_mode=ExecutionMode.BOOT,
            )

        renderer.render(response)
        return 0 if response.success else 1

    # Get plugin command definition
    command: Optional[CLICommand] = getattr(args, "_cli_command", None)
    if not command:
        # Try to find by name (handle : vs -)
        cmd_name = args.command.replace("-", ":")
        command = commands.get(cmd_name)
        if not command:
            print(f"ERROR: Unknown command: {args.command}", file=sys.stderr)
            return 1

    # Determine execution mode
    force_mode = None
    if args.offline:
        force_mode = ExecutionMode.OFFLINE

    # Collect command arguments (exclude global flags)
    cmd_args = {
        k: v
        for k, v in vars(args).items()
        if k not in ("command", "json", "yaml", "offline", "debug", "verbose", "_cli_command") and v is not None
    }

    # Execute plugin command
    executor = CLIExecutor()
    response = executor.execute(command, cmd_args, force_mode=force_mode)

    renderer.render(response)
    return 0 if response.success else 1


def cli_entry():
    """Entry point for console_scripts."""
    sys.exit(main())


if __name__ == "__main__":
    cli_entry()
