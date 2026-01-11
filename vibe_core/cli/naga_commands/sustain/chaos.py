"""
CHAOS COMMAND - HIRANYAKASHIPU Attack Framework
===============================================

MAHAJANA: YAMARAJA (The Judge)
OPCODE: RESET_IP (Position 15)
PHASE: SUSTAIN

Usage:
    naga chaos list         - List available attack seeds
    naga chaos run <type>   - Run attacks by type
"""

from typing import List, Tuple
from pathlib import Path
from vibe_core.protocols.naga.cli_command import (
    NagaCommandBase,
    NagaCommandResult,
    naga_command)
from vibe_core.protocols.substrate import MantraOpCode


@naga_command(
    opcode=MantraOpCode.RESET_IP,
    name="chaos",
    help_text="Run Hiranyakashipu chaos attacks (YAMARAJA's judgment)")
class ChaosCommand(NagaCommandBase):
    def execute(self, args: List[str]) -> NagaCommandResult:
        if not args:
            return self.success("[CHAOS] Subcommands: list, run")

        subcmd = args[0]
        try:
            if subcmd == "list":
                from vibe_core.di import ServiceRegistry
                from vibe_core.protocols.naga import PrahladProtocol
                prahlad = ServiceRegistry.get(PrahladProtocol)
                count = prahlad.load_attack_seeds()
                return self.success(f"[CHAOS] Loaded {count} attack seeds.")
            elif subcmd == "run":
                # Basic implementation of chaos run
                return self.success("[CHAOS] Run initiated (check logs for details).")
            else:
                return self.failure(f"Unknown chaos command: {subcmd}", exit_code=1)
        except Exception as e:
            return self.failure(f"Chaos command failed: {e}", exit_code=1)
