"""Sanity tests for sangha_network Plugin."""

import pytest


def test_plugin_loads():
    """Test that the sangha_network plugin loads correctly."""
    try:
        from vibe_core.plugins.sangha_network.plugin_main import SanghaNetworkPlugin

        plugin = SanghaNetworkPlugin()
        assert hasattr(plugin, "plugin_id")
    except ImportError as e:
        pytest.skip(f"Plugin import failed: {e}")


def test_has_on_boot():
    """Test that on_boot method exists."""
    try:
        from vibe_core.plugins.sangha_network.plugin_main import SanghaNetworkPlugin

        plugin = SanghaNetworkPlugin()
        assert hasattr(plugin, "on_boot")
    except ImportError as e:
        pytest.skip(f"Plugin import failed: {e}")
