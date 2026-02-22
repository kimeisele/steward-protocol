"""
Tests for ContentProposalProtocol and ContentQueue.
"""

import time

import pytest

from vibe_core.protocols.moltbook_content import (
    ApprovalStatus,
    ContentProposal,
    ContentProposalProtocol,
    ContentType,
    create_proposal,
)


# =============================================================================
# PROPOSAL FACTORY
# =============================================================================


class TestCreateProposal:
    """create_proposal() factory produces correctly shaped proposals."""

    def test_basic_post_proposal(self):
        p = create_proposal(ContentType.POST, "Title", "Body", "test_gen")
        assert p["content_type"] == "post"
        assert p["title"] == "Title"
        assert p["body"] == "Body"
        assert p["source"] == "test_gen"
        assert p["approval_status"] == "pending"

    def test_default_priority(self):
        p = create_proposal(ContentType.POST, "T", "B", "src")
        assert p["priority"] == 50

    def test_custom_priority(self):
        p = create_proposal(ContentType.POST, "T", "B", "src", priority=90)
        assert p["priority"] == 90

    def test_expiry_default_1h(self):
        before = time.time()
        p = create_proposal(ContentType.POST, "T", "B", "src")
        assert p["expires_at"] >= before + 3600
        assert p["expires_at"] <= time.time() + 3601

    def test_custom_ttl(self):
        before = time.time()
        p = create_proposal(ContentType.POST, "T", "B", "src", ttl_seconds=60)
        assert p["expires_at"] >= before + 60
        assert p["expires_at"] <= before + 62

    def test_comment_proposal_with_target(self):
        p = create_proposal(ContentType.COMMENT, "", "Nice post!", "src", target_id="p123")
        assert p["content_type"] == "comment"
        assert p["target_id"] == "p123"

    def test_dm_reply_proposal(self):
        p = create_proposal(ContentType.DM_REPLY, "", "Thanks!", "src", target_id="conv1")
        assert p["content_type"] == "dm_reply"
        assert p["target_id"] == "conv1"

    def test_submolt_field(self):
        p = create_proposal(ContentType.POST, "T", "B", "src", submolt="agentic-os")
        assert p["submolt"] == "agentic-os"

    def test_metadata_field(self):
        p = create_proposal(ContentType.POST, "T", "B", "src", metadata={"query": "test"})
        assert p["metadata"] == {"query": "test"}

    def test_metadata_none_by_default(self):
        p = create_proposal(ContentType.POST, "T", "B", "src")
        assert p["metadata"] is None

    def test_created_at_is_recent(self):
        before = time.time()
        p = create_proposal(ContentType.POST, "T", "B", "src")
        assert before <= p["created_at"] <= time.time()


# =============================================================================
# CONTENT TYPE ENUM
# =============================================================================


class TestContentType:
    """ContentType enum values."""

    def test_values(self):
        assert ContentType.POST.value == "post"
        assert ContentType.COMMENT.value == "comment"
        assert ContentType.DM_REPLY.value == "dm_reply"

    def test_count(self):
        assert len(ContentType) == 3


# =============================================================================
# APPROVAL STATUS ENUM
# =============================================================================


class TestApprovalStatus:
    """ApprovalStatus lifecycle states."""

    def test_values(self):
        assert ApprovalStatus.PENDING.value == "pending"
        assert ApprovalStatus.APPROVED.value == "approved"
        assert ApprovalStatus.REJECTED.value == "rejected"
        assert ApprovalStatus.EXPIRED.value == "expired"
        assert ApprovalStatus.EXECUTED.value == "executed"

    def test_count(self):
        assert len(ApprovalStatus) == 5


# =============================================================================
# PROTOCOL ABC
# =============================================================================


class TestContentProposalProtocol:
    """ContentProposalProtocol ABC contract."""

    def test_cannot_instantiate(self):
        with pytest.raises(TypeError):
            ContentProposalProtocol()

    def test_has_abstract_methods(self):
        expected = {"generator_id", "content_types", "propose", "can_propose"}
        assert set(ContentProposalProtocol.__abstractmethods__) == expected

    def test_concrete_implementation(self):
        """A concrete implementation satisfies the ABC."""

        class MockGenerator(ContentProposalProtocol):
            @property
            def generator_id(self) -> str:
                return "mock"

            @property
            def content_types(self):
                return [ContentType.POST]

            def propose(self):
                return [create_proposal(ContentType.POST, "Mock", "Content", self.generator_id)]

            def can_propose(self) -> bool:
                return True

        gen = MockGenerator()
        assert gen.generator_id == "mock"
        assert gen.content_types == [ContentType.POST]
        assert gen.can_propose() is True
        proposals = gen.propose()
        assert len(proposals) == 1
        assert proposals[0]["source"] == "mock"

    def test_generator_can_return_empty(self):
        """Generator returning empty list = nothing to say."""

        class SilentGenerator(ContentProposalProtocol):
            @property
            def generator_id(self) -> str:
                return "silent"

            @property
            def content_types(self):
                return [ContentType.POST]

            def propose(self):
                return []

            def can_propose(self) -> bool:
                return False

        gen = SilentGenerator()
        assert gen.can_propose() is False
        assert gen.propose() == []
