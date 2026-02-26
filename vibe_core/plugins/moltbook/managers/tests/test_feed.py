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


class TestSelectSubmolt:
    def test_returns_none_without_subscriptions(self):
        feed = _make_feed(subscribed_submolts=set())
        result = feed.select_submolt("test", lambda: MagicMock())
        assert result is None

    def test_returns_none_without_resonate(self):
        feed = _make_feed(subscribed_submolts={"general"})
        with patch("vibe_core.mahamantra.substrate.encoding.resonance_ranker.resonate", side_effect=Exception("no resonate")):
            result = feed.select_submolt("test", lambda: MagicMock())
        assert result is None
