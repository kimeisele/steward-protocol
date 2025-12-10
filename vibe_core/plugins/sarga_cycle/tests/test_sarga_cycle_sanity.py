"""
Sarga Cycle Plugin - Sanity Tests
===================================
Minimal test for container packaging compliance (OPUS-020).
"""


def test_sarga_cycle_plugin_imports():
    """Verify SargaCyclePlugin can be imported."""
    from vibe_core.plugins.sarga_cycle.plugin_main import SargaCyclePlugin

    assert SargaCyclePlugin is not None
    assert hasattr(SargaCyclePlugin, "on_boot")
    assert hasattr(SargaCyclePlugin, "plugin_id")


def test_sarga_cycle_plugin_instantiation():
    """Verify SargaCyclePlugin can be instantiated."""
    from vibe_core.plugins.sarga_cycle.plugin_main import SargaCyclePlugin

    plugin = SargaCyclePlugin()
    assert plugin.plugin_id == "sarga_cycle"
