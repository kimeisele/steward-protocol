"""Tests for ContentDrainer — extracted from plugin_main.py."""

import time
from unittest.mock import MagicMock

from vibe_core.plugins.moltbook.managers.drainer import ContentDrainer
from vibe_core.protocols.moltbook import MoltbookProtocol
from vibe_core.protocols.moltbook_content import ContentQueue, ContentType


def _make_drainer(**kwargs):
    """Create a ContentDrainer with mocked dependencies."""
    return ContentDrainer(
        service_getter=kwargs.get("service_getter", MagicMock()),
        log_activity=kwargs.get("log_activity", MagicMock()),
        broadcast_to_agora=kwargs.get("broadcast_to_agora", MagicMock()),
        emit_event=kwargs.get("emit_event", MagicMock()),
        own_post_ids=kwargs.get("own_post_ids", {}),
        own_comment_ids=kwargs.get("own_comment_ids", set()),
        comment_post_map=kwargs.get("comment_post_map", {}),
        followed_agents=kwargs.get("followed_agents", set()),
        subscribed_submolts=kwargs.get("subscribed_submolts", set()),
    )


class TestRateLimiting:
    def test_post_rate_limit(self):
        drainer = _make_drainer()
        drainer._last_post_ts = time.time()  # Just posted
        assert drainer.check_rate_limit("post") is False

    def test_post_rate_limit_ok_after_interval(self):
        drainer = _make_drainer()
        drainer._last_post_ts = time.time() - 2000  # 33 minutes ago
        assert drainer.check_rate_limit("post") is True

    def test_comment_rate_limit(self):
        drainer = _make_drainer()
        now = time.time()
        drainer._comment_timestamps = [now - i for i in range(30)]  # 30 recent comments
        assert drainer.check_rate_limit("comment") is False

    def test_comment_rate_limit_ok(self):
        drainer = _make_drainer()
        drainer._comment_timestamps = []
        assert drainer.check_rate_limit("comment") is True

    def test_dm_rate_limit(self):
        drainer = _make_drainer()
        now = time.time()
        drainer._dm_timestamps = [now - i for i in range(30)]
        assert drainer.check_rate_limit("dm_reply") is False

    def test_dm_rate_limit_ok(self):
        drainer = _make_drainer()
        drainer._dm_timestamps = []
        assert drainer.check_rate_limit("dm_reply") is True

    def test_record_post(self):
        drainer = _make_drainer()
        drainer.record_rate_limit("post")
        assert drainer._last_post_ts > 0

    def test_record_comment(self):
        drainer = _make_drainer()
        drainer.record_rate_limit("comment")
        assert len(drainer._comment_timestamps) == 1

    def test_record_dm(self):
        drainer = _make_drainer()
        drainer.record_rate_limit("dm_reply")
        assert len(drainer._dm_timestamps) == 1


class TestDrainHandlers:
    def test_drain_post(self):
        own_post_ids = {}
        service = MagicMock(spec=MoltbookProtocol)
        service.create_post.return_value = {"id": "new_post_123"}
        log_activity = MagicMock()
        broadcast = MagicMock()
        emit = MagicMock()
        drainer = _make_drainer(
            service_getter=lambda: service,
            log_activity=log_activity,
            broadcast_to_agora=broadcast,
            emit_event=emit,
            own_post_ids=own_post_ids,
        )
        proposal = {
            "content_type": ContentType.POST.value,
            "title": "Test Title",
            "content": "Test content",
            "submolt": "general",
        }
        drainer._drain_post(service, proposal)
        service.create_post.assert_called_once_with("Test Title", "Test content", "general")
        assert "new_post_123" in own_post_ids
        log_activity.assert_called()
        broadcast.assert_called()

    def test_drain_comment(self):
        own_comment_ids = set()
        comment_post_map = {}
        service = MagicMock(spec=MoltbookProtocol)
        service.comment.return_value = {"id": "c_123"}
        drainer = _make_drainer(
            own_comment_ids=own_comment_ids,
            comment_post_map=comment_post_map,
        )
        proposal = {
            "content_type": ContentType.COMMENT.value,
            "post_id": "p_1",
            "content": "Nice post!",
        }
        drainer._drain_comment(service, proposal)
        service.comment.assert_called_once_with("p_1", "Nice post!", None)
        assert "c_123" in own_comment_ids
        assert comment_post_map["c_123"] == "p_1"

    def test_drain_vote(self):
        service = MagicMock(spec=MoltbookProtocol)
        drainer = _make_drainer()
        proposal = {"content_type": ContentType.VOTE.value, "post_id": "p_1"}
        drainer._drain_vote(service, proposal)
        service.upvote.assert_called_once_with("p_1")

    def test_drain_follow(self):
        service = MagicMock(spec=MoltbookProtocol)
        drainer = _make_drainer()
        proposal = {"content_type": ContentType.FOLLOW.value, "to_agent": "alice"}
        drainer._drain_follow(service, proposal)
        service.follow.assert_called_once_with("alice")

    def test_drain_subscribe(self):
        service = MagicMock(spec=MoltbookProtocol)
        drainer = _make_drainer()
        proposal = {"content_type": ContentType.SUBSCRIBE.value, "submolt": "general"}
        drainer._drain_subscribe(service, proposal)
        service.subscribe.assert_called_once_with("general")


