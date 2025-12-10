"""
Tools Plugin - Sanity Tests
============================
Minimal test for container packaging compliance (OPUS-020).
"""



def test_tools_plugin_imports():
    """Verify ToolsPlugin can be imported."""
    from vibe_core.plugins.tools.plugin_main import ToolsPlugin

    assert ToolsPlugin is not None
    assert hasattr(ToolsPlugin, "on_boot")
    assert hasattr(ToolsPlugin, "plugin_id")


def test_tools_plugin_instantiation():
    """Verify ToolsPlugin can be instantiated."""
    from vibe_core.plugins.tools.plugin_main import ToolsPlugin

    plugin = ToolsPlugin()
    assert plugin.plugin_id == "tools"
