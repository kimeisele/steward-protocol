"""
OPUS-307 Phase D: Tool Protocol CLI

Auto-generated CLI for all tools. Zero manual wiring.
Reads directly from Tool Protocol (name, description, parameters_schema).

Usage:
    steward tool list                           # List all tools
    steward tool info <name>                    # Show tool schema
    steward tool run <name> [--param=value]     # Execute tool
    steward tool run <name> --json              # JSON output
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

from vibe_core.di import ServiceRegistry
from vibe_core.protocols.cli import CLIMeta, register_cli
from vibe_core.tool_discovery import ToolDiscovery
from vibe_core.tools.tool_protocol import Tool, ToolResult
from vibe_core.tools.tool_registry import ToolRegistry


@register_cli
class ToolCLI:
    """
    Auto-generated CLI for Tool Protocol.

    No manual command definitions needed.
    Discovers all tools and generates CLI from their schemas.
    """

    @property
    def meta(self) -> CLIMeta:
        """CLI metadata for registry discovery."""
        return CLIMeta(
            command="tool",
            description="Tool Protocol CLI (list, info, run)",
            domain="execution",
            subcommands=["list", "info", "run"],
            tags=["tool", "execution", "protocol"],
        )

    def __init__(self):
        """Initialize with auto-discovered tools."""
        self._registry: Optional[ToolRegistry] = None
        self._discovery: Optional[ToolDiscovery] = None

    def _ensure_registry(self) -> ToolRegistry:
        """Lazy-load tool registry with DI support (OPUS-307 D.1)."""
        if self._registry is None:
            # Pass ServiceRegistry to enable dependency injection
            self._discovery = ToolDiscovery(root_path=Path("."), services=ServiceRegistry)
            tools = self._discovery.discover_all_tools()

            self._registry = ToolRegistry()
            for tool in tools:
                try:
                    self._registry.register(tool)
                except (ValueError, TypeError):
                    pass  # Skip duplicate or invalid tools

        return self._registry

    def run(self, args: List[str]) -> int:
        """
        Main entry point for tool CLI.

        Routes to: list, info, run
        """
        if not args:
            self._print_usage()
            return 1

        subcommand = args[0]
        remaining = args[1:]

        if subcommand == "list":
            return self.cmd_list(remaining)
        elif subcommand == "info":
            return self.cmd_info(remaining)
        elif subcommand == "run":
            return self.cmd_run(remaining)
        elif subcommand in ("--help", "-h", "help"):
            self._print_usage()
            return 0
        else:
            print(f"Unknown subcommand: {subcommand}")
            self._print_usage()
            return 1

    def _print_usage(self):
        """Print tool CLI usage."""
        print("""
Tool Protocol CLI (OPUS-307 Phase D)

Usage:
    steward tool list [--json] [--agent <id>]    List all tools
    steward tool info <tool_name>                Show tool details
    steward tool run <tool_name> [--params]      Execute tool

Examples:
    steward tool list
    steward tool list --json
    steward tool list --agent watchman
    steward tool info watchman.standards
    steward tool run watchman.standards --action inspect_all
    steward tool run civic.bank --action get_balance --agent_id herald
