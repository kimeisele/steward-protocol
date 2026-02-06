"""
YIELD COMMAND - SHUKA's Detachment
===================================

MAHAJANA: SHUKA (The Detached Sage)
OPCODE: YIELD_CPU (Position 14)
PHASE: SUSTAIN

WHY SHUKA?
- Shuka was perfectly detached - he could yield anything
- He taught Bhagavatam and then left without attachment
- YIELD_CPU is about yielding control gracefully
- Shuka yields without clinging

MANTRA WORD: RAMA (Position 14)
"Rama yields to dharma"

YIELD_CPU = Yield control to allow others to proceed.
Shuka detaches, Shuka yields, Shuka transcends.

Usage:
    naga yield                    # Show yield status
    naga yield --processes        # Show process yields
    naga yield --async            # Show async yield points
    naga yield --cooperative      # Cooperative yielding status
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0xb821957b"  # GenesisByte: parampara % 37 == 0

import os
import sys
from typing import List, Tuple

from vibe_core.protocols.naga.cli_command import NagaCommandBase, NagaCommandResult, naga_command
from vibe_core.protocols.substrate import MantraOpCode

import logging
logger = logging.getLogger(__name__)


@naga_command(
    opcode=MantraOpCode.YIELD_CPU,
    name="yield",
    help_text="CPU yield and scheduling (SHUKA's detachment - SUSTAIN phase)",
)
class YieldCommand(NagaCommandBase):
    """
    Yield command implementation.

    SHUKA manages:
    - Process scheduling
    - Cooperative multitasking
    - Async yield points
    - Resource yielding

    The Detached Sage yields control gracefully.
    """

    def execute(self, args: List[str]) -> NagaCommandResult:
        """
        Execute yield command.

        Args:
            args: Command arguments
                --processes: Show process information
                --async: Show async status
                --cooperative: Show cooperative yielding

        Returns:
            NagaCommandResult with yield information
        """
        # Parse flags
        show_processes = "--processes" in args
        show_async = "--async" in args
        show_cooperative = "--cooperative" in args

        # Build output
        output_parts = []
        data: List[Tuple[str, str]] = [
            ("mahajana", "shuka"),
            ("opcode", "YIELD_CPU"),
            ("phase", "sustain"),
            ("position", "14"),
        ]

        output_parts.append("[SHUKA] Yield Status")
        output_parts.append("=" * 50)

        # Basic yield info
        yield_info = self._get_yield_info()
        output_parts.append("")
        output_parts.append("  Current State (Shuka's Awareness):")
        output_parts.append(f"    Process ID:       {yield_info['pid']}")
        output_parts.append(f"    Thread Count:     {yield_info['threads']}")
        output_parts.append(f"    CPU Affinity:     {yield_info['affinity']}")

        if show_processes:
            procs = self._get_process_info()
            output_parts.append("")
            output_parts.append("  Process Information:")
            for key, value in procs.items():
                output_parts.append(f"    {key}: {value}")

        if show_async:
            async_info = self._get_async_info()
            output_parts.append("")
            output_parts.append("  Async Status:")
            for key, value in async_info.items():
                output_parts.append(f"    {key}: {value}")

        if show_cooperative:
            coop = self._get_cooperative_info()
            output_parts.append("")
            output_parts.append("  Cooperative Yielding:")
            for item in coop:
                output_parts.append(f"    • {item}")

        output_parts.append("")
        output_parts.append("=" * 50)
        output_parts.append("YIELD_CPU: Ready to yield")

        return self.success("\n".join(output_parts), data=tuple(data))

    def _get_yield_info(self) -> dict:
        """Get basic yield information."""
        import threading

        info = {
            "pid": str(os.getpid()),
            "threads": str(threading.active_count()),
            "affinity": "all cores",
        }

        # Try to get CPU affinity (Linux only)
        try:
            affinity = os.sched_getaffinity(0)
            info["affinity"] = f"{len(affinity)} cores"
        except (AttributeError, OSError) as _exc:
            logger.exception("Unexpected error: %s", _exc)

        return info

    def _get_process_info(self) -> dict:
        """Get process information."""
        info = {}

        info["Python Version"] = f"{sys.version_info.major}.{sys.version_info.minor}"
        info["Platform"] = sys.platform
        info["Executable"] = sys.executable.split("/")[-1]

        # Memory info
        try:
            import resource

            usage = resource.getrusage(resource.RUSAGE_SELF)
            info["User Time"] = f"{usage.ru_utime:.2f}s"
            info["System Time"] = f"{usage.ru_stime:.2f}s"
        except Exception as _exc:
            logger.exception("Unexpected error: %s", _exc)

        return info

    def _get_async_info(self) -> dict:
        """Get async/await status."""
        info = {}

        try:
            import asyncio

            try:
                loop = asyncio.get_running_loop()
                info["Event Loop"] = "running"
                info["Loop Type"] = type(loop).__name__
            except RuntimeError:
                info["Event Loop"] = "not running"

            info["Asyncio Available"] = "yes"
        except ImportError:
            info["Asyncio"] = "not available"

        return info

    def _get_cooperative_info(self) -> list:
        """Get cooperative yielding information."""
        info = []

        # Check for yield points in code (conceptual)
        info.append("Generator support: enabled")
        info.append("Async/await: available")
        info.append("Threading: active")

        # Check if we're in a cooperative environment
        try:
            import asyncio

            info.append("Coroutine support: yes")
        except ImportError:
            info.append("Coroutine support: no")

        return info


# Export for direct import
__all__ = ["YieldCommand"]
