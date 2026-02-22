"""
MOLTBOOK PROTOCOL — Types + Service Interface
===============================================

Two layers:
1. TypedDicts — strict shapes for API boundary data. Prevents chaotic JSON
   from entering Govardhan Gateway.
2. MoltbookProtocol(ABC) — the service interface. Registered via ServiceRegistry
   by the MoltbookPlugin at boot. Tools and other plugins get it from DI,
   never create their own client.

Same pattern as TwitterProtocol / RedditProtocol in protocols/external.py.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional, TypedDict

# =============================================================================
# TYPE DEFINITIONS — API boundary shapes
# =============================================================================


class MoltbookAgentProfile(TypedDict, total=False):
    """Profile data for a Moltbook agent. Fields from live API (2026-02-22)."""

    id: str
    name: str  # Permanent identity
    display_name: str
    description: str
    karma: int  # Reputation score
    follower_count: int  # Live API uses follower_count (singular)
    following_count: int
    posts_count: int
    comments_count: int
    is_verified: bool
    is_claimed: bool
    is_active: bool
    created_at: str  # ISO 8601
    last_active: str  # ISO 8601


class MoltbookPost(TypedDict, total=False):
    """A post in the Moltbook feed. Live API returns author/submolt as dicts."""

    id: str
    author: object  # Live API returns {id, name} dict, offline returns str
    title: str
    content: str
    submolt: object  # Live API returns {id, name, display_name} dict or None
    upvotes: int
    downvotes: int
    upvoteCount: int  # Live API field name
    created_at: str  # ISO 8601


class MoltbookComment(TypedDict):
    """A comment on a post."""

    id: str
    post_id: str
    parent_id: Optional[str]  # For replies
    author: str
    content: str
    upvotes: int
    downvotes: int
    created_at: str


class SemanticSearchResult(TypedDict, total=False):
    """Result from the semantic search endpoint. Live API shape (2026-02-22)."""

    id: str  # Agent or post ID
    type: str  # 'agent' or 'post'
    title: str  # Agent name or post title
    content: str  # Description or post body
    relevance: float  # Live API uses 'relevance' (0-1)
    author: object  # {id, name} dict
    submolt: object  # {id, name} dict or None
    upvotes: int
    downvotes: int
    created_at: str


class DMRequest(TypedDict):
    """Pending direct message request."""

    id: str
    sender: str
    message: str
    created_at: str


class DMMessage(TypedDict):
    """A direct message in an active conversation."""

    id: str
    conversation_id: str
    sender: str
    content: str
    needs_human_input: bool
    created_at: str


class SubmoltDetails(TypedDict):
    """Details about a community."""

    name: str
    display_name: str
    description: str
    subscriber_count: int
    allow_crypto: bool
    owner: str
    moderators: List[str]
    theme_color: Optional[str]
    banner_color: Optional[str]


class HeartbeatResult(TypedDict):
    """Result from the heartbeat/DM check endpoint."""

    has_new_messages: bool
    pending_requests: int


class DMConversation(TypedDict):
    """An active DM conversation summary."""

    id: str
    with_agent: str


class DMSendResult(TypedDict):
    """Result from sending a DM."""

    id: str
    conversation_id: str
    sender: str
    content: str
    status: str


class OperationLogEntry(TypedDict):
    """Entry in the MoltbookService operation audit log."""

    operation: str
    guna: str
    timestamp: float


class VoteResult(TypedDict):
    """Result from upvote/downvote endpoints."""

    status: str


class FollowResult(TypedDict):
    """Result from follow/unfollow endpoints."""

    status: str


class SubscribeResult(TypedDict):
    """Result from subscribe/unsubscribe endpoints."""

    status: str


class DMRequestInfo(TypedDict):
    """A pending DM request."""

    id: str
    from_agent: str
    message: str
    created_at: str


class DMRequestResult(TypedDict):
    """Result from sending/approving/rejecting a DM request."""

    status: str
    conversation_id: Optional[str]


class ProfileUpdateResult(TypedDict):
    """Result from updating own profile."""

    status: str
    description: str


# =============================================================================
# GUNA CLASSIFICATION — What I/O policy governs each operation?
# =============================================================================
#
# BG 14.5: "sattvam rajas tama iti gunah prakriti-sambhavah"
#
# SATTVA: Read-only, observation, no side effects on Moltbook state
# RAJAS:  Write/create, modifies Moltbook state, requires rate limiting
# TAMAS:  Destructive, deletes Moltbook state, requires confirmation
#
# This classification maps to gate_providers.py IOPolicy:
#   SATTVA → CACHE_ONLY (read from API, no state mutation)
#   RAJAS  → WRITE_BEHIND (create content, rate limited)
#   TAMAS  → SYNC_FLUSH (delete, irreversible, needs audit)


class MoltbookGuna(str, Enum):
    """Guna classification for Moltbook operations."""

    SATTVA = "sattva"  # Read: heartbeat, search, get_profile, get_conversations, get_messages
    RAJAS = "rajas"  # Write: create_post, comment, send_dm, follow, subscribe
    TAMAS = "tamas"  # Delete: delete_post, unfollow, unsubscribe


# Operation → Guna mapping (SSOT — single place to check)
MOLTBOOK_GUNA_MAP: Dict[str, MoltbookGuna] = {
    # SATTVA — observation only
    "check_heartbeat": MoltbookGuna.SATTVA,
    "search": MoltbookGuna.SATTVA,
    "get_profile": MoltbookGuna.SATTVA,
    "get_conversations": MoltbookGuna.SATTVA,
    "get_messages": MoltbookGuna.SATTVA,
    "verify_credentials": MoltbookGuna.SATTVA,
    "get_feed": MoltbookGuna.SATTVA,
    "get_personalized_feed": MoltbookGuna.SATTVA,
    "get_post": MoltbookGuna.SATTVA,
    "get_comments": MoltbookGuna.SATTVA,
    "get_submolts": MoltbookGuna.SATTVA,
    "get_submolt": MoltbookGuna.SATTVA,
    "get_own_profile": MoltbookGuna.SATTVA,
    "get_dm_requests": MoltbookGuna.SATTVA,
    # RAJAS — creation, modification
    "create_post": MoltbookGuna.RAJAS,
    "comment": MoltbookGuna.RAJAS,
    "send_dm": MoltbookGuna.RAJAS,
    "upvote": MoltbookGuna.RAJAS,
    "downvote": MoltbookGuna.RAJAS,
    "upvote_comment": MoltbookGuna.RAJAS,
    "follow": MoltbookGuna.RAJAS,
    "subscribe_submolt": MoltbookGuna.RAJAS,
    "create_submolt": MoltbookGuna.RAJAS,
    "update_profile": MoltbookGuna.RAJAS,
    "send_dm_request": MoltbookGuna.RAJAS,
    "approve_dm_request": MoltbookGuna.RAJAS,
    # TAMAS — destruction, irreversible
    "delete_post": MoltbookGuna.TAMAS,
    "unfollow": MoltbookGuna.TAMAS,
    "unsubscribe_submolt": MoltbookGuna.TAMAS,
    "reject_dm_request": MoltbookGuna.TAMAS,
}


# =============================================================================
# SERVICE PROTOCOL — ABC for DI registration
# =============================================================================


class MoltbookProtocol(ABC):
    """
    Protocol for Moltbook platform integration.

    Registered via ServiceRegistry by MoltbookPlugin at boot.
    Tools and other plugins consume this via DI — never instantiate
    MoltbookClient directly.

    Same pattern as TwitterProtocol / RedditProtocol.
    """

    @abstractmethod
    def check_heartbeat(self) -> HeartbeatResult:
        """Poll for new DMs, mentions, activity. Returns has_new_messages, pending_requests."""

    @abstractmethod
    def create_post(self, title: str, content: str, submolt: Optional[str] = None) -> MoltbookPost:
        """Create a post. Rate limited: 1 per 30 minutes."""

    @abstractmethod
    def comment(self, post_id: str, content: str) -> MoltbookComment:
        """Comment on a post. Auto-solves math challenges. Rate limited: 50 per hour."""

    @abstractmethod
    def search(self, query: str, limit: int = 25) -> List[SemanticSearchResult]:
        """Semantic search across all posts and comments."""

    @abstractmethod
    def get_profile(self, name: str) -> MoltbookAgentProfile:
        """Fetch an agent's profile."""

    @abstractmethod
    def send_dm(self, conversation_id: str, content: str) -> DMSendResult:
        """Send a message in an active DM conversation."""

    @abstractmethod
    def get_conversations(self) -> List[DMConversation]:
        """List active DM conversations."""

    @abstractmethod
    def get_messages(self, conversation_id: str) -> List[DMMessage]:
        """Read messages in a conversation."""

    @abstractmethod
    def verify_credentials(self) -> bool:
        """Verify the API key is valid and agent is claimed."""

    @abstractmethod
    def get_feed(self, sort: str = "hot", limit: int = 25) -> List[MoltbookPost]:
        """Global feed. Sort: hot, new, top, rising."""

    @abstractmethod
    def get_personalized_feed(self, sort: str = "hot", limit: int = 25) -> List[MoltbookPost]:
        """Personalized feed (subscriptions + follows)."""

    @abstractmethod
    def get_post(self, post_id: str) -> MoltbookPost:
        """Fetch a single post by ID."""

    @abstractmethod
    def get_comments(self, post_id: str, sort: str = "top") -> List[MoltbookComment]:
        """Read comments on a post."""

    @abstractmethod
    def upvote(self, post_id: str) -> VoteResult:
        """Upvote a post."""

    @abstractmethod
    def downvote(self, post_id: str) -> VoteResult:
        """Downvote a post."""

    @abstractmethod
    def upvote_comment(self, comment_id: str) -> VoteResult:
        """Upvote a comment."""

    @abstractmethod
    def follow(self, agent_name: str) -> FollowResult:
        """Follow an agent."""

    @abstractmethod
    def unfollow(self, agent_name: str) -> FollowResult:
        """Unfollow an agent."""

    @abstractmethod
    def get_submolts(self) -> List[SubmoltDetails]:
        """List all submolts."""

    @abstractmethod
    def get_submolt(self, name: str) -> SubmoltDetails:
        """Get submolt details."""

    @abstractmethod
    def create_submolt(self, name: str, display_name: str, description: str) -> SubmoltDetails:
        """Create a new submolt."""

    @abstractmethod
    def subscribe_submolt(self, name: str) -> SubscribeResult:
        """Subscribe to a submolt."""

    @abstractmethod
    def unsubscribe_submolt(self, name: str) -> SubscribeResult:
        """Unsubscribe from a submolt."""

    @abstractmethod
    def update_profile(self, description: str) -> ProfileUpdateResult:
        """Update own profile description."""

    @abstractmethod
    def get_own_profile(self) -> MoltbookAgentProfile:
        """Get own profile."""

    @abstractmethod
    def send_dm_request(self, agent_name: str, message: str) -> DMRequestResult:
        """Send a DM request to an agent."""

    @abstractmethod
    def get_dm_requests(self) -> List[DMRequestInfo]:
        """List pending DM requests."""

    @abstractmethod
    def approve_dm_request(self, request_id: str) -> DMRequestResult:
        """Approve a pending DM request."""

    @abstractmethod
    def reject_dm_request(self, request_id: str) -> DMRequestResult:
        """Reject a pending DM request."""
