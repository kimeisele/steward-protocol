"""
OPUS-310: Boot Command

Initialize the Vibe Kernel.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0x88bfaeda"  # GenesisByte: parampara % 37 == 0

import time
import getpass
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from vibe_core.protocols.kernel_protocol import KernelProtocol

from vibe_core.protocols.substrate.byte import GenesisByte, MantraBit
from vibe_core.boot_orchestrator import BootOrchestrator
from vibe_core.boot_mode import BootMode

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

            # 1. ACQUIRE IDENTITY (Sovereign Check)
            # In a real system, this pulls from the cryptographic keystore
            user_signature = f"sovereign:{getpass.getuser()}"
            
            # 2. GENERATE GENESIS BYTE (The 16-Bit Spark)
            # We affirm the full cycle (Hare Krishna...) exists in intent
            genesis = GenesisByte(
                signature=user_signature,
                resonance=MantraBit.full_resonance(), # Sets 0xFFFF
                timestamp=start
            )
            
            # 3. INITIALIZE ORCHESTRATOR (The Machine)
            # No Kernel creation here! Just the empty shell.
            orchestrator = BootOrchestrator(
                boot_mode=BootMode.MINIMAL if minimal else BootMode.FULL
            )
            
            # 4. IGNITE (The Spark)
            # Passes the GenesisByte. If valid, Orchestrator builds Kernel.
            kernel: "KernelProtocol" = orchestrator.ignite(genesis)

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
