"""
MOLTBOOK CONTENT PROPOSAL PROTOCOL
====================================

Registry-driven content generation. NO hardcoded prompts.

Content generators implement ContentProposalProtocol and register via
ServiceRegistry. The ContentQueue discovers them automatically —
same pattern as VenuService discovering DIW subscribers.

Flow:
  ContentProposalProtocol.propose() → ContentProposal
  → ContentQueue (priority, rate-limit aware)
  → ApprovalGate (human or Cortex)
  → MoltbookService.create_post() / .comment() / .send_dm()

Rules:
  1. NO string-literal prompts in generators — all content is computed
  2. NO direct MoltbookService calls — only through the queue
  3. Every proposal carries its source, priority, and content type
  4. Proposals expire — stale content is worse than no content
"""

import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional, TypedDict


class ContentType(str, Enum):
    """What kind of Moltbook action this proposal produces."""

    POST = "post"
    COMMENT = "comment"
    DM_REPLY = "dm_reply"


class ApprovalStatus(str, Enum):
    """Lifecycle state of a content proposal."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    EXECUTED = "executed"


class ContentProposal(TypedDict):
    """A proposed piece of content for Moltbook."""

    content_type: str
    title: str
    body: str
    submolt: Optional[str]
    target_id: Optional[str]
    priority: int
    source: str
    created_at: float
    expires_at: float
    approval_status: str
    metadata: Optional[dict]


class ContentProposalProtocol(ABC):
    """
    ABC for content generators.

    Implementations register via ServiceRegistry. The ContentQueue
    discovers all registered generators and polls them for proposals.

    Each generator is responsible for ONE type of content. It decides
    WHETHER to propose (return empty list if nothing worth saying)
    and WHAT to propose (computed content, not hardcoded).
    """

    @property
    @abstractmethod
    def generator_id(self) -> str:
        """Unique identifier for this generator."""

    @property
    @abstractmethod
    def content_types(self) -> List[ContentType]:
        """Which content types this generator can produce."""

    @abstractmethod
    def propose(self) -> List[ContentProposal]:
        """
        Generate zero or more content proposals.

        Called by ContentQueue on each heartbeat cycle. Return empty
        list if there's nothing worth saying — silence is better
        than noise.

        Proposals are NOT executed immediately. They enter the queue
        and must pass through ApprovalGate before execution.
        """

    @abstractmethod
    def can_propose(self) -> bool:
        """
        Whether this generator has enough context to propose.

        Return False if dependencies are missing, data is stale,
        or the generator is in cooldown. The queue skips generators
        that return False.
        """


def create_proposal(
    content_type: ContentType,
    title: str,
    body: str,
    source: str,
    priority: int = 50,
    submolt: Optional[str] = None,
    target_id: Optional[str] = None,
    ttl_seconds: int = 3600,
    metadata: Optional[dict] = None,
) -> ContentProposal:
    """
    Factory for creating properly shaped proposals.

    Args:
        content_type: POST, COMMENT, or DM_REPLY
        title: Post title (ignored for comments/DMs)
        body: The actual content
        source: Generator ID that produced this
        priority: 0-100, higher = more important
        submolt: Target submolt for posts
        target_id: Post ID (for comments) or conversation ID (for DMs)
        ttl_seconds: How long before this proposal expires
        metadata: Optional extra context (e.g. which search query triggered this)
    """
    now = time.time()
    return ContentProposal(
        content_type=content_type.value,
        title=title,
        body=body,
        submolt=submolt,
        target_id=target_id,
        priority=priority,
        source=source,
        created_at=now,
        expires_at=now + ttl_seconds,
        approval_status=ApprovalStatus.PENDING.value,
        metadata=metadata,
    )
