"""
OPUS-310: Chat Command - Indriya-Compliant (Gemini Critique Fixed)

NATURAL FLOW (Living Entity Architecture):
    CLI (Vishaya/World) → ChatIndriya (Sense Organ) → ChatService (Brain) → LLM

VRTTI STATE MACHINE:
    1. User input → NIDRA → PRAMANA (wake up, perceive)
    2. Processing → PRAMANA → VIKALPA (inference)
    3. Response → VIKALPA → SMRTI (memory)
    4. Idle → SMRTI → NIDRA (sleep)

The CLI is the external world. It must touch the SENSES (Indriya),
not the SOUL (Service) directly. This is the natural order.

NO BYPASS SURGERY. Signal flows through proper channels.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "manu"
__position__ = 7
__genesis__ = "0xa2c02098"  # GenesisByte: parampara % 37 == 0

from typing import List
import uuid

from vibe_core.protocols.command import (
    BaseCommand,
    CommandContext,
    CommandResult,
    ParameterSpec,
    ParameterType,
)


class ChatCommand(BaseCommand):
    """Chat via ChatProtocol with full semantic routing."""

    name = "chat"
    description = "Chat with semantic routing (ChatProtocol → SemanticRouter → Mahajana)"
    source = "core"
    tags = ["chat", "protocol", "semantic"]

    _parameters = [
        ParameterSpec(
            name="message",
            param_type=ParameterType.STRING,
            required=True,
            description="The message to process (semantically routed)",
        ),
    ]

    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """Execute chat via ChatIndriya with Vrtti state management.

        NATURAL FLOW (Gemini Critique Compliant):
            CLI (Vishaya) → ChatIndriya (Sense Organ) → ChatService (Brain)

        The Indriya manages Vrtti state transitions:
            NIDRA → PRAMANA → VIKALPA → SMRTI → NIDRA
        """
        message = " ".join(args) if args else ""

        if not message:
            return CommandResult(
                success=False,
                error="No message provided. Usage: steward chat <message>",
            )

        try:
            # Import ChatIndriya (THE SENSE ORGAN - not ChatService directly!)
            from vibe_core.services.chat_indriya import get_chat_indriya

            # Get sense organ (via ServiceRegistry, NAGA-wrapped)
            indriya = get_chat_indriya()

            # Create session ID
            session_id = str(uuid.uuid4())

            # Execute through INDRIYA (not Service!)
            # This triggers: NIDRA → PRAMANA → VIKALPA → SMRTI → NIDRA
            response_tanmatra = await indriya.chat(message, session_id)

            # Extract response data from TanmatraMessage
            metadata = response_tanmatra.metadata or {}
            success = metadata.get("success", True)
            mahajana = metadata.get("mahajana", "narada")

            if success:
                return CommandResult(
                    success=True,
                    output=f"🕉️ [{mahajana}] {response_tanmatra.content}",
                    data={
                        "mahajana": mahajana,
                        "intent": response_tanmatra.intent.value,
                        "tanmatra": response_tanmatra.tanmatra.value,
                        "message_id": response_tanmatra.message_id,
                        "vrtti_compliant": True,  # Went through proper state machine
                    },
                )
            else:
                return CommandResult(
                    success=False,
                    error=f"Chat failed: {response_tanmatra.content}",
                )

        except Exception as e:
            return CommandResult(
                success=False,
                error=f"Chat failed: {e}",
            )
