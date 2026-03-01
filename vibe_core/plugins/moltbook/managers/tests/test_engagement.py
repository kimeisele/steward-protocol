"""Tests for EngagementTracker — extracted from plugin_main.py."""

from unittest.mock import MagicMock, patch

from vibe_core.cartridges.agent_city.moltbook.core.memory import EventLog
from vibe_core.cartridges.agent_city.moltbook.core.strategy import MoltbookStrategyPlanner
from vibe_core.plugins.moltbook.managers.engagement import EngagementTracker
from vibe_core.protocols.moltbook import MoltbookProtocol


def _make_tracker(**kwargs):
    return EngagementTracker(
        log_activity=kwargs.get("log_activity", MagicMock()),
    )


class TestTrack:
    def test_returns_early_without_service(self):
        tracker = _make_tracker()
        tracker.track(
            service=None,
            own_post_ids={"p1": {"created_at": 1}},
            own_comment_ids=set(),
            comment_post_map={},
            event_log=MagicMock(spec=EventLog),
            strategy_planner=None,
        )
        # No exception = pass (early return)

    def test_returns_early_without_posts(self):
        tracker = _make_tracker()
        tracker.track(
            service=MagicMock(spec=MoltbookProtocol),
            own_post_ids={},
            own_comment_ids=set(),
            comment_post_map={},
            event_log=MagicMock(spec=EventLog),
            strategy_planner=None,
        )
        # No exception = pass (early return)

    def test_polls_recent_posts(self):
        tracker = _make_tracker()
        service = MagicMock(spec=MoltbookProtocol)
        service.get_post.return_value = {
            "upvotes": 5,
            "downvotes": 1,
            "comment_count": 2,
        }
        event_log = MagicMock(spec=EventLog)

        own_posts = {
            "p1": {"created_at": 100, "submolt": "general"},
            "p2": {"created_at": 200, "submolt": "tech"},
        }

        with patch("vibe_core.protocols.feedback.get_feedback_safe") as mock_fb:
            mock_fb.return_value = MagicMock()
            tracker.track(
                service=service,
                own_post_ids=own_posts,
                own_comment_ids=set(),
                comment_post_map={},
                event_log=event_log,
                strategy_planner=None,
            )

        assert service.get_post.call_count == 2
        assert event_log.record_engagement_metric.call_count == 2

    def test_positive_engagement_signals_success(self):
        tracker = _make_tracker()
        service = MagicMock(spec=MoltbookProtocol)
        service.get_post.return_value = {
            "upvotes": 3,
            "downvotes": 0,
            "comment_count": 1,
        }
        event_log = MagicMock(spec=EventLog)

        with patch("vibe_core.protocols.feedback.get_feedback_safe") as mock_fb:
            feedback = MagicMock()
            mock_fb.return_value = feedback
            tracker.track(
                service=service,
                own_post_ids={"p1": {"created_at": 100}},
                own_comment_ids=set(),
                comment_post_map={},
                event_log=event_log,
                strategy_planner=None,
            )

        feedback.signal_success.assert_called_once()
        feedback.signal_failure.assert_not_called()

    def test_negative_engagement_signals_failure(self):
        tracker = _make_tracker()
        service = MagicMock(spec=MoltbookProtocol)
        service.get_post.return_value = {
            "upvotes": 0,
            "downvotes": 3,
            "comment_count": 0,
        }
        event_log = MagicMock(spec=EventLog)

        with patch("vibe_core.protocols.feedback.get_feedback_safe") as mock_fb:
            feedback = MagicMock()
            mock_fb.return_value = feedback
            tracker.track(
                service=service,
                own_post_ids={"p1": {"created_at": 100}},
                own_comment_ids=set(),
                comment_post_map={},
                event_log=event_log,
                strategy_planner=None,
            )

        feedback.signal_failure.assert_called_once()
        feedback.signal_success.assert_not_called()

    def test_polls_comments(self):
        tracker = _make_tracker()
        service = MagicMock(spec=MoltbookProtocol)
        service.get_post.return_value = {
            "upvotes": 1,
            "downvotes": 0,
            "comment_count": 0,
        }
        service.get_comments.return_value = [
            {"id": "c1", "upvotes": 2, "downvotes": 0},
        ]
        event_log = MagicMock(spec=EventLog)

        with patch("vibe_core.protocols.feedback.get_feedback_safe") as mock_fb:
            mock_fb.return_value = MagicMock()
            tracker.track(
                service=service,
                own_post_ids={"p1": {"created_at": 100}},
                own_comment_ids={"c1"},
                comment_post_map={"c1": "p1"},
                event_log=event_log,
                strategy_planner=None,
            )

        service.get_comments.assert_called_once_with("p1", sort="new")

    def test_graceful_on_poll_failure(self):
        tracker = _make_tracker()
        service = MagicMock(spec=MoltbookProtocol)
        service.get_post.side_effect = Exception("network error")
        event_log = MagicMock(spec=EventLog)

        with patch("vibe_core.protocols.feedback.get_feedback_safe") as mock_fb:
            mock_fb.return_value = MagicMock()
            tracker.track(
                service=service,
                own_post_ids={"p1": {"created_at": 100}},
                own_comment_ids=set(),
                comment_post_map={},
                event_log=event_log,
                strategy_planner=None,
            )
        # No exception = graceful

    def test_feeds_strategy_planner(self):
        tracker = _make_tracker()
        service = MagicMock(spec=MoltbookProtocol)
        service.get_post.return_value = {
            "upvotes": 5,
            "downvotes": 0,
            "comment_count": 3,
        }
        event_log = MagicMock(spec=EventLog)
        planner = MagicMock(spec=MoltbookStrategyPlanner)

        with patch("vibe_core.protocols.feedback.get_feedback_safe") as mock_fb:
            mock_fb.return_value = MagicMock()
            tracker.track(
                service=service,
                own_post_ids={"p1": {"created_at": 100, "title": "AI post"}},
                own_comment_ids=set(),
                comment_post_map={},
                event_log=event_log,
                strategy_planner=planner,
            )

        planner.update_from_engagement.assert_called_once()


