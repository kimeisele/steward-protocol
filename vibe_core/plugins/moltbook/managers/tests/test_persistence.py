"""Tests for PersistenceManager — extracted from plugin_main.py."""

import json

from vibe_core.plugins.moltbook.managers.persistence import PersistenceManager
from vibe_core.protocols.moltbook_content import ContentQueue


class TestPersistQueue:
    def test_persist_and_restore_queue(self, tmp_path):
        """Persist proposals and restore them in a new queue."""
        mgr = PersistenceManager(state_dir=tmp_path)
        queue = ContentQueue()
        queue.enqueue({"content_type": "post", "content": "hello", "priority": 1})
        queue.enqueue({"content_type": "comment", "content": "nice", "priority": 2})

        mgr.persist_queue(
            queue=queue,
            seen_message_ids={"m1", "m2"},
            seen_post_ids={"p1"},
            own_comment_ids={"c1"},
            commented_post_ids={"p2"},
            followed_agents={"alice"},
            subscribed_submolts={"general"},
            comment_post_map={"c1": "p1"},
            own_post_ids={"p3": {"submolt": "gen", "created_at": 100}},
        )

        # Verify files exist
        assert (tmp_path / "content_queue.json").exists()
        assert (tmp_path / "seen_ids.json").exists()

        # Restore into new queue
        new_queue = ContentQueue()
        restored = mgr.restore_queue(new_queue)

        assert new_queue.size == 2
        assert restored["seen_message_ids"] == {"m1", "m2"}
        assert restored["seen_post_ids"] == {"p1"}
        assert restored["own_comment_ids"] == {"c1"}
        assert restored["commented_post_ids"] == {"p2"}
        assert restored["followed_agents"] == {"alice"}
        assert restored["subscribed_submolts"] == {"general"}
        assert restored["comment_post_map"] == {"c1": "p1"}
        assert "p3" in restored["own_post_ids"]

    def test_persist_queue_no_state_dir(self):
        """No state dir → no-op."""
        mgr = PersistenceManager(state_dir=None)
        mgr.persist_queue(
            queue=ContentQueue(),
            seen_message_ids=set(),
            seen_post_ids=set(),
            own_comment_ids=set(),
            commented_post_ids=set(),
            followed_agents=set(),
            subscribed_submolts=set(),
            comment_post_map={},
            own_post_ids={},
        )
        # No exception = pass

    def test_restore_queue_no_state_dir(self):
        """No state dir → empty dict."""
        mgr = PersistenceManager(state_dir=None)
        assert mgr.restore_queue(ContentQueue()) == {}


class TestPersistPhaseState:
    def test_persist_and_restore_phase(self, tmp_path):
        mgr = PersistenceManager(state_dir=tmp_path)
        mgr.persist_phase_state(
            heartbeat_count=42,
            feed_topics=[{"id": "p1", "title": "topic1"}],
            intents=[{"action_type": "post", "topic": "AI", "reasoning": "hot"}],
        )

        restored = mgr.restore_phase_state()
        assert restored["heartbeat_count"] == 42
        assert len(restored["feed_topics"]) == 1
        assert restored["feed_topics"][0]["title"] == "topic1"
        assert len(restored["intent_dicts"]) == 1
        assert restored["intent_dicts"][0]["action_type"] == "post"

    def test_persist_phase_no_state_dir(self):
        mgr = PersistenceManager(state_dir=None)
        mgr.persist_phase_state(0, [], [])
        # No exception = pass

    def test_restore_phase_no_file(self, tmp_path):
        mgr = PersistenceManager(state_dir=tmp_path)
        assert mgr.restore_phase_state() == {}

    def test_restore_phase_wrong_version(self, tmp_path):
        phase_path = tmp_path / "phase_state.json"
        phase_path.write_text(json.dumps({"version": 999}))
        mgr = PersistenceManager(state_dir=tmp_path)
        assert mgr.restore_phase_state() == {}

    def test_caps_seen_ids(self, tmp_path):
        """Seen IDs are capped to max_seen_ids."""
        mgr = PersistenceManager(state_dir=tmp_path, max_seen_ids=5)
        queue = ContentQueue()

        mgr.persist_queue(
            queue=queue,
            seen_message_ids={f"m{i}" for i in range(20)},
            seen_post_ids={f"p{i}" for i in range(20)},
            own_comment_ids=set(),
            commented_post_ids=set(),
            followed_agents=set(),
            subscribed_submolts=set(),
            comment_post_map={},
            own_post_ids={},
        )

        restored = mgr.restore_queue(ContentQueue())
        assert len(restored["seen_message_ids"]) == 5
        assert len(restored["seen_post_ids"]) == 5
