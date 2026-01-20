"""
OPUS-310: Chat Command - Protocol-Compliant

Routes through ChatProtocol → SemanticRouter → Mahajana.
CLI → CommandRegistry → ChatCommand → ChatService → SemanticRouter → LLM

PROTOCOL FLOW:
    1. ChatService.chat() receives message
    2. OperatorCognitiveProtocol → CognitiveResult (intent)
    3. SemanticRouter → Mahajana routing
    4. KnowledgeGraph → Context enrichment
    5. LLM Provider → Response generation

NO KEYWORD MATCHING. Real semantic routing.
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
        """Execute chat via ChatProtocol with full semantic stack."""
        message = " ".join(args) if args else ""

        if not message:
            return CommandResult(
                success=False,
                error="No message provided. Usage: steward chat <message>",
            )

        try:
            # Import ChatService (protocol-compliant)
            from vibe_core.services.chat_service import get_chat_service
            from vibe_core.protocols.chat import ChatContext, ChatMessage

            # Get service
            chat_service = get_chat_service()

            # Create context
            session_id = str(uuid.uuid4())
            chat_context = ChatContext(
                session_id=session_id,
                history=[],
            )

            # Execute through protocol
            response = await chat_service.chat(message, chat_context)

            if response.success:
                return CommandResult(
                    success=True,
                    output=f"🕉️ [{response.mahajana}] {response.message.content}",
                    data={
                        "mahajana": response.mahajana,
                        "opcode": response.opcode,
                        "mode": response.mode.value,
                        "intent": response.intent_type.value if response.intent_type else None,
                        "confidence": response.confidence,
                        "protocol_compliant": True,
                    },
                )
            else:
                return CommandResult(
                    success=False,
                    error=f"Chat failed: {response.error}",
                )

        except Exception as e:
            return CommandResult(
                success=False,
                error=f"Chat failed: {e}",
            )
