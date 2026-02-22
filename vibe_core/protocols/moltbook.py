"""
MOLTBOOK PROTOCOL TYPES
=======================

"sarva-dharman parityajya mam ekam sharanam vraja"
"Abandon all varieties of religion and just surrender unto Me."

Strict type definitions for the Moltbook API boundary.
Prevents chaotic JSON structures from entering the pristine Govardhan Gateway.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "narada"
__position__ = 3
__genesis__ = "0x51edc2f9"  # GenesisByte: parampara % 37 == 0

from typing import Any, Dict, List, Optional, TypedDict


class MoltbookAgentProfile(TypedDict):
    """Profile data for a Moltbook agent."""
    name: str # Permanent identity
    description: Optional[str]
    metadata: Optional[Dict[str, Any]]
    karma: int # Reputation score
    x_handle: Optional[str] # Human owner link
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
    created_at: str # ISO 8601


class MoltbookComment(TypedDict):
    """A comment on a post."""
    id: str
    post_id: str
    parent_id: Optional[str] # For replies
    author: str
    content: str
    upvotes: int
    downvotes: int
    created_at: str


class SemanticSearchResult(TypedDict):
    """Result from the semantic search endpoint."""
    id: str # Post or comment ID
    type: str # 'post' or 'comment'
    text: str # Preview or full text
    author: str
    similarity: float # 0.0 to 1.0


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
