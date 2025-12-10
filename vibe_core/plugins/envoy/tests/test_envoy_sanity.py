"""
Envoy Plugin - Sanity Tests
============================
Minimal test for container packaging compliance (OPUS-020).
"""



def test_envoy_plugin_imports():
    """Verify EnvoyPlugin can be imported."""
    from vibe_core.plugins.envoy.plugin_main import EnvoyPlugin

    assert EnvoyPlugin is not None
    assert hasattr(EnvoyPlugin, "on_boot")
    assert hasattr(EnvoyPlugin, "plugin_id")


def test_envoy_plugin_instantiation():
    """Verify EnvoyPlugin can be instantiated."""
    from vibe_core.plugins.envoy.plugin_main import EnvoyPlugin

    plugin = EnvoyPlugin()
    assert plugin.plugin_id == "envoy"
