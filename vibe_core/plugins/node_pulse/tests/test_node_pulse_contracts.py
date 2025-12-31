"""
TEST: NodePulsePlugin Contract Tests
=====================================
Target: vibe_core/plugins/node_pulse/plugin_main.py
Standard: GAD-5000 (Plugin Contract Testing)

Tests verify:
1. Plugin identity and protocol compliance
2. on_boot lifecycle behavior
3. on_pulse behavior (KALA state updates)
4. on_shutdown behavior (presence release)
5. Agent registry integration
6. Status reporting
"""

from unittest.mock import MagicMock, patch

import pytest

from vibe_core.plugin_protocol import HookResult, KernelPlugin, PluginResult, PulsePhase
from vibe_core.plugins.node_pulse.plugin_main import NodePulsePlugin


class TestNodePulsePluginInit:
    """Test plugin initialization and identity."""

    def test_plugin_can_be_instantiated(self):
        """Plugin should instantiate without errors."""
        plugin = NodePulsePlugin()
        assert plugin is not None

    def test_plugin_has_correct_id(self):
        """Plugin ID should be 'node_pulse'."""
        plugin = NodePulsePlugin()
        assert plugin.plugin_id == "node_pulse"

    def test_plugin_has_priority(self):
        """Plugin should have priority 4 (after KALA)."""
        plugin = NodePulsePlugin()
        assert plugin.priority == 4

    def test_plugin_has_pulse_phase(self):
        """Plugin should run in ACTUATORS phase."""
        plugin = NodePulsePlugin()
        assert plugin.pulse_phase == PulsePhase.ACTUATORS

    def test_plugin_inherits_from_kernel_plugin(self):
        """Plugin should inherit from KernelPlugin."""
        plugin = NodePulsePlugin()
        assert isinstance(plugin, KernelPlugin)

    def test_plugin_starts_with_no_kernel(self):
        """Plugin should start without kernel reference."""
        plugin = NodePulsePlugin()
        assert plugin._kernel is None

    def test_plugin_starts_with_zero_pulse_count(self):
        """Plugin should start with pulse count of 0."""
        plugin = NodePulsePlugin()
        assert plugin._pulse_count == 0

    def test_plugin_starts_with_zero_agents_updated(self):
        """Plugin should start with agents updated count of 0."""
        plugin = NodePulsePlugin()
        assert plugin._agents_updated == 0


class TestNodePulseOnBoot:
    """Test on_boot behavior."""

    def test_on_boot_stores_kernel_reference(self):
        """on_boot should store kernel reference."""
        plugin = NodePulsePlugin()
        kernel = MagicMock()
        kernel.agent_registry = {}

        plugin.on_boot(kernel)

        assert plugin._kernel is kernel

    def test_on_boot_with_no_agents(self):
        """on_boot should handle empty agent registry."""
        plugin = NodePulsePlugin()
        kernel = MagicMock()
        kernel.agent_registry = {}

        # Should not raise
        plugin.on_boot(kernel)

        assert plugin._kernel is kernel

    def test_on_boot_with_agents(self):
        """on_boot should handle existing agents."""
        plugin = NodePulsePlugin()
        kernel = MagicMock()
        agent1 = MagicMock()
        agent1.agent_id = "test_agent_1"
        kernel.agent_registry = {"test_agent_1": agent1}

        # Should not raise
        plugin.on_boot(kernel)

        assert plugin._kernel is kernel

    def test_on_boot_handles_missing_agent_registry(self):
        """on_boot should handle kernel without agent_registry."""
        plugin = NodePulsePlugin()
        kernel = MagicMock(spec=[])  # No agent_registry attribute

        # Should not raise
        plugin.on_boot(kernel)

        assert plugin._kernel is kernel


