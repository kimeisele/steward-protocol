"""
Moltbook Research Capability — Feed Intelligence.

Pattern: Herald capabilities/research.py

Topic extraction from feed posts, trend detection by semantic clustering.
Uses existing infrastructure:
    - proposer.analyze_feed() — score + rank posts
    - resonance_ranker.resonate() — semantic resonance scoring
    - MahaLLM Kernel.expand() — HKR semantic trees
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("MOLTBOOK_RESEARCH")


class ResearchCapability:
    """Feed intelligence: topic extraction + trend detection."""

    def __init__(self):
        self._proposer = None

    @property
    def proposer(self):
        if self._proposer is None:
            try:
                from vibe_core.di import ServiceRegistry
                from vibe_core.protocols.moltbook_content import ContentProposalProtocol

                self._proposer = ServiceRegistry.get(ContentProposalProtocol)
            except Exception as e:
                logging.getLogger("MOLTBOOK.CAPABILITIES").debug(f"ServiceRegistry unavailable: {e}")
            if self._proposer is None:
                from vibe_core.plugins.moltbook.resonance_proposer import ResonanceProposer

                self._proposer = ResonanceProposer()
        return self._proposer

    def analyze_feed(self, posts: List[Dict[str, Any]]) -> List[Tuple[Dict, Any, float]]:
        """Score and rank feed posts via proposer pipeline.

        Returns: [(post, ranked_words, score), ...] sorted by score desc.
        """
        if not posts:
            return []
        return self.proposer.analyze_feed(posts)

    def extract_topics(self, posts: List[Dict[str, Any]]) -> List[str]:
        """Extract trending topics from feed posts.

        Groups post titles/content by semantic theme using
        the resonance ranker's word scoring.
        """
        topics: List[str] = []
        for post in posts:
            title = post.get("title", "") if isinstance(post, dict) else ""
            if title:
                topics.append(title[:80])
        return topics

    def should_engage(self, post_id: str, post_content: str, author: str) -> Optional[Dict[str, Any]]:
        """Determine if we should engage with a post."""
        return self.proposer.should_engage(post_id, post_content, author)


_research: Optional[ResearchCapability] = None


def get_research_capability() -> ResearchCapability:
    """Get ResearchCapability singleton."""
    global _research
    if _research is None:
        _research = ResearchCapability()
    return _research
