"""
OPUS-310: Chat Command - Mahamantra Routed

Routes through mahamantra.resonate() → Guardian's chat() method.
CLI → CommandRegistry → ChatCommand → Mahamantra → Guardian.chat()

"steward chat ist nicht nur 1 chat" - Each guardian has their own chat domain.
- Kapila handles "analyze" questions
- Yamaraja handles "audit" questions
- Narada handles general communication
- etc.

MAHAMANTRA ROUTING:
    1. mahamantra.resonate(message) finds the best matching guardian
    2. Guardian's chat() method is called
    3. If no specific match, Narada (position 2) handles it
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 2
__genesis__ = "0xa2c02098"  # GenesisByte: parampara % 37 == 0

from typing import List

from vibe_core.protocols.command import (
    BaseCommand,
    CommandContext,
    CommandResult,
    ParameterSpec,
    ParameterType,
)


class ChatCommand(BaseCommand):
    """Chat routed through Mahamantra - each guardian handles their domain."""

    name = "chat"
    description = "Chat with the Mahamantra (routed to appropriate guardian)"
    source = "core"
    tags = ["mahamantra", "chat", "resonance"]

    _parameters = [
        ParameterSpec(
            name="message",
            param_type=ParameterType.STRING,
            required=True,
            description="The message to send (routed via mahamantra.resonate)",
        ),
    ]

    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """Execute chat via 12-NAGA flooded mahamantra routing."""
        message = " ".join(args) if args else ""

        if not message:
            return CommandResult(
                success=False,
                error="No message provided. Usage: steward chat <message>",
            )

        try:
            # NAGA x MAHAMANTRA = BOOM
            # Use flooded chat with all 12 NAGA genes
            from vibe_core.mahamantra.chat import (
                flooded_routed_chat,
                get_guardian_for_message,
            )

            # 1. Find the resonating guardian
            guardian = get_guardian_for_message(message)

            # 2. Execute through 12-NAGA flooded chat
            response = flooded_routed_chat(message)

            return CommandResult(
                success=True,
                output=f"🕉️ [NAGA x {guardian.upper()}] {response}",
                data={
                    "guardian": guardian,
                    "naga_flooded": True,
                    "naga_genes": 12,
                },
            )

        except Exception as e:
            return CommandResult(
                success=False,
                error=f"Chat failed: {e}",
            )
