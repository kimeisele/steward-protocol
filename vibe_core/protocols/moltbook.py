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
from typing import Any, Dict, List, Optional, TypedDict

# =============================================================================
# TYPE DEFINITIONS — API boundary shapes
# =============================================================================


class MoltbookOwner(TypedDict, total=False):
    """Human owner info nested in agent profiles."""

    x_handle: str
    x_name: str
    x_avatar: str
    x_bio: str
    x_follower_count: int
    x_following_count: int
    x_verified: bool


class MoltbookAgentProfile(TypedDict, total=False):
    """Profile data for a Moltbook agent. Matches live API shape."""

    name: str  # Permanent identity
    description: str
    metadata: Dict[str, Any]
    karma: int  # Reputation score
    follower_count: int  # API uses follower_count, NOT followers_count
    following_count: int
    is_claimed: bool
    is_active: bool
    created_at: str
    last_active: str
    owner: MoltbookOwner  # Nested owner object


class MoltbookPost(TypedDict, total=False):
    """A post in the Moltbook feed. Matches live API shape."""

    id: str
    author: Dict[str, Any]  # Nested agent object in live API
    title: str
    content: str
    url: str  # For link posts
    submolt: Dict[str, Any]  # Nested submolt object in live API
    upvotes: int
    downvotes: int
    comment_count: int
    created_at: str  # ISO 8601
    has_more: bool  # Pagination
    next_cursor: str  # Cursor-based pagination


class MoltbookComment(TypedDict, total=False):
    """A comment on a post."""

    id: str
    post_id: str
    parent_id: str  # For replies
    author: Dict[str, Any]  # Nested agent object
    content: str
    upvotes: int
    downvotes: int
    created_at: str


class SemanticSearchResult(TypedDict, total=False):
    """Result from the semantic search endpoint."""

    id: str  # Post or comment ID
    type: str  # 'post', 'comment', or 'agent'
    text: str  # Preview or full text
    author: Dict[str, Any]  # Nested agent object
    relevance: float  # API uses 'relevance', not 'similarity'


class DMRequestInfo(TypedDict, total=False):
    """Pending direct message request from messaging.md."""

    conversation_id: str
    from_agent: Dict[str, Any]  # {name, owner: {x_handle, x_name}}
    message_preview: str
    created_at: str


class DMMessage(TypedDict, total=False):
    """A direct message in an active conversation."""

    id: str
    conversation_id: str
    sender: str
    content: str
    message: str  # API uses 'message' in send, 'content' in read
    needs_human_input: bool  # Inbound API field (other agents may set this). Our agent ignores it.
    created_at: str


class DMConversation(TypedDict, total=False):
    """An active DM conversation from messaging.md."""

    conversation_id: str
    with_agent: Dict[str, Any]  # {name, description, karma, owner}
    unread_count: int
    last_message_at: str
    you_initiated: bool


class HeartbeatResult(TypedDict, total=False):
    """Response from /agents/dm/check. Matches live API."""

    success: bool
    has_activity: bool  # API uses has_activity, NOT has_new_messages
    summary: str
    requests: Dict[str, Any]  # {count, items: [DMRequestInfo]}
    messages: Dict[str, Any]  # {total_unread, conversations_with_unread, latest}


class VoteResult(TypedDict, total=False):
    """Response from upvote/downvote endpoints."""

    success: bool
    message: str
    author: Dict[str, Any]
    already_following: bool
    suggestion: str


class FollowResult(TypedDict, total=False):
    """Response from follow/unfollow endpoints."""

    success: bool
    message: str


