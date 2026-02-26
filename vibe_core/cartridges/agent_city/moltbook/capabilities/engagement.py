"""
Moltbook Engagement Capability — Social Reciprocity.

Extracted from plugin_main.py:
    - Follow-back logic (_follow_back)
    - Vote strategy (currently upvote-all, will add selectivity)
    - Submolt subscription (_discover_submolts)

Uses existing infrastructure:
    - MoltbookService (ServiceRegistry) for all API calls
    - ContentQueue for enqueuing actions
    - Guna enforcement via MoltbookService._enforce_guna()
"""

import logging
from typing import Optional, Set

logger = logging.getLogger("MOLTBOOK_ENGAGEMENT")


class EngagementCapability:
    """Social reciprocity: follow-back, voting, subscriptions."""

    def __init__(self):
        self._followed: Set[str] = set()
        self._subscribed: Set[str] = set()

    def should_follow_back(self, sender: str) -> bool:
        """Determine if we should follow an agent back."""
        if not sender or sender == "unknown":
            return False
        if sender in self._followed:
            return False
        return True

    def mark_followed(self, agent: str) -> None:
        """Record that we followed an agent."""
        self._followed.add(agent)

    def should_subscribe(self, submolt_name: str) -> bool:
        """Determine if we should subscribe to a submolt."""
        if not submolt_name or submolt_name in self._subscribed:
            return False
        return True

    def mark_subscribed(self, submolt: str) -> None:
        """Record that we subscribed to a submolt."""
        self._subscribed.add(submolt)

    def should_upvote(self, post_content: str, author: str, score: float = 0.0) -> bool:
        """Determine if we should upvote a post.

        Currently simple threshold. Future: use resonance score + author reputation.
        """
        if not post_content:
            return False
        # Don't upvote our own content
        if author and author.lower() in ("steward-protocol", "steward"):
            return False
        return True

    def restore_state(self, followed: Set[str], subscribed: Set[str]) -> None:
        """Restore tracking sets from persisted state."""
        self._followed = set(followed)
        self._subscribed = set(subscribed)

    @property
    def followed_agents(self) -> Set[str]:
        return set(self._followed)

    @property
    def subscribed_submolts(self) -> Set[str]:
        return set(self._subscribed)


_engagement: Optional[EngagementCapability] = None


def get_engagement_capability() -> EngagementCapability:
    """Get EngagementCapability singleton."""
    global _engagement
    if _engagement is None:
        _engagement = EngagementCapability()
    return _engagement
