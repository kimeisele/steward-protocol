"""Tests for IntentExecutor — Kirtan failure recording.

Tests verify that when content generation returns None, the IntentExecutor
emits INTENT_FAILURE events (visible to Ouroboros) instead of silently dropping.
"""

from unittest.mock import MagicMock

from vibe_core.plugins.moltbook.managers.intent_executor import IntentExecutor
from vibe_core.protocols.moltbook_content import ContentQueue


def _make_intent(action_type="comment", topic="test topic", target_post_id="p1", mission_id="m1"):
    """Create a mock StrategicIntent."""
    intent = MagicMock()
    intent.action_type = action_type
    intent.target_post_id = target_post_id if action_type == "comment" else None
    intent.__dict__ = {
        "action_type": action_type,
        "topic": topic,
        "target_post_id": target_post_id,
        "mission_id": mission_id,
        "reasoning": "test reasoning",
        "engagement_context": "",
        "submolt_context": "",
        "content_format": "",
    }
    return intent


def _make_executor():
    """Create IntentExecutor with mocked plugin."""
    plugin = MagicMock()
    plugin._current_intents = []
    plugin._commented_post_ids = set()
    plugin._submolt_descriptions = {}
    plugin._last_post_heartbeat = 0
    plugin._heartbeat_count = 10
    plugin._content_queue = ContentQueue()
    plugin._emit_event = MagicMock()
    plugin._director_propose = MagicMock()
    plugin._select_submolt = MagicMock(return_value="test-submolt")
    return IntentExecutor(plugin), plugin


class TestIntentFailureRecording:
    """proposal=None → INTENT_FAILURE event emitted."""

    def test_comment_failure_emits_event(self):
        executor, plugin = _make_executor()
        plugin._director_propose.return_value = None
        plugin._current_intents = [_make_intent(action_type="comment", target_post_id="p1")]

        executor.execute_intents()

        calls = [c for c in plugin._emit_event.call_args_list if c[0][0] == "INTENT_FAILURE"]
        assert len(calls) == 1
        assert "comment" in calls[0][0][1].lower()
        assert calls[0][0][2]["post_id"] == "p1"

    def test_post_failure_emits_event(self):
        executor, plugin = _make_executor()
        plugin._director_propose.return_value = None
        plugin._current_intents = [_make_intent(action_type="post")]

        executor.execute_intents()

        calls = [c for c in plugin._emit_event.call_args_list if c[0][0] == "INTENT_FAILURE"]
        assert len(calls) == 1
        assert "post" in calls[0][0][1].lower()

    def test_comment_success_no_failure_event(self):
        executor, plugin = _make_executor()
        plugin._director_propose.return_value = {
            "content_type": "comment",
            "content": "Good comment content here.",
            "post_id": "p1",
        }
        plugin._current_intents = [_make_intent(action_type="comment", target_post_id="p1")]

        executor.execute_intents()

        failure_calls = [c for c in plugin._emit_event.call_args_list if c[0][0] == "INTENT_FAILURE"]
        assert len(failure_calls) == 0

    def test_post_success_no_failure_event(self):
        executor, plugin = _make_executor()
        plugin._director_propose.return_value = {
            "content_type": "post",
            "content": "# Title\nGood post content here.",
        }
        plugin._current_intents = [_make_intent(action_type="post")]

        executor.execute_intents()

        failure_calls = [c for c in plugin._emit_event.call_args_list if c[0][0] == "INTENT_FAILURE"]
        assert len(failure_calls) == 0


class TestStrategicSilence:
    """No intents → STRATEGIC_SILENCE event (existing behavior)."""

    def test_no_intents_emits_silence(self):
        executor, plugin = _make_executor()
        plugin._current_intents = []

        executor.execute_intents()

        calls = [c for c in plugin._emit_event.call_args_list if c[0][0] == "STRATEGIC_SILENCE"]
        assert len(calls) == 1


class TestCommentDedup:
    """Already-commented posts are skipped (existing behavior)."""

    def test_skip_already_commented(self):
        executor, plugin = _make_executor()
        plugin._commented_post_ids = {"p1"}
        plugin._current_intents = [_make_intent(action_type="comment", target_post_id="p1")]

        executor.execute_intents()

        # No propose call, no failure event (intentional skip, not failure)
        plugin._director_propose.assert_not_called()
