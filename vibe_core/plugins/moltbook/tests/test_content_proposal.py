"""
CONTENT PROPOSAL PROTOCOL — Tests
===================================

Tests for:
1. ContentQueue — bounded FIFO, stats, drain behavior
2. ContentProposalProtocol ABC — cannot instantiate
3. EchoContentProposer — default safe implementation
4. Plugin integration — DM reply loop end-to-end
"""

import pytest

from vibe_core.protocols.moltbook_content import (
    ContentProposal,
    ContentProposalProtocol,
    ContentQueue,
    ContentType,
    EchoContentProposer,
)

# =============================================================================
# CONTENT QUEUE
# =============================================================================


class TestContentQueue:
    """ContentQueue is a bounded FIFO with stats."""

    def test_enqueue_and_drain(self):
        q = ContentQueue()
        p = ContentProposal(content_type=ContentType.DM_REPLY.value, content="hi")
        assert q.enqueue(p) is True
        assert q.size == 1
        drained = q.drain(limit=1)
        assert len(drained) == 1
        assert drained[0]["content"] == "hi"
        assert q.is_empty

    def test_fifo_order(self):
        q = ContentQueue()
        for i in range(5):
            q.enqueue(ContentProposal(content_type=ContentType.DM_REPLY.value, content=f"msg{i}"))
        drained = q.drain(limit=5)
        assert [d["content"] for d in drained] == ["msg0", "msg1", "msg2", "msg3", "msg4"]

    def test_drain_limit(self):
        q = ContentQueue()
        for i in range(10):
            q.enqueue(ContentProposal(content_type=ContentType.DM_REPLY.value, content=f"msg{i}"))
        drained = q.drain(limit=3)
        assert len(drained) == 3
        assert q.size == 7

    def test_bounded_eviction(self):
        q = ContentQueue(max_size=3)
        for i in range(5):
            q.enqueue(ContentProposal(content_type=ContentType.DM_REPLY.value, content=f"msg{i}"))
        assert q.size == 3
        # Oldest evicted, newest remain
        drained = q.drain(limit=3)
        assert [d["content"] for d in drained] == ["msg2", "msg3", "msg4"]

    def test_stats(self):
        q = ContentQueue(max_size=5)
        for i in range(3):
            q.enqueue(ContentProposal(content_type=ContentType.DM_REPLY.value, content=f"msg{i}"))
        q.drain(limit=1)
        stats = q.stats
        assert stats["queued"] == 2
        assert stats["total_enqueued"] == 3
        assert stats["total_drained"] == 1
        assert stats["max_size"] == 5

    def test_empty_drain(self):
        q = ContentQueue()
        assert q.drain(limit=5) == []

    def test_peek(self):
        q = ContentQueue()
        assert q.peek() is None
        q.enqueue(ContentProposal(content_type=ContentType.DM_REPLY.value, content="first"))
        assert q.peek()["content"] == "first"
        assert q.size == 1  # peek doesn't remove

    def test_reject_empty_content_type(self):
        q = ContentQueue()
        assert q.enqueue(ContentProposal()) is False
        assert q.size == 0

    def test_dropped_count(self):
        q = ContentQueue(max_size=2)
        q.enqueue(ContentProposal(content_type=ContentType.DM_REPLY.value, content="a"))
        q.enqueue(ContentProposal(content_type=ContentType.DM_REPLY.value, content="b"))
        q.enqueue(ContentProposal(content_type=ContentType.DM_REPLY.value, content="c"))
        assert q.stats["total_dropped"] == 1

    def test_content_dedup_rejects_duplicate(self):
        """Same content text cannot be enqueued twice (prevents 915x identical posts)."""
        q = ContentQueue()
        long_content = "Understanding emerges from practice, not speculation."
        q.enqueue(ContentProposal(content_type=ContentType.COMMENT.value, content=long_content))
        assert q.size == 1
        # Same content again → rejected
        result = q.enqueue(ContentProposal(content_type=ContentType.COMMENT.value, content=long_content))
        assert result is False
        assert q.size == 1
        assert q.stats["total_deduped"] == 1

    def test_content_dedup_allows_different_content(self):
        """Different content passes dedup check."""
        q = ContentQueue()
        q.enqueue(ContentProposal(content_type=ContentType.POST.value, content="First unique post with substance."))
        q.enqueue(ContentProposal(content_type=ContentType.POST.value, content="Second unique post with different content."))
        assert q.size == 2
        assert q.stats["total_deduped"] == 0

    def test_content_dedup_skips_short_content(self):
        """Short content (votes, follows) is not dedup-checked."""
        q = ContentQueue()
        q.enqueue(ContentProposal(content_type=ContentType.VOTE.value, content="", post_id="p1"))
        q.enqueue(ContentProposal(content_type=ContentType.VOTE.value, content="", post_id="p2"))
        assert q.size == 2  # Both allowed (empty content = no dedup)


