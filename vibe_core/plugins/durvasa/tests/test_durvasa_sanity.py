"""Sanity tests for Durvasa Plugin."""

import pytest


def test_plugin_loads():
    """Test that the durvasa plugin loads correctly."""
    from vibe_core.plugins.durvasa.plugin_main import DurvasaPlugin

    plugin = DurvasaPlugin()
    assert plugin.plugin_id == "durvasa"


def test_on_boot_returns_ok():
    """Test that on_boot returns HookResult.ok without kernel."""
    from vibe_core.plugin_protocol import HookResult
    from vibe_core.plugins.durvasa.plugin_main import DurvasaPlugin

    plugin = DurvasaPlugin()
    # Boot without kernel stores None
    result = plugin.on_boot(kernel=None, config=None)
    assert result.ok is True


def test_enforce_prana_without_kernel():
    """Test that enforce_prana_limits returns 0 without kernel."""
    from vibe_core.plugins.durvasa.plugin_main import DurvasaPlugin

    plugin = DurvasaPlugin()
    # Without kernel, should return 0 sacrifices
    result = plugin.enforce_prana_limits(pressure=0.95)
    assert result == 0


def test_state_paths():
    """Test that state paths are returned."""
    from vibe_core.plugins.durvasa.plugin_main import DurvasaPlugin

    plugin = DurvasaPlugin()
    paths = plugin.get_state_paths()
    assert len(paths) == 1
    assert "durvasa" in str(paths[0])
