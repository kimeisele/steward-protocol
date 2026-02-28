"""Tests for FeedAnalyzer — extracted from plugin_main.py."""

from unittest.mock import MagicMock, patch

from vibe_core.plugins.moltbook.managers.feed import FeedAnalyzer
from vibe_core.protocols.moltbook import MoltbookProtocol
from vibe_core.protocols.moltbook_content import ContentProposalProtocol, ContentQueue


def _make_feed(**kwargs):
    return FeedAnalyzer(
        seen_post_ids=kwargs.get("seen_post_ids", set()),
        subscribed_submolts=kwargs.get("subscribed_submolts", set()),
        submolt_descriptions=kwargs.get("submolt_descriptions", {}),
    )


class TestScanFeed:
    def test_returns_empty_without_proposer(self):
        feed = _make_feed()
        result = feed.scan_feed(client=MagicMock(spec=MoltbookProtocol), proposer=None, content_queue=ContentQueue())
        assert result == []

    def test_returns_topics_from_feed(self):
        feed = _make_feed()
        client = MagicMock(spec=MoltbookProtocol)
        posts = [
            {"id": "p1", "title": "Post 1", "content": "Content 1"},
            {"id": "p2", "title": "Post 2", "content": "Content 2"},
        ]
        with patch("vibe_core.plugins.moltbook.managers.feed.run_async", return_value=posts):
            result = feed.scan_feed(
                client=client,
                proposer=MagicMock(spec=ContentProposalProtocol),
                content_queue=ContentQueue(),
            )
        assert len(result) == 2
        assert result[0]["id"] == "p1"

    def test_skips_already_seen_posts_for_engagement(self):
        seen = {"p1"}
        feed = _make_feed(seen_post_ids=seen)
        proposer = MagicMock(spec=ContentProposalProtocol)
        proposer.should_engage.return_value = {"content_type": "vote", "post_id": "p2"}
        posts = [
            {"id": "p1", "title": "Already seen", "content": "C1", "author": {"name": "a"}},
            {"id": "p2", "title": "New post", "content": "C2", "author": {"name": "b"}},
        ]
        queue = ContentQueue()
        with patch("vibe_core.plugins.moltbook.managers.feed.run_async", return_value=posts):
            feed.scan_feed(client=MagicMock(spec=MoltbookProtocol), proposer=proposer, content_queue=queue)
        # p1 was seen, only p2 should get engagement proposal
        assert "p2" in seen  # Now marked as seen
        # p1 engagement was skipped, p2 engagement was attempted
        assert proposer.should_engage.call_count == 1


class TestEnsureOwnSubmolt:
    """Autonomous submolt creation — 'steward-protocol'."""

    def test_skips_if_already_subscribed(self):
        feed = _make_feed(subscribed_submolts={"steward-protocol"})
        client = MagicMock(spec=MoltbookProtocol)
        queue = ContentQueue()
        feed.ensure_own_submolt(client, queue)
        # No API calls made
        assert queue.size == 0

    def test_subscribes_if_exists(self):
        """If submolt exists on server, just subscribe (don't create)."""
        feed = _make_feed()
        client = MagicMock()  # No spec — sync_create_submolt is on client, not protocol
        submolts = [{"name": "steward-protocol", "display_name": "Steward Protocol"}]
        queue = ContentQueue()
        with patch("vibe_core.plugins.moltbook.managers.feed.run_async", return_value=submolts):
            feed.ensure_own_submolt(client, queue)
        assert "steward-protocol" in feed._subscribed_submolts
        assert queue.size == 1
        # create_submolt should NOT be called
        client.sync_create_submolt.assert_not_called()

    def test_creates_if_not_exists(self):
        """If submolt doesn't exist, create it then subscribe."""
        feed = _make_feed()
        client = MagicMock()
        submolts = [{"name": "general", "display_name": "General"}]
        queue = ContentQueue()
        with patch("vibe_core.plugins.moltbook.managers.feed.run_async", return_value=submolts):
            feed.ensure_own_submolt(client, queue)
        client.sync_create_submolt.assert_called_once_with(
            "steward-protocol",
            "Steward Protocol",
            "Autonomous systems engineering — infrastructure, observability, distributed systems.",
        )
        assert "steward-protocol" in feed._subscribed_submolts
        assert queue.size == 1

    def test_handles_creation_failure(self):
        """If creation fails, don't subscribe."""
        feed = _make_feed()
        client = MagicMock()
        client.sync_create_submolt.side_effect = Exception("API error")
        submolts = []  # Doesn't exist
        queue = ContentQueue()
        with patch("vibe_core.plugins.moltbook.managers.feed.run_async", return_value=submolts):
            feed.ensure_own_submolt(client, queue)
        assert "steward-protocol" not in feed._subscribed_submolts
        assert queue.size == 0

    def test_handles_api_unavailable(self):
        """If get_submolts fails, graceful degradation."""
        feed = _make_feed()
        client = MagicMock()
        queue = ContentQueue()
        with patch("vibe_core.plugins.moltbook.managers.feed.run_async", side_effect=Exception("timeout")):
            feed.ensure_own_submolt(client, queue)
        assert queue.size == 0


class TestSelectSubmolt:
    def test_returns_none_without_subscriptions(self):
        feed = _make_feed(subscribed_submolts=set())
        result = feed.select_submolt("test", lambda: MagicMock())
        assert result is None

    def test_returns_none_with_empty_content(self):
        """select_submolt returns None when content tokenizes to nothing."""
        feed = _make_feed(subscribed_submolts={"general"})
        # All short/stop words → empty token set → no Jaccard match possible
        result = feed.select_submolt("a to is", lambda: MagicMock())
        assert result is None
