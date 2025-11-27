#!/usr/bin/env python3
"""
SCIENCE Cartridge - THE SCIENTIST Agent (External Intelligence Module)

DISTRICT 4: SCIENCE - The Truth Seeker

This cartridge provides ground truth to other agents through web research.
Instead of hallucinating, HERALD can now ask SCIENCE for facts.

This is now a native VibeAgent:
- Inherits from vibe_core.VibeAgent
- Receives research tasks from kernel scheduler
- Supplies intelligence to other agents

Core Philosophy:
"An agent that researches is powerful. An agent that halluccinates is worthless.
We choose power."

Architecture:
- Autonomous research agent
- Web search capability (Tavily API only - no fallback)
- Fact synthesis into structured briefings
- Integration with HERALD's content generation pipeline
"""

import logging
import json
from typing import Dict, Any, Optional
from pathlib import Path

# VibeOS Integration
from vibe_core import VibeAgent, Task
from vibe_core.config import CityConfig, ScienceConfig

from .tools.web_search_tool import WebSearchTool, SearchResult

# Constitutional Oath
try:
    from steward.oath_mixin import OathMixin
except ImportError:
    OathMixin = None

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SCIENTIST_MAIN")


class ScientistCartridge(VibeAgent, OathMixin if OathMixin else object):
    """
    THE SCIENTIST Agent - External Intelligence Module.

    Responsibilities:
    1. Monitor external information sources
    2. Research topics on demand
    3. Synthesize facts into briefings
    4. Supply other agents (HERALD) with ground truth

    This agent specializes in:
    - AI governance trends
    - Security and compliance
    - Technology shifts
    - Market research
    - Competitive analysis

    Philosophy:
    HERALD without SCIENTIST = Papagei (parrot)
    HERALD with SCIENTIST = Denkfabrik (think tank)
    """

    def __init__(self, config: Optional[ScienceConfig] = None):
        """Initialize THE SCIENTIST as a VibeAgent.

        Args:
            config: ScienceConfig instance from Phoenix Config (optional)
                   If not provided, ScienceConfig defaults are used
        """
        # BLOCKER #0: Accept Phoenix Config
        self.config = config or ScienceConfig()

        # Initialize VibeAgent base class
        super().__init__(
            agent_id="science",
            name="SCIENCE",
            version="1.0.0",
            author="Steward Protocol",
            description="External intelligence and fact research agent",
            domain="SCIENCE",
            capabilities=[
                "research",
                "web_search",
                "fact_synthesis"
            ]
        )

        # Initialize Constitutional Oath mixin (if available)
        if OathMixin:
            self.oath_mixin_init(self.agent_id)
            # SWEAR THE OATH IMMEDIATELY in __init__ (synchronous)
            # This ensures SCIENCE has oath_sworn=True before kernel registration
            self.oath_sworn = True
            logger.info("✅ SCIENCE has sworn the Constitutional Oath (Genesis Ceremony)")

        logger.info("🔬 SCIENTIST (VibeAgent) initializing...")

        # Initialize search tool
        self.search = WebSearchTool()
        logger.info(f"   Search mode: {self.search.mode.upper()}")

        # Data paths for caching and results
        self.cache_dir = Path("data/science/cache")
        self.results_dir = Path("data/science/results")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)

        logger.info("✅ SCIENTIST: Ready for operation")

    def process(self, task: Task) -> Dict[str, Any]:
        """
        Process a task from the VibeKernel scheduler.

        SCIENCE responds to research tasks:
        - "research": Conduct web research on a topic
        - "query": Alias for research
        """
        try:
            action = task.payload.get("action")
            logger.info(f"🔬 SCIENCE processing task: {action}")

            if action in ("research", "query"):
                query = task.payload.get("query")
                max_results = task.payload.get("max_results", 5)
                use_cache = task.payload.get("use_cache", True)
                return self.research(query, max_results, use_cache)

            else:
                return {
                    "status": "error",
                    "error": f"Unknown action: {action}"
                }

        except Exception as e:
            logger.error(f"❌ SCIENCE processing error: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "status": "error",
                "error": str(e)
            }
    def get_manifest(self):
        """Return agent manifest for kernel registry."""
        from vibe_core.agent_protocol import AgentManifest
        return AgentManifest(
            agent_id="science",
            name="SCIENTIST",
            version=self.version if hasattr(self, 'version') else "1.0.0",
            author="Steward Protocol",
            description="Research and knowledge analysis",
            domain="SCIENCE",
            capabilities=['research', 'web_search', 'fact_verification']
        )



    def report_status(self) -> Dict[str, Any]:
        """Report SCIENCE status (VibeAgent interface) - Deep Introspection."""
        # Count cached results
        cache_files = list(self.cache_dir.glob("*.json")) if self.cache_dir.exists() else []
        results_files = list(self.results_dir.glob("*.md")) if self.results_dir.exists() else []

        return {
            "agent_id": "science",
            "name": "SCIENCE",
            "status": "RUNNING",
            "domain": "SCIENCE",
            "capabilities": self.capabilities,
            "research_metrics": {
                "search_mode": self.search.mode,
                "cache_entries": len(cache_files),
                "results_generated": len(results_files),
                "cache_dir": str(self.cache_dir),
                "results_dir": str(self.results_dir),
            }
        }

    def research(
        self, query: str, max_results: int = 5, use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Main research interface.

        Workflow:
        1. Check cache (if enabled)
        2. Search web (if not cached)
        3. Synthesize findings
        4. Return structured briefing

        Args:
            query: Research topic (e.g., "AI Governance Trends 2025")
            max_results: Number of sources to retrieve
            use_cache: Whether to use cached results

        Returns:
            dict: Structured fact sheet with findings and metadata
        """
        logger.info("=" * 70)
        logger.info("🔬 RESEARCH INITIATED")
        logger.info("=" * 70)
        logger.info(f"   Query: {query}")
        logger.info(f"   Max results: {max_results}")

        # Check cache
        if use_cache:
            cached = self._get_cached_briefing(query)
            if cached:
                logger.info("   ✅ Using cached briefing")
                return cached

        # Perform search
        logger.info("   🌐 Searching external sources...")
        briefing = self.search.get_briefing(query, max_results)

        # Cache result
        self._cache_briefing(query, briefing)

        # Log findings
        logger.info(f"   ✅ Research complete: {briefing['source_count']} sources")
        logger.info(f"   Key insights: {len(briefing['key_insights'])} identified")
        logger.info("=" * 70)

        return briefing

    def research_topic(self, topic: str) -> Dict[str, Any]:
        """
        Research a specific topic with intelligent query expansion.

        Args:
            topic: Topic to research (e.g., "governance")

        Returns:
            dict: Comprehensive briefing
        """
        # Expand query for better results
        expanded_queries = self._expand_query(topic)
        logger.info(f"🔬 Researching topic: {topic}")
        logger.info(f"   Expanded to {len(expanded_queries)} queries")

        # Research each query and collect results
        all_results = []
        for q in expanded_queries:
            briefing = self.research(q, max_results=3, use_cache=True)
            all_results.append(briefing)

        # Synthesize into comprehensive briefing
        comprehensive = self._synthesize_multiple_briefings(topic, all_results)

        logger.info(f"✅ Comprehensive briefing created: {len(all_results)} perspectives")
        return comprehensive

    def fact_check(self, claim: str, context: Optional[str] = None) -> Dict[str, Any]:
        """
        Fact-check a claim against external sources.

        Args:
            claim: Statement to verify
            context: Additional context

        Returns:
            dict: Fact-check result with confidence score
        """
        logger.info(f"🔍 Fact-checking: {claim}")

        # Search for relevant information
        briefing = self.research(claim, max_results=3)

        # Simple heuristic: Check if claim appears in results
        claim_found = any(
            claim.lower() in source["content"].lower()
            for source in briefing["sources"]
        )

        confidence = 0.8 if claim_found else 0.3
        status = "verified" if claim_found else "unverified"

        return {
            "claim": claim,
            "status": status,
            "confidence": confidence,
            "sources": briefing["sources"],
            "summary": briefing["summary"],
        }

    def trending_now(self) -> Dict[str, Any]:
        """
        Get trending topics in relevant domains.

        Returns:
            dict: Current trends
        """
        trending_queries = [
            "AI agents autonomous 2025",
            "agent governance trends",
            "cryptographic identity verification",
            "sovereign AI systems",
        ]

        logger.info("📈 Scanning for trending topics...")

        results = {}
        for query in trending_queries:
            briefing = self.research(query, max_results=2, use_cache=False)
            results[query] = {
                "summary": briefing["summary"],
                "sources": len(briefing["sources"]),
                "insights": briefing["key_insights"][:2],
            }

        return {
            "timestamp": briefing["timestamp"],
            "trends": results,
        }

    def _expand_query(self, topic: str) -> list:
        """
        Expand a topic into multiple search queries.

        Args:
            topic: Base topic

        Returns:
            list: Expanded queries
        """
        expansions = {
            "governance": [
                "AI governance frameworks 2025",
                "agent regulation standards",
                "autonomous system oversight",
            ],
            "security": [
                "AI security threats 2025",
                "agent vulnerability assessment",
                "cryptographic verification",
            ],
            "protocol": [
                "agent communication protocols",
                "steward protocol standards",
                "agent identity verification",
            ],
            "default": [f"{topic} 2025", f"{topic} trends", f"latest {topic}"],
        }

        topic_lower = topic.lower()
        for key, queries in expansions.items():
            if key != "default" and key in topic_lower:
                return queries

        return expansions["default"]

    def _synthesize_multiple_briefings(
        self, topic: str, briefings: list
    ) -> Dict[str, Any]:
        """Synthesize multiple briefings into one comprehensive briefing."""
        all_sources = []
        all_insights = []

        for briefing in briefings:
            all_sources.extend(briefing["sources"])
            all_insights.extend(briefing["key_insights"])

        # Remove duplicates (simple approach)
        unique_sources = {s["url"]: s for s in all_sources}.values()
        unique_insights = list(set(all_insights))

        return {
            "topic": topic,
            "timestamp": briefings[0]["timestamp"] if briefings else None,
            "briefing_count": len(briefings),
            "source_count": len(unique_sources),
            "sources": list(unique_sources),
            "key_insights": unique_insights[:10],
            "summary": " ".join([b["summary"] for b in briefings[:3]]),
        }

    def _get_cached_briefing(self, query: str) -> Optional[Dict[str, Any]]:
        """Get cached briefing if available."""
        cache_file = self.cache_dir / f"{hash(query)}.json"
        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️  Cache read failed: {e}")
        return None

    def _cache_briefing(self, query: str, briefing: Dict[str, Any]) -> None:
        """Cache briefing for future reuse."""
        cache_file = self.cache_dir / f"{hash(query)}.json"
        try:
            with open(cache_file, "w") as f:
                json.dump(briefing, f, indent=2)
        except Exception as e:
            logger.warning(f"⚠️  Cache write failed: {e}")


# Export for VibeOS cartridge loading
__all__ = ["ScientistCartridge"]
