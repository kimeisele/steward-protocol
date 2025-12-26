"""
OPUS-310: Chat Command

Routes to CognitiveProtocol.process_intent().
CLI → CommandRegistry → ChatCommand → Kernel → CognitiveProtocol → MANAS

No hardcoded plugin names. No shortcuts.
"""

from typing import List

from vibe_core.protocols.command import (
    BaseCommand,
    CommandContext,
    CommandResult,
    ParameterSpec,
    ParameterType,
)


class ChatCommand(BaseCommand):
    """Chat with the cognitive layer."""

    name = "chat"
    description = "Chat with the cognitive layer (MANAS or fallback)"
    source = "core"
    tags = ["cognitive", "chat", "manas"]

    _parameters = [
        ParameterSpec(
            name="message",
            param_type=ParameterType.STRING,
            required=True,
            description="The message to send",
        ),
    ]

    async def execute(self, args: List[str], context: CommandContext) -> CommandResult:
        """Execute chat via kernel's cognitive protocol."""
        message = " ".join(args) if args else ""

        if not message:
            return CommandResult(
                success=False,
                error="No message provided. Usage: steward chat <message>",
            )

        kernel = context.kernel
        if not kernel:
            return CommandResult(
                success=False,
                error="Kernel not available. Run 'steward boot' first.",
            )

        # Check for cognitive support
        if not hasattr(kernel, "process_operator_input"):
            return CommandResult(
                success=False,
                error="Kernel does not support cognitive processing (OPUS-309 required)",
            )

        try:
            # Import here to avoid circular dependency
            from vibe_core.protocols.cognition import IntentType

            result = await kernel.process_operator_input(message, context.session_id)

            # Handle by intent type
            if result.intent_type == IntentType.CHAT:
                return CommandResult(
                    success=True,
                    output=f"🗣️ {result.response}",
                    data={"intent": "chat", "confidence": result.confidence},
                )

            elif result.intent_type == IntentType.EXECUTE:
                output = f"🎯 Execution intent: {result.syscall_type}\n"
                if result.syscall_params:
                    output += f"   Parameters: {result.syscall_params}\n"
                output += f"   Confidence: {result.confidence:.0%}"
                if result.reasoning:
                    output += f"\n   Reasoning: {result.reasoning}"
                return CommandResult(
                    success=True,
                    output=output,
                    data={
                        "intent": "execute",
                        "syscall": result.syscall_type,
                        "params": result.syscall_params,
                    },
                )

            elif result.intent_type == IntentType.ROUTE:
                output = f"🔀 Routing to: {result.target}"
                if result.reasoning:
                    output += f"\n   Reason: {result.reasoning}"
                return CommandResult(
                    success=True,
                    output=output,
                    data={"intent": "route", "target": result.target},
                )

            elif result.intent_type == IntentType.QUERY:
                if result.query_result:
                    import json

                    return CommandResult(
                        success=True,
                        output=json.dumps(result.query_result, indent=2),
                        data={"intent": "query", "result": result.query_result},
                    )
                return CommandResult(
                    success=True,
                    output=f"🔍 Query: {result.query_type}",
                    data={"intent": "query", "type": result.query_type},
                )

            else:
                return CommandResult(
                    success=True,
                    output=f"Unknown intent type: {result.intent_type}",
                )

        except Exception as e:
            return CommandResult(
                success=False,
                error=f"Chat failed: {e}",
            )
