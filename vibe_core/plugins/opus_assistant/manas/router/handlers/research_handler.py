"""
Research Handler - Knowledge and research intent processing.

OPUS-171 Phase 5: Extracted from IntentRouter.

Handles:
- research_topic, web_search
- get_best_practices, find_implementation_guide
- knowledge_query, search_knowledge, get_context
- run_mutation_tests, mutation_protocol
"""

import asyncio
import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional

from .base import AgentType, BaseHandler, register_handler

if TYPE_CHECKING:
    from vibe_core.plugins.opus_assistant.manas.intent_generator import Intent

logger = logging.getLogger("MANAS.Handler.Research")


@register_handler
class ResearchHandler(BaseHandler):
    """
    Handle research and web search intents.

    Routes to VIDYA for external research queries.
    """

    name = "research"
    intent_types = [
        "research_topic",
        "web_search",
        "get_best_practices",
        "find_implementation_guide",
    ]
    agent_type = AgentType.RESEARCH
    priority = 10

    def handle(self, intent: "Intent") -> Dict[str, Any]:
        """Route to VIDYA for research/web search tasks."""
        from vibe_core.plugins.opus_assistant.vidya.research_interface import ResearchInterface

        logger.info(f"🔬 VIDYA handling: {intent.title}")

        try:
            research = ResearchInterface(kernel=self._kernel)

            # Extract query
            query = intent.params.get("query") or intent.params.get("topic") or intent.title

            # Get event loop
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            # Choose method based on intent type
            if intent.intent_type == "get_best_practices":
                topic = intent.params.get("topic", query)
                result = loop.run_until_complete(research.get_best_practices(topic))
            elif intent.intent_type == "find_implementation_guide":
                task = intent.params.get("task", query)
                result = loop.run_until_complete(research.get_implementation_guide(task))
            else:
                max_results = intent.params.get("max_results", 5)
                result = loop.run_until_complete(research.query(query, max_results=max_results))

            return {
                "success": result.success,
                "handler": self.name,
                "mode": result.mode,
                "query": result.query,
                "sources_count": len(result.sources),
                "summary": result.summary[:500] if result.summary else "",
                "key_insights": result.key_insights[:3] if result.key_insights else [],
                "error": result.error,
            }
        except Exception as e:
            return {"success": False, "handler": self.name, "error": str(e)}


@register_handler
class KnowledgeHandler(BaseHandler):
    """
    Handle knowledge graph query intents.

    Routes to UnifiedKnowledgeGraph for local knowledge queries.
    """

    name = "knowledge"
    intent_types = [
        "knowledge_query",
        "search_knowledge",
        "get_context",
    ]
    agent_type = AgentType.RESEARCH
    priority = 8

    def handle(self, intent: "Intent") -> Dict[str, Any]:
        """Route to UnifiedKnowledgeGraph for knowledge queries."""
        from vibe_core.knowledge.graph import get_knowledge_graph

        logger.info(f"📚 KnowledgeGraph handling: {intent.title}")

        try:
            graph = get_knowledge_graph()

            query = intent.params.get("query") or intent.params.get("concept") or intent.title

            if intent.intent_type == "get_context":
                context = graph.compile_prompt_context(query)
                return {
                    "success": True,
                    "handler": self.name,
                    "context": context[:2000] if context else "",
                    "message": f"Context compiled for: {query}",
                }
            else:
                nodes = graph.search_nodes(query)
                return {
                    "success": True,
                    "handler": self.name,
                    "nodes_found": len(nodes),
                    "nodes": [{"id": n.id, "name": n.name, "type": n.type.value} for n in nodes[:10]],
                    "message": f"Found {len(nodes)} nodes for: {query}",
                }
        except Exception as e:
            return {"success": False, "handler": self.name, "error": str(e)}


@register_handler
class MutationHandler(BaseHandler):
    """
    Handle mutation testing intents.

    OPUS-038: Routes to MutationHandlers for mutation testing.
    """

    name = "mutation"
    intent_types = [
        "run_mutation_tests",
        "mutation_protocol",
    ]
    agent_type = AgentType.TESTING
    priority = 5

    def handle(self, intent: "Intent") -> Dict[str, Any]:
        """Route to MutationHandlers for mutation testing."""
        from vibe_core.plugins.opus_assistant.events.mutation_handlers import get_mutation_handlers

        logger.info(f"🧬 MutationHandlers handling: {intent.title}")

        try:
            handlers = get_mutation_handlers(workspace=self._workspace)

            source_code = intent.params.get("source_code", "")
            test_code = intent.params.get("test_code", "")
            module_name = intent.params.get("module_name", "legacy_module")

            if not source_code or not test_code:
                return {
                    "success": False,
                    "handler": self.name,
                    "error": "Missing source_code or test_code parameters",
                }

            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            result = loop.run_until_complete(
                handlers.run_mutation_protocol(
                    {
                        "source_code": source_code,
                        "test_code": test_code,
                        "module_name": module_name,
                    }
                )
            )

            return {
                "success": result.get("success", False),
                "handler": self.name,
                "kill_rate": result.get("kill_rate", 0.0),
                "total_mutants": result.get("total_mutants", 0),
                "killed": result.get("killed", 0),
                "survived": result.get("survived", 0),
                "message": f"Mutation test: {result.get('kill_rate', 0):.1%} kill rate",
            }
        except Exception as e:
            return {"success": False, "handler": self.name, "error": str(e)}
