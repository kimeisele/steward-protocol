"""
AUDIT COMMAND - VYASA's Records
===============================

MAHAJANA: VYASA (The Avatara Compiler)
OPCODE: ASSERT_TRUTH (Position 4)
PHASE: PURIFY

Usage:
    naga audit                    # Show recent events
    naga audit --type <type>      # Filter by event type
    naga audit --limit <n>        # Limit number of results
"""

from typing import List, Tuple
from vibe_core.protocols.naga.cli_command import (
    NagaCommandBase,
    NagaCommandResult,
    naga_command)
from vibe_core.protocols.substrate import MantraOpCode


@naga_command(
    opcode=MantraOpCode.ASSERT_TRUTH,
    name="audit",
    help_text="Query Ledger audit trail (VYASA's records)")
class AuditCommand(NagaCommandBase):
    def execute(self, args: List[str]) -> NagaCommandResult:
        try:
            from vibe_core.di import ServiceRegistry
            from vibe_core.protocols.naga import NagaFederationProtocol

            federation = ServiceRegistry.get(NagaFederationProtocol)
            if not federation or not federation.sesha:
                return self.failure("Sesha (Ledger) not available. Boot the kernel first.", exit_code=1)

            limit = 10
            event_type = None

            for i, arg in enumerate(args):
                if arg == "--limit" and i + 1 < len(args):
                    limit = int(args[i + 1])
                elif arg == "--type" and i + 1 < len(args):
                    event_type = args[i + 1]

            sesha = federation.sesha
            if event_type:
                events = sesha.get_events_by_type(event_type, limit=limit)
            else:
                events = sesha.get_recent_events(limit=limit)

            output_lines = [
                "[VYASA] Audit Trail",
                "=" * 60,
                f"  Recent Events (limit={limit}):",
            ]

            for event in events:
                e = event.to_dict() if hasattr(event, "to_dict") else event
                output_lines.append(f"    [{e.get('event_type', 'UNKNOWN')}] {e.get('timestamp', '')}")
                output_lines.append(f"      Agent: {e.get('agent_id', 'unknown')}")

            output_lines.append("=" * 60)
            
            return self.success("\n".join(output_lines))
        except Exception as e:
            return self.failure(f"Audit query failed: {e}", exit_code=1)
