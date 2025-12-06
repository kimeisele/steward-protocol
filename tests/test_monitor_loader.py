"""
TEST: Monitor Loader
====================
Tests for Glass Box system introspection.
"""

from unittest.mock import MagicMock

from vibe_core.cli.monitor_loader import MonitorLoader


class TestMonitorLoader:
    """Test monitor discovery."""

    def teardown_method(self):
        MonitorLoader.clear_cache()

    def test_discover_monitors_no_plugins(self):
        """Should return empty registry if no plugins."""
        kernel = MagicMock()
        kernel.plugin_manager.plugins = []

        monitors = MonitorLoader.discover_monitors(kernel)
        assert len(monitors) == 0

    def test_discover_monitors_with_plugin(self):
        """Should discover monitors from plugin."""
        # Mock plugin
        plugin = MagicMock()
        plugin.plugin_id = "test_plugin"

        # Mock monitor
        monitor = MagicMock()
        monitor.monitor_id = "test_monitor"
        monitor.monitor_type = "gauge"
        monitor.description = "Test Monitor"

        plugin.get_monitors.return_value = [monitor]

        kernel = MagicMock()
        kernel.plugin_manager.plugins = [plugin]

        monitors = MonitorLoader.discover_monitors(kernel)
        assert "test_monitor" in monitors
        assert monitors["test_monitor"].plugin_id == "test_plugin"

    def test_cache_behavior(self):
        """Should cache results."""
        kernel = MagicMock()
        kernel.plugin_manager.plugins = []

        # First call
        MonitorLoader.discover_monitors(kernel)
        assert MonitorLoader._cache is not None

        # Modify kernel plugins (should be ignored due to cache)
        kernel.plugin_manager.plugins = ["garbage"]
        MonitorLoader.discover_monitors(kernel)

        # Should still be empty if cache used
        assert len(MonitorLoader._cache) == 0
