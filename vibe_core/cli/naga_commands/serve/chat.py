"""
CHAT COMMAND - PRAHLADA's Service (Dumb I/O Interface)
======================================================

MAHAJANA: PRAHLADA (The Resilient)
OPCODE: EXTEND_CAP (Position 9)
PHASE: SERVE

ARCHITECTURE (Live Computed Routing):
    User Input → mahamantra() → Position/Guardian → CLI Command

    mahamantra() routing is 100% LIVE COMPUTED:
    Input → Seed (MahaCompression) → Attractor (MahaModularSynth) → Position = attractor % 16

    NO HARDCODED KEYWORDS.
    NO PATTERN MATCHING.
    PURE MATHEMATICAL ROUTING FROM THE SEED.

PRAHLADA is just a relay. The Core decides via computation.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xedb5ebb8"  # GenesisByte: parampara % 37 == 0

from typing import List, Optional

from vibe_core.mahamantra.substrate.harmonics import ResonanceHarmonics
from vibe_core.protocols.naga.cli_command import (
    NAGA_COMMAND_REGISTRY,
    NagaCommandBase,
    NagaCommandResult,
    naga_command,
)
from vibe_core.protocols.substrate import MantraOpCode

# =============================================================================
# GUARDIAN → COMMAND MAPPING (The only config here)
# =============================================================================
# Maps guardian names to CLI commands they can execute.
# This is WIRING, not INTELLIGENCE.

GUARDIAN_COMMANDS = {
    "vyasa": "boot",  # Position 0 - System Wake
    "brahma": "spawn",  # Position 1 - Creation
    "narada": "chat",  # Position 2 - Communication (fallback to self)
    "shambhu": "purge",  # Position 3 - Destruction
    "prithu": "scan",  # Position 4 - Compile/Structure
    "kumaras": "purify",  # Position 5 - Purification
    "kapila": "analyze",  # Position 6 - Analysis
    "manu": "govern",  # Position 7 - Governance
    "parashurama": "execute",  # Position 8 - Execution
    "prahlada": None,  # Position 9 - Chat (self - no routing)
    "janaka": "schedule",  # Position 10 - Scheduling
    "bhishma": "persist",  # Position 11 - Persistence
    "nrisimha": "guard",  # Position 12 - Security
    "bali": "allocate",  # Position 13 - Resources
    "shuka": "intel",  # Position 14 - Observation
    "yamaraja": "audit",  # Position 15 - Judgment
}


@naga_command(
    opcode=MantraOpCode.EXTEND_CAP,
    name="chat",
    help_text="PRAHLADA - Chat with the system, routes via mahamantra() live computed",
)
class ChatCommand(NagaCommandBase):
    """
    Chat command - dumb I/O interface.

    ALL INTELLIGENCE IS IN THE CORE (mahamantra):
    - MahaCompression computes seed from input
    - MahaModularSynth computes attractor from seed
    - Position = attractor % 16 (deterministic)

    This command just:
    1. Calls mahamantra(input) for live computed routing
    2. Maps guardian → CLI command
    3. Executes and returns result
    """

    def execute(self, args: List[str]) -> NagaCommandResult:
        """Execute chat via mahamantra() - live computed routing."""
        from vibe_core.cli.naga_commands import discover_commands

        discover_commands()

        if not args:
            return self.failure(
                "No message provided. Usage: naga chat <message>",
                exit_code=1,
            )

        message = " ".join(args)

        # === THE CORE DECIDES (LIVE COMPUTED ROUTING) ===
        # mahamantra() uses: Input → Seed → Attractor → Position = attractor % 16
        # NO keywords, NO hardcoded patterns - 100% mathematically computed
        from vibe_core.mahamantra import mahamantra

        result = mahamantra(message)

        # Extract routing info from live computed result
        guardian = result.get("guardian")
        position = result.get("position", -1)
        quarter = result.get("quarter", "unknown")

        # Live computed routing = deterministic = always confident
        # Score represents routing confidence (1.0 = fully computed)
        score = 1.0 if guardian else 0.0

        # === ROUTING DECISION ===
        if guardian:
            # Route to guardian's command (live computed)
            command_name = GUARDIAN_COMMANDS.get(guardian.lower())

            if command_name and command_name != "chat":
                return self._route_to_command(command_name, guardian, message, score)

        # Fallback: PRAHLADA responds directly (prahlada maps to None in GUARDIAN_COMMANDS)
        return self._chat_response(message, score, guardian)

    def _route_to_command(self, command_name: str, guardian: str, message: str, score: float) -> NagaCommandResult:
        """Route to another command based on resonance."""
        command = NAGA_COMMAND_REGISTRY.get(command_name)

        if not command:
            # Command not found - fall back to chat response
            return self._chat_response(message, score, guardian, note=f"(Command '{command_name}' not registered)")

        # Execute routed command
        result = command.execute([])  # No args extraction - keep it simple

        # Attribution header
        header = f"[PRAHLADA → {guardian.upper()}] Resonance: {score:.2f}\n\n"

        return NagaCommandResult(
            success=result.success,
            exit_code=result.exit_code,
            output=header + result.output,
            error=result.error,
            opcode=result.opcode,
            data=result.data
            + (
                ("routed_by", "prahlada"),
                ("resonance_score", score),
                ("guardian", guardian),
            ),
        )

    def _chat_response(self, message: str, score: float, guardian: Optional[str], note: str = "") -> NagaCommandResult:
        """
        Direct response when resonance too low for routing.

        NO KEYWORD MATCHING. Just report the resonance state.
        The Core decides, CLI reports.
        """
        # Report resonance state - no interpretation
        response = f"[PRAHLADA] Resonance: {score:.3f}"
        if guardian:
            response += f" → {guardian.upper()}"
        if score < ResonanceHarmonics.THRESHOLD_REFINE:
            response += " (below threshold)"
        response += f'\n\nInput: "{message}"'
        if note:
            response += f"\n{note}"

        return self.success(
            response,
            data=(
                ("resonance_score", score),
                ("guardian", guardian or "none"),
                ("threshold", ResonanceHarmonics.THRESHOLD_REFINE),
            ),
        )

    def _get_help(self) -> str:
        """Help text - shows the INTENT_MAP truth, not local lies."""
        from vibe_core.mahamantra.substrate.intents import INTENT_MAP
        from vibe_core.mahamantra.substrate.seed import ALL_GUARDIANS

        lines = ["[PRAHLADA] Available intents (from INTENT_MAP SSOT):\n"]

        for pos, intents in sorted(INTENT_MAP.items()):
            guardian = ALL_GUARDIANS[pos].upper()
            cmd = GUARDIAN_COMMANDS.get(ALL_GUARDIANS[pos], "?")
            keywords = ", ".join(intents[:5])
            if len(intents) > 5:
                keywords += "..."
            lines.append(f"  {guardian} ({cmd}): {keywords}")

        return "\n".join(lines)


__all__ = ["ChatCommand", "GUARDIAN_COMMANDS"]
