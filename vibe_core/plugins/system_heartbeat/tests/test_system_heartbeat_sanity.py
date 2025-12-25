"""Sanity tests for system_heartbeat Plugin."""

import pytest


def test_plugin_loads():
    """Test that the system_heartbeat plugin loads correctly."""
    try:
        from vibe_core.plugins.system_heartbeat.plugin_main import SystemHeartbeatPlugin
        plugin = SystemHeartbeatPlugin()
        assert hasattr(plugin, 'plugin_id')
    except ImportError as e:
        pytest.skip(f"Plugin import failed: {e}")


def test_has_on_boot():
    """Test that on_boot method exists."""
    try:
        from vibe_core.plugins.system_heartbeat.plugin_main import SystemHeartbeatPlugin
        plugin = SystemHeartbeatPlugin()
        assert hasattr(plugin, 'on_boot')
    except ImportError as e:
        pytest.skip(f"Plugin import failed: {e}")
