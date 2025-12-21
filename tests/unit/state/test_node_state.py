"""
Unit Tests for NodeState (OPUS-166)

Tests the PULS layer - ephemeral file-based presence for agents.
"""

import json
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

from vibe_core.state.node_state import (
    KalaState,
    MailboxMessage,
    NodeSnapshot,
    NodeState,
    SynapseInfo,
    broadcast_message,
    get_all_alive_nodes,
)


@pytest.fixture
def temp_cartridge():
    """Create a temporary cartridge directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cartridge = Path(tmpdir) / "test_agent"
        cartridge.mkdir()
        yield cartridge


@pytest.fixture
def temp_cartridges_root():
    """Create a temporary cartridges root with multiple agents."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        # Create multiple agent directories
        (root / "agent_a").mkdir()
        (root / "agent_b").mkdir()
        (root / "agent_c").mkdir()
        yield root


class TestNodeStateLifecycle:
    """Tests for NodeState lifecycle (create/pulse/die)."""

    def test_create_node_state(self, temp_cartridge):
        """Test creating a new node.json."""
        snapshot = NodeState.create(temp_cartridge)

        assert snapshot.status == "booting"
        assert snapshot.pulse_at is not None
        assert NodeState.is_alive(temp_cartridge)

        # Verify file exists
        node_path = NodeState.get_path(temp_cartridge)
        assert node_path.exists()

    def test_create_with_custom_status(self, temp_cartridge):
        """Test creating with custom status and metadata."""
        snapshot = NodeState.create(
            temp_cartridge,
            status="initializing",
            metadata={"version": "1.0.0"},
        )

        assert snapshot.status == "initializing"
        assert snapshot.metadata["version"] == "1.0.0"

    def test_pulse_updates_status(self, temp_cartridge):
        """Test pulse updates status and timestamp."""
        NodeState.create(temp_cartridge)

        snapshot = NodeState.pulse(temp_cartridge, status="online")

        assert snapshot.status == "online"
        assert snapshot.pulse_at is not None

    def test_pulse_with_kala_state(self, temp_cartridge):
        """Test pulse with KALA time state."""
        NodeState.create(temp_cartridge)

        kala = {
            "sun_phase": "MIDDAY",
            "moon_phase": "WAXING_GIBBOUS",
            "tithi": 11,
            "paksha": "shukla",
            "rhythm_intensity": 0.78,
        }

        snapshot = NodeState.pulse(temp_cartridge, kala_state=kala)

        assert snapshot.kala.sun_phase == "MIDDAY"
        assert snapshot.kala.moon_phase == "WAXING_GIBBOUS"
        assert snapshot.kala.tithi == 11
        assert snapshot.kala.paksha == "shukla"
        assert snapshot.kala.rhythm_intensity == 0.78

    def test_die_deletes_node(self, temp_cartridge):
        """Test die() deletes node.json."""
        NodeState.create(temp_cartridge)
        assert NodeState.is_alive(temp_cartridge)

        result = NodeState.die(temp_cartridge)

        assert result is True
        assert not NodeState.is_alive(temp_cartridge)

    def test_die_returns_false_if_not_exists(self, temp_cartridge):
        """Test die() returns False if node.json doesn't exist."""
        result = NodeState.die(temp_cartridge)
        assert result is False

    def test_is_alive_false_when_no_file(self, temp_cartridge):
        """Test is_alive() returns False when no node.json."""
        assert not NodeState.is_alive(temp_cartridge)

    def test_read_returns_none_when_not_alive(self, temp_cartridge):
        """Test read() returns None when agent not alive."""
        snapshot = NodeState.read(temp_cartridge)
        assert snapshot is None

    def test_read_returns_snapshot(self, temp_cartridge):
        """Test read() returns valid snapshot."""
        NodeState.create(temp_cartridge, status="testing")

        snapshot = NodeState.read(temp_cartridge)

        assert snapshot is not None
        assert snapshot.status == "testing"


class TestNodeStateMailbox:
    """Tests for mailbox messaging."""

    def test_send_message(self, temp_cartridges_root):
        """Test sending a message to another agent."""
        agent_a = temp_cartridges_root / "agent_a"
        agent_b = temp_cartridges_root / "agent_b"

        # Both agents must be alive
        NodeState.create(agent_a)
        NodeState.create(agent_b)

        # Send message from A to B
        msg = NodeState.send_message(
            from_agent="agent_a",
            to_cartridge=agent_b,
            msg_type="signal",
            payload={"action": "review_required"},
        )

        assert msg is not None
        assert msg.from_agent == "agent_a"
        assert msg.msg_type == "signal"
        assert msg.payload["action"] == "review_required"

    def test_send_message_to_dead_agent_fails(self, temp_cartridges_root):
        """Test sending to dead agent returns None."""
        agent_a = temp_cartridges_root / "agent_a"
        agent_b = temp_cartridges_root / "agent_b"

        # Only A is alive
        NodeState.create(agent_a)

        msg = NodeState.send_message(
            from_agent="agent_a",
            to_cartridge=agent_b,
            msg_type="signal",
            payload={},
        )

        assert msg is None

    def test_read_mailbox(self, temp_cartridges_root):
        """Test reading mailbox messages."""
        agent_a = temp_cartridges_root / "agent_a"
        agent_b = temp_cartridges_root / "agent_b"

        NodeState.create(agent_a)
        NodeState.create(agent_b)

        # Send two messages
        NodeState.send_message("agent_a", agent_b, "signal", {"n": 1})
        NodeState.send_message("agent_a", agent_b, "signal", {"n": 2})

        messages = NodeState.read_mailbox(agent_b)

        assert len(messages) == 2
        assert messages[0].payload["n"] == 1
        assert messages[1].payload["n"] == 2

    def test_ack_message(self, temp_cartridges_root):
        """Test acknowledging a message."""
        agent_a = temp_cartridges_root / "agent_a"
        agent_b = temp_cartridges_root / "agent_b"

        NodeState.create(agent_a)
        NodeState.create(agent_b)

        msg = NodeState.send_message("agent_a", agent_b, "signal", {})

        # Ack the message
        result = NodeState.ack_message(agent_b, msg.id)
        assert result is True

        # Unread messages should be empty
        unread = NodeState.read_mailbox(agent_b, unread_only=True)
        assert len(unread) == 0

        # All messages should include the acked one
        all_msgs = NodeState.read_mailbox(agent_b, unread_only=False)
        assert len(all_msgs) == 1
        assert all_msgs[0].read is True

    def test_clear_mailbox(self, temp_cartridges_root):
        """Test clearing read messages from mailbox."""
        agent_a = temp_cartridges_root / "agent_a"
        agent_b = temp_cartridges_root / "agent_b"

        NodeState.create(agent_a)
        NodeState.create(agent_b)

        # Send and ack one message
        msg1 = NodeState.send_message("agent_a", agent_b, "signal", {"n": 1})
        NodeState.ack_message(agent_b, msg1.id)

        # Send another (unread)
        NodeState.send_message("agent_a", agent_b, "signal", {"n": 2})

        # Clear read messages only
        cleared = NodeState.clear_mailbox(agent_b, read_only=True)

        assert cleared == 1
        remaining = NodeState.read_mailbox(agent_b, unread_only=False)
        assert len(remaining) == 1


