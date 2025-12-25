"""Sanity tests for Boot Optimizer Plugin."""

import pytest


def test_plugin_loads():
    """Test that the boot_optimizer plugin loads correctly."""
    from vibe_core.plugins.boot_optimizer.plugin_main import BootOptimizerPlugin

    plugin = BootOptimizerPlugin()
    assert plugin.plugin_id == "boot_optimizer"


def test_on_boot_returns_ok():
    """Test that on_boot returns HookResult.ok."""
    from vibe_core.plugin_protocol import HookResult
    from vibe_core.plugins.boot_optimizer.plugin_main import BootOptimizerPlugin

    plugin = BootOptimizerPlugin()
    result = plugin.on_boot(kernel=None, config=None)
    assert result.ok is True
