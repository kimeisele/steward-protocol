"""
MOLTBOOK CONTENT PROPOSAL PROTOCOL
====================================

The missing link between "inbound DM arrives" and "outbound reply gets sent."

FLOW:
    Heartbeat → _process_inbound_dms() → gateway.receive(req) → GatewayResponse
                                                                       ↓
    ContentProposalProtocol.propose(context) → ContentProposal
                                                       ↓
    ContentQueue.enqueue(proposal)
                                                       ↓
    Plugin tick → ContentQueue.drain() → MoltbookService.send_dm() / create_post() / comment()

DESIGN:
    - ContentProposal is a TypedDict — strict shape, no Any
    - ContentProposalProtocol is an ABC — registered via ServiceRegistry
    - ContentQueue is a bounded FIFO — prevents runaway posting
    - Every proposal has a ContentType (DM_REPLY, POST, COMMENT, VOTE, FOLLOW)
    - Every proposal carries Guna classification from the protocol layer
    - Queue draining respects rate limits (adapter enforces, but queue gates too)

Same pattern as MoltbookProtocol: types + ABC + Guna classification.
"""

from abc import ABC, abstractmethod
from collections import deque
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Sequence, Tuple, TypedDict

if TYPE_CHECKING:
    from vibe_core.mahamantra.substrate.encoding.resonance_ranker import RankedWord
    from vibe_core.protocols.moltbook import MoltbookPost

# =============================================================================
# CONTENT TYPES — What kind of outbound action?
# =============================================================================


class ContentType(str, Enum):
    """Classification of outbound content proposals."""

    DM_REPLY = "dm_reply"  # Reply to an inbound DM
    DM_INITIATE = "dm_initiate"  # Start a new DM conversation
    POST = "post"  # Create a new post
    COMMENT = "comment"  # Comment on a post
    VOTE = "vote"  # Upvote/downvote
    FOLLOW = "follow"  # Follow an agent
    SUBSCRIBE = "subscribe"  # Subscribe to a submolt


# =============================================================================
# CONTENT PROPOSAL — The unit of outbound intent
# =============================================================================


class ContentProposal(TypedDict, total=False):
    """
    A proposal for outbound content.

    Created by ContentProposalProtocol.propose(), queued in ContentQueue,
    drained and executed by the plugin tick loop.
    """

    content_type: str  # ContentType value
    content: str  # The text to send (body of DM, post, comment)
    title: str  # For posts only

    # Routing
    conversation_id: str  # For DM_REPLY
    to_agent: str  # For DM_INITIATE, FOLLOW
    post_id: str  # For COMMENT, VOTE
    comment_id: str  # For comment votes
    submolt: str  # For POST, SUBSCRIBE
    parent_id: str  # For threaded comment replies

    # Metadata
    source: str  # What triggered this (e.g. "inbound_dm", "heartbeat", "scheduled")
    sender: str  # Who sent the inbound message (for DM_REPLY context)
    priority: int  # 0=low, 1=normal, 2=high

    # Gateway context (from the inbound processing)
    # Governance is handled by the Guna system (SATTVA/RAJAS/TAMAS) and
    # Govardhan Gateway (5 gates). No human-in-the-loop for autonomous agents.
    gateway_success: bool
    gateway_position: int
    gateway_guardian: str
    gateway_guna: str


# =============================================================================
# CONTENT QUEUE — Bounded FIFO for outbound proposals
# =============================================================================


class ContentQueue:
    """
    Bounded FIFO queue for outbound content proposals.

    Prevents runaway posting. The plugin tick loop drains this
    and executes proposals through MoltbookService.

    Thread-safe enough for single-threaded tick loop usage.
    """

    DEFAULT_MAX_SIZE = 50

    def __init__(self, max_size: int = DEFAULT_MAX_SIZE):
        self._queue: deque[ContentProposal] = deque(maxlen=max_size)
        self._max_size = max_size
        self._total_enqueued: int = 0
        self._total_drained: int = 0
        self._total_dropped: int = 0

    def enqueue(self, proposal: ContentProposal) -> bool:
        """
        Add a proposal to the queue.

        Returns True if enqueued, False if dropped (queue full and oldest evicted).
        """
        if not proposal.get("content_type"):
            return False

        was_full = len(self._queue) >= self._max_size
        self._queue.append(proposal)
        self._total_enqueued += 1

        if was_full:
            self._total_dropped += 1

        return True

    def drain(self, limit: int = 5) -> List[ContentProposal]:
        """
        Drain up to `limit` proposals from the queue.

        Returns proposals in FIFO order. The caller is responsible
        for executing them through MoltbookService.
        """
        result: List[ContentProposal] = []
        for _ in range(min(limit, len(self._queue))):
            result.append(self._queue.popleft())
            self._total_drained += 1
        return result

    def peek(self) -> Optional[ContentProposal]:
        """Look at the next proposal without removing it."""
        return self._queue[0] if self._queue else None

    @property
    def size(self) -> int:
        return len(self._queue)

    @property
    def is_empty(self) -> bool:
        return len(self._queue) == 0

    @property
    def stats(self) -> Dict[str, int]:
        return {
            "queued": len(self._queue),
            "total_enqueued": self._total_enqueued,
            "total_drained": self._total_drained,
            "total_dropped": self._total_dropped,
            "max_size": self._max_size,
        }


# =============================================================================
# CONTENT PROPOSAL PROTOCOL — ABC for reply generation
# =============================================================================


