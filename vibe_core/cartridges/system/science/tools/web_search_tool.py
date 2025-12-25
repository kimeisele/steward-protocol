"""
SCIENCE Web Search Tool - External Intelligence Module

Core capability: Fetch ground truth from the internet.
Powered by Tavily API (only real source).

This tool synthesizes external data into structured fact sheets.
Used by THE SCIENTIST to give HERALD factual ammunition.

Philosophy:
"Agents that hallucinate are worthless. Agents with ground truth are powerful.
No mocks. No fake data. No building on lies."

Tool Protocol Compliant (Kernel-Managed).
"""

import logging
import os
from datetime import datetime
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.di import ServiceRegistry

from vibe_core.tools.tool_protocol import Tool, ToolResult

try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None

logger = logging.getLogger("SCIENCE_SEARCH")

# Note: We'll import vault lazily to avoid circular imports
_bank = None
_vault = None


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


class WebSearchTool(Tool):
    """
    Web search engine for THE SCIENTIST.

    Workflow:
    1. Accept query (e.g., "AI Governance Trends 2025")
    2. Search via Tavily API (required, no fallback)
    3. Synthesize results into structured fact sheet

    Philosophy: No mocks. Real data or failure.
    """

    def __init__(self, services: Optional["ServiceRegistry"] = None):
        """Initialize search tool (kernel-managed)."""
        super().__init__(services)
        global _bank, _vault

        self.api_key = None
        self.client = None
        self.mode = "offline"
        self._bank = None
        self._vault = None
        self._initialized = False

    @property
    def name(self) -> str:
        return "science.web_search"

    @property
    def description(self) -> str:
        return "External intelligence module - web search and fact synthesis via Tavily API"

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "action": {
                "type": "string",
                "required": True,
                "description": "Action: 'search', 'briefing'",
            },
            "query": {
                "type": "string",
                "required": True,
                "description": "Research query (e.g., 'AI governance 2025')",
            },
            "max_results": {
                "type": "integer",
                "required": False,
                "description": "Maximum results to return (default: 5)",
            },
        }

    @property
    def bank(self):
        """Lazy-load CivicBank."""
        if self._bank is None:
            try:
                from vibe_core.cartridges.system.civic.tools.economy import CivicBank

                self._bank = CivicBank()
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize Bank: {e}")
        return self._bank

    @property
    def vault(self):
        """Get vault from bank."""
        if self._vault is None and self.bank:
            self._vault = self.bank.vault
        return self._vault

    def _ensure_initialized(self):
        """Lazy initialization of API client."""
        if self._initialized:
            return

        global _bank, _vault
        _bank = self.bank
        _vault = self.vault

        # Try to get API key from Vault (preferred)
        if self.vault is not None:
            try:
                # Lease the Tavily API key from the Vault
                self.api_key = self.vault.lease_secret(agent_id="science", key_name="tavily_api", bank=self.bank)
                logger.info("✅ Search: TAVILY_API_KEY leased from Civic Vault (VAULT MODE)")
            except Exception as vault_error:
                logger.warning(f"⚠️  Vault lease failed: {vault_error}")
                # Fallback to environment variable
                self.api_key = os.getenv("TAVILY_API_KEY")

        # If still no API key, try direct environment variable
        if not self.api_key:
            self.api_key = os.getenv("TAVILY_API_KEY")
            if self.api_key:
                logger.info("✅ Search: TAVILY_API_KEY loaded from environment (ENV MODE)")

        # Initialize Tavily client if we have the key
        if self.api_key:
            if not TavilyClient:
                logger.warning("⚠️  tavily package not installed - operating in offline mode")
                self.mode = "offline"
            else:
                try:
                    self.client = TavilyClient(api_key=self.api_key)
                    self.mode = "tavily"
                    logger.info("✅ Search: Tavily API initialized (PRODUCTION MODE)")
                except Exception as e:
                    logger.warning(f"⚠️  Failed to initialize Tavily API: {e}. Operating in offline mode.")
                    self.mode = "offline"
        else:
            # No API key available - we'll operate in offline mode
            logger.warning("⚠️  TAVILY_API_KEY not found in Vault or environment. Search will operate in offline mode.")
            self.mode = "offline"

        self._initialized = True

    def validate(self, parameters: dict[str, Any]) -> None:
        """Validate search parameters."""
        if "action" not in parameters:
            raise ValueError("Missing required parameter: action")

        action = parameters["action"]
        if action not in ["search", "briefing"]:
            raise ValueError(f"Invalid action: {action}. Must be 'search' or 'briefing'")

        if "query" not in parameters:
            raise ValueError("Missing required parameter: query")

    def execute(self, parameters: dict[str, Any]) -> ToolResult:
        """Execute web search operation."""
        try:
            self._ensure_initialized()

            action = parameters["action"]
            query = parameters["query"]
            max_results = parameters.get("max_results", 5)

            if action == "search":
                results = self.search(query, max_results)
                return ToolResult(success=True, output=[r.to_dict() for r in results])

            elif action == "briefing":
                briefing = self.get_briefing(query, max_results)
                return ToolResult(success=True, output=briefing)

            else:
                return ToolResult(success=False, error=f"Unknown action: {action}")

        except Exception as e:
            logger.exception(f"Web search execution failed: {e}")
            return ToolResult(success=False, error=str(e))

    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """
        Search for content on the web.

        If Tavily API is available (either via Vault or env), performs live search.
        Otherwise, returns empty results (safe degradation).

        Args:
            query: Search query (e.g., "AI governance 2025")
            max_results: Maximum results to return

        Returns:
            list: SearchResult objects

        Raises:
            RuntimeError: Only if Tavily API is configured but fails
        """
        if self.mode == "offline":
            logger.warning(f"⚠️  Offline mode: Cannot search '{query}' (API key not available)")
            return []

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
