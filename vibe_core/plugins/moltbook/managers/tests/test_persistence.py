"""Tests for PersistenceManager — extracted from plugin_main.py."""

import json
from unittest.mock import MagicMock, patch

from vibe_core.plugins.moltbook.managers.persistence import (
    PersistenceManager,
    _governed_write,
)
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


class TestGovernedWrite:
    """_governed_write routes through EnforceGateProvider when available."""

    def test_uses_gate_when_available(self, tmp_path):
        """Governed write calls gate.write() with correct args."""
        mock_gate = MagicMock()
        mock_result = MagicMock()
        mock_result.success = True
        mock_gate.write.return_value = mock_result

        with patch(
            "vibe_core.plugins.moltbook.managers.persistence.get_sync_gate",
            create=True,
        ) as mock_get_gate:
            # Patch the lazy import inside _governed_write
            with patch.dict(
                "sys.modules",
                {
                    "vibe_core.mahamantra.substrate.vm.gate_providers": MagicMock(
                        get_sync_gate=lambda: mock_gate,
                    ),
                },
            ):
                _governed_write(
                    "test_file.json",
                    {"key": "value"},
                    tmp_path / "test_file.json",
                    actor="test_actor",
                )

        # Gate should have been called
        mock_gate.write.assert_called_once()
        call_args = mock_gate.write.call_args
        assert call_args[0][0] == "test_file.json"
        assert call_args[0][1] == {"key": "value"}
        assert call_args[1]["actor"] == "test_actor"

    def test_falls_back_when_gate_unavailable(self, tmp_path):
        """When gate import fails, falls back to direct Path.write_text."""
        target = tmp_path / "fallback.json"
        data = {"fallback": True}

        # Ensure the import fails by patching to raise
        with patch.dict("sys.modules", {"vibe_core.mahamantra.substrate.vm.gate_providers": None}):
            _governed_write("fallback.json", data, target, actor="test")

        assert target.exists()
        written = json.loads(target.read_text())
        assert written["fallback"] is True

    def test_gate_blocked_falls_back_to_direct_write(self, tmp_path):
        """When gate blocks the write, fallback to direct write (state > policy)."""
        mock_gate = MagicMock()
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.reason = "POLICY_DENIED"
        mock_gate.write.return_value = mock_result

        target = tmp_path / "blocked.json"

        with patch.dict(
            "sys.modules",
            {
                "vibe_core.mahamantra.substrate.vm.gate_providers": MagicMock(
                    get_sync_gate=lambda: mock_gate,
                ),
            },
        ):
            _governed_write("blocked.json", {"data": 1}, target, actor="test")

        # File SHOULD exist — gate blocked but fallback direct write fires
        assert target.exists()


class TestGovernedPersistence:
    """PersistenceManager uses _governed_write for all state writes."""

    def test_persist_queue_writes_files(self, tmp_path):
        """persist_queue produces correct state files (via fallback in test)."""
        mgr = PersistenceManager(state_dir=tmp_path)
        queue = ContentQueue()
        queue.enqueue({"content_type": "post", "content": "hello", "priority": 1})

        mgr.persist_queue(
            queue=queue,
            seen_message_ids={"m1"},
            seen_post_ids={"p1"},
            own_comment_ids=set(),
            commented_post_ids=set(),
            followed_agents=set(),
            subscribed_submolts=set(),
            comment_post_map={},
            own_post_ids={},
        )

        # Both files created via _governed_write fallback
        assert (tmp_path / "content_queue.json").exists()
        assert (tmp_path / "seen_ids.json").exists()

    def test_persist_phase_state_writes_file(self, tmp_path):
        """persist_phase_state produces phase_state.json."""
        mgr = PersistenceManager(state_dir=tmp_path)
        mgr.persist_phase_state(
            heartbeat_count=10,
            feed_topics=[{"title": "test"}],
            intents=[],
        )

        assert (tmp_path / "phase_state.json").exists()
        data = json.loads((tmp_path / "phase_state.json").read_text())
        assert data["heartbeat_count"] == 10

    def test_restore_unaffected_by_governance(self, tmp_path):
        """Reads are direct (SATTVA) — governance doesn't affect restore."""
        # Write state directly (simulating previous session)
        queue_data = {
            "version": 1,
            "proposals": [{"content_type": "post", "content": "hi", "priority": 1}],
            "stats": {"total_enqueued": 1, "total_drained": 0, "total_dropped": 0},
        }
        (tmp_path / "content_queue.json").write_text(json.dumps(queue_data))

        seen_data = {
            "version": 5,
            "message_ids": ["m1"],
            "post_ids": ["p1"],
            "own_comment_ids": [],
            "commented_post_ids": [],
            "followed_agents": [],
            "subscribed_submolts": [],
            "comment_post_map": {},
            "own_post_ids": {},
        }
        (tmp_path / "seen_ids.json").write_text(json.dumps(seen_data))

        mgr = PersistenceManager(state_dir=tmp_path)
        queue = ContentQueue()
        restored = mgr.restore_queue(queue)

        assert queue.size == 1
        assert restored["seen_message_ids"] == {"m1"}
        assert restored["seen_post_ids"] == {"p1"}
