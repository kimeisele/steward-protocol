"""
SCIENCE Web Search Tool - External Intelligence Module

Core capability: Fetch ground truth from the internet.
Powered by Tavily API (only real source).

This tool synthesizes external data into structured fact sheets.
Used by THE SCIENTIST to give HERALD factual ammunition.

Philosophy:
"Agents that hallucinate are worthless. Agents with ground truth are powerful.
No mocks. No fake data. No building on lies."
"""

import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None

logger = logging.getLogger("SCIENCE_SEARCH")


class SearchResult:
    """Structured search result from external source."""

    def __init__(self, title: str, url: str, content: str, source: str = "unknown"):
        """
        Args:
            title: Article/page title
            url: Source URL
            content: Text content
            source: "tavily" or "mock"
        """
        self.title = title
        self.url = url
        self.content = content
        self.source = source
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "url": self.url,
            "content": self.content,
            "source": self.source,
            "timestamp": self.timestamp,
        }


class WebSearchTool:
    """
    Web search engine for THE SCIENTIST.

    Workflow:
    1. Accept query (e.g., "AI Governance Trends 2025")
    2. Search via Tavily API (required, no fallback)
    3. Synthesize results into structured fact sheet

    Philosophy: No mocks. Real data or failure.
    """

    def __init__(self):
        """Initialize search tool with Tavily API (required, no fallback)."""
        self.api_key = os.getenv("TAVILY_API_KEY")

        if not self.api_key:
            raise ValueError(
                "❌ CRITICAL: TAVILY_API_KEY environment variable not set. "
                "SCIENCE agent requires real search capability. "
                "No mocks. No fallbacks. Provide a real API key or the system fails."
            )

        if not TavilyClient:
            raise ImportError(
                "❌ CRITICAL: tavily package not installed. "
                "Install via: pip install tavily-python"
            )

        try:
            self.client = TavilyClient(api_key=self.api_key)
            self.mode = "tavily"  # FIX: Initialize the mode attribute
            logger.info("✅ Search: Tavily API initialized (PRODUCTION MODE)")
        except Exception as e:
            raise RuntimeError(
                f"❌ CRITICAL: Failed to initialize Tavily API: {e}. "
                f"Check your API key and network connectivity."
            )

    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """
        Search for content on the web via Tavily (only real source).

        Args:
            query: Search query (e.g., "AI governance 2025")
            max_results: Maximum results to return

        Returns:
            list: SearchResult objects

        Raises:
            RuntimeError: If Tavily search fails (no fallback to mocks)
        """
        return self._search_tavily(query, max_results)

    def _search_tavily(self, query: str, max_results: int) -> List[SearchResult]:
        """Search via Tavily API (no fallback - fail loudly if it fails)."""
        try:
            logger.info(f"🌐 Searching Tavily: {query}")
            response = self.client.search(
                query=query,
                search_depth="basic",
                max_results=max_results,
                include_answer=True,
            )

            results = []

            # Add synthesized answer as first result
            if response.get("answer"):
                results.append(
                    SearchResult(
                        title="Synthesized Answer",
                        url="[synthesized]",
                        content=response["answer"],
                        source="tavily",
                    )
                )

            # Add individual results
            for item in response.get("results", []):
                results.append(
                    SearchResult(
                        title=item.get("title", "Untitled"),
                        url=item.get("url", ""),
                        content=item.get("content", ""),
                        source="tavily",
                    )
                )

            logger.info(f"✅ Found {len(results)} results via Tavily")
            return results

        except Exception as e:
            raise RuntimeError(
                f"❌ CRITICAL: Tavily search failed for query '{query}': {e}. "
                f"System requires real search results. No mocks. No fallbacks."
            )

    def synthesize_fact_sheet(self, query: str, results: List[SearchResult]) -> Dict[str, Any]:
        """
        Synthesize search results into a structured fact sheet.

        This is what HERALD will use for content generation.

        Args:
            query: Original search query
            results: List of SearchResult objects

        Returns:
            dict: Structured fact sheet with key insights
        """
        fact_sheet = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "mode": self.mode,  # initialized in __init__ - safe access
            "source_count": len(results),
            "sources": [r.to_dict() for r in results],
            "key_insights": self._extract_key_insights(results),
            "summary": self._generate_summary(results),
        }

        return fact_sheet

    def _extract_key_insights(self, results: List[SearchResult]) -> List[str]:
        """Extract key insights from results by identifying first sentences."""
        insights = []
        for result in results:
            # Extract first sentences from content
            sentences = result.content.split(".")
            for sentence in sentences[:2]:
                if sentence.strip() and len(sentence.strip()) > 10:
                    insights.append(sentence.strip())
        return insights[:5]  # Top 5 insights

    def _generate_summary(self, results: List[SearchResult]) -> str:
        """Generate summary from results by combining leading content."""
        if not results:
            return "No results found."

        # Combine first sentences from top results
        summary_parts = []
        for result in results[:3]:
            first_sentence = result.content.split(".")[0].strip()
            if first_sentence and len(first_sentence) > 10:
                summary_parts.append(first_sentence)

        return " ".join(summary_parts)

    def get_briefing(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Full pipeline: Search -> Synthesize -> Return structured briefing.

        This is the main interface used by HERALD.

        Args:
            query: Research query
            max_results: Number of results

        Returns:
            dict: Complete fact sheet ready for HERALD
        """
        results = self.search(query, max_results)
        fact_sheet = self.synthesize_fact_sheet(query, results)
        return fact_sheet
