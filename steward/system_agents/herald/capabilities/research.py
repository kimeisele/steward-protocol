"""
HERALD Research Capability
Provides market intelligence via Tavily API.
Kernel-compatible module (configured via system.yaml).
"""

import logging
import os
from typing import Any, Dict, Optional

from tavily import TavilyClient

logger = logging.getLogger("HERALD_RESEARCH")


class ResearchCapability:
    """
    Market Intelligence Engine powered by Tavily.
    Scans for AI trends, security incidents, agent failures.

    Configuration via kernel.get_config("capabilities.research")
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize research capability.

        Args:
            config: Research capability config from system.yaml
        """
        self.config = config
        self.api_key = os.getenv("TAVILY_API_KEY")
        self.client = None
        self.enabled = config.get("enabled", True)

        if self.api_key and self.enabled:
            try:
                self.client = TavilyClient(api_key=self.api_key)
                logger.info("✅ RESEARCH CAPABILITY: Tavily initialized")
            except Exception as e:
                logger.warning(f"⚠️  RESEARCH: Tavily init failed: {e}")
        elif not self.api_key:
            logger.warning("⚠️  RESEARCH: No TAVILY_API_KEY found. Running in degraded mode.")

    def scan(self, query: str) -> Optional[str]:
        """
        Search Tavily for trending content.

        Args:
            query: Search query (e.g., "AI agents autonomous")

        Returns:
            str: Search answer or None if unavailable
        """
        if not self.client:
            logger.debug("⚠️  RESEARCH: Tavily unavailable")
            return None

        try:
            response = self.client.search(
                query=query,
                search_depth=self.config.get("depth", "basic"),
                max_results=self.config.get("max_results", 5),
                include_answer=True,
            )

            result = response.get("answer") or response.get("results", [{}])[0].get("content")
            if result:
                logger.info("📡 MARKET SIGNAL DETECTED")
            return result

        except Exception as e:
            logger.error(f"❌ RESEARCH FAILED: {e}")
            return None

    def find_trending_topic(self, min_relevance: float = 0.5) -> Optional[Dict]:
        """
        Find trending topic matching keywords from config.

        Args:
            min_relevance: Minimum relevance score (0.0-1.0)

        Returns:
            dict: Best matching article with metadata or None
        """
        keywords = self.config.get("keywords", [])
        best_article = None
        best_score = 0.0
        search_query_used = None

        for keyword in keywords:
            logger.info(f"🔍 Searching: {keyword}...")
            result = self.scan(keyword)

            if result:
                # Simple scoring: just use it if found
                score = min_relevance
                best_article = {
                    "content": result,
                    "query": keyword,
                }
                best_score = score
                search_query_used = keyword
                break

        if best_article:
            return {
                "article": best_article,
                "score": best_score,
                "search_query": search_query_used,
            }

        return None
