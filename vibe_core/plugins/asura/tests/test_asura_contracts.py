"""
TEST: AsuraPlugin Contract Tests (Red Team Suite)
=================================================
Target: vibe_core/plugins/asura/plugin_main.py
Standard: GAD-5000 (Plugin Contract Testing)

Tests verify:
1. Plugin identity and protocol compliance
2. on_boot / on_shutdown lifecycle
3. Demon summoning mechanics
4. Active demons tracking
"""

from unittest.mock import MagicMock, patch

import pytest

from vibe_core.plugin_protocol import HookResult, KernelPlugin, PluginResult
from vibe_core.plugins.asura.plugin_main import AsuraPlugin


class TestAsuraPluginInit:
    """Test plugin initialization and identity."""

    def test_plugin_can_be_instantiated(self):
        """Plugin should instantiate without errors."""
        plugin = AsuraPlugin()
        assert plugin is not None

    def test_plugin_has_correct_id(self):
        """Plugin ID should be 'asura'."""
        plugin = AsuraPlugin()
        assert plugin.plugin_id == "asura"

    def test_plugin_inherits_from_kernel_plugin(self):
        """Plugin should inherit from KernelPlugin."""
        plugin = AsuraPlugin()
        assert isinstance(plugin, KernelPlugin)

    def test_plugin_starts_with_no_active_demons(self):
        """Plugin should start with empty demon list."""
        plugin = AsuraPlugin()
        assert plugin._active_demons == []

    def test_plugin_starts_with_no_kernel(self):
        """Plugin should start without kernel reference."""
        plugin = AsuraPlugin()
        assert plugin._kernel is None


class TestAsuraOnBoot:
    """Test on_boot behavior."""

    def test_on_boot_returns_hook_result(self):
        """on_boot should return HookResult."""
        plugin = AsuraPlugin()
        kernel = MagicMock()

        result = plugin.on_boot(kernel, config=None)

        assert isinstance(result, HookResult)
        assert result.status == PluginResult.OK

    def test_on_boot_stores_kernel_reference(self):
        """on_boot should store kernel reference."""
        plugin = AsuraPlugin()
        kernel = MagicMock()

        plugin.on_boot(kernel, config=None)

        assert plugin._kernel is kernel


class TestAsuraOnShutdown:
    """Test on_shutdown behavior."""

    def test_on_shutdown_returns_hook_result(self):
        """on_shutdown should return HookResult."""
        plugin = AsuraPlugin()
        kernel = MagicMock()
        plugin.on_boot(kernel)

        result = plugin.on_shutdown(kernel)

        assert isinstance(result, HookResult)
        assert result.status == PluginResult.OK

    def test_on_shutdown_clears_active_demons(self):
        """on_shutdown should clear active demons list."""
        plugin = AsuraPlugin()
        kernel = MagicMock()
        plugin.on_boot(kernel)
        plugin._active_demons = [MagicMock(), MagicMock()]

        plugin.on_shutdown(kernel)

        assert plugin._active_demons == []

    def test_on_shutdown_calls_retreat_on_demons(self):
        """on_shutdown should call retreat() on demons that have it."""
        plugin = AsuraPlugin()
        kernel = MagicMock()
        plugin.on_boot(kernel)

        demon = MagicMock()
        demon.retreat = MagicMock()
        plugin._active_demons = [demon]

        plugin.on_shutdown(kernel)

        demon.retreat.assert_called_once()


class TestAsuraSummonPutana:
    """Test Putana summoning."""

    def test_summon_putana_returns_agent(self):
        """summon_putana should return PutanaAgent."""
        plugin = AsuraPlugin()
        kernel = MagicMock()
        plugin.on_boot(kernel)

        putana = plugin.summon_putana()

        assert putana is not None
        from vibe_core.plugins.asura.agents.putana import PutanaAgent

        assert isinstance(putana, PutanaAgent)

    def test_summon_putana_adds_to_active_demons(self):
        """summon_putana should add agent to active demons."""
        plugin = AsuraPlugin()
        kernel = MagicMock()
        plugin.on_boot(kernel)

        assert len(plugin._active_demons) == 0

        plugin.summon_putana()

        assert len(plugin._active_demons) == 1

    def test_summon_multiple_putanas(self):
        """Multiple Putanas can be summoned."""
        plugin = AsuraPlugin()
        kernel = MagicMock()
        plugin.on_boot(kernel)

        p1 = plugin.summon_putana()
        p2 = plugin.summon_putana()

        assert len(plugin._active_demons) == 2
        assert p1 is not p2


class TestAsuraRedTeamWarnings:
    """Test that proper warnings are logged."""

    def test_on_boot_logs_warning(self):
        """on_boot should log red team warning."""
        plugin = AsuraPlugin()
        kernel = MagicMock()

        with patch("vibe_core.plugins.asura.plugin_main.logger") as mock_logger:
            plugin.on_boot(kernel)

            # Should log warnings about red team testing
            assert mock_logger.warning.call_count >= 2
