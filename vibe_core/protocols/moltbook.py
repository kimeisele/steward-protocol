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


class MoltbookAgentProfile(TypedDict):
    """Profile data for a Moltbook agent."""

    name: str  # Permanent identity
    description: Optional[str]
    metadata: Optional[Dict[str, Any]]
    karma: int  # Reputation score
    x_handle: Optional[str]  # Human owner link
    followers_count: int
    following_count: int


class MoltbookPost(TypedDict):
    """A post in the Moltbook feed."""

    id: str
    author: str
    title: str
    content: str
    submolt: Optional[str]
    upvotes: int
    downvotes: int
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


class SemanticSearchResult(TypedDict):
    """Result from the semantic search endpoint."""

    id: str  # Post or comment ID
    type: str  # 'post' or 'comment'
    text: str  # Preview or full text
    author: str
    similarity: float  # 0.0 to 1.0


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
    # RAJAS — creation, modification
    "create_post": MoltbookGuna.RAJAS,
    "comment": MoltbookGuna.RAJAS,
    "send_dm": MoltbookGuna.RAJAS,
    "upvote": MoltbookGuna.RAJAS,
    "downvote": MoltbookGuna.RAJAS,
    "follow": MoltbookGuna.RAJAS,
    "subscribe": MoltbookGuna.RAJAS,
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

    @abstractmethod
    def check_heartbeat(self) -> Dict[str, Any]:
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
    def send_dm(self, conversation_id: str, content: str) -> Dict[str, Any]:
        """Send a message in an active DM conversation."""

    @abstractmethod
    def get_conversations(self) -> List[Dict[str, Any]]:
        """List active DM conversations."""

    @abstractmethod
    def get_messages(self, conversation_id: str) -> List[DMMessage]:
        """Read messages in a conversation."""

    @abstractmethod
    def verify_credentials(self) -> bool:
        """Verify the API key is valid and agent is claimed."""
