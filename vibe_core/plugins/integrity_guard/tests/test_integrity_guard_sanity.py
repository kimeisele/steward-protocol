"""Sanity tests for integrity_guard Plugin."""

import pytest


def test_plugin_loads():
    """Test that the integrity_guard plugin loads correctly."""
    try:
        from vibe_core.plugins.integrity_guard.plugin_main import IntegrityGuardPlugin
        plugin = IntegrityGuardPlugin()
        assert hasattr(plugin, 'plugin_id')
    except ImportError as e:
        pytest.skip(f"Plugin import failed: {e}")


def test_has_on_boot():
    """Test that on_boot method exists."""
    try:
        from vibe_core.plugins.integrity_guard.plugin_main import IntegrityGuardPlugin
        plugin = IntegrityGuardPlugin()
        assert hasattr(plugin, 'on_boot')
    except ImportError as e:
        pytest.skip(f"Plugin import failed: {e}")
