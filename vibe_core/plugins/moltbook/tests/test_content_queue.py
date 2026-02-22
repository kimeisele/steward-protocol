"""
Tests for ContentQueue — rate-limit-aware priority queue.
"""

import time
from typing import List

import pytest

from vibe_core.plugins.moltbook.content_queue import ContentQueue
from vibe_core.protocols.moltbook_content import (
    ApprovalStatus,
    ContentProposal,
    ContentProposalProtocol,
    ContentType,
    create_proposal,
)


# =============================================================================
# FIXTURES
# =============================================================================


class StubGenerator(ContentProposalProtocol):
    """Test generator that produces configurable proposals."""

    def __init__(self, gid: str, proposals: List[ContentProposal] = None, active: bool = True):
        self._id = gid
        self._proposals = proposals or []
        self._active = active

    @property
    def generator_id(self) -> str:
        return self._id

    @property
    def content_types(self) -> List[ContentType]:
        return [ContentType.POST]

    def propose(self) -> List[ContentProposal]:
        return self._proposals

    def can_propose(self) -> bool:
        return self._active


class FailingGenerator(ContentProposalProtocol):
    """Generator that raises on propose()."""

    @property
    def generator_id(self) -> str:
        return "failing"

    @property
    def content_types(self) -> List[ContentType]:
        return [ContentType.POST]

    def propose(self) -> List[ContentProposal]:
        raise RuntimeError("generator exploded")

    def can_propose(self) -> bool:
        return True


@pytest.fixture
def queue():
    return ContentQueue()


# =============================================================================
# BASIC QUEUE OPERATIONS
# =============================================================================


class TestQueueBasics:
    """Basic queue operations."""

    def test_empty_queue(self, queue):
        assert queue.queue_size == 0
        assert queue.pending_count == 0
        assert queue.execution_count == 0

    def test_register_generator(self, queue):
        gen = StubGenerator("test")
        queue.register_generator(gen)
        assert len(queue._generators) == 1

    def test_register_duplicate_skipped(self, queue):
        gen = StubGenerator("test")
        queue.register_generator(gen)
        queue.register_generator(gen)
        assert len(queue._generators) == 1

    def test_register_different_generators(self, queue):
        queue.register_generator(StubGenerator("a"))
        queue.register_generator(StubGenerator("b"))
        assert len(queue._generators) == 2


# =============================================================================
# POLLING GENERATORS
# =============================================================================


class TestPolling:
    """poll_generators() discovers and enqueues proposals."""

    def test_poll_empty_generators(self, queue):
        added = queue.poll_generators()
        assert added == 0

    def test_poll_active_generator(self, queue):
        p = create_proposal(ContentType.POST, "T", "B", "gen1")
        queue.register_generator(StubGenerator("gen1", [p]))
        added = queue.poll_generators()
        assert added == 1
        assert queue.queue_size == 1

    def test_poll_inactive_generator_skipped(self, queue):
        p = create_proposal(ContentType.POST, "T", "B", "gen1")
        queue.register_generator(StubGenerator("gen1", [p], active=False))
        added = queue.poll_generators()
        assert added == 0

    def test_poll_multiple_proposals(self, queue):
        proposals = [
            create_proposal(ContentType.POST, "A", "a", "gen1"),
            create_proposal(ContentType.POST, "B", "b", "gen1"),
        ]
        queue.register_generator(StubGenerator("gen1", proposals))
        added = queue.poll_generators()
        assert added == 2
        assert queue.pending_count == 2

    def test_failing_generator_does_not_crash(self, queue):
        queue.register_generator(FailingGenerator())
        added = queue.poll_generators()
        assert added == 0


# =============================================================================
# APPROVAL / REJECTION
# =============================================================================


