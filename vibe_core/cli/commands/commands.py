"""
OPUS-310: Commands Command (Meta-Introspection)

Show all registered commands in the system.
This is the "steward commands" that reveals everything.

For MANAS to see the full map of capabilities.
"""

from typing import List

from vibe_core.protocols.command import (
    BaseCommand,
    CommandContext,
    CommandResult,
    ParameterSpec,
    ParameterType,
)


class CommandsCommand(BaseCommand):
    """List all available commands in the system."""

    name = "commands"
    description = "List all registered commands (for discovery)"
    source = "core"
    tags = ["meta", "discovery", "help"]

    _parameters = [
        ParameterSpec(
            name="query",
            param_type=ParameterType.STRING,
            required=False,
            description="Search filter for commands",
        ),
        ParameterSpec(
            name="--json",
            param_type=ParameterType.BOOLEAN,
            required=False,
            default=False,
            description="Output as JSON",
        ),
    ]

    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """List all commands."""
        from vibe_core.cli.command_registry import CommandRegistry

        as_json = "--json" in args
        query = None

        # Parse args
        for arg in args:
            if not arg.startswith("--"):
                query = arg
                break

        registry = CommandRegistry.get_instance()

        # Get commands
        if query:
            commands = registry.search(query)
        else:
            commands = registry.list_commands()

        # Sort by source then name
        commands.sort(key=lambda c: (c.source, c.name))

        if as_json:
            import json

            data = [
                {
                    "name": c.name,
                    "description": c.description,
                    "source": c.source,
                    "parameters": [
                        {
                            "name": p.name,
                            "type": p.param_type.value,
                            "required": p.required,
                        }
                        for p in c.parameters
                    ],
                    "tags": c.tags,
                }
                for c in commands
            ]
            return CommandResult(
                success=True,
                output=json.dumps(data, indent=2),
                data={"commands": data},
            )

        # Human-readable output
        output = "📜 Available Commands\n"
        output += "═" * 50 + "\n\n"

        # Group by source
        by_source: dict = {}
        for cmd in commands:
            source = cmd.source
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(cmd)

        for source, cmds in by_source.items():
            output += f"┌─ {source}\n"
            for cmd in cmds:
                output += f"│  {cmd.name:20} {cmd.description[:40]}\n"
            output += "│\n"

        # Stats
        stats = registry.stats()
        output += "─" * 50 + "\n"
        output += f"Total: {stats['total']} commands"
        if stats["pending_wiring"]:
            output += f" ({stats['pending_wiring']} pending wiring)"
        output += "\n"

        return CommandResult(
            success=True,
            output=output,
            data={"count": len(commands), "by_source": by_source},
        )