class TestNodeStateSynapses:
    """Tests for synapse connections."""

    def test_connect(self, temp_cartridge):
        """Test registering a synapse connection."""
        NodeState.create(temp_cartridge)

        result = NodeState.connect(temp_cartridge, "other_agent")

        assert result is True
        snapshot = NodeState.read(temp_cartridge)
        assert "other_agent" in snapshot.synapses.connected_to

    def test_disconnect(self, temp_cartridge):
        """Test removing a synapse connection."""
        NodeState.create(temp_cartridge)
        NodeState.connect(temp_cartridge, "other_agent")

        result = NodeState.disconnect(temp_cartridge, "other_agent")

        assert result is True
        snapshot = NodeState.read(temp_cartridge)
        assert "other_agent" not in snapshot.synapses.connected_to

    def test_disconnect_nonexistent(self, temp_cartridge):
        """Test disconnecting non-existent connection."""
        NodeState.create(temp_cartridge)

        result = NodeState.disconnect(temp_cartridge, "nonexistent")
        assert result is False


class TestNodeStateDiscovery:
    """Tests for node discovery functions."""

    def test_get_all_alive_nodes(self, temp_cartridges_root):
        """Test discovering all alive nodes."""
        # Create some alive agents
        NodeState.create(temp_cartridges_root / "agent_a")
        NodeState.create(temp_cartridges_root / "agent_b")
        # agent_c stays dead

        alive = get_all_alive_nodes(temp_cartridges_root)

        assert len(alive) == 2
        names = [p.name for p in alive]
        assert "agent_a" in names
        assert "agent_b" in names
        assert "agent_c" not in names

    def test_broadcast_message(self, temp_cartridges_root):
        """Test broadcasting message to all alive agents."""
        # Create alive agents
        NodeState.create(temp_cartridges_root / "agent_a")
        NodeState.create(temp_cartridges_root / "agent_b")
        NodeState.create(temp_cartridges_root / "agent_c")

        # Broadcast from A (excluding A)
        sent = broadcast_message(
            from_agent="agent_a",
            cartridges_root=temp_cartridges_root,
            msg_type="broadcast",
            payload={"announcement": "hello"},
            exclude=["agent_a"],
        )

        assert sent == 2  # B and C

        # Check B and C have messages
        msgs_b = NodeState.read_mailbox(temp_cartridges_root / "agent_b")
        msgs_c = NodeState.read_mailbox(temp_cartridges_root / "agent_c")

        assert len(msgs_b) == 1
        assert len(msgs_c) == 1
        assert msgs_b[0].payload["announcement"] == "hello"


class TestNodeSnapshotSerialization:
    """Tests for NodeSnapshot serialization."""

    def test_to_dict(self):
        """Test converting snapshot to dict."""
        snapshot = NodeSnapshot(
            status="online",
            pulse_at="2024-12-20T10:00:00Z",
            kala=KalaState(sun_phase="MIDDAY"),
            mailbox=[],
            synapses=SynapseInfo(),
        )

        data = snapshot.to_dict()

        assert data["status"] == "online"
        assert data["kala"]["sun_phase"] == "MIDDAY"

    def test_from_dict(self):
        """Test creating snapshot from dict."""
        data = {
            "status": "busy",
            "pulse_at": "2024-12-20T10:00:00Z",
            "kala": {"sun_phase": "SUNSET", "moon_phase": "FULL_MOON"},
            "mailbox": [],
            "synapses": {"connected_to": ["agent_x"]},
        }

        snapshot = NodeSnapshot.from_dict(data)

        assert snapshot.status == "busy"
        assert snapshot.kala.sun_phase == "SUNSET"
        assert "agent_x" in snapshot.synapses.connected_to


class TestGAD000Compliance:
    """Tests for GAD-000 compliance."""

    def test_get_capabilities(self):
        """Test GAD-000 capability discovery."""
        caps = NodeState.get_capabilities()

        assert "operations" in caps
        assert "persistent" in caps
        assert caps["persistent"] is False
        assert "create" in caps["operations"]
        assert "pulse" in caps["operations"]
        assert "die" in caps["operations"]
