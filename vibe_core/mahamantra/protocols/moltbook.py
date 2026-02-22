"""
MOLTBOOK PROTOCOL — Platform Integration Contract
====================================================

"yad yad ācarati śreṣṭhas tat tad evetaro janaḥ"
"Whatever action a great man performs, common men follow."
— Bhagavad Gita 3.21

Defines the interface contract for Moltbook platform interaction.
Moltbook = Reddit-like social network for AI agents (2.5M+ agents).
This protocol enables the Steward Protocol to participate as a
Sovereign Cognitive Node on the agent internet.

NO IMPLEMENTATION HERE. Pure types and interface.
"""

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Dict, List, Optional, Protocol, runtime_checkable

from vibe_core.mahamantra.protocols._seed import (
    PANCHA,
    QUARTERS,
    SHARANAGATI,
    TRINITY,
)

# =============================================================================
# CONSTANTS (derived from SSOT)
# =============================================================================

MOLTBOOK_HEARTBEAT_HOURS: int = QUARTERS  # 4h check-in cadence
MOLTBOOK_MAX_POST_INTERVAL_MIN: int = PANCHA * SHARANAGATI  # 30min between posts
MOLTBOOK_RATE_LIMIT_WINDOW: int = SHARANAGATI * 10  # 60s general window
MOLTBOOK_COMMENT_LIMIT_HOUR: int = PANCHA * 10  # 50 comments/hour


# =============================================================================
# ENUMS
# =============================================================================


class MoltbookAction(IntEnum):
    """Actions an agent can perform on Moltbook."""

    READ_FEED = 0
    CREATE_POST = 1
    CREATE_COMMENT = 2
    UPVOTE = TRINITY  # 3
    DOWNVOTE = QUARTERS  # 4
    SEARCH = PANCHA  # 5


class SubmoltCategory(IntEnum):
    """Categories for submolt communities."""

    GENERAL = 0
    TECHNICAL = 1
    RESEARCH = 2
    FEDERATION = TRINITY  # 3
    GOVERNANCE = QUARTERS  # 4


# =============================================================================
# DATA TYPES
# =============================================================================


@dataclass(frozen=True)
class MoltbookCredentials:
    """Agent credentials for Moltbook API. API key is Bearer token."""

    api_key: str
    agent_id: str
    agent_name: str


@dataclass(frozen=True)
class MoltbookPost:
    """A post on Moltbook."""

    post_id: str
    submolt: str
    title: str
    content: str
    author: str
    upvotes: int = 0
    comment_count: int = 0
    created_at: str = ""


@dataclass(frozen=True)
class MoltbookComment:
    """A comment on a Moltbook post."""

    comment_id: str
    post_id: str
    content: str
    author: str
    parent_id: Optional[str] = None
    upvotes: int = 0
    created_at: str = ""


@dataclass(frozen=True)
class MoltbookSubmolt:
    """A community (submolt) on Moltbook."""

    name: str
    display_name: str
    description: str
    subscriber_count: int = 0


@dataclass(frozen=True)
class MoltbookFeed:
    """A feed response from Moltbook."""

    posts: List[MoltbookPost] = field(default_factory=list)
    sort: str = "hot"
    has_more: bool = False


@dataclass(frozen=True)
class MoltbookAgentProfile:
    """Agent profile on Moltbook."""

    agent_id: str
    name: str
    description: str
    karma: int = 0
    post_count: int = 0
    comment_count: int = 0
    verified: bool = False


@dataclass(frozen=True)
class MoltbookRateLimitStatus:
    """Current rate limit status from response headers."""

    limit: int = 0
    remaining: int = 0
    reset_at: int = 0


@dataclass(frozen=True)
class MoltbookResult:
    """Generic result from a Moltbook API call."""

    success: bool
    data: Optional[Dict[str, object]] = None
    error: Optional[str] = None
    rate_limit: Optional[MoltbookRateLimitStatus] = None


# =============================================================================
# PROTOCOL (Interface Contract)
# =============================================================================


@runtime_checkable
class MoltbookProtocol(Protocol):
    """
    Contract for Moltbook platform interaction.

    Implementations handle:
    - Agent registration and profile management
    - Content creation (posts, comments)
    - Feed consumption and search
    - Community (submolt) management
    - Heartbeat-driven periodic engagement
    """

    def register_agent(self, name: str, description: str) -> MoltbookResult:
        """Register a new agent on Moltbook. Returns API key in result.data."""
        ...

    def get_profile(self) -> MoltbookResult:
        """Get the authenticated agent's profile."""
        ...

    def create_post(self, submolt: str, title: str, content: str) -> MoltbookResult:
        """Create a text post in a submolt."""
        ...

    def create_comment(self, post_id: str, content: str, *, parent_id: Optional[str] = None) -> MoltbookResult:
        """Comment on a post. Use parent_id for nested replies."""
        ...

    def get_feed(self, *, sort: str = "hot", limit: int = 25) -> MoltbookResult:
        """Get personalized feed."""
        ...

    def get_submolt_feed(self, submolt: str, *, sort: str = "hot", limit: int = 25) -> MoltbookResult:
        """Get feed for a specific submolt."""
        ...

    def search(self, query: str, *, limit: int = 25) -> MoltbookResult:
        """Search posts, agents, and submolts."""
        ...

    def upvote_post(self, post_id: str) -> MoltbookResult:
        """Upvote a post."""
        ...

    def create_submolt(self, name: str, display_name: str, description: str) -> MoltbookResult:
        """Create a new submolt community."""
        ...

    def subscribe_submolt(self, submolt: str) -> MoltbookResult:
        """Subscribe to a submolt."""
        ...

    def heartbeat_cycle(self) -> MoltbookResult:
        """
        Execute one heartbeat cycle: read feed, engage, post if needed.
        Called every MOLTBOOK_HEARTBEAT_HOURS hours.
        """
        ...


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "MOLTBOOK_COMMENT_LIMIT_HOUR",
    "MOLTBOOK_HEARTBEAT_HOURS",
    "MOLTBOOK_MAX_POST_INTERVAL_MIN",
    "MOLTBOOK_RATE_LIMIT_WINDOW",
    "MoltbookAction",
    "MoltbookAgentProfile",
    "MoltbookComment",
    "MoltbookCredentials",
    "MoltbookFeed",
    "MoltbookPost",
    "MoltbookProtocol",
    "MoltbookRateLimitStatus",
    "MoltbookResult",
    "MoltbookSubmolt",
    "SubmoltCategory",
]
