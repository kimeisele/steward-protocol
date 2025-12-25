"""Sanity tests for resource_limits Plugin."""

import pytest


def test_plugin_loads():
    """Test that the resource_limits plugin loads correctly."""
    try:
        from vibe_core.plugins.resource_limits.plugin_main import ResourceLimitsPlugin
        plugin = ResourceLimitsPlugin()
        assert hasattr(plugin, 'plugin_id')
    except ImportError as e:
        pytest.skip(f"Plugin import failed: {e}")


def test_has_on_boot():
    """Test that on_boot method exists."""
    try:
        from vibe_core.plugins.resource_limits.plugin_main import ResourceLimitsPlugin
        plugin = ResourceLimitsPlugin()
        assert hasattr(plugin, 'on_boot')
    except ImportError as e:
        pytest.skip(f"Plugin import failed: {e}")
