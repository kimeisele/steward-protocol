"""
Library - Research and Knowledge Room

OPUS-133: "Die Bibliothek, wo MANAS Wissen sammelt."

The Library is where MANAS can research topics, gather knowledge,
and expand its understanding. It integrates with external search
APIs (like Tavily) for real-time knowledge retrieval.

Capabilities:
    research     - Search for information on a topic
    deep_dive    - Thorough research with multiple queries
    fact_check   - Verify claims against external sources
    synthesize   - Combine multiple sources into understanding

<!-- @HARNESS
files:
  - path: vibe_core/plugins/opus_assistant/manas/dojo/rooms/library.py
    required: true
wiring:
  - pattern: "class Library"
    in: vibe_core/plugins/opus_assistant/manas/dojo/rooms/library.py
  - pattern: "TAVILY_API_KEY"
    in: vibe_core/plugins/opus_assistant/manas/dojo/rooms/library.py
-->
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("DOJO.LIBRARY")


@dataclass
class ResearchResult:
    """Result of a library research query."""

    query: str
    sources: List[Dict[str, Any]]
    summary: str
    confidence: float
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeEntry:
    """A piece of knowledge stored in the library."""

    topic: str
    content: str
    source: str
    verified: bool
    added_at: str
    tags: List[str] = field(default_factory=list)


class Library:
    """
    The Library - Research and knowledge room for MANAS.

    Usage:
        library = Library(workspace)

        # Research a topic
        result = library.research("Python async patterns")

        # Deep dive with multiple queries
        knowledge = library.deep_dive("VivekaAction dharmic scoring")

        # Store knowledge for later
        library.store("dharmic_score", "Score between 0-1 indicating...", "research")
    """

    def __init__(self, workspace: Path):
        self._workspace = workspace
        self._knowledge_path = workspace / ".opus_state" / "library" / "knowledge.json"
        self._research_cache_path = workspace / ".opus_state" / "library" / "cache"
        self._tavily_api_key = os.environ.get("TAVILY_API_KEY")

        # Initialize storage
        self._knowledge_path.parent.mkdir(parents=True, exist_ok=True)
        self._research_cache_path.mkdir(parents=True, exist_ok=True)

    @property
    def is_connected(self) -> bool:
        """Check if external research API is available."""
        return self._tavily_api_key is not None

    def research(self, query: str, max_results: int = 5) -> ResearchResult:
        """
        Research a topic using external knowledge sources.

        Args:
            query: The research query
            max_results: Maximum number of sources to return

        Returns:
            ResearchResult with sources and summary
        """
        logger.info(f"📚 LIBRARY: Researching '{query}'")

        if not self.is_connected:
            return self._offline_research(query)

        try:
            return self._tavily_research(query, max_results)
        except Exception as e:
            logger.warning(f"📚 LIBRARY: External research failed: {e}")
            return self._offline_research(query)

    def _tavily_research(self, query: str, max_results: int) -> ResearchResult:
        """Perform research using Tavily API."""
        try:
            from tavily import TavilyClient

            client = TavilyClient(api_key=self._tavily_api_key)
            response = client.search(query, max_results=max_results)

            sources = []
            for result in response.get("results", []):
                sources.append(
                    {
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "content": result.get("content", ""),
                        "score": result.get("score", 0.0),
                    }
                )

            # Generate summary from results
            summary = self._synthesize_results(query, sources)

            result = ResearchResult(
                query=query,
                sources=sources,
                summary=summary,
                confidence=min(1.0, len(sources) * 0.2),  # More sources = more confident
                timestamp=datetime.now().isoformat(),
                metadata={"source": "tavily", "results_count": len(sources)},
            )

            # Cache the result
            self._cache_research(result)

            logger.info(f"📚 LIBRARY: Found {len(sources)} sources")
            return result

        except ImportError:
            logger.warning("📚 LIBRARY: tavily package not installed")
            return self._offline_research(query)

    def _offline_research(self, query: str) -> ResearchResult:
        """Fallback research using local knowledge only."""
        logger.info("📚 LIBRARY: Using offline mode (no API key or package)")

        # Check local knowledge base
        local_results = self._search_local_knowledge(query)

        return ResearchResult(
            query=query,
            sources=local_results,
            summary=f"Offline research for '{query}'. {len(local_results)} local entries found.",
            confidence=0.3 if local_results else 0.1,
            timestamp=datetime.now().isoformat(),
            metadata={"source": "local", "offline": True},
        )

    def _synthesize_results(self, query: str, sources: List[Dict[str, Any]]) -> str:
        """Synthesize a summary from research sources."""
        if not sources:
            return f"No results found for '{query}'"

        # Simple synthesis - combine top content
        contents = [s.get("content", "")[:200] for s in sources[:3]]
        return f"Research on '{query}': " + " ... ".join(contents)

    def deep_dive(self, topic: str, aspects: Optional[List[str]] = None) -> Dict[str, ResearchResult]:
        """
        Perform deep research on a topic from multiple angles.

        Args:
            topic: The main topic to research
            aspects: Optional list of specific aspects to explore

        Returns:
            Dict mapping aspect names to ResearchResults
        """
        if aspects is None:
            aspects = [
                f"{topic} definition",
                f"{topic} examples",
                f"{topic} best practices",
                f"{topic} common issues",
            ]

        results = {}
        for aspect in aspects:
            results[aspect] = self.research(aspect)

        logger.info(f"📚 LIBRARY: Deep dive complete - {len(results)} aspects researched")
        return results

    def store(self, topic: str, content: str, source: str, tags: Optional[List[str]] = None) -> None:
        """
        Store knowledge in the library for later retrieval.

        Args:
            topic: Knowledge topic/key
            content: The knowledge content
            source: Where this knowledge came from
            tags: Optional categorization tags
        """
        entry = KnowledgeEntry(
            topic=topic,
            content=content,
            source=source,
            verified=False,
            added_at=datetime.now().isoformat(),
            tags=tags or [],
        )

        # Load existing knowledge
        knowledge = self._load_knowledge()
        knowledge[topic] = {
            "content": entry.content,
            "source": entry.source,
            "verified": entry.verified,
            "added_at": entry.added_at,
            "tags": entry.tags,
        }

        # Save
        self._save_knowledge(knowledge)
        logger.info(f"📚 LIBRARY: Stored knowledge '{topic}'")

    def retrieve(self, topic: str) -> Optional[Dict[str, Any]]:
        """Retrieve stored knowledge by topic."""
        knowledge = self._load_knowledge()
        return knowledge.get(topic)

    def _search_local_knowledge(self, query: str) -> List[Dict[str, Any]]:
        """Search local knowledge base for relevant entries."""
        knowledge = self._load_knowledge()
        results = []

        query_lower = query.lower()
        for topic, data in knowledge.items():
            if query_lower in topic.lower() or query_lower in data.get("content", "").lower():
                results.append(
                    {
                        "title": topic,
                        "content": data.get("content", ""),
                        "source": "local:" + data.get("source", "unknown"),
                    }
                )

        return results

    def _load_knowledge(self) -> Dict[str, Any]:
        """Load knowledge from disk."""
        if self._knowledge_path.exists():
            try:
                return json.loads(self._knowledge_path.read_text())
            except (json.JSONDecodeError, IOError):
                pass
        return {}

    def _save_knowledge(self, knowledge: Dict[str, Any]) -> None:
        """Save knowledge to disk."""
        self._knowledge_path.write_text(json.dumps(knowledge, indent=2))

    def _cache_research(self, result: ResearchResult) -> None:
        """Cache research result for future reference."""
        cache_file = self._research_cache_path / f"{hash(result.query)}.json"
        cache_file.write_text(
            json.dumps(
                {
                    "query": result.query,
                    "summary": result.summary,
                    "sources_count": len(result.sources),
                    "timestamp": result.timestamp,
                },
                indent=2,
            )
        )
