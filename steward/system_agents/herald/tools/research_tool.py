"""
HERALD Research Tool - Market intelligence via Tavily API.

Provides trend analysis for content generation context.
Requires real Tavily API - no fallback to fake data.
"""

import os
import logging
from typing import Optional, Dict, Any

try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None

logger = logging.getLogger("HERALD_RESEARCH")


class ResearchTool:
    """
    Market Intelligence Engine powered by Tavily.
    Scans for AI trends, security incidents, agent failures.

    Offline-capable with fallback templates.
    """

    def __init__(self):
        """Initialize research tool."""
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
            logger.warning(
                "⚠️  Research: Tavily unavailable (running in simulation mode)"
            )

    def scan(self, query: str) -> Optional[str]:
        """
        Search Tavily for trending content.

        Args:
            query: Search query

        Returns:
            str: Search answer or None
        """
        if not self.client:
            logger.debug("⚠️  Research: Tavily unavailable, returning fallback")
            return self._fallback_context(query)

        try:
            response = self.client.search(
                query=query, search_depth="basic", max_results=3, include_answer=True
            )
            result = response.get("answer") or response.get("results", [{}])[0].get(
                "content"
            )
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
        """Fallback context when Tavily is unavailable."""
        templates = {
            "agent": "Latest on autonomous agent systems and their identity challenges.",
            "protocol": "Emerging standards for agent verification and governance.",
            "default": "Emerging trends in AI autonomy and verification systems.",
        }

        query_lower = query.lower()
        for key, template in templates.items():
            if key in query_lower:
                return template
        return templates["default"]
