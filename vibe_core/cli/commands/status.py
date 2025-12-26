"""
OPUS-310: Status Command

Show current system status.
"""

from typing import List

from vibe_core.protocols.command import (
    BaseCommand,
    CommandContext,
    CommandResult,
)


class StatusCommand(BaseCommand):
    """Show current system status."""

    name = "status"
    description = "Show current Vibe Kernel status"
    source = "core"
    tags = ["kernel", "status", "info"]

    _parameters = []

    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """Get kernel status."""
        kernel = context.kernel

        if not kernel:
            return CommandResult(
                success=False,
                error="Kernel not available. Run 'steward boot' first.",
            )

        try:
            status = kernel.get_status() if hasattr(kernel, "get_status") else {}

            output = "📊 System Status\n"
            output += "─" * 40 + "\n"

            # Core status
            output += f"   Kernel: {status.get('status', 'unknown')}\n"

            # Cognitive
            if hasattr(kernel, "_cognitive"):
                cog_type = type(kernel._cognitive).__name__
                caps = []
                if hasattr(kernel._cognitive, "get_capabilities"):
                    caps = kernel._cognitive.get_capabilities()[:3]
                output += f"   Cognitive: {cog_type}\n"
                if caps:
                    output += f"   Capabilities: {', '.join(caps)}...\n"

            # Health
            if "health" in status:
                health = status["health"]
                output += f"   Health: {health.get('score', 'N/A')}%\n"

            # Plugins
            if hasattr(kernel, "plugins"):
                output += f"   Plugins: {len(kernel.plugins)} loaded\n"

            # Events
            if hasattr(kernel, "event_bus"):
                eb = kernel.event_bus
                if hasattr(eb, "stats"):
                    stats = eb.stats()
                    output += f"   Events: {stats.get('total_events', 0)} total\n"

            return CommandResult(
                success=True,
                output=output,
                data={"status": status},
            )

        except Exception as e:
            return CommandResult(
                success=False,
                error=f"Status check failed: {e}",
            )
