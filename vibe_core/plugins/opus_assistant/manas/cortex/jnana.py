"""
OPUS-043: JNANA (The Conversation) - Intelligent Response Handler.
OPUS-045: KRIYA (Action) - Chat to Intent Bridge Integration.
OPUS-048: DHARMA (Das kosmische Gesetz) - Architectural Drift Integration.
OPUS-050: VEDA (The Four-Fold Knowledge) - Pipeline Integration.
OPUS-052: AKASHA (The Cosmic Ether) - Knowledge Graph Integration.
OPUS-053: SILPA (The Self-Architect) - Safe Code Refactoring Integration.
OPUS-054: SUTRA (The Thread) - Wiki Documentation Weaver Integration.
OPUS-055: SANKALPA (The Will) - Proactive Strategy Integration.

Sanskrit: Jnana = Knowledge through dialogue/understanding.
Sanskrit: Kriya = Completed Action / Sacred Deed.
Sanskrit: Dharma = The cosmic law, duty, order that prevents chaos.
Sanskrit: Veda = Sacred Knowledge, the four-fold processing wisdom.
Sanskrit: Akasha = Ether/Space, the element that contains all knowledge.
Sanskrit: Silpa = Art, Craft, Architecture - the ability to reshape.
Sanskrit: Sutra = Thread, String - weaving knowledge into documentation.
Sanskrit: Sankalpa = Solemn Vow, Will - the intention that shapes reality.

This handler makes MANAS truly intelligent by:
1. Gathering system context (Prakriti state, git status, CI status)
2. Loading memories (what we did last)
3. Building an LLM prompt with full context
4. Calling the LLM for intelligent responses
5. [KRIYA] Extracting action intents from responses

OPUS-050 Architecture (VEDA-4 Pipeline):
    Message → VedaPipeline
                  │
                  ├── 1. SHABDA (Das Wort)
                  │       └── Tokenize, extract keywords, detect language
                  │
                  ├── 2. ARTHA (Die Bedeutung)
                  │       └── Map tokens to intents, determine route
                  │
                  ├── 3. PRATYAYA (Das Vertrauen)
                  │       └── Check authorization, validate state
                  │
                  └── 4. KARMA (Die Handlung)
                          └── Execute handler → SamvadaResponse

"First the word is heard (Shabda), then its meaning understood (Artha),
then trust is established (Pratyaya), and only then can action flow (Karma)."
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from .akasha import handle_akasha_query
from .dharma import check_drift_for_chat
from .kriya import KriyaBridge, KriyaExtractor
from .mandala import get_mandala_for_chat
from .samvada import SamvadaMessage, SamvadaResponse
from .sankalpa import handle_sankalpa_query
from .shell import ShellCortex
from .silpa import handle_silpa_query
from .sutra import handle_sutra_query
from .veda import VedaContext, VedaPipeline, VedaTrustLevel

# OPUS-048: Keywords that trigger drift checking (German + English)
# NOTE: These are now also defined in veda.py (Artha.INTENT_KEYWORDS)
# Kept here for backwards compatibility during transition
DRIFT_KEYWORDS = {
    # German
    "drift",
    "verstöße",
    "verstoße",
    "architektur-drift",
    "compliance",
    "dharma",
    "architektur prüfen",
    "architektur audit",
    # English
    "architecture",
    "violations",
    "architectural drift",
    "architecture check",
    "audit architecture",
}

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

        # OPUS-045: KRIYA bridge for chat-to-action
        self._kriya = KriyaBridge(workspace=self._workspace)

        # OPUS-050: VEDA Pipeline for four-fold processing
        self._veda = VedaPipeline(default_trust=VedaTrustLevel.USER)
        self._register_veda_handlers()

        # Context service (lazy loaded)
        self._context_service = None

        # Memory store (lazy loaded)
        self._memory = None

        # LLM provider (auto-loaded from config/env via factory)
        # OPUS-076: NO PUSSY MODE - real LLM calls, not simulation!
        try:
            from vibe_core.runtime.providers.factory import get_default_provider

            self._llm_provider = get_default_provider()
            logger.info(f"🧠 JNANA: LLM provider loaded ({type(self._llm_provider).__name__})")
        except Exception as e:
            logger.warning(f"🧠 JNANA: No LLM provider available ({e}), basic mode")
            self._llm_provider = None

    def _register_veda_handlers(self) -> None:
        """
        Register all KARMA handlers with the VEDA pipeline.

        OPUS-050: Each handler is wrapped to work with VedaContext.
        """

        # Status handler
        async def veda_status(ctx: VedaContext) -> str:
            msg = ctx.original_message
            response = await self._handle_status(msg)
            return response.content

        # Intents handler
        async def veda_intents(ctx: VedaContext) -> str:
            msg = ctx.original_message
            response = await self._handle_intents(msg)
            return response.content

        # Capabilities handler
        async def veda_capabilities(ctx: VedaContext) -> str:
            msg = ctx.original_message
            response = await self._handle_capabilities(msg)
            return response.content

        # Help handler
        async def veda_help(ctx: VedaContext) -> str:
            return (
                "MANAS (Mind/Will) can help you with:\n\n"
                "• 'status' - Check system status\n"
                "• 'intents' - View pending MANAS intents\n"
                "• 'capabilities' - List system capabilities\n"
                "• 'drift' / 'architecture' - Check architectural compliance\n"
                "• 'mandala' - View agent configuration\n"
                "• 'knowledge' / 'akasha' - Query knowledge graph\n"
                "  - 'What depends on X?'\n"
                "  - 'What is X?'\n"
                "• 'silpa' / 'refactor' - Safe code refactoring\n"
                "  - Platinum Protocol (test-guarded)\n"
                "• 'wiki' / 'sutra' - Wiki documentation\n"
                "  - 'preview wiki' - Show wiki page preview\n"
                "  - 'update wiki' - Generate and push to GitHub\n"
                "• 'sankalpa' / 'missions' - Proactive strategy\n"
                "  - 'list missions' - Show active missions\n"
                "  - 'show mission <name>' - Mission details\n"
                "• ACTION requests → Intent generation (with LLM)\n\n"
                "With LLM: Ask 'Why is CI red?' or say 'Analysiere die Tests'"
            )

        # Drift/Architecture/Compliance handler (DHARMA)
        async def veda_drift(ctx: VedaContext) -> str:
            msg = ctx.original_message
            response = await self._handle_drift(msg)
            return response.content

        # MANDALA (Configuration) handler
        async def veda_mandala(ctx: VedaContext) -> str:
            return get_mandala_for_chat(workspace=self._workspace)

        # AKASHA (Knowledge Graph) handler
        async def veda_akasha(ctx: VedaContext) -> str:
            msg = ctx.original_message
            content = msg.content if hasattr(msg, "content") else str(msg)
            return handle_akasha_query(content, workspace=self._workspace)

        # SILPA (Self-Refactoring) handler
        async def veda_silpa(ctx: VedaContext) -> str:
            msg = ctx.original_message
            content = msg.content if hasattr(msg, "content") else str(msg)
            return handle_silpa_query(content, workspace=self._workspace)

        # SUTRA (Wiki Documentation) handler
        async def veda_sutra(ctx: VedaContext) -> str:
            msg = ctx.original_message
            content = msg.content if hasattr(msg, "content") else str(msg)
            return handle_sutra_query(content, workspace=self._workspace)

        # SANKALPA (Proactive Strategy) handler
        async def veda_sankalpa(ctx: VedaContext) -> str:
            msg = ctx.original_message
            content = msg.content if hasattr(msg, "content") else str(msg)
            return handle_sankalpa_query(content, workspace=self._workspace)

        # Action handler
        async def veda_action(ctx: VedaContext) -> str:
            # Actions require LLM for intelligent processing
            msg = ctx.original_message
            if self._llm_provider:
                response = await self._handle_chat_with_llm(msg, is_action=True)
                return response.content
            else:
                return (
                    f'🎯 Aktionsanfrage erkannt: "{msg.content}"\n\n'
                    f"MANAS ist im Basismodus (kein LLM konfiguriert).\n"
                    f"Für intelligente Intent-Generierung bitte LLM-Provider konfigurieren.\n\n"
                    f"Alternativ: Verwende 'steward intents' für manuelle Intent-Verwaltung."
                )

        # Chat/LLM handler
        async def veda_chat(ctx: VedaContext) -> str:
            msg = ctx.original_message
            response = await self._handle_chat_with_llm(msg, is_action=False)
            return response.content

        # Register all handlers
        self._veda.karma.register_handler("_handle_status", veda_status)
        self._veda.karma.register_handler("_handle_intents", veda_intents)
        self._veda.karma.register_handler("_handle_capabilities", veda_capabilities)
        self._veda.karma.register_handler("_handle_help", veda_help)
        self._veda.karma.register_handler("_handle_drift", veda_drift)
        self._veda.karma.register_handler("_handle_mandala", veda_mandala)
        self._veda.karma.register_handler("_handle_akasha", veda_akasha)
        self._veda.karma.register_handler("_handle_silpa", veda_silpa)
        self._veda.karma.register_handler("_handle_sutra", veda_sutra)
        self._veda.karma.register_handler("_handle_sankalpa", veda_sankalpa)
        self._veda.karma.register_handler("_handle_action", veda_action)
        self._veda.karma.register_handler("_handle_chat_llm", veda_chat)

        logger.info("🕉️ VEDA handlers registered")

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

    def _invoke_llm(self, messages: List[Dict[str, str]]) -> str:
        """
        Invoke LLM provider with native messages format.

        Args:
            messages: List of {"role": ..., "content": ...} dicts

        Returns:
            LLM response content string
        """
        if not self._llm_provider:
            raise RuntimeError("No LLM provider configured")

        # Pass messages directly to provider (OpenRouter supports native messages)
        # Fallback: provider wraps as single user message if messages= not supported
        response = self._llm_provider.invoke(messages=messages)
        return response.content

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
        """
        Format memories for prompt.

        OPUS-074 WIRING: Memory Feedback Loop - failures are highlighted
        so MANAS learns from past mistakes and avoids repeating them.
        """
        if not memories:
            return "No recent memories."

        lines = []
        failures = []

        for m in memories[:5]:
            outcome = m.get("outcome", "unknown")
            desc = m.get("description", "")[:50]
            intent_type = m.get("intent_type", "")
            feedback = m.get("feedback", "")

            if outcome == "failed":
                # OPUS-074: Highlight failures with feedback for learning
                failure_info = f"🛑 FAILED: {desc}"
                if feedback:
                    failure_info += f"\n   Error: {feedback[:100]}"
                failures.append(failure_info)
            elif outcome == "rejected":
                failures.append(f"❌ REJECTED: {desc}")
            else:
                lines.append(f"- [{outcome}] {desc}")

        # OPUS-074: Put failures FIRST for prominence (learning from mistakes)
        result_parts = []
        if failures:
            result_parts.append("⚠️ RECENT FAILURES (avoid these patterns):")
            result_parts.extend(failures)
            result_parts.append("")  # blank line

        if lines:
            result_parts.append("Recent successes:")
            result_parts.extend(lines)

        return "\n".join(result_parts) if result_parts else "No recent memories."

    async def handle(self, msg: SamvadaMessage) -> SamvadaResponse:
        """
        Handle an incoming message through the VEDA four-fold pipeline.

        OPUS-050: All messages now flow through:
            Shabda → Artha → Pratyaya → Karma

        Args:
            msg: The incoming message

        Returns:
            SamvadaResponse with intelligent reply
        """
        logger.info(f"JNANA processing via VEDA: {msg.content[:50]}...")

        try:
            # Special case: explicit msg_type routing (legacy support)
            if msg.msg_type == "status":
                return await self._handle_status(msg)
            elif msg.msg_type == "intents":
                return await self._handle_intents(msg)
            elif msg.msg_type == "capabilities":
                return await self._handle_capabilities(msg)

            # OPUS-050: Process through VEDA pipeline
            ctx = await self._veda.process(msg)

            # Convert KarmaResult to SamvadaResponse
            if ctx.karma and ctx.karma.success:
                return SamvadaResponse(
                    success=True,
                    content=ctx.karma.content,
                    msg_id=msg.msg_id,
                )
            elif ctx.karma:
                return SamvadaResponse(
                    success=False,
                    content="",
                    error=ctx.karma.error or "VEDA pipeline failed",
                    msg_id=msg.msg_id,
                )
            else:
                return SamvadaResponse(
                    success=False,
                    content="",
                    error="VEDA pipeline did not produce result",
                    msg_id=msg.msg_id,
                )

        except Exception as e:
            logger.error(f"JNANA handler error: {e}")
            return SamvadaResponse(
                success=False,
                content="",
                error=f"Handler error: {e}",
                msg_id=msg.msg_id,
            )

    async def handle_legacy(self, msg: SamvadaMessage) -> SamvadaResponse:
        """
        Legacy handle method (pre-OPUS-050) - kept for reference.

        DEPRECATED: Use handle() which routes through VEDA pipeline.
        """
        logger.warning("Using legacy handle method - consider upgrading to VEDA pipeline")

        try:
            if msg.msg_type == "status":
                return await self._handle_status(msg)
            elif msg.msg_type == "intents":
                return await self._handle_intents(msg)
            elif msg.msg_type == "capabilities":
                return await self._handle_capabilities(msg)
            else:
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

    async def _handle_drift(self, msg: SamvadaMessage) -> SamvadaResponse:
        """
        Handle drift/architecture queries via DHARMA.

        OPUS-048: The Constitutional Court of Code.
        """
        try:
            result = check_drift_for_chat()
            return SamvadaResponse(
                success=True,
                content=result,
                msg_id=msg.msg_id,
            )
        except Exception as e:
            logger.error(f"DHARMA audit failed: {e}")
            return SamvadaResponse(
                success=False,
                content="",
                error=f"DHARMA audit error: {e}",
                msg_id=msg.msg_id,
            )

    async def _handle_chat_with_llm(self, msg: SamvadaMessage, is_action: bool = False) -> SamvadaResponse:
        """
        Handle chat with LLM integration.

        OPUS-050: Extracted from _handle_chat for use in VEDA pipeline.
        Called by KARMA phase handlers.

        Args:
            msg: The incoming message
            is_action: Whether this is an action request (KRIYA)

        Returns:
            SamvadaResponse with LLM-generated or fallback content
        """
        # Use LLM if available
        if self._llm_provider:
            try:
                prompt = self.build_prompt(msg)

                # OPUS-045: Extend prompt with KRIYA instructions for action requests
                if is_action:
                    prompt = self._kriya.extend_prompt_for_action(prompt, msg.content)
                    logger.debug("KRIYA: Extended prompt for action request")

                response_text = self._invoke_llm(prompt)

                # OPUS-045: Process response through KRIYA to extract intents
                if is_action:
                    response_text, intent = self._kriya.process_response(response_text, msg.content)
                    if intent:
                        logger.info(f"KRIYA: Created intent '{intent.id}' from chat")

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

        content_lower = msg.content.lower()

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

    async def _handle_chat(self, msg: SamvadaMessage) -> SamvadaResponse:
        """
        Handle general chat with LLM integration.

        OPUS-045: Now includes KRIYA for action-to-intent bridging.
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

        # OPUS-048: Check for drift/architecture queries
        if any(kw in content_lower for kw in DRIFT_KEYWORDS):
            return await self._handle_drift(msg)

        # OPUS-045: Check if this is an action request
        is_action = KriyaExtractor.is_action_request(msg.content)

        # Use LLM if available
        if self._llm_provider:
            try:
                prompt = self.build_prompt(msg)

                # OPUS-045: Extend prompt with KRIYA instructions for action requests
                if is_action:
                    prompt = self._kriya.extend_prompt_for_action(prompt, msg.content)
                    logger.debug("KRIYA: Extended prompt for action request")

                response_text = self._invoke_llm(prompt)

                # OPUS-045: Process response through KRIYA to extract intents
                if is_action:
                    response_text, intent = self._kriya.process_response(response_text, msg.content)
                    if intent:
                        logger.info(f"KRIYA: Created intent '{intent.id}' from chat")

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

        # OPUS-045: Fallback for action requests without LLM
        if is_action:
            return SamvadaResponse(
                success=True,
                content=(
                    f'🎯 Aktionsanfrage erkannt: "{msg.content}"\n\n'
                    f"MANAS ist im Basismodus (kein LLM konfiguriert).\n"
                    f"Für intelligente Intent-Generierung bitte LLM-Provider konfigurieren.\n\n"
                    f"Alternativ: Verwende 'steward intents' für manuelle Intent-Verwaltung."
                ),
                msg_id=msg.msg_id,
            )

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
                    "• 'capabilities' - List system capabilities\n"
                    "• 'drift' / 'architecture' - Check architectural compliance\n"
                    "• ACTION requests → Intent generation (with LLM)\n\n"
                    "With LLM: Ask 'Why is CI red?' or say 'Analysiere die Tests'"
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
