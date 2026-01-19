"""
PRAHLAD COMMAND - PRAHLADA's Resilience
=======================================

MAHAJANA: PRAHLADA (The Devotee)
OPCODE: EXEC_SERVICE (Position 9)
PHASE: SERVE

Usage:
    naga prahlad dharma     - Run Dharma audit
    naga prahlad coverage   - Get coverage intelligence
    naga prahlad verify     - Run NAGA self-verification
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "yamaraja"
__position__ = 15
__genesis__ = "0x9ccb973f"  # GenesisByte: parampara % 37 == 0

from typing import List, Tuple
from vibe_core.protocols.naga.cli_command import NagaCommandBase, NagaCommandResult, naga_command
from vibe_core.protocols.substrate import MantraOpCode


@naga_command(
    opcode=MantraOpCode.EXTEND_CAP, name="prahlad", help_text="Access Prahlad Resilience Agent (PRAHLADA's resilience)"
)
class PrahladCommand(NagaCommandBase):
    def execute(self, args: List[str]) -> NagaCommandResult:
        if not args:
            return self.success("[PRAHLADA] Subcommands: dharma, coverage, verify")

        subcmd = args[0]
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.naga import PrahladProtocol

            prahlad = ServiceRegistry.get(PrahladProtocol)
            if not prahlad:
                return self.failure("PrahladProtocol not available.", exit_code=1)

            if subcmd == "dharma":
                score = prahlad.dharma_audit()
                output = f"[PRAHLADA] Dharma Audit: {score.total_score:.1f}%\nStatus: {'DHARMIC' if score.total_score >= 80 else 'ADHARMIC'}"
                return self.success(output)
            elif subcmd == "coverage":
                intel = prahlad.get_coverage_intelligence()
                output = f"[PRAHLADA] Coverage: {intel.get('total_tests', 0)} tests available."
                return self.success(output)
            elif subcmd == "verify":
                passed = prahlad.verify_self_integrity(quiet=False)
                output = "[PRAHLADA] NAGA IS WATERTIGHT" if passed else "[PRAHLADA] NAGA COMPROMISED"
                return self.success(output if passed else output, exit_code=0 if passed else 1)
            else:
                return self.failure(f"Unknown prahlad command: {subcmd}", exit_code=1)
        except Exception as e:
            return self.failure(f"Prahlad command failed: {e}", exit_code=1)
