"""
E2E Tests for NodePulse Plugin (OPUS-166)

Tests the LASAGNE architecture:
1. Layer 4 (Runtime): Agent boot calls ensure_presence()
2. Pulse updates all registered agents with KALA state
3. Shutdown calls release_presence() on all agents
4. Self-healing: if node.json deleted, next pulse recreates it
"""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from vibe_core.plugins.node_pulse.plugin_main import NodePulsePlugin
from vibe_core.protocols.agent import VibeAgent
from vibe_core.state.node_state import NodeState


class MockCartridgeAgent(VibeAgent):
    """Mock agent with a known cartridge path for testing."""

    def __init__(self, agent_id: str, cartridge_path: Path):
        super().__init__(agent_id=agent_id, name=f"Test {agent_id}")
        self._test_cartridge_path = cartridge_path

    def process(self, task):
        return {"status": "ok"}

    def get_cartridge_path(self) -> Path:
        """Override to return test path."""
        return self._test_cartridge_path


@pytest.fixture
def temp_cartridges():
    """Create temporary cartridge directories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Create cartridge directories
        cartridges = {}
        for name in ["dharma", "envoy", "librarian"]:
            path = root / name
            path.mkdir()
            (path / "steward.json").write_text(json.dumps({"agent_id": name}))
            cartridges[name] = path

        yield cartridges


@pytest.fixture
def mock_agents(temp_cartridges):
    """Create mock agents with cartridge paths."""
    agents = {}
    for name, path in temp_cartridges.items():
        agents[name] = MockCartridgeAgent(name, path)
    return agents


@pytest.fixture
def mock_kernel(mock_agents):
    """Create a mock kernel with agent_registry."""
    kernel = MagicMock()
    kernel.agent_registry = mock_agents
    kernel.plugin_loader = MagicMock()
    kernel.plugin_loader.get_active_plugins.return_value = []
    return kernel


@pytest.fixture
def mock_transaction():
    """Create a mock pulse transaction."""
    return MagicMock()


class TestVibeAgentPresence:
    """Tests for VibeAgent presence methods."""

    def test_ensure_presence_creates_node_json(self, temp_cartridges):
        """Test that ensure_presence creates node.json."""
        agent = MockCartridgeAgent("dharma", temp_cartridges["dharma"])

        result = agent.ensure_presence(status="online")

        assert result is True
        assert NodeState.is_alive(temp_cartridges["dharma"])

    def test_release_presence_deletes_node_json(self, temp_cartridges):
        """Test that release_presence deletes node.json."""
        agent = MockCartridgeAgent("dharma", temp_cartridges["dharma"])
        agent.ensure_presence()

        result = agent.release_presence()

        assert result is True
        assert not NodeState.is_alive(temp_cartridges["dharma"])

    def test_set_kernel_calls_ensure_presence(self, temp_cartridges):
        """Test that set_kernel automatically calls ensure_presence."""
        agent = MockCartridgeAgent("dharma", temp_cartridges["dharma"])
        mock_kernel = MagicMock()

        agent.set_kernel(mock_kernel)

        # Agent should be alive after set_kernel
        assert NodeState.is_alive(temp_cartridges["dharma"])

    def test_ensure_presence_with_kala_state(self, temp_cartridges):
        """Test that ensure_presence includes KALA state."""
        agent = MockCartridgeAgent("dharma", temp_cartridges["dharma"])

        kala = {
            "sun_phase": "MIDDAY",
            "moon_phase": "FULL_MOON",
            "tithi": 15,
        }
        agent.ensure_presence(status="online", kala_state=kala)

        snapshot = NodeState.read(temp_cartridges["dharma"])
        assert snapshot.kala.sun_phase == "MIDDAY"
        assert snapshot.kala.moon_phase == "FULL_MOON"


class TestNodePulseWithRegistry:
    """Tests for NodePulsePlugin using kernel.agent_registry."""

    def test_on_boot_counts_registered_agents(self, mock_kernel):
        """Test that on_boot counts agents from registry."""
        plugin = NodePulsePlugin()

        plugin.on_boot(mock_kernel)

        status = plugin.get_status()
        assert status["agents_registered"] == 3  # dharma, envoy, librarian

    def test_on_pulse_updates_all_agents(self, mock_kernel, mock_transaction, temp_cartridges):
        """Test that on_pulse updates all registered agents."""
        plugin = NodePulsePlugin()
        plugin.on_boot(mock_kernel)

        result = plugin.on_pulse(mock_kernel, mock_transaction)

        from vibe_core.plugin_protocol import PluginResult

        assert result.status == PluginResult.OK
        assert result.data["agents_updated"] == 3

        # All agents should be alive
        for path in temp_cartridges.values():
            assert NodeState.is_alive(path)

    def test_on_pulse_with_kala_state(self, mock_kernel, mock_transaction, temp_cartridges):
        """Test that on_pulse propagates KALA state to all agents."""
        # Mock KALA plugin
        mock_kala = MagicMock()
        mock_kala.plugin_id = "kala"
        mock_kala.get_current_state.return_value = {
            "sun_phase": "SUNSET",
            "moon_phase": "NEW_MOON",
            "tithi": 1,
            "paksha": "shukla",
            "rhythm_intensity": 0.5,
        }
        mock_kernel.plugin_loader.get_active_plugins.return_value = [mock_kala]

        plugin = NodePulsePlugin()
        plugin.on_boot(mock_kernel)
        plugin.on_pulse(mock_kernel, mock_transaction)

        # Check KALA state was written
        snapshot = NodeState.read(temp_cartridges["dharma"])
        assert snapshot.kala.sun_phase == "SUNSET"

    def test_on_shutdown_releases_all_agents(self, mock_kernel, mock_transaction, temp_cartridges):
        """Test that on_shutdown releases all agent presence."""
        plugin = NodePulsePlugin()
        plugin.on_boot(mock_kernel)
        plugin.on_pulse(mock_kernel, mock_transaction)

        # All should be alive
        for path in temp_cartridges.values():
            assert NodeState.is_alive(path)

        plugin.on_shutdown(mock_kernel)

        # All should be dead
        for path in temp_cartridges.values():
            assert not NodeState.is_alive(path)


class TestSelfHealing:
    """Tests for self-healing behavior."""

    def test_deleted_node_recreated_on_pulse(self, mock_kernel, mock_transaction, temp_cartridges):
        """Test that deleted node.json is recreated on next pulse."""
        plugin = NodePulsePlugin()
        plugin.on_boot(mock_kernel)
        plugin.on_pulse(mock_kernel, mock_transaction)

        dharma_path = temp_cartridges["dharma"]

        # Verify alive
        assert NodeState.is_alive(dharma_path)

        # Simulate user deleting node.json
        NodeState.die(dharma_path)
        assert not NodeState.is_alive(dharma_path)

        # Next pulse should recreate it (self-healing!)
        plugin.on_pulse(mock_kernel, mock_transaction)

        assert NodeState.is_alive(dharma_path)

    def test_multiple_deletes_heal_repeatedly(self, mock_kernel, mock_transaction, temp_cartridges):
        """Test that multiple deletes are all healed."""
        plugin = NodePulsePlugin()
        plugin.on_boot(mock_kernel)

        dharma_path = temp_cartridges["dharma"]

        for _ in range(3):
            plugin.on_pulse(mock_kernel, mock_transaction)
            assert NodeState.is_alive(dharma_path)

            # Delete
            NodeState.die(dharma_path)
            assert not NodeState.is_alive(dharma_path)

        # Final pulse heals
        plugin.on_pulse(mock_kernel, mock_transaction)
        assert NodeState.is_alive(dharma_path)


class TestMessaging:
    """Tests for inter-agent messaging via node.json."""

    def test_send_message_between_agents(self, mock_kernel, mock_transaction, temp_cartridges):
        """Test sending a message from one agent to another."""
        plugin = NodePulsePlugin()
        plugin.on_boot(mock_kernel)
        plugin.on_pulse(mock_kernel, mock_transaction)

        dharma = temp_cartridges["dharma"]
        envoy = temp_cartridges["envoy"]

        # Send message
        msg = NodeState.send_message(
            from_agent="dharma",
            to_cartridge=envoy,
            msg_type="signal",
            payload={"action": "review"},
        )

        assert msg is not None

        # Read mailbox
        messages = NodeState.read_mailbox(envoy)
        assert len(messages) == 1
        assert messages[0].payload["action"] == "review"


class TestEdgeCases:
    """Edge case tests."""

    def test_agent_without_cartridge_path(self, mock_kernel, mock_transaction):
        """Test agent that can't determine its cartridge path."""

        class PathlessAgent(VibeAgent):
            def process(self, task):
                return {}

            def get_cartridge_path(self):
                return None  # Can't determine path

        mock_kernel.agent_registry = {"pathless": PathlessAgent("pathless", "Pathless")}

        plugin = NodePulsePlugin()
        plugin.on_boot(mock_kernel)
        result = plugin.on_pulse(mock_kernel, mock_transaction)

        # Should not error, just skip this agent
        assert result.data["agents_updated"] == 0
        assert result.data["errors"] == 0

    def test_empty_registry(self, mock_transaction):
        """Test with no registered agents."""
        empty_kernel = MagicMock()
        empty_kernel.agent_registry = {}
        empty_kernel.plugin_loader = MagicMock()
        empty_kernel.plugin_loader.get_active_plugins.return_value = []

        plugin = NodePulsePlugin()
        plugin.on_boot(empty_kernel)
        result = plugin.on_pulse(empty_kernel, mock_transaction)

        assert result.data["agents_updated"] == 0
