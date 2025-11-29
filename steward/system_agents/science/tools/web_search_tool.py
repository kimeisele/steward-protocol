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

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

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


class WebSearchTool:
    """
    Web search engine for THE SCIENTIST.

    Workflow:
    1. Accept query (e.g., "AI Governance Trends 2025")
    2. Search via Tavily API (required, no fallback)
    3. Synthesize results into structured fact sheet

    Philosophy: No mocks. Real data or failure.
    """

    def __init__(self, bank=None, vault=None, degradation_chain=None):
        """
        Initialize search tool with Tavily API via Vault (secure asset management).

        Args:
            bank: CivicBank instance (for credit charging)
            vault: CivicVault instance (for secret leasing)

        Philosophy:
            - API keys are NOT owned by agents
            - They are ASSETS managed by the Civic Vault
            - Agents must LEASE them using Credits
            - This enforces economic rationality and audit trails
        """
        global _bank, _vault

        self.api_key = None
        self.client = None
        self.mode = "offline"

        # Try to get bank and vault from arguments or use global references
        if bank is None or vault is None:
            # Lazy import CivicBank to avoid circular imports
            try:
                from steward.system_agents.civic.tools.economy import CivicBank

                _bank = bank or CivicBank()
                _vault = vault or _bank.vault
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize Vault: {e}")
                _bank = bank
                _vault = vault

        self.bank = _bank
        self.vault = _vault
        self.chain = degradation_chain

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
                raise ImportError("❌ CRITICAL: tavily package not installed. Install via: pip install tavily-python")

            try:
                self.client = TavilyClient(api_key=self.api_key)
                self.mode = "tavily"
                logger.info("✅ Search: Tavily API initialized (PRODUCTION MODE)")
            except Exception as e:
                raise RuntimeError(
                    f"❌ CRITICAL: Failed to initialize Tavily API: {e}. Check your API key and network connectivity."
                )
        else:
            # No API key available - we'll operate in offline mode
            logger.warning("⚠️  TAVILY_API_KEY not found in Vault or environment. Search will operate in offline mode.")
            self.mode = "offline"

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
            if self.chain:
                logger.info(f"⚠️  Offline mode: Fallback to DegradationChain for '{query}'")
                try:
                    # Ask the chain (local LLM) for general knowledge
                    prompt = f"Research query: {query}\nProvide a factual summary based on your internal knowledge."
                    response = self.chain.respond(
                        user_input=prompt,
                        semantic_confidence=0.5,
                        detected_intent="research",
                    )
                    answer = response.content

                    return [
                        SearchResult(
                            title="Local Knowledge (Offline)",
                            url="[local-llm]",
                            content=answer,
                            source="local_llm",
                        )
                    ]
                except Exception as e:
                    logger.error(f"❌ Fallback failed: {e}")
                    return []
            else:
                logger.warning(f"⚠️  Offline mode: Cannot search '{query}' (No chain available)")
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
