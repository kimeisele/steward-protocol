"""
E2E Tests for NodePulse Plugin (OPUS-166)

Tests the full lifecycle:
1. Boot creates node.json files
2. Pulse updates with KALA state
3. Shutdown deletes node.json files
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from vibe_core.plugins.node_pulse.plugin_main import NodePulsePlugin
from vibe_core.state.node_state import NodeState


@pytest.fixture
def temp_project():
    """Create a temporary project structure with cartridges."""
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Create cartridge structure
        agent_city = root / "vibe_core" / "cartridges" / "agent_city"
        system = root / "vibe_core" / "cartridges" / "system"
        agent_city.mkdir(parents=True)
        system.mkdir(parents=True)

        # Create agent_city cartridges
        for name in ["dharma", "envoy", "librarian"]:
            cart = agent_city / name
            cart.mkdir()
            (cart / "steward.json").write_text(json.dumps({"agent_id": name}))

        # Create system cartridges
        for name in ["archivist", "herald"]:
            cart = system / name
            cart.mkdir()
            (cart / "steward.json").write_text(json.dumps({"agent_id": name}))

        yield root


@pytest.fixture
def mock_kernel():
    """Create a mock kernel."""
    kernel = MagicMock()
    kernel.plugin_loader = MagicMock()
    kernel.plugin_loader.get_active_plugins.return_value = []
    return kernel


@pytest.fixture
def mock_transaction():
    """Create a mock pulse transaction."""
    return MagicMock()


class TestNodePulseLifecycle:
    """E2E tests for complete node.json lifecycle."""

    def test_boot_creates_node_json(self, temp_project, mock_kernel):
        """Test that on_boot creates node.json for all cartridges."""
        plugin = NodePulsePlugin()

        with patch.object(Path, "cwd", return_value=temp_project):
            plugin.on_boot(mock_kernel)

        # Check all cartridges have node.json
        expected_cartridges = ["dharma", "envoy", "librarian", "archivist", "herald"]
        for name in expected_cartridges:
            # Find the cartridge path
            for subdir in ["agent_city", "system"]:
                path = temp_project / "vibe_core" / "cartridges" / subdir / name
                if path.exists():
                    assert NodeState.is_alive(path), f"{name} should be alive"
                    snapshot = NodeState.read(path)
                    assert snapshot.status == "online"

    def test_pulse_updates_node_json(self, temp_project, mock_kernel, mock_transaction):
        """Test that on_pulse updates node.json with KALA state."""
        plugin = NodePulsePlugin()

        # Mock KALA plugin
        mock_kala = MagicMock()
        mock_kala.plugin_id = "kala"
        mock_kala.get_current_state.return_value = {
            "sun_phase": "MIDDAY",
            "moon_phase": "WAXING_GIBBOUS",
            "tithi": 11,
            "paksha": "shukla",
            "rhythm_intensity": 0.78,
        }
        mock_kernel.plugin_loader.get_active_plugins.return_value = [mock_kala]

        with patch.object(Path, "cwd", return_value=temp_project):
            plugin.on_boot(mock_kernel)
            result = plugin.on_pulse(mock_kernel, mock_transaction)

        from vibe_core.plugin_protocol import PluginResult

        assert result.status == PluginResult.OK

        # Check KALA state was written
        dharma_path = temp_project / "vibe_core" / "cartridges" / "agent_city" / "dharma"
        snapshot = NodeState.read(dharma_path)

        assert snapshot.kala.sun_phase == "MIDDAY"
        assert snapshot.kala.moon_phase == "WAXING_GIBBOUS"
        assert snapshot.kala.tithi == 11

    def test_shutdown_deletes_node_json(self, temp_project, mock_kernel):
        """Test that on_shutdown deletes all node.json files."""
        plugin = NodePulsePlugin()

        with patch.object(Path, "cwd", return_value=temp_project):
            # Boot first
            plugin.on_boot(mock_kernel)

            # Verify nodes exist
            dharma_path = temp_project / "vibe_core" / "cartridges" / "agent_city" / "dharma"
            assert NodeState.is_alive(dharma_path)

            # Shutdown
            plugin.on_shutdown(mock_kernel)

        # All nodes should be dead
        for subdir in ["agent_city", "system"]:
            cartridge_dir = temp_project / "vibe_core" / "cartridges" / subdir
            if cartridge_dir.exists():
                for cart in cartridge_dir.iterdir():
                    if cart.is_dir():
                        assert not NodeState.is_alive(cart), f"{cart.name} should be offline"

    def test_full_lifecycle(self, temp_project, mock_kernel, mock_transaction):
        """Test complete boot -> pulse -> shutdown lifecycle."""
        plugin = NodePulsePlugin()

        # Mock KALA
        mock_kala = MagicMock()
        mock_kala.plugin_id = "kala"
        mock_kala.get_current_state.return_value = {"sun_phase": "SUNSET"}
        mock_kernel.plugin_loader.get_active_plugins.return_value = [mock_kala]

        with patch.object(Path, "cwd", return_value=temp_project):
            # 1. BOOT
            plugin.on_boot(mock_kernel)

            # All should be online
            status = plugin.get_status()
            assert status["cartridges_total"] == 5
            assert status["cartridges_alive"] == 5

            # 2. PULSE (multiple)
            for _ in range(3):
                plugin.on_pulse(mock_kernel, mock_transaction)

            assert plugin._pulse_count == 3

            # 3. SHUTDOWN
            plugin.on_shutdown(mock_kernel)

            # All should be offline
            status_after = plugin.get_status()
            assert status_after["cartridges_alive"] == 0


class TestNodePulseWithKALA:
    """Tests for KALA integration."""

    def test_pulse_without_kala(self, temp_project, mock_kernel, mock_transaction):
        """Test pulse works even without KALA plugin."""
        plugin = NodePulsePlugin()

        # No KALA plugin
        mock_kernel.plugin_loader.get_active_plugins.return_value = []

        with patch.object(Path, "cwd", return_value=temp_project):
            plugin.on_boot(mock_kernel)
            result = plugin.on_pulse(mock_kernel, mock_transaction)

        from vibe_core.plugin_protocol import PluginResult

        assert result.status == PluginResult.OK
        assert result.data["kala_state"] == {}  # Empty state

    def test_kala_state_propagates_to_all_nodes(self, temp_project, mock_kernel, mock_transaction):
        """Test KALA state is written to all node.json files."""
        plugin = NodePulsePlugin()

        mock_kala = MagicMock()
        mock_kala.plugin_id = "kala"
        mock_kala.get_current_state.return_value = {
            "sun_phase": "BRAHMA_MUHURTA",
            "is_day": True,
        }
        mock_kernel.plugin_loader.get_active_plugins.return_value = [mock_kala]

        with patch.object(Path, "cwd", return_value=temp_project):
            plugin.on_boot(mock_kernel)
            plugin.on_pulse(mock_kernel, mock_transaction)

        # Check all nodes have KALA state
        for path in plugin._cartridge_paths:
            snapshot = NodeState.read(path)
            assert snapshot.kala.sun_phase == "BRAHMA_MUHURTA"


class TestNodePulseMessaging:
    """Tests for inter-agent messaging via node.json."""

    def test_send_message_between_agents(self, temp_project, mock_kernel):
        """Test sending a message from one agent to another."""
        plugin = NodePulsePlugin()

        with patch.object(Path, "cwd", return_value=temp_project):
            plugin.on_boot(mock_kernel)

        # Send message from dharma to envoy
        dharma = temp_project / "vibe_core" / "cartridges" / "agent_city" / "dharma"
        envoy = temp_project / "vibe_core" / "cartridges" / "agent_city" / "envoy"

        msg = NodeState.send_message(
            from_agent="dharma",
            to_cartridge=envoy,
            msg_type="signal",
            payload={"guidance": "check_karma"},
        )

        assert msg is not None
        assert msg.from_agent == "dharma"

        # Read mailbox
        messages = NodeState.read_mailbox(envoy)
        assert len(messages) == 1
        assert messages[0].payload["guidance"] == "check_karma"

    def test_broadcast_to_all_agents(self, temp_project, mock_kernel):
        """Test broadcasting a message to all agents."""
        plugin = NodePulsePlugin()

        with patch.object(Path, "cwd", return_value=temp_project):
            plugin.on_boot(mock_kernel)

        from vibe_core.state.node_state import broadcast_message

        # Broadcast from herald to all
        cartridges_root = temp_project / "vibe_core" / "cartridges"
        sent = broadcast_message(
            from_agent="herald",
            cartridges_root=cartridges_root,
            msg_type="broadcast",
            payload={"announcement": "system_update"},
            exclude=["herald"],
        )

        # Should send to 4 agents (5 total - 1 excluded)
        assert sent == 4


class TestNodePulseEdgeCases:
    """Edge case tests."""

    def test_handles_missing_cartridge_dirs(self, mock_kernel):
        """Test handles missing cartridge directories gracefully."""
        plugin = NodePulsePlugin()

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            # Don't create cartridge dirs

            with patch.object(Path, "cwd", return_value=root):
                plugin.on_boot(mock_kernel)

            assert len(plugin._cartridge_paths) == 0

    def test_handles_cartridge_without_steward_json(self, temp_project, mock_kernel):
        """Test skips directories without steward.json."""
        # Create a directory without steward.json
        invalid = temp_project / "vibe_core" / "cartridges" / "agent_city" / "invalid"
        invalid.mkdir()
        # No steward.json

        plugin = NodePulsePlugin()

        with patch.object(Path, "cwd", return_value=temp_project):
            plugin.on_boot(mock_kernel)

        # Invalid should not be in the list
        cart_names = [p.name for p in plugin._cartridge_paths]
        assert "invalid" not in cart_names