class TestNodePulseOnPulse:
    """Test on_pulse behavior."""

    def test_on_pulse_returns_hook_result(self):
        """on_pulse should return HookResult."""
        plugin = NodePulsePlugin()
        kernel = MagicMock()
        kernel.agent_registry = {}
        transaction = MagicMock()

        result = plugin.on_pulse(kernel, transaction)

        assert isinstance(result, HookResult)
        assert result.status == PluginResult.OK

    def test_on_pulse_increments_pulse_count(self):
        """on_pulse should increment pulse count."""
        plugin = NodePulsePlugin()
        kernel = MagicMock()
        kernel.agent_registry = {}
        transaction = MagicMock()

        assert plugin._pulse_count == 0
        plugin.on_pulse(kernel, transaction)
        assert plugin._pulse_count == 1
        plugin.on_pulse(kernel, transaction)
        assert plugin._pulse_count == 2

    def test_on_pulse_with_no_agents(self):
        """on_pulse should handle empty agent registry."""
        plugin = NodePulsePlugin()
        kernel = MagicMock()
        kernel.agent_registry = {}
        transaction = MagicMock()

        result = plugin.on_pulse(kernel, transaction)

        assert result.status == PluginResult.OK
        assert result.data["agents_updated"] == 0
        assert result.data["errors"] == 0

    def test_on_pulse_updates_agent_with_ensure_presence(self):
        """on_pulse should call ensure_presence on agents."""
        plugin = NodePulsePlugin()
        kernel = MagicMock()

        agent = MagicMock()
        agent.agent_id = "test_agent"
        agent.ensure_presence = MagicMock(return_value=True)
        kernel.agent_registry = {"test_agent": agent}

        # Boot plugin to set kernel reference
        plugin.on_boot(kernel)

        transaction = MagicMock()
        result = plugin.on_pulse(kernel, transaction)

        agent.ensure_presence.assert_called_once()
        assert result.data["agents_updated"] == 1
        assert result.data["errors"] == 0

    def test_on_pulse_handles_agent_without_ensure_presence(self):
        """on_pulse should skip agents without ensure_presence."""
        plugin = NodePulsePlugin()
        kernel = MagicMock()

        agent = MagicMock(spec=["agent_id"])  # No ensure_presence method
        agent.agent_id = "test_agent"
        kernel.agent_registry = {"test_agent": agent}
        transaction = MagicMock()

        result = plugin.on_pulse(kernel, transaction)

        # Should not crash
        assert result.status == PluginResult.OK
        assert result.data["agents_updated"] == 0

    def test_on_pulse_handles_ensure_presence_returning_false(self):
        """on_pulse should handle agents that can't determine their path."""
        plugin = NodePulsePlugin()
        kernel = MagicMock()

        agent = MagicMock()
        agent.agent_id = "dynamic_agent"
        agent.ensure_presence = MagicMock(return_value=False)  # Can't determine path
        kernel.agent_registry = {"dynamic_agent": agent}
        transaction = MagicMock()

        result = plugin.on_pulse(kernel, transaction)

        # Should still succeed, but not count as updated
        assert result.status == PluginResult.OK
        assert result.data["agents_updated"] == 0
        assert result.data["errors"] == 0

    def test_on_pulse_handles_agent_errors(self):
        """on_pulse should handle errors from agents gracefully."""
        plugin = NodePulsePlugin()
        kernel = MagicMock()

        agent = MagicMock()
        agent.agent_id = "broken_agent"
        agent.ensure_presence = MagicMock(side_effect=RuntimeError("Test error"))
        kernel.agent_registry = {"broken_agent": agent}

        # Boot plugin to set kernel reference
        plugin.on_boot(kernel)

        transaction = MagicMock()
        result = plugin.on_pulse(kernel, transaction)

        # Should still return OK, but count error
        assert result.status == PluginResult.OK
        assert result.data["agents_updated"] == 0
        assert result.data["errors"] == 1

    def test_on_pulse_includes_kala_state_in_result(self):
        """on_pulse should include KALA state in result data."""
        plugin = NodePulsePlugin()
        kernel = MagicMock()
        kernel.agent_registry = {}
        transaction = MagicMock()

        result = plugin.on_pulse(kernel, transaction)

        assert "kala_state" in result.data
        assert isinstance(result.data["kala_state"], dict)

    def test_on_pulse_includes_pulse_count_in_result(self):
        """on_pulse should include pulse count in result data."""
        plugin = NodePulsePlugin()
        kernel = MagicMock()
        kernel.agent_registry = {}
        transaction = MagicMock()

        result = plugin.on_pulse(kernel, transaction)

        assert "pulse_count" in result.data
        assert result.data["pulse_count"] == 1

    def test_on_pulse_updates_multiple_agents(self):
        """on_pulse should update multiple agents."""
        plugin = NodePulsePlugin()
        kernel = MagicMock()

        agent1 = MagicMock()
        agent1.agent_id = "agent_1"
        agent1.ensure_presence = MagicMock(return_value=True)

        agent2 = MagicMock()
        agent2.agent_id = "agent_2"
        agent2.ensure_presence = MagicMock(return_value=True)

        kernel.agent_registry = {"agent_1": agent1, "agent_2": agent2}

        # Boot plugin to set kernel reference
        plugin.on_boot(kernel)

        transaction = MagicMock()
        result = plugin.on_pulse(kernel, transaction)

        assert result.data["agents_updated"] == 2
        agent1.ensure_presence.assert_called_once()
        agent2.ensure_presence.assert_called_once()