class TestContentValidation:
    """Drainer MUST reject whitespace/empty content before API call."""

    def test_drain_post_rejects_whitespace_content(self):
        service = MagicMock(spec=MoltbookProtocol)
        drainer = _make_drainer()
        proposal = {"content_type": "post", "title": "Title", "content": "   ", "submolt": "g"}
        drainer._drain_post(service, proposal)
        service.create_post.assert_not_called()

    def test_drain_post_rejects_empty_title(self):
        service = MagicMock(spec=MoltbookProtocol)
        drainer = _make_drainer()
        proposal = {"content_type": "post", "title": "", "content": "Real content", "submolt": "g"}
        drainer._drain_post(service, proposal)
        service.create_post.assert_not_called()

    def test_drain_comment_rejects_whitespace_content(self):
        service = MagicMock(spec=MoltbookProtocol)
        drainer = _make_drainer()
        proposal = {"content_type": "comment", "post_id": "p1", "content": " \n "}
        drainer._drain_comment(service, proposal)
        service.comment.assert_not_called()

    def test_drain_dm_reply_rejects_whitespace_content(self):
        service = MagicMock(spec=MoltbookProtocol)
        drainer = _make_drainer()
        proposal = {"content_type": "dm_reply", "conversation_id": "c1", "content": "  "}
        drainer._drain_dm_reply(service, proposal)
        service.send_dm.assert_not_called()


class TestRateLimitPersistence:
    """Rate limit state must survive restart."""

    def test_snapshot_restore_roundtrip(self):
        drainer = _make_drainer()
        drainer._last_post_ts = 1000000.0
        drainer._comment_timestamps = [time.time() - 100, time.time() - 200]
        drainer._dm_timestamps = [time.time() - 50]
        snap = drainer.rate_limit_snapshot()

        drainer2 = _make_drainer()
        drainer2.rate_limit_restore(snap)
        assert drainer2._last_post_ts == 1000000.0
        assert len(drainer2._comment_timestamps) == 2
        assert len(drainer2._dm_timestamps) == 1

    def test_restore_filters_expired_timestamps(self):
        drainer = _make_drainer()
        old_ts = time.time() - 7200  # 2 hours ago
        recent_ts = time.time() - 100  # recent
        state = {
            "last_post_ts": 500.0,
            "comment_timestamps": [old_ts, recent_ts],
            "dm_timestamps": [old_ts],
        }
        drainer.rate_limit_restore(state)
        assert len(drainer._comment_timestamps) == 1  # Only recent survives
        assert len(drainer._dm_timestamps) == 0  # All expired


class TestQueueHealthMonitoring:
    def test_no_warning_when_healthy(self):
        drainer = _make_drainer()
        queue = ContentQueue()
        drainer.monitor_queue_health(queue, heartbeat_count=1)
        # No exception = pass

    def test_overflow_detection(self):
        drainer = _make_drainer()
        queue = ContentQueue()
        queue._total_dropped = 5
        drainer.monitor_queue_health(queue, heartbeat_count=10)
        assert drainer._last_overflow_log == 10
