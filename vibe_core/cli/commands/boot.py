"""
OPUS-310: Boot Command

Initialize the Vibe Kernel.
"""

import time
from typing import List

from vibe_core.protocols.command import (
    BaseCommand,
    CommandContext,
    CommandResult,
    ParameterSpec,
    ParameterType,
)


class BootCommand(BaseCommand):
    """Initialize and boot the Vibe Kernel."""

    name = "boot"
    description = "Initialize the Vibe Kernel and load plugins"
    source = "core"
    tags = ["kernel", "boot", "init"]

    _parameters = [
        ParameterSpec(
            name="--minimal",
            param_type=ParameterType.BOOLEAN,
            required=False,
            default=False,
            description="Boot with minimal plugins",
        ),
    ]

    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """Boot the kernel."""
        minimal = "--minimal" in args

        try:
            start = time.time()

            # Import kernel
            from vibe_core.kernel_impl import RealVibeKernel

            # Boot
            kernel = RealVibeKernel(load_plugins=not minimal)

            elapsed = time.time() - start

            # Get status
            status = kernel.get_status() if hasattr(kernel, "get_status") else {}

            output = f"🚀 Kernel booted in {elapsed:.2f}s\n"
            output += f"   Status: {status.get('status', 'unknown')}\n"

            # Check cognitive
            if hasattr(kernel, "_cognitive"):
                cog_type = type(kernel._cognitive).__name__
                output += f"   Cognitive: {cog_type}\n"

            # Plugin count
            if hasattr(kernel, "plugins"):
                output += f"   Plugins: {len(kernel.plugins)}\n"

            return CommandResult(
                success=True,
                output=output,
                data={
                    "boot_time": elapsed,
                    "status": status,
                    "minimal": minimal,
                },
            )

        except Exception as e:
            return CommandResult(
                success=False,
                error=f"Boot failed: {e}",
            )
