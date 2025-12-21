"""ASURA Plugin Sanity Tests"""


def test_asura_plugin_imports():
    """Verify ASURA plugin can be imported."""
    from vibe_core.plugins.asura.plugin_main import AsuraPlugin

    assert AsuraPlugin is not None


def test_asura_plugin_instantiation():
    """Verify ASURA plugin can be instantiated."""
    from vibe_core.plugins.asura.plugin_main import AsuraPlugin

    plugin = AsuraPlugin()
    assert plugin.plugin_id == "asura"
