"""
Test Mode Plugin - Sanity Tests
=================================
Minimal test for container packaging compliance (OPUS-020).
"""



def test_test_mode_plugin_imports():
    """Verify TestModePlugin can be imported."""
    from vibe_core.plugins.test_mode.plugin_main import TestModePlugin

    assert TestModePlugin is not None
    assert hasattr(TestModePlugin, "on_boot")
    assert hasattr(TestModePlugin, "plugin_id")


def test_test_mode_plugin_instantiation():
    """Verify TestModePlugin can be instantiated."""
    from vibe_core.plugins.test_mode.plugin_main import TestModePlugin

    plugin = TestModePlugin()
    assert plugin.plugin_id == "test_mode"
