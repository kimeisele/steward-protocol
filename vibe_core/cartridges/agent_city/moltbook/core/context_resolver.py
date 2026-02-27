"""ContextResolver — INPUT phase context gathering.

Extracted from AgencyDirector._input() and related query methods.

Queries (all graceful degradation — works standalone):
    1. Knowledge Graph → domain context
    2. MahaLLM Kernel → guardian vocabulary + semantic expansion
    3. ServiceRegistry → discover available agents/capabilities
    4. Previous validation feedback (retry loop)
"""

import logging
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger("MOLTBOOK_CONTEXT")


class ContextResolver:
    """Gather context from all available systems for the INPUT phase.

    Constructor takes a callable that returns the event_log (lazy access).
    """

    def __init__(self, event_log_getter: Callable):
        self._get_event_log = event_log_getter

    def gather(self, content_type: str, raw_input: str, **ctx: Any) -> Dict[str, Any]:
        """INPUT phase: gather context from all available systems.

        Queries (all graceful degradation — works standalone):
            1. Knowledge Graph → domain context
            2. MahaLLM Kernel → guardian vocabulary + semantic expansion
            3. ServiceRegistry → discover available agents/capabilities
            4. Previous validation feedback (retry loop)
        """
        input_ctx: Dict[str, Any] = {
            "content_type": content_type,
            "raw_input": raw_input,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        topic = raw_input[:200] if raw_input else content_type

        # Knowledge Graph: domain context
        kg_context = self._query_knowledge(topic)
        if kg_context:
            input_ctx["knowledge_context"] = kg_context

        # MahaLLM Kernel: guardian semantic expansion
        kernel_context = self._query_kernel(topic)
        if kernel_context:
            input_ctx["kernel_context"] = kernel_context

        # ServiceRegistry: discover available agent capabilities
        available = self._discover_capabilities()
        if available:
            input_ctx["available_agents"] = available

        # Previous validation feedback (retry loop)
        event_log = self._get_event_log()
        feedback = event_log.get_last_validation_feedback()
        if feedback:
            input_ctx["previous_violations"] = feedback.get("violations", [])
            input_ctx["previous_draft"] = feedback.get("draft")

        input_ctx.update(ctx)
        return input_ctx

    def _query_knowledge(self, topic: str) -> str:
        """Query Knowledge Graph for domain context."""
        try:
            from vibe_core.knowledge.resolver import get_resolver

            resolver = get_resolver()
            ctx = resolver.compile_context(topic)
            moltbook_ctx = resolver.compile_context("moltbook")
            if moltbook_ctx and moltbook_ctx != ctx:
                ctx = f"{ctx}\n{moltbook_ctx}" if ctx else moltbook_ctx
            return ctx
        except Exception as e:
            logger.warning(f"Knowledge query failed: {e}")
            return ""

    def _query_kernel(self, topic: str) -> Optional[Dict[str, Any]]:
        """Query MahaLLM Kernel for semantic expansion + guardian insight.

        The Kernel IS the Mahajana system. Each guardian has a unique
        4D position → unique vocabulary → unique perspective on any topic.
        """
        try:
            from vibe_core.mahamantra.substrate.encoding.maha_llm_kernel import get_kernel

            kernel = get_kernel()

            result: Dict[str, Any] = {}

            # Which guardian resonates with this topic?
            profile = kernel.guardian_for_text(topic) if hasattr(kernel, "guardian_for_text") else None
            if profile:
                result["resonant_guardian"] = str(profile)

            # Semantic expansion via HKR trees
            if hasattr(kernel, "expand"):
                expansion = kernel.expand(topic)
                if expansion and hasattr(expansion, "words"):
                    result["expanded_vocabulary"] = [getattr(w, "meaning", str(w)) for w in expansion.words[:5]]

            return result if result else None
        except Exception as e:
            logger.warning(f"Kernel query failed: {e}")
            return None

    def _discover_capabilities(self) -> Optional[Dict[str, List[str]]]:
        """Discover available agent capabilities via ServiceRegistry.

        Returns dict of {protocol_name: [available_methods]} for
        registered services. Moltbook can then query these at runtime.
        """
        try:
            from vibe_core.di import ServiceRegistry

            available: Dict[str, List[str]] = {}

            # Check for registered proposer (content intelligence)
            from vibe_core.protocols.moltbook_content import ContentProposalProtocol

            if ServiceRegistry.is_registered(ContentProposalProtocol):
                available["content_proposal"] = ["analyze", "propose_comment", "propose_post", "propose_dm_reply"]

            # Check for event bus (communication)
            from vibe_core.protocols.mahajanas.narada.events import EventBusProtocol

            if ServiceRegistry.is_registered(EventBusProtocol):
                available["event_bus"] = ["emit", "subscribe", "get_history"]

            return available if available else None
        except Exception as e:
            logger.warning(f"Capability discovery failed: {e}")
            return None