class TestNodePulseOnShutdown:
    """Test on_shutdown behavior."""

    def test_on_shutdown_with_no_agents(self):
        """on_shutdown should handle empty agent registry."""
        plugin = NodePulsePlugin()
        kernel = MagicMock()
        kernel.agent_registry = {}

        # Should not raise
        plugin.on_shutdown(kernel)

    def test_on_shutdown_calls_release_presence(self):
        """on_shutdown should call release_presence on agents."""
        plugin = NodePulsePlugin()
        kernel = MagicMock()

        agent = MagicMock()
        agent.agent_id = "test_agent"
        agent.release_presence = MagicMock(return_value=True)
        kernel.agent_registry = {"test_agent": agent}

        # Boot plugin to set kernel reference
        plugin.on_boot(kernel)

        plugin.on_shutdown(kernel)

        agent.release_presence.assert_called_once()

    def test_on_shutdown_handles_agent_without_release_presence(self):
        """on_shutdown should skip agents without release_presence."""
        plugin = NodePulsePlugin()
        kernel = MagicMock()

        agent = MagicMock(spec=["agent_id"])  # No release_presence method
        agent.agent_id = "test_agent"
        kernel.agent_registry = {"test_agent": agent}

        # Should not crash
        plugin.on_shutdown(kernel)

    def test_on_shutdown_handles_errors(self):
        """on_shutdown should handle errors from agents gracefully."""
        plugin = NodePulsePlugin()
        kernel = MagicMock()

        agent = MagicMock()
        agent.agent_id = "broken_agent"
        agent.release_presence = MagicMock(side_effect=RuntimeError("Test error"))
        kernel.agent_registry = {"broken_agent": agent}

        # Should not crash
        plugin.on_shutdown(kernel)

    def test_on_shutdown_releases_multiple_agents(self):
        """on_shutdown should release multiple agents."""
        plugin = NodePulsePlugin()
        kernel = MagicMock()

        agent1 = MagicMock()
        agent1.agent_id = "agent_1"
        agent1.release_presence = MagicMock(return_value=True)

        agent2 = MagicMock()
        agent2.agent_id = "agent_2"
        agent2.release_presence = MagicMock(return_value=True)

        kernel.agent_registry = {"agent_1": agent1, "agent_2": agent2}

        # Boot plugin to set kernel reference
        plugin.on_boot(kernel)

        plugin.on_shutdown(kernel)

        agent1.release_presence.assert_called_once()
        agent2.release_presence.assert_called_once()


class TestNodePulseGetStatus:
    """Test get_status method."""

    def test_get_status_returns_dict(self):
        """get_status should return dict."""
        plugin = NodePulsePlugin()
        kernel = MagicMock()
        kernel.agent_registry = {}
        plugin._kernel = kernel

        status = plugin.get_status()

        assert isinstance(status, dict)

    def test_get_status_includes_plugin_id(self):
        """get_status should include plugin_id."""
        plugin = NodePulsePlugin()
        kernel = MagicMock()
        kernel.agent_registry = {}
        plugin._kernel = kernel

        status = plugin.get_status()

        assert status["plugin_id"] == "node_pulse"

    def test_get_status_includes_pulse_count(self):
        """get_status should include pulse_count."""
        plugin = NodePulsePlugin()
        kernel = MagicMock()
        kernel.agent_registry = {}
        plugin._kernel = kernel
        plugin._pulse_count = 5

        status = plugin.get_status()

        assert status["pulse_count"] == 5

    def test_get_status_includes_agents_registered(self):
        """get_status should include agents_registered count."""
        plugin = NodePulsePlugin()
        kernel = MagicMock()

        agent1 = MagicMock()
        agent2 = MagicMock()
        kernel.agent_registry = {"agent_1": agent1, "agent_2": agent2}
        plugin._kernel = kernel

        status = plugin.get_status()

        assert status["agents_registered"] == 2

    def test_get_status_includes_last_update_count(self):
        """get_status should include last_update_count."""
        plugin = NodePulsePlugin()
        kernel = MagicMock()
        kernel.agent_registry = {}
        plugin._kernel = kernel
        plugin._agents_updated = 3

        status = plugin.get_status()

        assert status["last_update_count"] == 3