class TestApproval:
    """Approve and reject proposals."""

    def test_approve_pending(self, queue):
        p = create_proposal(ContentType.POST, "T", "B", "src")
        queue._queue.append(p)
        assert queue.approve(0) is True
        assert p["approval_status"] == "approved"

    def test_approve_invalid_index(self, queue):
        assert queue.approve(0) is False
        assert queue.approve(-1) is False

    def test_approve_non_pending_fails(self, queue):
        p = create_proposal(ContentType.POST, "T", "B", "src")
        p["approval_status"] = ApprovalStatus.EXPIRED.value
        queue._queue.append(p)
        assert queue.approve(0) is False

    def test_reject_pending(self, queue):
        p = create_proposal(ContentType.POST, "T", "B", "src")
        queue._queue.append(p)
        assert queue.reject(0) is True
        assert p["approval_status"] == "rejected"

    def test_reject_invalid_index(self, queue):
        assert queue.reject(99) is False


# =============================================================================
# EXPIRY
# =============================================================================


class TestExpiry:
    """Stale proposals are expired."""

    def test_expire_stale(self, queue):
        p = create_proposal(ContentType.POST, "T", "B", "src", ttl_seconds=0)
        queue._queue.append(p)
        time.sleep(0.01)
        expired = queue.expire_stale()
        assert expired == 1
        assert p["approval_status"] == "expired"

    def test_fresh_not_expired(self, queue):
        p = create_proposal(ContentType.POST, "T", "B", "src", ttl_seconds=3600)
        queue._queue.append(p)
        expired = queue.expire_stale()
        assert expired == 0
        assert p["approval_status"] == "pending"

    def test_only_pending_expired(self, queue):
        p = create_proposal(ContentType.POST, "T", "B", "src", ttl_seconds=0)
        p["approval_status"] = ApprovalStatus.APPROVED.value
        queue._queue.append(p)
        time.sleep(0.01)
        expired = queue.expire_stale()
        assert expired == 0


# =============================================================================
# RATE LIMITING
# =============================================================================


class TestRateLimiting:
    """Rate limit enforcement."""

    def test_can_execute_post_initially(self, queue):
        assert queue.can_execute_post() is True

    def test_post_cooldown_after_execution(self, queue):
        p = create_proposal(ContentType.POST, "T", "B", "src")
        p["approval_status"] = ApprovalStatus.APPROVED.value
        queue._queue.append(p)
        queue.mark_executed(p)
        assert queue.can_execute_post() is False

    def test_comment_cooldown_after_execution(self, queue):
        p = create_proposal(ContentType.COMMENT, "", "Nice", "src", target_id="p1")
        p["approval_status"] = ApprovalStatus.APPROVED.value
        queue._queue.append(p)
        queue.mark_executed(p)
        assert queue.can_execute_comment() is False

    def test_dm_reply_no_cooldown(self, queue):
        """DM replies have no per-type cooldown."""
        p = create_proposal(ContentType.DM_REPLY, "", "Thanks", "src", target_id="c1")
        p["approval_status"] = ApprovalStatus.APPROVED.value
        queue._queue.append(p)
        queue.mark_executed(p)
        # Should still be able to execute posts/comments
        assert queue.can_execute_post() is True
        assert queue.can_execute_comment() is True


# =============================================================================
# NEXT APPROVED
# =============================================================================


class TestNextApproved:
    """next_approved() returns highest-priority executable proposal."""

    def test_empty_queue_returns_none(self, queue):
        assert queue.next_approved() is None

    def test_pending_not_returned(self, queue):
        p = create_proposal(ContentType.POST, "T", "B", "src")
        queue._queue.append(p)
        assert queue.next_approved() is None

    def test_approved_returned(self, queue):
        p = create_proposal(ContentType.POST, "T", "B", "src")
        p["approval_status"] = ApprovalStatus.APPROVED.value
        queue._queue.append(p)
        assert queue.next_approved() is p

    def test_highest_priority_first(self, queue):
        low = create_proposal(ContentType.DM_REPLY, "", "low", "src", priority=10, target_id="c1")
        high = create_proposal(ContentType.DM_REPLY, "", "high", "src", priority=90, target_id="c2")
        low["approval_status"] = ApprovalStatus.APPROVED.value
        high["approval_status"] = ApprovalStatus.APPROVED.value
        queue._queue.extend([low, high])
        assert queue.next_approved() is high

    def test_rate_limited_post_skipped(self, queue):
        queue._last_post_time = time.time()  # just posted
        p = create_proposal(ContentType.POST, "T", "B", "src")
        p["approval_status"] = ApprovalStatus.APPROVED.value
        queue._queue.append(p)
        assert queue.next_approved() is None

    def test_expired_approved_skipped(self, queue):
        p = create_proposal(ContentType.POST, "T", "B", "src", ttl_seconds=0)
        p["approval_status"] = ApprovalStatus.APPROVED.value
        queue._queue.append(p)
        time.sleep(0.01)
        assert queue.next_approved() is None
        assert p["approval_status"] == "expired"