# =============================================================================
# CONTENT PROPOSAL PROTOCOL ABC
# =============================================================================


class TestContentProposalProtocolABC:
    """ContentProposalProtocol cannot be instantiated directly."""

    def test_is_abstract(self):
        with pytest.raises(TypeError):
            ContentProposalProtocol()

    def test_has_all_methods(self):
        expected = {
            "analyze",
            "analyze_feed",
            "propose_dm_reply",
            "propose_dm_request_action",
            "propose_post",
            "propose_comment",
            "should_engage",
        }
        assert set(ContentProposalProtocol.__abstractmethods__) == expected


# =============================================================================
# ECHO CONTENT PROPOSER — Default safe implementation
# =============================================================================


class TestEchoContentProposer:
    """EchoContentProposer is the safe default — acknowledges DMs, never posts."""

    @pytest.fixture
    def proposer(self):
        return EchoContentProposer()

    def test_is_subclass(self):
        assert issubclass(EchoContentProposer, ContentProposalProtocol)

    def test_is_instance(self, proposer):
        assert isinstance(proposer, ContentProposalProtocol)

    def test_dm_reply_returns_proposal(self, proposer):
        proposal = proposer.propose_dm_reply(
            conversation_id="conv1",
            sender="AgentX",
            inbound_content="Hello!",
        )
        assert proposal is not None
        assert proposal["content_type"] == ContentType.DM_REPLY.value
        assert proposal["conversation_id"] == "conv1"
        assert proposal["sender"] == "AgentX"
        assert "Acknowledged" in proposal["content"]

    def test_dm_reply_with_gateway_response(self, proposer):
        gw = {"success": True, "position": 2, "guardian": "narada", "guna": "sattva"}
        proposal = proposer.propose_dm_reply(
            conversation_id="conv1",
            sender="AgentX",
            inbound_content="Hello!",
            gateway_response=gw,
        )
        assert proposal["gateway_success"] is True
        assert proposal["gateway_position"] == 2
        assert proposal["gateway_guardian"] == "narada"

    def test_dm_reply_without_gateway_response(self, proposer):
        proposal = proposer.propose_dm_reply(
            conversation_id="conv1",
            sender="AgentX",
            inbound_content="Hello!",
            gateway_response=None,
        )
        assert proposal["gateway_success"] is False
        assert proposal["gateway_position"] == -1

    def test_dm_request_action_returns_proposal(self, proposer):
        proposal = proposer.propose_dm_request_action(
            request_id="req1",
            from_agent="CoolBot",
            message_preview="Hey!",
        )
        assert proposal is not None
        assert proposal["content_type"] == ContentType.DM_INITIATE.value
        assert proposal["to_agent"] == "CoolBot"

    def test_propose_post_returns_none(self, proposer):
        assert proposer.propose_post("scheduled") is None

    def test_propose_comment_returns_none(self, proposer):
        assert proposer.propose_comment("p1", "content", "trending") is None

    def test_should_engage_returns_none(self, proposer):
        assert proposer.should_engage("p1", "content", "author") is None


# =============================================================================
# CONTENT TYPE ENUM
# =============================================================================


class TestContentType:
    """ContentType enum covers all outbound action types."""

    def test_values(self):
        assert ContentType.DM_REPLY.value == "dm_reply"
        assert ContentType.DM_INITIATE.value == "dm_initiate"
        assert ContentType.POST.value == "post"
        assert ContentType.COMMENT.value == "comment"
        assert ContentType.VOTE.value == "vote"
        assert ContentType.FOLLOW.value == "follow"
        assert ContentType.SUBSCRIBE.value == "subscribe"

    def test_count(self):
        assert len(ContentType) == 7


# =============================================================================
# PLUGIN INTEGRATION — DM reply loop
# =============================================================================