""")

    def cmd_list(self, args: List[str]) -> int:
        """List all available tools."""
        registry = self._ensure_registry()
        tool_names = sorted(registry.list_tools())

        # Parse args
        json_output = "--json" in args
        agent_filter = None
        for i, arg in enumerate(args):
            if arg == "--agent" and i + 1 < len(args):
                agent_filter = args[i + 1]

        # Filter by agent if specified
        if agent_filter:
            tool_names = [n for n in tool_names if n.startswith(f"{agent_filter}.")]

        if json_output:
            tools_data = []
            for name in tool_names:
                tool = registry.get(name)
                if tool:
                    agent_id = name.split(".")[0] if "." in name else "core"
                    tools_data.append(
                        {
                            "name": name,
                            "agent_id": agent_id,
                            "description": tool.description[:100] if tool.description else "",
                        }
                    )
            print(json.dumps(tools_data, indent=2))
        else:
            print(f"\nAvailable Tools ({len(tool_names)}):\n")

            # Group by agent
            by_agent: Dict[str, List[str]] = {}
            for name in tool_names:
                agent_id = name.split(".")[0] if "." in name else "core"
                if agent_id not in by_agent:
                    by_agent[agent_id] = []
                by_agent[agent_id].append(name)

            for agent_id in sorted(by_agent.keys()):
                print(f"  [{agent_id}]")
                for name in by_agent[agent_id]:
                    tool = registry.get(name)
                    desc = (
                        tool.description[:50] + "..."
                        if tool and len(tool.description) > 50
                        else (tool.description if tool else "")
                    )
                    print(f"    {name:40} {desc}")
                print()

        return 0

    def cmd_info(self, args: List[str]) -> int:
        """Show detailed tool information."""
        if not args:
            print("Usage: steward tool info <tool_name>")
            return 1

        tool_name = args[0]
        registry = self._ensure_registry()
        tool = registry.get(tool_name)

        if not tool:
            print(f"Tool not found: {tool_name}")
            print("\nAvailable tools:")
            for name in sorted(registry.list_tools())[:10]:
                print(f"  {name}")
            if len(registry.list_tools()) > 10:
                print(f"  ... and {len(registry.list_tools()) - 10} more")
            return 1

        print(f"\nTool: {tool.name}")
        print(f"Description: {tool.description}")
        print("\nParameters:")

        schema = tool.parameters_schema
        if not schema:
            print("  (no parameters)")
        else:
            for param_name, param_info in schema.items():
                if isinstance(param_info, dict):
                    param_type = param_info.get("type", "any")
                    required = param_info.get("required", False)
                    desc = param_info.get("description", "")
                    default = param_info.get("default", None)

                    req_str = "[REQUIRED]" if required else "[optional]"
                    default_str = f" (default: {default})" if default is not None else ""

                    print(f"  --{param_name} ({param_type}) {req_str}{default_str}")
                    if desc:
                        print(f"      {desc}")
                else:
                    print(f"  --{param_name}: {param_info}")

        print("\nExample:")
        print(f"  steward tool run {tool.name} --action <value>")

        return 0

    def cmd_run(self, args: List[str]) -> int:
        """Execute a tool."""
        if not args:
            print("Usage: steward tool run <tool_name> [--param=value ...]")
            return 1

        tool_name = args[0]
        remaining = args[1:]

        registry = self._ensure_registry()
        tool = registry.get(tool_name)

        if not tool:
            print(f"Tool not found: {tool_name}")
            return 1

        # Parse parameters from args
        params = self._parse_params(remaining)
        json_output = params.pop("json", False)

        # Validate
        try:
            tool.validate(params)
        except (ValueError, TypeError) as e:
            print(f"Parameter validation failed: {e}")
            print(f"\nUse 'steward tool info {tool_name}' to see required parameters.")
            return 1

        # Execute
        try:
            result = tool.execute(params)
        except Exception as e:
            print(f"Execution error: {e}")
            return 1

        # Output
        if json_output:
            output = {
                "success": result.success,
                "output": result.output,
                "error": result.error,
            }
            print(json.dumps(output, indent=2, default=str))
        else:
            if result.success:
                if isinstance(result.output, dict):
                    print(json.dumps(result.output, indent=2, default=str))
                else:
                    print(result.output)
            else:
                print(f"Error: {result.error}")

        return 0 if result.success else 1

    def _parse_params(self, args: List[str]) -> Dict[str, Any]:
        """
        Parse CLI arguments into parameter dict.

        Supports:
            --param=value
            --param value
            --flag (boolean true)
        """
        params: Dict[str, Any] = {}
        i = 0

        while i < len(args):
            arg = args[i]

            if arg.startswith("--"):
                if "=" in arg:
                    # --param=value
                    key, value = arg[2:].split("=", 1)
                    params[key] = self._parse_value(value)
                elif i + 1 < len(args) and not args[i + 1].startswith("--"):
                    # --param value
                    key = arg[2:]
                    value = args[i + 1]
                    params[key] = self._parse_value(value)
                    i += 1
                else:
                    # --flag (boolean)
                    key = arg[2:]
                    params[key] = True

            i += 1

        return params

    def _parse_value(self, value: str) -> Any:
        """Parse string value to appropriate type."""
        # Try JSON first (for objects, arrays, booleans)
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass

        # Try int
        try:
            return int(value)
        except ValueError:
            pass

        # Try float
        try:
            return float(value)
        except ValueError:
            pass

        # Return as string
        return value


# Module-level function for easy import
def run_tool_cli(args: List[str]) -> int:
    """Run the tool CLI with given arguments."""
    cli = ToolCLI()
    return cli.run(args)
