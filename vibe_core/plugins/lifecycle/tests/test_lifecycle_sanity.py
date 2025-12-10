"""
Lifecycle Plugin - Sanity Tests
================================
Minimal test for container packaging compliance (OPUS-020).
"""



def test_lifecycle_plugin_imports():
    """Verify LifecyclePlugin can be imported."""
    from vibe_core.plugins.lifecycle.plugin_main import LifecyclePlugin

    assert LifecyclePlugin is not None
    assert hasattr(LifecyclePlugin, "on_boot")
    assert hasattr(LifecyclePlugin, "plugin_id")


def test_lifecycle_plugin_instantiation():
    """Verify LifecyclePlugin can be instantiated."""
    from vibe_core.plugins.lifecycle.plugin_main import LifecyclePlugin

    plugin = LifecyclePlugin()
    assert plugin.plugin_id == "lifecycle"
