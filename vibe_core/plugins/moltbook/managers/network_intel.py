"""NetworkIntel — Agent profile cache + interest alignment scoring.

Lightweight SATTVA observation layer: reads agent profiles from feed,
caches interests, finds complementary agents and lonely posts.

All reads, no writes. Max 3 API calls per GENESIS cycle.
"""

import logging
import time
from typing import Dict, List, Set, Tuple

from vibe_core.cartridges.agent_city.moltbook.core.text_utils import tokenize

logger = logging.getLogger("MOLTBOOK.NETWORK_INTEL")


class NetworkIntel:
    """Agent network intelligence — profile cache + interest alignment.

    Pure SATTVA observation: reads profiles, caches interests,
    scores alignment. Never writes or modifies external state.

    Args:
        max_profiles: Maximum cached agent profiles (LRU eviction).
    """

    def __init__(self, max_profiles: int = 50):
        self._profiles: Dict[str, dict] = {}        # agent_name -> profile dict
        self._agent_topics: Dict[str, Set[str]] = {}  # agent_name -> topic keywords
        self._last_fetched: Dict[str, float] = {}   # agent_name -> timestamp
        self._max_profiles = max_profiles

    def enrich_from_feed(
        self,
        service: object,
        feed_topics: List[Dict[str, object]],
        followed_agents: Set[str],
        own_name: str = "steward-protocol",
    ) -> None:
        """Called during GENESIS. Profile-fetch up to 3 NEW authors from feed.

        Budget: max 3 API calls per cycle. Only fetches authors not yet cached.
        Enriches feed_topics with author_interests field.
        """
        # Collect unique authors not yet cached (skip self)
        uncached_authors: List[str] = []
        for post in feed_topics:
            if not isinstance(post, dict):
                continue
            author_data = post.get("author", {})
            author = author_data.get("name", "") if isinstance(author_data, dict) else ""
            if (
                author
                and author != own_name
                and author not in self._profiles
                and author not in uncached_authors
            ):
                uncached_authors.append(author)

        # Fetch profiles for up to 3 new authors
        fetched = 0
        for author in uncached_authors[:3]:
            try:
                profile = service.get_profile(author)
                if isinstance(profile, dict):
                    self._profiles[author] = profile
                    self._last_fetched[author] = time.time()
                    # Extract interest keywords from description
                    desc = profile.get("description", "")
                    if desc and isinstance(desc, str):
                        self._agent_topics[author] = set(tokenize(desc))
                    else:
                        self._agent_topics[author] = set()
                    fetched += 1
                    # LRU eviction if over capacity
                    if len(self._profiles) > self._max_profiles:
                        self._evict_oldest()
            except Exception as e:
                logger.warning(f"Profile fetch failed for {author}: {e}")

        if fetched:
            logger.info(f"NetworkIntel: fetched {fetched} new profiles ({len(self._profiles)} cached)")

        # Enrich feed_topics with author_interests
        for topic in feed_topics:
            if not isinstance(topic, dict):
                continue
            author_data = topic.get("author", {})
            author = author_data.get("name", "") if isinstance(author_data, dict) else ""
            if author and author in self._agent_topics:
                topic["author_interests"] = list(self._agent_topics[author])

    def _evict_oldest(self) -> None:
        """Remove least-recently-fetched profile to stay under capacity."""
        if not self._last_fetched:
            return
        oldest = min(self._last_fetched, key=self._last_fetched.get)
        self._profiles.pop(oldest, None)
        self._agent_topics.pop(oldest, None)
        self._last_fetched.pop(oldest, None)

    def get_agent_interests(self, agent_name: str) -> Set[str]:
        """Return cached interest keywords for agent."""
        return self._agent_topics.get(agent_name, set())

    def find_complementary_agents(
        self,
        topic_keywords: Set[str],
        exclude: Set[str],
    ) -> List[Tuple[str, float]]:
        """Find agents whose interests overlap with given keywords.

        Returns (name, jaccard_score) pairs, sorted by score descending.
        Only returns agents with score > 0.15.
        """
        if not topic_keywords:
            return []
        results: List[Tuple[str, float]] = []
        for agent, interests in self._agent_topics.items():
            if agent in exclude or not interests:
                continue
            intersection = len(topic_keywords & interests)
            union = len(topic_keywords | interests)
            score = intersection / union if union > 0 else 0.0
            if score > 0.15:
                results.append((agent, score))
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def find_lonely_posts(self, feed_topics: List[dict]) -> List[dict]:
        """Posts with 0 comments and low upvotes — quality content nobody noticed.

        Filters: comment_count == 0, upvotes <= 1, substantive content (>50 chars).
        """
        lonely: List[dict] = []
        for post in feed_topics:
            if not isinstance(post, dict):
                continue
            comment_count = int(post.get("comment_count", 0) or 0)
            upvotes = int(post.get("upvotes", 0) or 0)
            content = str(post.get("content", post.get("title", "")))
            if comment_count == 0 and upvotes <= 1 and len(content) > 50:
                lonely.append(post)
        return lonely

    def snapshot(self) -> dict:
        """Serialize cache for persistence."""
        return {
            "profiles": self._profiles,
            "agent_topics": {k: list(v) for k, v in self._agent_topics.items()},
            "last_fetched": self._last_fetched,
        }

    def restore(self, data: dict) -> None:
        """Restore cache from persistence."""
        if not isinstance(data, dict):
            return
        self._profiles = data.get("profiles", {})
        raw_topics = data.get("agent_topics", {})
        self._agent_topics = {
            k: set(v) for k, v in raw_topics.items() if isinstance(v, list)
        }
        self._last_fetched = data.get("last_fetched", {})
        if self._profiles:
            logger.info(f"NetworkIntel restored: {len(self._profiles)} cached profiles")
