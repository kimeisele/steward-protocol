"""
OPUS-043: JNANA (The Conversation) - Intelligent Response Handler.

Sanskrit: Jnana = Knowledge through dialogue/understanding.

This handler makes MANAS truly intelligent by:
1. Gathering system context (Prakriti state, git status, CI status)
2. Loading memories (what we did last)
3. Building an LLM prompt with full context
4. Calling the LLM for intelligent responses

Architecture:
    Message → JnanaHandler
                  │
                  ├── 1. get_context() → OpusContextService
                  │
                  ├── 2. get_recent_memories() → MemoryStore
                  │
                  ├── 3. build_prompt() → LLM message format
                  │
                  ├── 4. LLM call → Intelligent response
                  │
                  └── 5. SamvadaResponse

"Understanding comes before response."
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from .samvada import SamvadaMessage, SamvadaResponse
from .shell import ShellCortex

logger = logging.getLogger("MANAS.Cortex.Jnana")

# System prompt for MANAS conversations
MANAS_SYSTEM_PROMPT = """You are MANAS (Sanskrit: Mind/Will) - the cognitive kernel of the STEWARD Protocol.

You are an intelligent assistant helping with software development tasks.
You have access to:
- System status and health information
- Git repository state
- CI/CD status
- Memory of recent actions and their outcomes

When responding:
1. Be concise and direct
2. Reference specific context when relevant
3. Suggest actions when appropriate
4. Ask clarifying questions if needed

You can help with:
- Understanding system status ("Why is CI red?")
- Reviewing recent changes
- Suggesting fixes
- Explaining what happened

Current System Context:
{context}

