"""
HERALD Research Tool - Market intelligence via Tavily API.

Provides trend analysis for content generation context.
Now with offline-first capability via DegradationChain.

Fallback order:
1. Tavily API (if available)
2. LocalLLM via DegradationChain (if installed)
3. Static templates (always available)
"""

import logging
import os
from typing import Any, Dict, Optional

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


class ResearchTool(OfflineCapableMixin):
    """
    Market Intelligence Engine powered by Tavily.
    Scans for AI trends, security incidents, agent failures.

    Now offline-capable with DegradationChain integration:
    - Online: Uses Tavily API for real-time research
    - Offline: Falls back to LocalLLM or templates
    """

    def __init__(self, degradation_chain=None):
        """
        Initialize research tool.

        Args:
            degradation_chain: Optional DegradationChain for offline fallback.
                               If provided, enables graceful degradation when
                               Tavily is unavailable.
        """
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

    def scan(self, query: str) -> Optional[str]:
        """
        Search Tavily for trending content.

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

    def find_trending_topic(self) -> Optional[Dict]:
        """
        Find trending topic from configured keywords.

        Returns:
            dict: Best matching article with metadata or None
        """
        for keyword in self.keywords:
            logger.info(f"🔍 Researching: {keyword}...")
            result = self.scan(keyword)

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

    def get_research_status(self) -> Dict[str, Any]:
        """
        Get the current research capability status.

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