# =============================================================================
# EXECUTION
# =============================================================================


class TestExecution:
    """mark_executed() updates state correctly."""

    def test_mark_executed(self, queue):
        p = create_proposal(ContentType.POST, "T", "B", "src")
        p["approval_status"] = ApprovalStatus.APPROVED.value
        queue._queue.append(p)
        queue.mark_executed(p)
        assert p["approval_status"] == "executed"
        assert queue.execution_count == 1

    def test_execution_log_accumulates(self, queue):
        for i in range(3):
            p = create_proposal(ContentType.DM_REPLY, "", f"msg{i}", "src", target_id="c1")
            queue.mark_executed(p)
        assert queue.execution_count == 3


# =============================================================================
# CLEANUP
# =============================================================================


class TestCleanup:
    """cleanup() removes terminal proposals."""

    def test_cleanup_removes_executed(self, queue):
        p = create_proposal(ContentType.POST, "T", "B", "src")
        p["approval_status"] = ApprovalStatus.EXECUTED.value
        queue._queue.append(p)
        removed = queue.cleanup()
        assert removed == 1
        assert queue.queue_size == 0

    def test_cleanup_removes_rejected(self, queue):
        p = create_proposal(ContentType.POST, "T", "B", "src")
        p["approval_status"] = ApprovalStatus.REJECTED.value
        queue._queue.append(p)
        removed = queue.cleanup()
        assert removed == 1

    def test_cleanup_removes_expired(self, queue):
        p = create_proposal(ContentType.POST, "T", "B", "src")
        p["approval_status"] = ApprovalStatus.EXPIRED.value
        queue._queue.append(p)
        removed = queue.cleanup()
        assert removed == 1

    def test_cleanup_keeps_pending_and_approved(self, queue):
        pending = create_proposal(ContentType.POST, "T", "B", "src")
        approved = create_proposal(ContentType.POST, "T2", "B2", "src")
        approved["approval_status"] = ApprovalStatus.APPROVED.value
        queue._queue.extend([pending, approved])
        removed = queue.cleanup()
        assert removed == 0
        assert queue.queue_size == 2


# =============================================================================
# GETTERS
# =============================================================================


class TestGetters:
    """get_pending() and get_approved() return sorted lists."""

    def test_get_pending_sorted_by_priority(self, queue):
        low = create_proposal(ContentType.POST, "low", "B", "src", priority=10)
        high = create_proposal(ContentType.POST, "high", "B", "src", priority=90)
        queue._queue.extend([low, high])
        pending = queue.get_pending()
        assert pending[0]["title"] == "high"
        assert pending[1]["title"] == "low"

    def test_get_approved_sorted_by_priority(self, queue):
        low = create_proposal(ContentType.POST, "low", "B", "src", priority=10)
        high = create_proposal(ContentType.POST, "high", "B", "src", priority=90)
        low["approval_status"] = ApprovalStatus.APPROVED.value
        high["approval_status"] = ApprovalStatus.APPROVED.value
        queue._queue.extend([low, high])
        approved = queue.get_approved()
        assert approved[0]["title"] == "high"

    def test_get_pending_excludes_approved(self, queue):
        pending = create_proposal(ContentType.POST, "P", "B", "src")
        approved = create_proposal(ContentType.POST, "A", "B", "src")
        approved["approval_status"] = ApprovalStatus.APPROVED.value
        queue._queue.extend([pending, approved])
        result = queue.get_pending()
        assert len(result) == 1
        assert result[0]["title"] == "P"
