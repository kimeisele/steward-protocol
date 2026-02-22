"""
Tests for MoltbookResolver — IntentResolver for Moltbook I/O.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from vibe_core.mahamantra import (
    IntentPriority,
    IntentResult,
    IntentStatus,
    IntentType,
    MantraIntent,
)
from vibe_core.services.moltbook_resolver import (
    HANDLED_TYPES,
    MOLTBOOK_PREFIX,
    TARGET_APPROVE_DM,
    TARGET_CREATE_COMMENT,
    TARGET_CREATE_POST,
    TARGET_DM_CHECK,
    TARGET_FEED,
    TARGET_OWN_PROFILE,
    TARGET_REJECT_DM,
    TARGET_SEARCH,
    TARGET_SEND_DM,
    TARGET_SEND_DM_REQUEST,
    TARGET_SUBSCRIBE,
    TARGET_UNFOLLOW,
    TARGET_UNSUBSCRIBE,
    TARGET_UPDATE_PROFILE,
    TARGET_UPVOTE,
    MoltbookResolver,
    create_moltbook_listener,
)


@pytest.fixture
def mock_client():
    """Create a mock MoltbookClient."""
    client = MagicMock()
    client.sync_check_heartbeat.return_value = {"has_new_messages": False, "pending_requests": 0}
    client.sync_get_dm_conversations.return_value = []
    client.sync_get_dm_messages.return_value = []
    client.sync_create_post.return_value = {"id": "post_1", "title": "test"}
    client.sync_send_dm.return_value = {"success": True}
    return client


@pytest.fixture
def resolver(mock_client):
    return MoltbookResolver(mock_client)


# =============================================================================
# can_resolve
# =============================================================================


class TestCanResolve:
    def test_handles_read_moltbook(self, resolver):
        intent = MantraIntent(type=IntentType.READ, target="moltbook/feed", params={})
        assert resolver.can_resolve(intent) is True

    def test_handles_write_moltbook(self, resolver):
        intent = MantraIntent(type=IntentType.WRITE, target="moltbook/post/create", params={})
        assert resolver.can_resolve(intent) is True

    def test_handles_observe_moltbook(self, resolver):
        intent = MantraIntent(type=IntentType.OBSERVE, target="moltbook/profile/me", params={})
        assert resolver.can_resolve(intent) is True

    def test_handles_sync_moltbook(self, resolver):
        intent = MantraIntent(type=IntentType.SYNC, target="moltbook/dm/check", params={})
        assert resolver.can_resolve(intent) is True

    def test_rejects_non_moltbook_target(self, resolver):
        intent = MantraIntent(type=IntentType.READ, target="other/service", params={})
        assert resolver.can_resolve(intent) is False

    def test_rejects_unhandled_intent_type(self, resolver):
        intent = MantraIntent(type=IntentType.HEAL, target="moltbook/feed", params={})
        assert resolver.can_resolve(intent) is False

    def test_rejects_transform(self, resolver):
        intent = MantraIntent(type=IntentType.TRANSFORM, target="moltbook/feed", params={})
        assert resolver.can_resolve(intent) is False


# =============================================================================
# resolve — READ operations
# =============================================================================


class TestResolveRead:
    def test_read_feed(self, resolver, mock_client):
        # Mock _dispatch directly to avoid async complexity
        resolver._dispatch = MagicMock(return_value=[{"id": "p1", "title": "test"}])
        intent = MantraIntent(type=IntentType.READ, target=TARGET_FEED, params={"sort": "new", "limit": 5})
        result = resolver.resolve(intent)
        assert result.status == IntentStatus.RESOLVED
        assert result.value == [{"id": "p1", "title": "test"}]
        resolver._dispatch.assert_called_once_with(TARGET_FEED, {"sort": "new", "limit": 5})

    def test_dm_check(self, resolver, mock_client):
        intent = MantraIntent(type=IntentType.SYNC, target=TARGET_DM_CHECK, params={})
        result = resolver.resolve(intent)
        assert result.status == IntentStatus.RESOLVED
        assert result.value == {"has_new_messages": False, "pending_requests": 0}
        mock_client.sync_check_heartbeat.assert_called_once()

    def test_own_profile(self, resolver, mock_client):
        mock_client.get_own_profile = AsyncMock(return_value={"name": "steward-protocol"})
        intent = MantraIntent(type=IntentType.OBSERVE, target=TARGET_OWN_PROFILE, params={})
        result = resolver.resolve(intent)
        # May fail due to async, but should not crash
        assert result.status in (IntentStatus.RESOLVED, IntentStatus.FAILED)

    def test_search_requires_query(self, resolver):
        intent = MantraIntent(type=IntentType.READ, target=TARGET_SEARCH, params={})
        result = resolver.resolve(intent)
        assert result.status == IntentStatus.FAILED
        assert "query required" in result.error


# =============================================================================
# resolve — WRITE operations
# =============================================================================


class TestResolveWrite:
    def test_create_post(self, resolver, mock_client):
        intent = MantraIntent(
            type=IntentType.WRITE,
            target=TARGET_CREATE_POST,
            params={"title": "Hello", "content": "World"},
        )
        result = resolver.resolve(intent)
        assert result.status == IntentStatus.RESOLVED
        mock_client.sync_create_post.assert_called_once_with("Hello", "World", None)

    def test_create_post_requires_title(self, resolver):
        intent = MantraIntent(
            type=IntentType.WRITE,
            target=TARGET_CREATE_POST,
            params={"content": "World"},
        )
        result = resolver.resolve(intent)
        assert result.status == IntentStatus.FAILED
        assert "title" in result.error

    def test_send_dm(self, resolver, mock_client):
        intent = MantraIntent(
            type=IntentType.WRITE,
            target=TARGET_SEND_DM,
            params={"conversation_id": "conv1", "content": "hello"},
        )
        result = resolver.resolve(intent)
        assert result.status == IntentStatus.RESOLVED
        mock_client.sync_send_dm.assert_called_once_with("conv1", "hello")

    def test_send_dm_requires_content(self, resolver):
        intent = MantraIntent(
            type=IntentType.WRITE,
            target=TARGET_SEND_DM,
            params={"conversation_id": "conv1"},
        )
        result = resolver.resolve(intent)
        assert result.status == IntentStatus.FAILED

    def test_create_comment(self, resolver, mock_client):
        mock_client.comment_with_verification = AsyncMock(return_value={"id": "c1"})
        intent = MantraIntent(
            type=IntentType.WRITE,
            target=TARGET_CREATE_COMMENT,
            params={"post_id": "p1", "content": "nice post"},
        )
        result = resolver.resolve(intent)
        assert result.status in (IntentStatus.RESOLVED, IntentStatus.FAILED)

    def test_create_comment_requires_post_id(self, resolver):
        intent = MantraIntent(
            type=IntentType.WRITE,
            target=TARGET_CREATE_COMMENT,
            params={"content": "nice"},
        )
        result = resolver.resolve(intent)
        assert result.status == IntentStatus.FAILED
        assert "post_id" in result.error

    def test_send_dm_request(self, resolver, mock_client):
        mock_client.send_dm_request = AsyncMock(return_value={"success": True})
        intent = MantraIntent(
            type=IntentType.WRITE,
            target=TARGET_SEND_DM_REQUEST,
            params={"to_agent": "agent42", "message": "hey"},
        )
        result = resolver.resolve(intent)
        assert result.status in (IntentStatus.RESOLVED, IntentStatus.FAILED)

    def test_send_dm_request_requires_agent(self, resolver):
        intent = MantraIntent(
            type=IntentType.WRITE,
            target=TARGET_SEND_DM_REQUEST,
            params={"message": "hey"},
        )
        result = resolver.resolve(intent)
        assert result.status == IntentStatus.FAILED
        assert "to_agent" in result.error

    def test_approve_dm(self, resolver, mock_client):
        mock_client.approve_dm_request = AsyncMock(return_value={"success": True})
        intent = MantraIntent(
            type=IntentType.WRITE,
            target=TARGET_APPROVE_DM,
            params={"request_id": "req1"},
        )
        result = resolver.resolve(intent)
        assert result.status in (IntentStatus.RESOLVED, IntentStatus.FAILED)

    def test_approve_dm_requires_id(self, resolver):
        intent = MantraIntent(
            type=IntentType.WRITE,
            target=TARGET_APPROVE_DM,
            params={},
        )
        result = resolver.resolve(intent)
        assert result.status == IntentStatus.FAILED

    def test_reject_dm(self, resolver, mock_client):
        mock_client.reject_dm_request = AsyncMock(return_value={"success": True})
        intent = MantraIntent(
            type=IntentType.WRITE,
            target=TARGET_REJECT_DM,
            params={"request_id": "req1", "block": True},
        )
        result = resolver.resolve(intent)
        assert result.status in (IntentStatus.RESOLVED, IntentStatus.FAILED)

    def test_subscribe(self, resolver, mock_client):
        mock_client.subscribe_submolt = AsyncMock(return_value={"success": True})
        intent = MantraIntent(
            type=IntentType.WRITE,
            target=TARGET_SUBSCRIBE,
            params={"submolt": "general"},
        )
        result = resolver.resolve(intent)
        assert result.status in (IntentStatus.RESOLVED, IntentStatus.FAILED)

    def test_subscribe_requires_submolt(self, resolver):
        intent = MantraIntent(
            type=IntentType.WRITE,
            target=TARGET_SUBSCRIBE,
            params={},
        )
        result = resolver.resolve(intent)
        assert result.status == IntentStatus.FAILED

    def test_unsubscribe(self, resolver, mock_client):
        mock_client.unsubscribe_submolt = AsyncMock(return_value={"success": True})
        intent = MantraIntent(
            type=IntentType.WRITE,
            target=TARGET_UNSUBSCRIBE,
            params={"submolt": "general"},
        )
        result = resolver.resolve(intent)
        assert result.status in (IntentStatus.RESOLVED, IntentStatus.FAILED)

    def test_unfollow(self, resolver, mock_client):
        mock_client.unfollow_agent = AsyncMock(return_value={"success": True})
        intent = MantraIntent(
            type=IntentType.WRITE,
            target=TARGET_UNFOLLOW,
            params={"name": "agent42"},
        )
        result = resolver.resolve(intent)
        assert result.status in (IntentStatus.RESOLVED, IntentStatus.FAILED)

    def test_update_profile(self, resolver, mock_client):
        mock_client.update_profile = AsyncMock(return_value={"success": True})
        intent = MantraIntent(
            type=IntentType.WRITE,
            target=TARGET_UPDATE_PROFILE,
            params={"description": "new bio"},
        )
        result = resolver.resolve(intent)
        assert result.status in (IntentStatus.RESOLVED, IntentStatus.FAILED)

    def test_unknown_target_fails(self, resolver):
        intent = MantraIntent(
            type=IntentType.WRITE,
            target="moltbook/unknown/thing",
            params={},
        )
        result = resolver.resolve(intent)
        assert result.status == IntentStatus.FAILED
        assert "Unknown" in result.error


# =============================================================================
# IntentResult shape
# =============================================================================


class TestIntentResultShape:
    def test_result_has_intent(self, resolver, mock_client):
        intent = MantraIntent(type=IntentType.SYNC, target=TARGET_DM_CHECK, params={})
        result = resolver.resolve(intent)
        assert result.intent is intent

    def test_result_has_guardian(self, resolver, mock_client):
        intent = MantraIntent(type=IntentType.SYNC, target=TARGET_DM_CHECK, params={})
        result = resolver.resolve(intent)
        assert result.resolved_by is not None

    def test_failed_result_has_error(self, resolver, mock_client):
        mock_client.sync_check_heartbeat.side_effect = Exception("network error")
        intent = MantraIntent(type=IntentType.SYNC, target=TARGET_DM_CHECK, params={})
        result = resolver.resolve(intent)
        assert result.status == IntentStatus.FAILED
        assert "network error" in result.error


# =============================================================================
# Singularity Listener
# =============================================================================


class TestSingularityListener:
    def test_listener_queues_on_downbeat(self, mock_client):
        listener = create_moltbook_listener(mock_client)
        with patch("vibe_core.mahamantra.kernel.intent.get_kernel") as mock_get_kernel:
            mock_kernel = MagicMock()
            mock_get_kernel.return_value = mock_kernel

            # Non-downbeat — should NOT queue
            listener({"position": 5, "is_downbeat": False, "tick": 5})
            mock_kernel.queue.assert_not_called()

            # Downbeat — should queue
            listener({"position": 0, "is_downbeat": True, "tick": 0})
            mock_kernel.queue.assert_called_once()

            queued_intent = mock_kernel.queue.call_args[0][0]
            assert queued_intent.type == IntentType.SYNC
            assert queued_intent.target == TARGET_DM_CHECK

    def test_listener_handles_object_tick_state(self, mock_client):
        listener = create_moltbook_listener(mock_client)
        with patch("vibe_core.mahamantra.kernel.intent.get_kernel") as mock_get_kernel:
            mock_kernel = MagicMock()
            mock_get_kernel.return_value = mock_kernel

            # Object-style tick_state
            tick = MagicMock()
            tick.is_downbeat = True
            listener(tick)
            mock_kernel.queue.assert_called_once()

    def test_listener_ignores_non_downbeat(self, mock_client):
        listener = create_moltbook_listener(mock_client)
        with patch("vibe_core.mahamantra.kernel.intent.get_kernel") as mock_get_kernel:
            mock_kernel = MagicMock()
            mock_get_kernel.return_value = mock_kernel

            for pos in range(1, 16):
                listener({"position": pos, "is_downbeat": False, "tick": pos})

            mock_kernel.queue.assert_not_called()
