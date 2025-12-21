"""
OPUS-042: SAMVADA Handler - MANAS Message Processing.

This handler connects SamvadaListener to the MANAS CognitiveKernel,
allowing real-time dialogue between human and machine.

Architecture:
    Message → SamvadaHandler → CognitiveKernel → Response
                    │
                    ├── status: Query system status via ShellCortex
                    ├── intents: Get pending intents
                    └── chat: LLM-powered response (future)

"The mind must understand before it responds."
"""

import logging
from pathlib import Path
from typing import Optional

from .samvada import SamvadaMessage, SamvadaResponse
from .shell import ShellCortex

logger = logging.getLogger("MANAS.Cortex.SamvadaHandler")


class SamvadaHandler:
    """
    Handler for SAMVADA messages.

    Connects human messages to MANAS intelligence.

    Message Types:
    - status: Query system status
    - intents: Get pending MANAS intents
    - capabilities: Get system capabilities
    - chat: General conversation (requires LLM)

    Usage:
        handler = SamvadaHandler(workspace=Path("."))
        response = await handler.handle(message)
    """

    def __init__(self, workspace: Optional[Path] = None):
        """
        Initialize the handler.

        Args:
            workspace: Workspace root path
        """
        self._workspace = workspace or Path.cwd()
        self._shell = ShellCortex(workspace=self._workspace)

    async def handle(self, msg: SamvadaMessage) -> SamvadaResponse:
        """
        Handle an incoming message.

        Args:
            msg: The incoming message

        Returns:
            SamvadaResponse with MANAS reply
        """
        logger.info(f"Processing message: {msg.msg_type} - {msg.content[:50]}...")

        try:
            # Route by message type
            if msg.msg_type == "status":
                return await self._handle_status(msg)
            elif msg.msg_type == "intents":
                return await self._handle_intents(msg)
            elif msg.msg_type == "capabilities":
                return await self._handle_capabilities(msg)
            else:
                # Default: chat (interpret intent from content)
                return await self._handle_chat(msg)

        except Exception as e:
            logger.error(f"Handler error: {e}")
            return SamvadaResponse(
                success=False,
                content="",
                error=f"Handler error: {e}",
                msg_id=msg.msg_id,
            )

    async def _handle_status(self, msg: SamvadaMessage) -> SamvadaResponse:
        """Handle status query."""
        result = self._shell.execute_safe(["status"])

        if result.blocked:
            return SamvadaResponse(
                success=False,
                content="",
                error=result.error,
                msg_id=msg.msg_id,
            )

        status_text = result.stdout.strip() if result.stdout else "Status check complete"

        return SamvadaResponse(
            success=True,
            content=f"System Status:\n{status_text}",
            msg_id=msg.msg_id,
        )

    async def _handle_intents(self, msg: SamvadaMessage) -> SamvadaResponse:
        """Handle intents query."""
        try:
            from ..cognitive_kernel import CognitiveKernel

            # OPUS-167: Use singleton pattern to avoid expensive re-initialization
            kernel = CognitiveKernel.get_instance(workspace=self._workspace)
            pending = kernel.get_pending_intents()

            if not pending:
                return SamvadaResponse(
                    success=True,
                    content="No pending intents. MANAS is idle.",
                    msg_id=msg.msg_id,
                )

            intent_list = "\n".join([f"- [{i.priority.value.upper()}] {i.title}" for i in pending[:5]])

            return SamvadaResponse(
                success=True,
                content=f"Pending Intents ({len(pending)}):\n{intent_list}",
                msg_id=msg.msg_id,
            )

        except Exception as e:
            logger.warning(f"Could not get intents: {e}")
            return SamvadaResponse(
                success=True,
                content="Intent buffer not available.",
                msg_id=msg.msg_id,
            )

    async def _handle_capabilities(self, msg: SamvadaMessage) -> SamvadaResponse:
        """Handle capabilities query."""
        result = self._shell.execute_safe(["capabilities"])

        if result.blocked:
            return SamvadaResponse(
                success=False,
                content="",
                error=result.error,
                msg_id=msg.msg_id,
            )

        return SamvadaResponse(
            success=True,
            content=f"Capabilities:\n{result.stdout[:500]}",
            msg_id=msg.msg_id,
        )

    async def _handle_chat(self, msg: SamvadaMessage) -> SamvadaResponse:
        """
        Handle general chat message.

        For now, this provides a simple response. In the future,
        this will integrate with the LLM for intelligent responses.
        """
        content = msg.content.lower()

        # Simple keyword matching for common queries
        if "status" in content:
            return await self._handle_status(msg)
        elif "intent" in content:
            return await self._handle_intents(msg)
        elif "capabilit" in content:
            return await self._handle_capabilities(msg)
        elif "help" in content:
            return SamvadaResponse(
                success=True,
                content=(
                    "MANAS can help you with:\n"
                    "- 'status' - Check system status\n"
                    "- 'intents' - View pending MANAS intents\n"
                    "- 'capabilities' - List system capabilities\n"
                    "\nFor complex queries, I'll do my best to understand."
                ),
                msg_id=msg.msg_id,
            )
        else:
            # Default response for unrecognized queries
            return SamvadaResponse(
                success=True,
                content=(
                    f'MANAS acknowledges: "{msg.content}"\n\n'
                    "I'm currently in basic mode. For full LLM-powered responses, "
                    "the kernel must be booted with LLM support.\n\n"
                    "Try: 'status', 'intents', or 'help' for available commands."
                ),
                msg_id=msg.msg_id,
            )


async def create_manas_handler(workspace: Optional[Path] = None) -> "SamvadaHandler":
    """
    Factory function to create a MANAS-connected handler.

    Args:
        workspace: Workspace root path

    Returns:
        SamvadaHandler instance
    """
    return SamvadaHandler(workspace=workspace)
