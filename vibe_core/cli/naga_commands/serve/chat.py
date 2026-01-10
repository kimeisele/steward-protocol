"""
CHAT COMMAND - PRAHLADA's Service
=================================

MAHAJANA: PRAHLADA (The Resilient)
OPCODE: EXEC_SERVICE (Position 9)
PHASE: SERVE

WHY PRAHLADA?
- Prahlada maintained devotion despite all obstacles
- He is the embodiment of resilience in service
- Chat requires persistent, resilient connection

MANTRA WORD: RAMA (Position 9)
"Rama protects those who take shelter"

Usage:
    naga chat "Hello, how are you?"
    naga chat --context security "Analyze this threat"
"""

from typing import List, Tuple

from vibe_core.protocols.naga.cli_command import (
    Mahajana,
    NagaCommandBase,
    NagaCommandResult,
    naga_command,
)
from vibe_core.protocols.substrate import MantraOpCode


@naga_command(
    opcode=MantraOpCode.EXEC_SERVICE,
    mahajana=Mahajana.PRAHLADA,
    name="chat",
    help_text="Chat with the cognitive layer (PRAHLADA's service)",
)
class ChatCommand(NagaCommandBase):
    """
    Chat command implementation.

    Routes to cognitive protocol for natural language processing.
    Resilient: falls back gracefully if cognitive layer unavailable.
    """

    def execute(self, args: List[str]) -> NagaCommandResult:
        """
        Execute chat command.

        Args:
            args: Message parts to join

        Returns:
            NagaCommandResult with response or error
        """
        if not args:
            return self.failure(
                "No message provided. Usage: naga chat <message>",
                exit_code=1,
            )

        message = " ".join(args)

        # Check for context flag
        context = "general"
        if "--context" in args:
            try:
                idx = args.index("--context")
                context = args[idx + 1]
                # Remove context args from message
                message = " ".join(args[:idx] + args[idx + 2:])
            except (IndexError, ValueError):
                return self.failure(
                    "Invalid --context flag. Usage: --context <type>",
                    exit_code=1,
                )

        # Try to get cognitive response
        try:
            response = self._process_chat(message, context)
            return self.success(
                response,
                data=(
                    ("message", message),
                    ("context", context),
                    ("mahajana", "prahlada"),
                ),
            )
        except Exception as e:
            # Prahlada is resilient - graceful degradation
            return self.failure(
                f"Chat service unavailable: {e}",
                exit_code=2,
            )

    def _process_chat(self, message: str, context: str) -> str:
        """
        Process chat message through cognitive layer.

        This is a placeholder - actual implementation would route
        to CognitiveProtocol or MANAS.
        """
        # Placeholder: actual implementation would use:
        # - vibe_core.protocols.cognition.CognitiveProtocol
        # - Or direct MANAS integration

        # For now, acknowledge receipt
        return f"[PRAHLADA] Received: {message} (context: {context})"


# Export for direct import
__all__ = ["ChatCommand"]