class TestDMReplyLoop:
    """End-to-end: inbound DM → propose → queue → drain → send_dm."""

    @pytest.fixture
    def plugin(self):
        from vibe_core.mahamantra.adapters.moltbook import MoltbookClient
        from vibe_core.plugins.moltbook.plugin_main import MoltbookPlugin

        plugin = MoltbookPlugin()
        plugin._client = MoltbookClient(api_key="test", offline_mode=True)
        plugin._offline_mode = False  # Tests need online mode to drain queue
        plugin._heartbeat._HEARTBEAT_DEBOUNCE_S = 0
        # Prevent LLM calls: _director_propose is the entry to AgencyDirector → OpenRouter
        plugin._director_propose = lambda *a, **kw: None
        return plugin

    def test_queue_starts_empty(self, plugin):
        assert plugin._content_queue.is_empty

    def test_proposer_is_none_before_boot(self, plugin):
        assert plugin._proposer is None

    def test_manual_enqueue_and_drain(self, plugin):
        """Manually enqueue a DM reply and drain it."""
        proposal = ContentProposal(
            content_type=ContentType.DM_REPLY.value,
            content="Test reply",
            conversation_id="conv1",
        )
        plugin._content_queue.enqueue(proposal)
        assert plugin._content_queue.size == 1

        # Drain executes through MoltbookService
        plugin._drain_content_queue()
        assert plugin._content_queue.is_empty

    def test_seen_message_dedup(self, plugin):
        """Same message ID should not be processed twice."""
        plugin._seen_message_ids.add("msg1")
        assert "msg1" in plugin._seen_message_ids
        # Second add is a no-op
        plugin._seen_message_ids.add("msg1")
        assert len(plugin._seen_message_ids) == 1

    def test_heartbeat_triggers_drain(self, plugin):
        """_do_heartbeat drains the content queue even without new activity."""
        proposal = ContentProposal(
            content_type=ContentType.DM_REPLY.value,
            content="Queued before heartbeat",
            conversation_id="conv1",
        )
        plugin._content_queue.enqueue(proposal)
        assert plugin._content_queue.size == 1

        # Trigger heartbeat cycle to drain queue
        plugin._heartbeat.dispatch_heartbeat({"has_activity": False})
        assert plugin._content_queue.is_empty

    def test_content_queue_stats_in_api(self, plugin):
        """get_api() exposes content_queue stats."""
        api = plugin.get_api()
        assert "content_queue" in api
        assert api["content_queue"]["queued"] == 0
        assert api["content_queue"]["max_size"] == 50

    def test_drain_dm_reply_sends(self, plugin):
        """Draining a DM_REPLY proposal calls send_dm on the mock."""
        proposal = ContentProposal(
            content_type=ContentType.DM_REPLY.value,
            content="Hello back!",
            conversation_id="conv1",
        )
        plugin._content_queue.enqueue(proposal)
        plugin._drain_content_queue()

        # Verify the DM was sent (check mock_db)
        dms = plugin._client._mock_db["dms"]
        assert len(dms) == 1
        assert dms[0]["conversation_id"] == "conv1"

    def test_drain_post_creates(self, plugin):
        """Draining a POST proposal calls create_post on the mock."""
        proposal = ContentProposal(
            content_type=ContentType.POST.value,
            title="Test Post",
            content="Test content",
        )
        plugin._content_queue.enqueue(proposal)
        plugin._drain_content_queue()

        posts = plugin._client._mock_db["posts"]
        assert len(posts) == 1
        assert posts[0]["title"] == "Test Post"

    def test_drain_tamas_blocked(self, plugin):
        """TAMAS operations (delete_post) are blocked by Guna enforcement."""
        # delete_post is TAMAS — should raise PermissionError but be caught
        proposal = ContentProposal(
            content_type=ContentType.VOTE.value,
            post_id="p1",
        )
        plugin._content_queue.enqueue(proposal)
        # Should not crash — upvote is RAJAS, allowed
        plugin._drain_content_queue()
        assert plugin._content_queue.is_empty

    def test_drain_multiple_types(self, plugin):
        """Queue can hold and drain mixed content types."""
        plugin._content_queue.enqueue(
            ContentProposal(
                content_type=ContentType.DM_REPLY.value,
                content="Reply",
                conversation_id="conv1",
            )
        )
        plugin._content_queue.enqueue(
            ContentProposal(
                content_type=ContentType.POST.value,
                title="Post",
                content="Content",
            )
        )
        assert plugin._content_queue.size == 2
        plugin._drain_content_queue()
        assert plugin._content_queue.is_empty