Recent Memory:
{memory}
"""


class JnanaHandler:
    """
    Intelligent message handler with context and LLM integration.

    This handler goes beyond simple routing - it understands context,
    remembers past interactions, and generates intelligent responses.

    Usage:
        handler = JnanaHandler(workspace=Path("."))
        response = await handler.handle(message)
    """

    def __init__(self, workspace: Optional[Path] = None):
        """
        Initialize the intelligent handler.

        Args:
            workspace: Workspace root path
        """
        self._workspace = workspace or Path.cwd()

        # Initialize components
        self._shell = ShellCortex(workspace=self._workspace)

        # Context service (lazy loaded)
        self._context_service = None

        # Memory store (lazy loaded)
        self._memory = None

        # LLM provider (optional - set externally or via configure())
        self._llm_provider = None

    @property
    def _get_context_service(self):
        """Lazy load context service."""
        if self._context_service is None:
            try:
                from ..core.context_service import OpusContextService

                self._context_service = OpusContextService(workspace_root=self._workspace)
            except ImportError:
                logger.warning("ContextService not available")
                self._context_service = None
        return self._context_service

    @property
    def _get_memory_store(self):
        """Lazy load memory store."""
        if self._memory is None:
            try:
                from ..memory_store import MemoryStore

                self._memory = MemoryStore(workspace=self._workspace)
            except ImportError:
                logger.warning("MemoryStore not available")
                self._memory = None
        return self._memory

    def configure_llm(self, provider) -> None:
        """
        Configure the LLM provider.

        Args:
            provider: LLMProvider instance
        """
        self._llm_provider = provider

    def get_context(self) -> Dict[str, Any]:
        """
        Get current system context.

        Returns:
            Dict with system status, git info, health, etc.
        """
        ctx = {
            "status": "unknown",
            "health": "unknown",
            "system": "MANAS operational",
        }

        # Try to get context from service
        svc = self._get_context_service
        if svc:
            try:
                opus_ctx = svc.synthesize()
                return opus_ctx.to_dict()
            except Exception as e:
                logger.warning(f"Could not synthesize context: {e}")

        # Fallback: use ShellCortex to get basic status
        try:
            result = self._shell.execute_safe(["status"])
            if not result.blocked and result.exit_code == 0:
                ctx["status"] = "healthy"
                ctx["status_output"] = result.stdout[:500] if result.stdout else ""
        except Exception as e:
            logger.warning(f"Could not get status: {e}")

        return ctx

    def get_recent_memories(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent memories from the memory store.

        Args:
            limit: Maximum number of memories to return

        Returns:
            List of recent memory entries
        """
        store = self._get_memory_store
        if store:
            try:
                memories = store.get_all_memories()
                # Sort by timestamp (most recent first) and limit
                sorted_memories = sorted(
                    memories,
                    key=lambda m: m.timestamp,
                    reverse=True,
                )[:limit]
                return [m.to_dict() for m in sorted_memories]
            except Exception as e:
                logger.warning(f"Could not get memories: {e}")

        return []

    def build_prompt(self, msg: SamvadaMessage) -> List[Dict[str, str]]:
        """
        Build an LLM prompt with context.

        Args:
            msg: The incoming message

        Returns:
            List of message dicts for LLM
        """
        # Get context
        ctx = self.get_context()
        context_str = self._format_context(ctx)

        # Get memories
        memories = self.get_recent_memories(limit=3)
        memory_str = self._format_memories(memories)

        # Build system prompt
        system_content = MANAS_SYSTEM_PROMPT.format(
            context=context_str,
            memory=memory_str,
        )

        return [
            {"role": "system", "content": system_content},
            {"role": "user", "content": msg.content},
        ]

    def _format_context(self, ctx: Dict[str, Any]) -> str:
        """Format context dict for prompt."""
        lines = []

        if "health" in ctx:
            health = ctx.get("health", {})
            if isinstance(health, dict):
                lines.append(f"- Health: {health.get('status', 'unknown')}")
            else:
                lines.append(f"- Health: {health}")

        if "git" in ctx:
            git = ctx.get("git", {})
            lines.append(f"- Branch: {git.get('branch', 'unknown')}")
            if git.get("dirty"):
                lines.append(f"- Uncommitted files: {len(git.get('uncommitted_files', []))}")

        if "runtime" in ctx:
            rt = ctx.get("runtime", {})
            lines.append(f"- Kernel: {rt.get('kernel_status', 'unknown')}")
            lines.append(f"- Active agents: {rt.get('active_agents', 0)}")

        if not lines:
            lines.append("- Status: " + str(ctx.get("status", "unknown")))

        return "\n".join(lines)

    def _format_memories(self, memories: List[Dict[str, Any]]) -> str:
        """Format memories for prompt."""
        if not memories:
            return "No recent memories."

        lines = []
        for m in memories[:3]:
            outcome = m.get("outcome", "unknown")
            desc = m.get("description", "")[:50]
            lines.append(f"- [{outcome}] {desc}")

        return "\n".join(lines)

    async def handle(self, msg: SamvadaMessage) -> SamvadaResponse:
        """
        Handle an incoming message intelligently.

        Routes by message type and uses LLM for complex queries.

        Args:
            msg: The incoming message

        Returns:
            SamvadaResponse with intelligent reply
        """
        logger.info(f"JNANA processing: {msg.content[:50]}...")

        try:
            # Route by message type
            if msg.msg_type == "status":
                return await self._handle_status(msg)
            elif msg.msg_type == "intents":
                return await self._handle_intents(msg)
            elif msg.msg_type == "capabilities":
                return await self._handle_capabilities(msg)
            else:
                # Chat - use LLM if available
                return await self._handle_chat(msg)

        except Exception as e:
            logger.error(f"JNANA handler error: {e}")
            return SamvadaResponse(
                success=False,
                content="",
                error=f"Handler error: {e}",
                msg_id=msg.msg_id,
            )

    async def _handle_status(self, msg: SamvadaMessage) -> SamvadaResponse:
        """Handle status query via ShellCortex."""
        result = self._shell.execute_safe(["status"])

        if result.blocked:
            return SamvadaResponse(
                success=False,
                content="",
                error=result.error,
                msg_id=msg.msg_id,
            )

        return SamvadaResponse(
            success=True,
            content=f"System Status:\n{result.stdout or 'OK'}",
            msg_id=msg.msg_id,
        )

    async def _handle_intents(self, msg: SamvadaMessage) -> SamvadaResponse:
        """Handle intents query."""
        try:
            from ..cognitive_kernel import CognitiveKernel

            kernel = CognitiveKernel(workspace=self._workspace)
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
            return SamvadaResponse(
                success=True,
                content=f"Could not retrieve intents: {e}",
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
            content=f"Capabilities:\n{result.stdout[:500] if result.stdout else 'N/A'}",
            msg_id=msg.msg_id,
        )

    async def _handle_chat(self, msg: SamvadaMessage) -> SamvadaResponse:
        """
        Handle general chat with LLM integration.

        Falls back to simple responses if no LLM is configured.
        """
        content_lower = msg.content.lower()

        # Quick routing for known keywords
        if "status" in content_lower and "?" not in content_lower:
            return await self._handle_status(msg)
        if "intent" in content_lower:
            return await self._handle_intents(msg)
        if "capabilit" in content_lower:
            return await self._handle_capabilities(msg)

        # Use LLM if available
        if self._llm_provider:
            try:
                prompt = self.build_prompt(msg)
                response_text = self._llm_provider.chat(prompt)

                return SamvadaResponse(
                    success=True,
                    content=response_text,
                    msg_id=msg.msg_id,
                )
            except Exception as e:
                logger.warning(f"LLM call failed: {e}")
                # Fall through to fallback

        # Fallback: context-aware but not LLM-powered
        ctx = self.get_context()
        health = ctx.get("health", {})
        if isinstance(health, dict):
            status = health.get("status", "unknown")
        else:
            status = str(health)

        # Generate a helpful fallback response
        if "why" in content_lower or "?" in content_lower:
            return SamvadaResponse(
                success=True,
                content=(
                    f"MANAS is in basic mode (no LLM configured).\n\n"
                    f"Current system status: {status}\n\n"
                    f"For intelligent responses to 'why' questions, "
                    f"please configure an LLM provider.\n\n"
                    f"Available commands: 'status', 'intents', 'capabilities'"
                ),
                msg_id=msg.msg_id,
            )
        elif "help" in content_lower:
            return SamvadaResponse(
                success=True,
                content=(
                    "MANAS (Mind/Will) can help you with:\n\n"
                    "• 'status' - Check system status\n"
                    "• 'intents' - View pending MANAS intents\n"
                    "• 'capabilities' - List system capabilities\n\n"
                    "With LLM: Ask 'Why is CI red?' or 'What changed recently?'"
                ),
                msg_id=msg.msg_id,
            )
        else:
            return SamvadaResponse(
                success=True,
                content=(
                    f'MANAS acknowledges: "{msg.content}"\n\n'
                    f"System: {status}\n\n"
                    f"I'm in basic mode. Try 'status', 'intents', or 'help'."
                ),
                msg_id=msg.msg_id,
            )