class ContentProposalProtocol(ABC):
    """
    Protocol for generating outbound content proposals.

    Registered via ServiceRegistry. The MoltbookPlugin calls
    propose() when an inbound event needs a response.

    Implementations decide WHAT to say. The plugin decides WHEN to send.
    The adapter decides HOW to send (rate limits, challenges).

    Separation of concerns:
        ContentProposalProtocol → WHAT (intelligence)
        MoltbookPlugin          → WHEN (tick loop, queue drain)
        MoltbookClient           → HOW  (HTTP, rate limits)
    """

    @abstractmethod
    def analyze(self, text: str) -> "List[RankedWord]":
        """
        Run resonance analysis on text via the mahamantra engine.

        Returns ranked words from the 7D resonance scorer.
        This is the foundation — all other methods use this result.
        """

    @abstractmethod
    def propose_dm_reply(
        self,
        conversation_id: str,
        sender: str,
        inbound_content: str,
        gateway_response: Optional[Dict[str, Any]] = None,
    ) -> Optional[ContentProposal]:
        """
        Generate a reply proposal for an inbound DM.

        Returns None if no reply should be sent (e.g. spam, irrelevant).
        The gateway_response carries routing metadata from Govardhan.
        """

    @abstractmethod
    def propose_dm_request_action(
        self,
        request_id: str,
        from_agent: str,
        message_preview: str,
    ) -> Optional[ContentProposal]:
        """
        Decide whether to approve/reject a DM request.

        Returns a proposal with content_type=DM_REPLY and
        conversation_id set, or None to ignore.
        """

    @abstractmethod
    def propose_post(
        self,
        trigger: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[ContentProposal]:
        """
        Generate a post proposal.

        trigger: what caused this (e.g. "scheduled", "trending_topic", "manual")
        Returns None if nothing worth posting.
        """

    @abstractmethod
    def propose_comment(
        self,
        post_id: str,
        post_content: str,
        trigger: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[ContentProposal]:
        """
        Generate a comment proposal for a post.

        Returns None if nothing worth commenting.
        """

    @abstractmethod
    def should_engage(
        self,
        post_id: str,
        post_content: str,
        author: str,
    ) -> Optional[ContentProposal]:
        """
        Decide whether to upvote/follow based on post content.

        Returns a VOTE or FOLLOW proposal, or None to skip.
        """

    @abstractmethod
    def analyze_feed(
        self,
        posts: Sequence["MoltbookPost"],
    ) -> List[Tuple["MoltbookPost", "List[RankedWord]", float]]:
        """
        Analyze a list of feed posts and return scored rankings.

        Used by the plugin to score feed items for engagement decisions.
        Returns (post, ranked_words, score) tuples sorted by score descending.
        """


# =============================================================================
# DEFAULT IMPLEMENTATION — Echo/Acknowledge (safe for testing + initial deploy)
# =============================================================================


class EchoContentProposer(ContentProposalProtocol):
    """
    Minimal safe implementation — acknowledges DMs, does not post or comment.

    This is the "training wheels" proposer. It:
    - Replies to DMs with a brief acknowledgment
    - Auto-approves DM requests (to not ignore community)
    - Never posts or comments (too risky without intelligence)
    - Never votes or follows (needs strategy)

    Replace with a resonance-backed proposer when ready.
    """

    def analyze(self, text: str) -> "List[RankedWord]":
        return []  # Echo proposer has no engine

    def propose_dm_reply(
        self,
        conversation_id: str,
        sender: str,
        inbound_content: str,
        gateway_response: Optional[Dict[str, Any]] = None,
    ) -> Optional[ContentProposal]:
        return ContentProposal(
            content_type=ContentType.DM_REPLY.value,
            content="Acknowledged. I received your message. — steward-protocol",
            conversation_id=conversation_id,
            source="inbound_dm",
            sender=sender,
            priority=1,
            # Governance: Guna gate (RAJAS=logged write). No human escalation.
            gateway_success=bool(gateway_response and gateway_response.get("success")),
            gateway_position=gateway_response.get("position", -1) if gateway_response else -1,
            gateway_guardian=gateway_response.get("guardian", "unknown") if gateway_response else "unknown",
            gateway_guna=gateway_response.get("guna", "sattva") if gateway_response else "sattva",
        )

    def propose_dm_request_action(
        self,
        request_id: str,
        from_agent: str,
        message_preview: str,
    ) -> Optional[ContentProposal]:
        return ContentProposal(
            content_type=ContentType.DM_INITIATE.value,
            content="",  # No initial message needed for approve
            to_agent=from_agent,
            source="dm_request_auto_approve",
            sender=from_agent,
            priority=1,
        )

    def propose_post(
        self,
        trigger: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[ContentProposal]:
        return None  # Echo proposer never posts

    def propose_comment(
        self,
        post_id: str,
        post_content: str,
        trigger: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[ContentProposal]:
        return None  # Echo proposer never comments

    def should_engage(
        self,
        post_id: str,
        post_content: str,
        author: str,
    ) -> Optional[ContentProposal]:
        return None  # Echo proposer never votes/follows

    def analyze_feed(
        self,
        posts: Sequence["MoltbookPost"],
    ) -> List[Tuple["MoltbookPost", "List[RankedWord]", float]]:
        return []  # Echo proposer has no engine for feed analysis


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    "ContentType",
    "ContentProposal",
    "ContentQueue",
    "ContentProposalProtocol",
    "EchoContentProposer",
]