class TestNodePulseGetKalaState:
    """Test _get_kala_state method."""

    def test_get_kala_state_with_no_kernel(self):
        """_get_kala_state should return empty dict without kernel."""
        plugin = NodePulsePlugin()

        kala_state = plugin._get_kala_state()

        assert kala_state == {}

    def test_get_kala_state_with_no_kala_plugin(self):
        """_get_kala_state should return empty dict if KALA not found."""
        plugin = NodePulsePlugin()
        kernel = MagicMock()
        plugin._kernel = kernel

        # Mock plugin_loader with no KALA plugin
        mock_plugin = MagicMock()
        mock_plugin.plugin_id = "other_plugin"
        kernel.plugin_loader.get_active_plugins.return_value = [mock_plugin]

        kala_state = plugin._get_kala_state()

        assert kala_state == {}

    def test_get_kala_state_with_kala_plugin(self):
        """_get_kala_state should extract KALA state from plugin."""
        plugin = NodePulsePlugin()
        kernel = MagicMock()
        plugin._kernel = kernel

        # Mock KALA plugin
        kala_plugin = MagicMock()
        kala_plugin.plugin_id = "kala"
        kala_plugin.get_current_state.return_value = {
            "sun_phase": "DAY",
            "moon_phase": "WAXING_GIBBOUS",
            "tithi": 10,
            "paksha": "shukla",
            "rhythm_intensity": 0.8,
        }
        kernel.plugin_loader.get_active_plugins.return_value = [kala_plugin]

        kala_state = plugin._get_kala_state()

        assert kala_state["sun_phase"] == "DAY"
        assert kala_state["moon_phase"] == "WAXING_GIBBOUS"
        assert kala_state["tithi"] == 10
        assert kala_state["paksha"] == "shukla"
        assert kala_state["rhythm_intensity"] == 0.8

    def test_get_kala_state_handles_error_in_kala_state(self):
        """_get_kala_state should return empty dict if KALA has error."""
        plugin = NodePulsePlugin()
        kernel = MagicMock()
        plugin._kernel = kernel

        # Mock KALA plugin with error state
        kala_plugin = MagicMock()
        kala_plugin.plugin_id = "kala"
        kala_plugin.get_current_state.return_value = {"error": "Test error"}
        kernel.plugin_loader.get_active_plugins.return_value = [kala_plugin]

        kala_state = plugin._get_kala_state()

        assert kala_state == {}

    def test_get_kala_state_handles_exception(self):
        """_get_kala_state should handle exceptions gracefully."""
        plugin = NodePulsePlugin()
        kernel = MagicMock()
        plugin._kernel = kernel

        # Mock plugin_loader that raises exception
        kernel.plugin_loader.get_active_plugins.side_effect = RuntimeError("Test error")

        kala_state = plugin._get_kala_state()

        assert kala_state == {}


class TestNodePulseGetRegisteredAgents:
    """Test _get_registered_agents method."""

    def test_get_registered_agents_with_no_kernel(self):
        """_get_registered_agents should return empty list without kernel."""
        plugin = NodePulsePlugin()

        agents = plugin._get_registered_agents()

        assert agents == []

    def test_get_registered_agents_with_empty_registry(self):
        """_get_registered_agents should return empty list with empty registry."""
        plugin = NodePulsePlugin()
        kernel = MagicMock()
        kernel.agent_registry = {}
        plugin._kernel = kernel

        agents = plugin._get_registered_agents()

        assert agents == []

    def test_get_registered_agents_with_agents(self):
        """_get_registered_agents should return list of agents."""
        plugin = NodePulsePlugin()
        kernel = MagicMock()

        agent1 = MagicMock()
        agent2 = MagicMock()
        kernel.agent_registry = {"agent_1": agent1, "agent_2": agent2}
        plugin._kernel = kernel

        agents = plugin._get_registered_agents()

        assert len(agents) == 2
        assert agent1 in agents
        assert agent2 in agents

    def test_get_registered_agents_handles_missing_registry(self):
        """_get_registered_agents should handle kernel without agent_registry."""
        plugin = NodePulsePlugin()
        kernel = MagicMock(spec=[])  # No agent_registry attribute
        plugin._kernel = kernel

        agents = plugin._get_registered_agents()

        assert agents == []

    def test_get_registered_agents_handles_exception(self):
        """_get_registered_agents should handle exceptions gracefully."""
        plugin = NodePulsePlugin()
        kernel = MagicMock()
        # Make agent_registry raise exception when accessed
        type(kernel).agent_registry = property(lambda self: (_ for _ in ()).throw(RuntimeError("Test error")))
        plugin._kernel = kernel

        agents = plugin._get_registered_agents()

        assert agents == []
