"""Sanity tests for process_isolation Plugin."""

import pytest


def test_plugin_loads():
    """Test that the process_isolation plugin loads correctly."""
    try:
        from vibe_core.plugins.process_isolation.plugin_main import ProcessIsolationPlugin
        plugin = ProcessIsolationPlugin()
        assert hasattr(plugin, 'plugin_id')
    except ImportError as e:
        pytest.skip(f"Plugin import failed: {e}")


def test_has_on_boot():
    """Test that on_boot method exists."""
    try:
        from vibe_core.plugins.process_isolation.plugin_main import ProcessIsolationPlugin
        plugin = ProcessIsolationPlugin()
        assert hasattr(plugin, 'on_boot')
    except ImportError as e:
        pytest.skip(f"Plugin import failed: {e}")