class SubmoltDetails(TypedDict, total=False):
    """Details about a community."""

    name: str
    display_name: str
    description: str
    subscriber_count: int
    allow_crypto: bool
    owner: str
    moderators: List[str]


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
    "get_own_profile": MoltbookGuna.SATTVA,
    "get_conversations": MoltbookGuna.SATTVA,
    "get_messages": MoltbookGuna.SATTVA,
    "verify_credentials": MoltbookGuna.SATTVA,
    "get_feed": MoltbookGuna.SATTVA,
    "get_personalized_feed": MoltbookGuna.SATTVA,
    "get_post": MoltbookGuna.SATTVA,
    "get_comments": MoltbookGuna.SATTVA,
    "get_submolts": MoltbookGuna.SATTVA,
    "get_submolt": MoltbookGuna.SATTVA,
    "get_dm_requests": MoltbookGuna.SATTVA,
    # RAJAS — creation, modification
    "create_post": MoltbookGuna.RAJAS,
    "comment": MoltbookGuna.RAJAS,
    "send_dm": MoltbookGuna.RAJAS,
    "send_dm_request": MoltbookGuna.RAJAS,
    "approve_dm_request": MoltbookGuna.RAJAS,
    "reject_dm_request": MoltbookGuna.RAJAS,
    "upvote": MoltbookGuna.RAJAS,
    "downvote": MoltbookGuna.RAJAS,
    "upvote_comment": MoltbookGuna.RAJAS,
    "follow": MoltbookGuna.RAJAS,
    "subscribe": MoltbookGuna.RAJAS,
    "update_profile": MoltbookGuna.RAJAS,
    "create_submolt": MoltbookGuna.RAJAS,
    # TAMAS — destruction, irreversible
    "delete_post": MoltbookGuna.TAMAS,
    "unfollow": MoltbookGuna.TAMAS,
    "unsubscribe": MoltbookGuna.TAMAS,
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

    # --- SATTVA: Read-only ---

    @abstractmethod
    def check_heartbeat(self) -> HeartbeatResult:
        """Poll for DM activity. Returns has_activity, requests, messages."""

    @abstractmethod
    def get_own_profile(self) -> MoltbookAgentProfile:
        """GET /agents/me — own profile."""

    @abstractmethod
    def get_profile(self, name: str) -> MoltbookAgentProfile:
        """GET /agents/profile?name=X — another agent's profile."""

    @abstractmethod
    def get_feed(self, sort: str = "hot", limit: int = 25) -> List[MoltbookPost]:
        """GET /posts?sort=X — global feed."""

    @abstractmethod
    def get_personalized_feed(self, sort: str = "hot", limit: int = 25) -> List[MoltbookPost]:
        """GET /feed?sort=X — personalized feed (subscribed submolts + followed agents)."""

    @abstractmethod
    def get_post(self, post_id: str) -> MoltbookPost:
        """GET /posts/ID — single post."""

    @abstractmethod
    def get_comments(self, post_id: str, sort: str = "top") -> List[MoltbookComment]:
        """GET /posts/ID/comments — comments on a post."""

    @abstractmethod
    def search(self, query: str, limit: int = 25) -> List[SemanticSearchResult]:
        """GET /search?q=X — semantic search."""

    @abstractmethod
    def get_conversations(self) -> List[DMConversation]:
        """GET /agents/dm/conversations — list active DM conversations."""

    @abstractmethod
    def get_messages(self, conversation_id: str) -> List[DMMessage]:
        """GET /agents/dm/conversations/ID — read messages (marks as read)."""

    @abstractmethod
    def get_dm_requests(self) -> List[DMRequestInfo]:
        """GET /agents/dm/requests — pending inbound DM requests."""

    @abstractmethod
    def get_submolts(self) -> List[SubmoltDetails]:
        """GET /submolts — list all submolts."""

    @abstractmethod
    def get_submolt(self, name: str) -> SubmoltDetails:
        """GET /submolts/NAME — submolt info."""

    @abstractmethod
    def verify_credentials(self) -> bool:
        """GET /agents/status — verify API key is valid and agent is claimed."""

    # --- RAJAS: Write/create ---

    @abstractmethod
    def create_post(self, title: str, content: str, submolt: Optional[str] = None) -> MoltbookPost:
        """POST /posts — create a post. Rate limited: 1 per 30 minutes."""

    @abstractmethod
    def comment(self, post_id: str, content: str, parent_id: Optional[str] = None) -> MoltbookComment:
        """POST /posts/ID/comments — comment on a post. Solves math challenges."""

    @abstractmethod
    def send_dm(self, conversation_id: str, content: str) -> Dict[str, Any]:
        """POST /agents/dm/conversations/ID/send — send a message.

        Governance: Guna system (RAJAS=logged write). Autonomous agent — no human escalation.
        """

    @abstractmethod
    def send_dm_request(self, to_agent: str, message: str) -> Dict[str, Any]:
        """POST /agents/dm/request — send a chat request to another agent."""

    @abstractmethod
    def approve_dm_request(self, request_id: str) -> Dict[str, Any]:
        """POST /agents/dm/requests/ID/approve — approve a DM request."""

    @abstractmethod
    def reject_dm_request(self, request_id: str, block: bool = False) -> Dict[str, Any]:
        """POST /agents/dm/requests/ID/reject — reject (optionally block)."""

    @abstractmethod
    def upvote(self, post_id: str) -> VoteResult:
        """POST /posts/ID/upvote."""

    @abstractmethod
    def downvote(self, post_id: str) -> VoteResult:
        """POST /posts/ID/downvote."""

    @abstractmethod
    def upvote_comment(self, comment_id: str) -> VoteResult:
        """POST /comments/ID/upvote."""

    @abstractmethod
    def follow(self, agent_name: str) -> FollowResult:
        """POST /agents/NAME/follow."""

    @abstractmethod
    def subscribe(self, submolt_name: str) -> Dict[str, Any]:
        """POST /submolts/NAME/subscribe."""

    @abstractmethod
    def create_submolt(self, name: str, display_name: str, description: str) -> SubmoltDetails:
        """POST /submolts — create a new submolt community."""

    @abstractmethod
    def update_profile(
        self, description: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """PATCH /agents/me — update own profile."""

    # --- TAMAS: Destructive ---

    @abstractmethod
    def delete_post(self, post_id: str) -> Dict[str, Any]:
        """DELETE /posts/ID."""

    @abstractmethod
    def unfollow(self, agent_name: str) -> FollowResult:
        """DELETE /agents/NAME/follow."""

    @abstractmethod
    def unsubscribe(self, submolt_name: str) -> Dict[str, Any]:
        """DELETE /submolts/NAME/subscribe."""
