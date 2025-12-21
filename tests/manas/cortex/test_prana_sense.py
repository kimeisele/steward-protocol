"""
Tests for PranaSense (OPUS-166)

Tests the agent presence awareness cortex module.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from vibe_core.plugins.opus_assistant.manas.cortex.prana_sense import (
    AgentPresence,
    PranaSense,
    PresenceChange,
)
from vibe_core.state.node_state import NodeState


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace with cartridge structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Create cartridge structure
        agent_city = root / "vibe_core" / "cartridges" / "agent_city"
        system = root / "vibe_core" / "cartridges" / "system"
        agent_city.mkdir(parents=True)
        system.mkdir(parents=True)

        # Create cartridges
        for name in ["dharma", "envoy", "librarian"]:
            cart = agent_city / name
            cart.mkdir()
            (cart / "steward.json").write_text(json.dumps({"agent_id": name}))

        for name in ["archivist", "herald"]:
            cart = system / name
            cart.mkdir()
            (cart / "steward.json").write_text(json.dumps({"agent_id": name}))

        yield root


class TestPranaSenseBasics:
    """Basic PranaSense tests."""

    def test_init_discovers_cartridges(self, temp_workspace):
        """Test that PranaSense discovers cartridges on init."""
        sense = PranaSense(workspace=temp_workspace)

        assert len(sense._known_cartridges) == 5
        assert "dharma" in sense._known_cartridges
        assert "envoy" in sense._known_cartridges
        assert "archivist" in sense._known_cartridges

    def test_name_property(self, temp_workspace):
        """Test sense name property."""
        sense = PranaSense(workspace=temp_workspace)
        assert sense.name == "prana_sense"


class TestPranaSensePerception:
    """Tests for perceive() method."""

    def test_perceive_all_dead(self, temp_workspace):
        """Test perception when all agents are dead (no node.json)."""
        sense = PranaSense(workspace=temp_workspace)

        perception = sense.perceive()

        assert perception.total_registered == 5
        assert perception.total_alive == 0
        assert perception.total_dead == 5
        assert len(perception.alive_agents) == 0
        assert len(perception.dead_agents) == 5

    def test_perceive_some_alive(self, temp_workspace):
        """Test perception when some agents are alive."""
        sense = PranaSense(workspace=temp_workspace)

        # Make dharma and envoy alive
        dharma_path = temp_workspace / "vibe_core" / "cartridges" / "agent_city" / "dharma"
        envoy_path = temp_workspace / "vibe_core" / "cartridges" / "agent_city" / "envoy"

        NodeState.create(dharma_path, status="online")
        NodeState.create(envoy_path, status="online")

        perception = sense.perceive()

        assert perception.total_alive == 2
        assert perception.total_dead == 3
        assert {a.agent_id for a in perception.alive_agents} == {"dharma", "envoy"}

    def test_perceive_detects_births(self, temp_workspace):
        """Test that perceive detects agent births."""
        sense = PranaSense(workspace=temp_workspace)

        # First perceive - all dead
        p1 = sense.perceive()
        assert p1.total_alive == 0
        assert len(p1.births) == 0

        # Create dharma's node.json (birth)
        dharma_path = temp_workspace / "vibe_core" / "cartridges" / "agent_city" / "dharma"
        NodeState.create(dharma_path, status="online")

        # Second perceive - should detect birth
        p2 = sense.perceive()
        assert p2.total_alive == 1
        assert "dharma" in p2.births

    def test_perceive_detects_deaths(self, temp_workspace):
        """Test that perceive detects agent deaths."""
        sense = PranaSense(workspace=temp_workspace)

        # Create dharma
        dharma_path = temp_workspace / "vibe_core" / "cartridges" / "agent_city" / "dharma"
        NodeState.create(dharma_path, status="online")

        # First perceive - dharma alive
        p1 = sense.perceive()
        assert p1.total_alive == 1

        # Kill dharma
        NodeState.die(dharma_path)

        # Second perceive - should detect death
        p2 = sense.perceive()
        assert p2.total_alive == 0
        assert "dharma" in p2.deaths


class TestPranaSenseHelpers:
    """Tests for helper methods."""

    def test_get_alive_agents(self, temp_workspace):
        """Test get_alive_agents method."""
        sense = PranaSense(workspace=temp_workspace)

        # Initially all dead
        assert sense.get_alive_agents() == []

        # Make some alive
        dharma_path = temp_workspace / "vibe_core" / "cartridges" / "agent_city" / "dharma"
        NodeState.create(dharma_path)

        alive = sense.get_alive_agents()
        assert "dharma" in alive

    def test_get_dead_agents(self, temp_workspace):
        """Test get_dead_agents method."""
        sense = PranaSense(workspace=temp_workspace)

        # All should be dead initially
        dead = sense.get_dead_agents()
        assert len(dead) == 5

    def test_is_agent_alive(self, temp_workspace):
        """Test is_agent_alive method."""
        sense = PranaSense(workspace=temp_workspace)

        dharma_path = temp_workspace / "vibe_core" / "cartridges" / "agent_city" / "dharma"

        # Initially dead
        assert not sense.is_agent_alive("dharma")

        # Make alive
        NodeState.create(dharma_path)
        assert sense.is_agent_alive("dharma")

        # Kill
        NodeState.die(dharma_path)
        assert not sense.is_agent_alive("dharma")

    def test_get_agent_presence(self, temp_workspace):
        """Test get_agent_presence method."""
        sense = PranaSense(workspace=temp_workspace)

        dharma_path = temp_workspace / "vibe_core" / "cartridges" / "agent_city" / "dharma"

        # Dead agent
        presence = sense.get_agent_presence("dharma")
        assert presence is not None
        assert not presence.is_alive
        assert presence.status == "offline"

        # Make alive
        NodeState.create(dharma_path, status="online")
        presence = sense.get_agent_presence("dharma")
        assert presence.is_alive
        assert presence.status == "online"

    def test_unknown_agent(self, temp_workspace):
        """Test querying unknown agent."""
        sense = PranaSense(workspace=temp_workspace)

        assert not sense.is_agent_alive("unknown_agent")
        assert sense.get_agent_presence("unknown_agent") is None


class TestShrutaSenseIntegration:
    """Tests for ShrutaSense integration."""

    def test_handle_vibration_node_json_created(self, temp_workspace):
        """Test handling node.json creation vibration."""
        sense = PranaSense(workspace=temp_workspace)

        # Mock a vibration
        vibration = MagicMock()
        vibration.path = temp_workspace / "vibe_core" / "cartridges" / "agent_city" / "dharma" / "node.json"
        vibration.event_type = "created"

        change = sense.handle_vibration(vibration)

        assert change is not None
        assert change.agent_id == "dharma"
        assert change.change_type == "birth"

    def test_handle_vibration_node_json_deleted(self, temp_workspace):
        """Test handling node.json deletion vibration."""
        sense = PranaSense(workspace=temp_workspace)

        vibration = MagicMock()
        vibration.path = temp_workspace / "vibe_core" / "cartridges" / "agent_city" / "envoy" / "node.json"
        vibration.event_type = "deleted"

        change = sense.handle_vibration(vibration)

        assert change is not None
        assert change.agent_id == "envoy"
        assert change.change_type == "death"

    def test_handle_vibration_ignores_non_node_json(self, temp_workspace):
        """Test that non-node.json vibrations are ignored."""
        sense = PranaSense(workspace=temp_workspace)

        vibration = MagicMock()
        vibration.path = temp_workspace / "vibe_core" / "cartridges" / "agent_city" / "dharma" / "steward.json"
        vibration.event_type = "modified"

        change = sense.handle_vibration(vibration)

        assert change is None

    def test_register_with_shruta(self, temp_workspace):
        """Test registering with ShrutaSense."""
        sense = PranaSense(workspace=temp_workspace)

        mock_shruta = MagicMock()

        sense.register_with_shruta(mock_shruta)

        mock_shruta.add_handler.assert_called_once_with(sense.handle_vibration)


class TestPresenceWithKalaState:
    """Tests for KALA state in presence."""

    def test_presence_includes_kala_state(self, temp_workspace):
        """Test that presence includes KALA time state."""
        sense = PranaSense(workspace=temp_workspace)

        dharma_path = temp_workspace / "vibe_core" / "cartridges" / "agent_city" / "dharma"

        kala = {
            "sun_phase": "MIDDAY",
            "moon_phase": "FULL_MOON",
            "tithi": 15,
        }
        NodeState.pulse(dharma_path, status="online", kala_state=kala)

        perception = sense.perceive()

        dharma = next(a for a in perception.alive_agents if a.agent_id == "dharma")
        assert dharma.kala_state is not None
        assert dharma.kala_state["sun_phase"] == "MIDDAY"


class TestMailboxAwareness:
    """Tests for mailbox awareness."""

    def test_presence_shows_unread_messages(self, temp_workspace):
        """Test that presence shows unread message count."""
        sense = PranaSense(workspace=temp_workspace)

        dharma_path = temp_workspace / "vibe_core" / "cartridges" / "agent_city" / "dharma"
        envoy_path = temp_workspace / "vibe_core" / "cartridges" / "agent_city" / "envoy"

        NodeState.create(dharma_path)
        NodeState.create(envoy_path)

        # Send message to dharma
        NodeState.send_message("envoy", dharma_path, "signal", {"test": True})
        NodeState.send_message("envoy", dharma_path, "signal", {"test": True})

        perception = sense.perceive()

        dharma = next(a for a in perception.alive_agents if a.agent_id == "dharma")
        assert dharma.mailbox_count == 2
