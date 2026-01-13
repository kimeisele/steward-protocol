"""
RESET COMMAND - YAMARAJA's Justice
===================================

MAHAJANA: YAMARAJA (The Lord of Death/Dharma)
OPCODE: RESET_IP (Position 15)
PHASE: SUSTAIN

WHY YAMARAJA?
- Yamaraja is the lord of death - the ultimate reset
- He judges and resets karma
- RESET_IP is about returning to initial state
- Yamaraja brings closure and new beginnings

MANTRA WORD: RAMA (Position 15)
"Rama resets the cosmic cycle"

RESET_IP = Reset the instruction pointer / return to start.
Yamaraja ends cycles, Yamaraja judges, Yamaraja resets.

This is position 15 - the final position before the cycle repeats.

Usage:
    naga reset                    # Show reset options
    naga reset --soft             # Soft reset (clear transient state)
    naga reset --hard             # Hard reset (full reinitialization)
    naga reset --cycle            # Show cycle position
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0xd0612810"  # GenesisByte: parampara % 37 == 0

from pathlib import Path
from typing import List, Tuple
from datetime import datetime

from vibe_core.protocols.naga.cli_command import (
    NagaCommandBase,
    NagaCommandResult,
    naga_command)
from vibe_core.protocols.substrate import MantraOpCode


@naga_command(
    opcode=MantraOpCode.AUDIT_SEAL,
    name="reset",
    help_text="System reset (YAMARAJA's judgment - SUSTAIN phase, final position)")
class ResetCommand(NagaCommandBase):
    """
    Reset command implementation.

    YAMARAJA manages:
    - Soft resets (clear transient state)
    - Hard resets (full reinitialization)
    - Cycle completion
    - Final judgment

    The Lord of Dharma resets for a new cycle.
    Position 15 - the end that becomes the beginning.
    """

    def execute(self, args: List[str]) -> NagaCommandResult:
        """
        Execute reset command.

        Args:
            args: Command arguments
                --soft: Soft reset (clear transient state)
                --hard: Hard reset (full reinitialization)
                --cycle: Show Mahamantra cycle position

        Returns:
            NagaCommandResult with reset information
        """
        # Parse flags
        do_soft = "--soft" in args
        do_hard = "--hard" in args
        show_cycle = "--cycle" in args

        # Build output
        output_parts = []
        data: List[Tuple[str, str]] = [
            ("mahajana", "yamaraja"),
            ("opcode", "RESET_IP"),
            ("phase", "sustain"),
            ("position", "15"),
        ]

        output_parts.append("[YAMARAJA] Reset Status")
        output_parts.append("=" * 50)

        # Show cycle information
        if show_cycle or (not do_soft and not do_hard):
            cycle_info = self._get_cycle_info()
            output_parts.append("")
            output_parts.append("  Mahamantra Cycle (Yamaraja's Domain):")
            output_parts.append(f"    Current Position:  15 (RESET_IP)")
            output_parts.append(f"    Next Position:     0 (SYS_WAKE)")
            output_parts.append(f"    Cycle Status:      {cycle_info['status']}")
            output_parts.append(f"    Commands Ready:    {cycle_info['commands']}")

        if do_soft:
            result = self._soft_reset()
            output_parts.append("")
            output_parts.append("  Soft Reset (Yamaraja's Mercy):")
            for key, value in result.items():
                output_parts.append(f"    {key}: {value}")
            data.append(("action", "soft_reset"))

        if do_hard:
            result = self._hard_reset()
            output_parts.append("")
            output_parts.append("  Hard Reset (Yamaraja's Judgment):")
            for key, value in result.items():
                output_parts.append(f"    {key}: {value}")
            data.append(("action", "hard_reset"))

        output_parts.append("")
        output_parts.append("=" * 50)
        output_parts.append("RESET_IP: Cycle complete - ready for SYS_WAKE")
        output_parts.append("")
        output_parts.append("\"From YAMARAJA back to PRITHU - the eternal cycle.\"")

        return self.success(
            "\n".join(output_parts),
            data=tuple(data))

    def _get_cycle_info(self) -> dict:
        """Get Mahamantra cycle information."""
        try:
            from vibe_core.cli.naga_commands import discover_commands
            from vibe_core.protocols.naga.cli_command import NAGA_COMMAND_REGISTRY

            discover_commands()
            cmd_count = len(NAGA_COMMAND_REGISTRY._commands)

            if cmd_count >= 16:
                status = "COMPLETE (all 16 positions filled)"
            else:
                status = f"PARTIAL ({cmd_count}/16 positions)"

            return {
                "status": status,
                "commands": str(cmd_count),
            }
        except Exception:
            return {
                "status": "UNKNOWN",
                "commands": "unavailable",
            }

    def _soft_reset(self) -> dict:
        """Perform soft reset - clear transient state."""
        result = {}

        # Clear any transient caches
        try:
            import gc

            collected = gc.collect()
            result["Garbage Collected"] = f"{collected} objects"
        except Exception:
            result["Garbage Collection"] = "skipped"

        # Clear module caches (but don't unload)
        result["Module Caches"] = "preserved"
        result["Registry State"] = "preserved"
        result["Timestamp"] = datetime.now().strftime("%H:%M:%S")

        return result

    def _hard_reset(self) -> dict:
        """Perform hard reset - full state clear."""
        result = {}

        # This would be more aggressive in a real implementation
        # For safety, we just report what would happen

        result["Action"] = "simulated (safety mode)"
        result["Would Clear"] = "all transient state"
        result["Would Preserve"] = "configuration, identity"
        result["Recommendation"] = "restart process for full reset"

        # Clear what we safely can
        try:
            import gc

            gc.collect()
            result["GC"] = "complete"
        except Exception:
            pass

        return result


# Export for direct import
__all__ = ["ResetCommand"]
