"""
BITE COMMAND - YAMARAJA's Judgment
==================================

MAHAJANA: YAMARAJA (The Judge)
OPCODE: RESET_IP (Position 15)
PHASE: SUSTAIN

Usage:
    naga bite <violation_type> [--details <json>]
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0xf8f27f0f"  # GenesisByte: parampara % 37 == 0

import json
from typing import List, Tuple
from vibe_core.protocols.naga.cli_command import (
    NagaCommandBase,
    NagaCommandResult,
    naga_command)
from vibe_core.protocols.substrate import MantraOpCode


@naga_command(
    opcode=MantraOpCode.AUDIT_SEAL,
    name="bite",
    help_text="Record a violation to Ledger (TAKSHAKA bite / YAMARAJA judgment)")
class BiteCommand(NagaCommandBase):
    def execute(self, args: List[str]) -> NagaCommandResult:
        if not args:
            return self.failure("Usage: naga bite <violation_type> [--details <json>]", exit_code=1)

        violation_type = args[0]
        details = {}

        for i, arg in enumerate(args):
            if arg == "--details" and i + 1 < len(args):
                details = json.loads(args[i + 1])

        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.naga import NagaFederationProtocol, VajraViolation

            federation = ServiceRegistry.get(NagaFederationProtocol)
            if federation and federation.takshaka:
                violation = VajraViolation(
                    violation_type=violation_type,
                    source="naga_cli",
                    details=details,
                )
                event_id = federation.takshaka.bite(violation)
                output = f"[YAMARAJA] Bite Recorded: {event_id}\nViolation: {violation_type}"
                return self.success(output)
            else:
                return self.failure("Takshaka not available to perform bite.", exit_code=1)
        except Exception as e:
            return self.failure(f"Bite failed: {e}", exit_code=1)
