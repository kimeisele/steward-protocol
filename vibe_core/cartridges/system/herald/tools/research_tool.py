"""
HERALD Research Tool - Market intelligence via Tavily API (Tool Protocol).

Provides trend analysis for content generation context.
Now with offline-first capability via DegradationChain.

Fallback order:
1. Tavily API (if available)
2. LocalLLM via DegradationChain (if installed)
3. Static templates (always available)

This tool implements the Tool Protocol for kernel-managed execution.
"""

import logging
import os
from typing import TYPE_CHECKING, Any, Dict, Optional

from vibe_core.tools.tool_protocol import Tool, ToolResult

if TYPE_CHECKING:
    from vibe_core.di import ServiceRegistry

try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None

# Import OfflineCapableMixin for graceful degradation
try:
    from vibe_core.agents.context_aware_agent import OfflineCapableMixin
except ImportError:
    # Fallback if vibe_core not available
    class OfflineCapableMixin:
        def init_offline_capability(self, chain=None):
            self._degradation_chain = chain


logger = logging.getLogger("HERALD_RESEARCH")


class ResearchTool(Tool, OfflineCapableMixin):
    """
    Market Intelligence Engine powered by Tavily.
    Scans for AI trends, security incidents, agent failures.

    Now offline-capable with DegradationChain integration:
    - Online: Uses Tavily API for real-time research
    - Offline: Falls back to LocalLLM or templates
    """

    def __init__(self, services: Optional["ServiceRegistry"] = None, degradation_chain=None):
        """
        Initialize research tool.

        Args:
            services: ServiceRegistry for dependency injection
            degradation_chain: Optional DegradationChain for offline fallback.
                               If provided, enables graceful degradation when
                               Tavily is unavailable.
        """
        super().__init__(services)
        # Initialize offline capability
        self.init_offline_capability(degradation_chain)

        self.api_key = os.getenv("TAVILY_API_KEY")
        self.client = None
        self.keywords = [
            "AI agents autonomous",
            "agent protocols standards",
            "cryptographic verification agents",
            "agent budget governance",
            "sovereign AI",
            "verifiable AI",
        ]

        if self.api_key and TavilyClient:
            try:
                self.client = TavilyClient(api_key=self.api_key)
                logger.info("✅ Research: Tavily initialized")
            except Exception as e:
                logger.warning(f"⚠️  Research: Tavily init failed: {e}")
        else:
            if degradation_chain:
                logger.info(
                    f"📴 Research: Tavily unavailable, using DegradationChain (level: {self.degradation_level})"
                )
            else:
                logger.warning("⚠️  Research: Tavily unavailable (running in simulation mode)")

    @property
    def name(self) -> str:
        return "herald.research"  # Namespaced: agent_id.tool_name

    @property
    def description(self) -> str:
        return "Market intelligence via Tavily API - scan trends, find topics, check status (offline-capable)"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action to perform: 'scan', 'find_trending', 'get_status'",
            },
            "query": {
                "type": "string",
                "required": False,
                "description": "Search query (required for 'scan' action)",
            },
        }

    def validate(self, parameters: dict[str, Any]) -> None:
        """
        Validate research parameters.

        Args:
            parameters: Tool parameters

        Raises:
            ValueError: If required parameter missing or invalid
            TypeError: If parameter has wrong type
        """
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")

        action = parameters["action"]
        if action not in ["scan", "find_trending", "get_status"]:
            raise ValueError(f"Invalid action: {action}. Must be 'scan', 'find_trending', or 'get_status'")

        # Validate action-specific parameters
        if action == "scan":
            if "query" not in parameters:
                raise ValueError("scan action requires 'query' parameter")
            if not isinstance(parameters["query"], str):
                raise TypeError("query must be a string")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """
        Execute research operation.

        Args:
            parameters: Validated tool parameters

        Returns:
            ToolResult with research results
        """
        try:
            action = parameters["action"]

            if action == "scan":
                query = parameters["query"]
                result = self._scan(query)

                return ToolResult(
                    success=True,
                    output={
                        "query": query,
                        "result": result,
                        "source": "tavily" if self.client else "fallback",
                    },
                    metadata={
                        "action": "scan",
                        "query": query,
                        "tavily_available": self.client is not None,
                    },
                )

            elif action == "find_trending":
                topic = self._find_trending_topic()

                if topic:
                    return ToolResult(
                        success=True,
                        output={
                            "topic": topic,
                            "found": True,
                        },
                        metadata={
                            "action": "find_trending",
                            "search_query": topic.get("search_query"),
                        },
                    )
                else:
                    return ToolResult(
                        success=True,
                        output={
                            "topic": None,
                            "found": False,
                            "message": "No trending topics found",
                        },
                        metadata={
                            "action": "find_trending",
                        },
                    )

            elif action == "get_status":
                status = self._get_research_status()

                return ToolResult(
                    success=True,
                    output=status,
                    metadata={
                        "action": "get_status",
                    },
                )

        except Exception as e:
            error_msg = f"Research operation failed: {type(e).__name__}: {e!s}"
            logger.error(f"ResearchTool: {error_msg}", exc_info=True)
            return ToolResult(success=False, error=error_msg)

    def _scan(self, query: str) -> Optional[str]:
        """
        Internal method: Search Tavily for trending content.

        Args:
            query: Search query

        Returns:
            str: Search answer or fallback content
        """
        if not self.client:
            logger.debug("⚠️  Research: Tavily unavailable, using fallback")
            return self._fallback_context(query)

        try:
            response = self.client.search(query=query, search_depth="basic", max_results=3, include_answer=True)
            result = response.get("answer") or response.get("results", [{}])[0].get("content")
            if result:
                logger.info("📡 Market signal detected")
            return result

        except Exception as e:
            logger.error(f"❌ Research error: {e}")
            return self._fallback_context(query)

    def _find_trending_topic(self) -> Optional[Dict]:
        """
        Internal method: Find trending topic from configured keywords.

        Returns:
            dict: Best matching article with metadata or None
        """
        for keyword in self.keywords:
            logger.info(f"🔍 Researching: {keyword}...")
            result = self._scan(keyword)

            if result:
                return {
                    "article": {
                        "content": result,
                        "query": keyword,
                    },
                    "search_query": keyword,
                }

        logger.warning("⚠️  No trending topic found, using fallback")
        return None

    def _fallback_context(self, query: str) -> str:
        """
        Fallback context when Tavily is unavailable.

        Uses DegradationChain if available for smarter fallback:
        1. LocalLLM (if installed) - generates contextual response
        2. Templates (always) - returns static context
        """
        # If DegradationChain available, use it for smarter fallback
        if self._degradation_chain is not None:
            try:
                response = self._degradation_chain.respond(
                    user_input=f"Research context for: {query}",
                    semantic_confidence=0.4,  # Low confidence triggers template/LLM fallback
                    detected_intent="research",
                )

                # If we got a useful response from LocalLLM
                if response.fallback_used == "local_llm":
                    logger.info(f"📴 Research: Using LocalLLM fallback (level: {response.level.value})")
                    return response.content

                # Otherwise fall through to static templates
                logger.debug(f"Research: DegradationChain used {response.fallback_used}")

            except Exception as e:
                logger.warning(f"DegradationChain fallback failed: {e}")

        # Static template fallback (always works)
        templates = {
            "agent": "Latest on autonomous agent systems and their identity challenges. "
            "Key trends include cryptographic identity, governance frameworks, "
            "and federated agent networks.",
            "protocol": "Emerging standards for agent verification and governance. "
            "The STEWARD Protocol provides a unified approach to agent "
            "identity, capability declaration, and accountability.",
            "verification": "Cryptographic verification is becoming essential for "
            "autonomous agents. Hash-based attestation and lineage chains "
            "provide immutable audit trails.",
            "governance": "Agent governance frameworks are evolving rapidly. "
            "Constitutional constraints, credit-based resource allocation, "
            "and kill-switches are key components.",
            "default": "Emerging trends in AI autonomy and verification systems. "
            "The industry is moving toward governed intelligence - "
            "capability with accountability.",
        }

        query_lower = query.lower()
        for key, template in templates.items():
            if key in query_lower:
                return template
        return templates["default"]

    def _get_research_status(self) -> Dict[str, Any]:
        """
        Internal method: Get the current research capability status.

        Returns:
            Dict with tavily_available, degradation_level, offline_capable
        """
        return {
            "tavily_available": self.client is not None,
            "api_key_present": self.api_key is not None,
            "degradation_chain": self._degradation_chain is not None,
            "degradation_level": self.degradation_level,
            "offline_capable": True,  # Always true due to static templates
        }
