"""
MOLTBOOK CONTENT QUEUE
=======================

Rate-limit-aware priority queue for content proposals.

Sits between ContentProposalProtocol generators and the ApprovalGate.
Discovers generators via ServiceRegistry (FOLDER=EXISTENCE pattern).

Responsibilities:
  1. Poll registered generators for proposals
  2. Enqueue proposals by priority
  3. Expire stale proposals
  4. Enforce rate limits before dequeuing
  5. Track execution history for audit

Does NOT execute proposals — that's the ApprovalGate's job.
"""

import logging
import time
from typing import List, Optional

from vibe_core.protocols.moltbook_content import (
    ApprovalStatus,
    ContentProposal,
    ContentProposalProtocol,
    ContentType,
)

logger = logging.getLogger("MOLTBOOK.QUEUE")

# Moltbook rate limits
_POST_COOLDOWN_SECONDS = 30 * 60  # 1 post per 30 minutes
_COMMENT_COOLDOWN_SECONDS = 72  # 50 per hour ≈ 1 per 72 seconds


class ContentQueue:
    """
    Priority queue for Moltbook content proposals.

    Thread-safe is NOT required — this runs in the Mahamantra tick loop
    which is single-threaded.
    """

    def __init__(self) -> None:
        self._queue: List[ContentProposal] = []
        self._generators: List[ContentProposalProtocol] = []
        self._last_post_time: float = 0.0
        self._last_comment_time: float = 0.0
        self._execution_log: List[ContentProposal] = []

    @property
    def pending_count(self) -> int:
        """Number of proposals waiting for approval/execution."""
        return sum(1 for p in self._queue if p["approval_status"] == ApprovalStatus.PENDING.value)

    @property
    def queue_size(self) -> int:
        """Total proposals in queue (all statuses)."""
        return len(self._queue)

    @property
    def execution_count(self) -> int:
        """Total proposals executed."""
        return len(self._execution_log)

    def register_generator(self, generator: ContentProposalProtocol) -> None:
        """Register a content generator. Idempotent — skips duplicates."""
        for existing in self._generators:
            if existing.generator_id == generator.generator_id:
                return
        self._generators.append(generator)
        logger.info(f"Registered content generator: {generator.generator_id}")

    def poll_generators(self) -> int:
        """
        Poll all registered generators for new proposals.

        Returns the number of new proposals added.
        """
        added = 0
        for gen in self._generators:
            if not gen.can_propose():
                continue
            try:
                proposals = gen.propose()
                for p in proposals:
                    self._queue.append(p)
                    added += 1
            except Exception as e:
                logger.warning(f"Generator {gen.generator_id} failed: {e}")
        return added

    def expire_stale(self) -> int:
        """
        Mark expired proposals. Returns count of newly expired.
        """
        now = time.time()
        expired = 0
        for p in self._queue:
            if p["approval_status"] == ApprovalStatus.PENDING.value and p["expires_at"] < now:
                p["approval_status"] = ApprovalStatus.EXPIRED.value
                expired += 1
        return expired

    def approve(self, index: int) -> bool:
        """
        Approve a proposal by queue index.

        Returns True if approved, False if index invalid or not pending.
        """
        if index < 0 or index >= len(self._queue):
            return False
        p = self._queue[index]
        if p["approval_status"] != ApprovalStatus.PENDING.value:
            return False
        p["approval_status"] = ApprovalStatus.APPROVED.value
        return True

    def reject(self, index: int) -> bool:
        """Reject a proposal by queue index."""
        if index < 0 or index >= len(self._queue):
            return False
        p = self._queue[index]
        if p["approval_status"] != ApprovalStatus.PENDING.value:
            return False
        p["approval_status"] = ApprovalStatus.REJECTED.value
        return True

    def can_execute_post(self) -> bool:
        """Whether rate limits allow a post right now."""
        return (time.time() - self._last_post_time) >= _POST_COOLDOWN_SECONDS

    def can_execute_comment(self) -> bool:
        """Whether rate limits allow a comment right now."""
        return (time.time() - self._last_comment_time) >= _COMMENT_COOLDOWN_SECONDS

    def next_approved(self) -> Optional[ContentProposal]:
        """
        Get the highest-priority approved proposal that can be executed
        within rate limits. Returns None if nothing is ready.

        Does NOT remove from queue — call mark_executed() after success.
        """
        # Sort approved by priority (descending)
        approved = [
            (i, p) for i, p in enumerate(self._queue)
            if p["approval_status"] == ApprovalStatus.APPROVED.value
        ]
        approved.sort(key=lambda x: x[1]["priority"], reverse=True)

        now = time.time()
        for _idx, p in approved:
            # Check expiry
            if p["expires_at"] < now:
                p["approval_status"] = ApprovalStatus.EXPIRED.value
                continue

            # Check rate limits
            ct = p["content_type"]
            if ct == ContentType.POST.value and not self.can_execute_post():
                continue
            if ct == ContentType.COMMENT.value and not self.can_execute_comment():
                continue
            # DM replies have no rate limit beyond the global 100/min

            return p

        return None

    def mark_executed(self, proposal: ContentProposal) -> None:
        """
        Mark a proposal as executed and update rate limit timestamps.
        """
        proposal["approval_status"] = ApprovalStatus.EXECUTED.value
        self._execution_log.append(proposal)

        ct = proposal["content_type"]
        now = time.time()
        if ct == ContentType.POST.value:
            self._last_post_time = now
        elif ct == ContentType.COMMENT.value:
            self._last_comment_time = now

    def cleanup(self) -> int:
        """
        Remove executed, rejected, and expired proposals from queue.
        Returns count removed.
        """
        terminal = {ApprovalStatus.EXECUTED.value, ApprovalStatus.REJECTED.value, ApprovalStatus.EXPIRED.value}
        before = len(self._queue)
        self._queue = [p for p in self._queue if p["approval_status"] not in terminal]
        return before - len(self._queue)

    def get_pending(self) -> List[ContentProposal]:
        """Get all pending proposals, sorted by priority (highest first)."""
        pending = [p for p in self._queue if p["approval_status"] == ApprovalStatus.PENDING.value]
        pending.sort(key=lambda p: p["priority"], reverse=True)
        return pending

    def get_approved(self) -> List[ContentProposal]:
        """Get all approved proposals, sorted by priority (highest first)."""
        approved = [p for p in self._queue if p["approval_status"] == ApprovalStatus.APPROVED.value]
        approved.sort(key=lambda p: p["priority"], reverse=True)
        return approved
