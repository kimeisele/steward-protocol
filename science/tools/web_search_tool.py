"""
SCIENCE Web Search Tool - External Intelligence Module

Core capability: Fetch ground truth from the internet.
Powered by Tavily API (best search agent standard), with robust mock fallback.

This tool synthesizes external data into structured fact sheets.
Used by THE SCIENTIST to give HERALD factual ammunition.

Philosophy:
"Agents that hallucinate are worthless. Agents with ground truth are powerful."
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
    2. Search via Tavily API (if available)
    3. Fallback to mock data (if offline)
    4. Synthesize results into structured fact sheet
    """

    def __init__(self):
        """Initialize search tool with Tavily API or mock mode."""
        self.api_key = os.getenv("TAVILY_API_KEY")
        self.client = None
        self.mode = "offline"  # Default to offline

        if self.api_key and TavilyClient:
            try:
                self.client = TavilyClient(api_key=self.api_key)
                self.mode = "online"
                logger.info("✅ Search: Tavily API initialized (ONLINE MODE)")
            except Exception as e:
                logger.warning(f"⚠️  Search: Tavily init failed: {e} (MOCK MODE)")
                self.mode = "offline"
        else:
            logger.warning(
                "⚠️  Search: Tavily API key not found (MOCK MODE - for development)"
            )
            self.mode = "offline"

    def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """
        Search for content on the web.

        Args:
            query: Search query (e.g., "AI governance 2025")
            max_results: Maximum results to return

        Returns:
            list: SearchResult objects
        """
        if self.mode == "online":
            return self._search_tavily(query, max_results)
        else:
            logger.info(f"🔍 Search (MOCK): {query}")
            return self._search_mock(query, max_results)

    def _search_tavily(self, query: str, max_results: int) -> List[SearchResult]:
        """Search via Tavily API."""
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
            logger.error(f"❌ Tavily search error: {e}")
            logger.warning("Falling back to mock data...")
            return self._search_mock(query, max_results)

    def _search_mock(self, query: str, max_results: int) -> List[SearchResult]:
        """
        Mock search data for development/offline mode.

        Provides plausible data for common topics to enable testing
        without requiring API keys.
        """
        query_lower = query.lower()

        # Knowledge base: topic -> list of mock results
        knowledge_base = {
            "ai governance": [
                SearchResult(
                    title="AI Governance Frameworks 2025: Standards and Best Practices",
                    url="https://example.com/ai-governance-2025",
                    content="""
Recent developments in AI governance show a shift towards:
1. Decentralized governance models (vs centralized regulation)
2. Verifiable computation and cryptographic proofs
3. Agent autonomy with measurable constraints
4. Real-time compliance monitoring
5. Multi-stakeholder oversight structures

Key trends: EU AI Act implementation, US executive orders,
autonomous agent registration requirements, cryptographic identity verification.
""",
                    source="mock",
                ),
                SearchResult(
                    title="Building Trust in Autonomous Agents",
                    url="https://example.com/agent-trust-2025",
                    content="""
Organizations deploying autonomous agents face governance challenges:
- Identity and accountability mechanisms
- Credit/budget constraints on autonomous action
- Cryptographic signing and verification
- Event-sourced audit trails
- Democratic oversight of agent behavior

Solution: Implementation of standardized agent protocols with
immutable governance rules coded into the agent itself.
""",
                    source="mock",
                ),
            ],
            "agent protocol": [
                SearchResult(
                    title="Steward Protocol: A New Standard for Autonomous Agents",
                    url="https://example.com/steward-protocol",
                    content="""
The Steward Protocol introduces a framework for agent governance:
1. Immutable identity (Steward Key)
2. Event sourcing (full audit trail)
3. Cryptographic signing of artifacts
4. Budget constraints and credit systems
5. Governance-first architecture

This enables autonomous agents to operate with full transparency
and democratic oversight.
""",
                    source="mock",
                ),
            ],
            "cryptographic verification": [
                SearchResult(
                    title="Cryptographic Verification for Autonomous Systems",
                    url="https://example.com/crypto-verification",
                    content="""
Latest cryptographic techniques for agent verification:
- Ed25519 signatures for artifact authentication
- Merkle trees for immutable audit logs
- Zero-knowledge proofs for privacy-preserving verification
- Threshold signatures for distributed governance

Real-world deployments show 99.9% verification success rates
with minimal performance overhead.
""",
                    source="mock",
                ),
            ],
            "agent budget": [
                SearchResult(
                    title="Credit Systems for Autonomous Agents",
                    url="https://example.com/agent-credits",
                    content="""
Economic constraints on autonomous action:
- Per-action credit costs
- Dynamic pricing based on impact
- Credit auctions for high-value actions
- Governance-approved budget allocations

Benefits: Prevents spam, aligns incentives, enables democratic control.
""",
                    source="mock",
                ),
            ],
            "sovereign ai": [
                SearchResult(
                    title="Sovereign AI: Building Independent Intelligent Systems",
                    url="https://example.com/sovereign-ai",
                    content="""
Defining sovereign AI:
- Self-governing autonomous agents
- Independent decision-making capability
- Cryptographic identity and accountability
- Democratic governance mechanisms
- Immutable audit trails

2025 outlook: Expect rapid adoption in enterprise and research contexts.
""",
                    source="mock",
                ),
            ],
            "default": [
                SearchResult(
                    title="Latest Trends in Artificial Intelligence",
                    url="https://example.com/ai-trends-2025",
                    content="""
Major AI trends in 2025:
1. Autonomous agent proliferation
2. Governance and regulatory frameworks
3. Verification and cryptographic identity
4. Multi-agent systems and coordination
5. Transparency and auditability

The convergence of AI capability and governance is reshaping
how we think about autonomous systems.
""",
                    source="mock",
                ),
            ],
        }

        # Find best matching topic
        for topic, results in knowledge_base.items():
            if topic != "default" and topic in query_lower:
                logger.info(f"📚 Mock data found for topic: {topic}")
                return results[:max_results]

        # Default fallback
        logger.info("📚 Using default mock data")
        return knowledge_base["default"][:max_results]

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
            "mode": self.mode,
            "source_count": len(results),
            "sources": [r.to_dict() for r in results],
            "key_insights": self._extract_key_insights(results),
            "summary": self._generate_summary(results),
        }

        return fact_sheet

    def _extract_key_insights(self, results: List[SearchResult]) -> List[str]:
        """Extract key insights from results (placeholder for NLP)."""
        insights = []
        for result in results:
            # Simple heuristic: split by sentences and take first few
            sentences = result.content.split(".")
            for sentence in sentences[:2]:
                if sentence.strip():
                    insights.append(sentence.strip())
        return insights[:5]  # Top 5 insights

    def _generate_summary(self, results: List[SearchResult]) -> str:
        """Generate summary from results (placeholder for NLP)."""
        if not results:
            return "No results found."

        # Simple approach: concatenate first sentences
        summary_parts = []
        for result in results[:3]:
            first_sentence = result.content.split(".")[0].strip()
            if first_sentence:
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