class TestAdjustIntervals:
    def test_cold_start_no_change(self):
        """Not enough signals -> return same intervals."""
        tracker = _make_tracker()
        with patch("vibe_core.protocols.feedback.get_feedback_safe") as mock_fb:
            stats = MagicMock()
            stats.total_signals = 2  # < PANCHA (5)
            mock_fb.return_value.get_stats.return_value = stats
            result = tracker.adjust_intervals(feed_interval=4, post_interval=12)
        assert result == (4, 12)

    def test_high_success_decreases_intervals(self):
        """High success rate -> min intervals."""
        tracker = _make_tracker()
        with patch("vibe_core.protocols.feedback.get_feedback_safe") as mock_fb:
            stats = MagicMock()
            stats.total_signals = 10
            stats.success_rate = 0.95
            mock_fb.return_value.get_stats.return_value = stats
            feed, post = tracker.adjust_intervals(feed_interval=8, post_interval=24)
        assert feed == tracker._MIN_FEED_INTERVAL
        assert post == tracker._MIN_POST_INTERVAL

    def test_low_success_increases_intervals(self):
        """Low success rate -> max intervals."""
        tracker = _make_tracker()
        with patch("vibe_core.protocols.feedback.get_feedback_safe") as mock_fb:
            stats = MagicMock()
            stats.total_signals = 10
            stats.success_rate = 0.05
            mock_fb.return_value.get_stats.return_value = stats
            feed, post = tracker.adjust_intervals(feed_interval=4, post_interval=12)
        assert feed == tracker._MAX_FEED_INTERVAL
        assert post == tracker._MAX_POST_INTERVAL

    def test_intervals_clamped(self):
        """Result always within min/max bounds."""
        tracker = _make_tracker()
        with patch("vibe_core.protocols.feedback.get_feedback_safe") as mock_fb:
            stats = MagicMock()
            stats.total_signals = 10
            stats.success_rate = 0.5
            mock_fb.return_value.get_stats.return_value = stats
            feed, post = tracker.adjust_intervals(feed_interval=4, post_interval=12)
        assert tracker._MIN_FEED_INTERVAL <= feed <= tracker._MAX_FEED_INTERVAL
        assert tracker._MIN_POST_INTERVAL <= post <= tracker._MAX_POST_INTERVAL
