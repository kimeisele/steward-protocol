"""
Interface Plugin - Sanity Tests
================================
Minimal test for container packaging compliance (OPUS-020).
"""


def test_interface_plugin_imports():
    """Verify InterfacePlugin can be imported."""
    from vibe_core.plugins.interface.plugin_main import InterfacePlugin

    assert InterfacePlugin is not None
    assert hasattr(InterfacePlugin, "on_boot")
    assert hasattr(InterfacePlugin, "plugin_id")


def test_interface_plugin_instantiation():
    """Verify InterfacePlugin can be instantiated."""
    from vibe_core.plugins.interface.plugin_main import InterfacePlugin

    plugin = InterfacePlugin()
    assert plugin.plugin_id == "interface"


def test_renderer_discovery():
    """Verify renderers can be discovered."""
    from pathlib import Path

    renderers_dir = Path(__file__).parent.parent / "renderers"
    assert renderers_dir.exists(), "renderers/ directory must exist"

    renderer_files = list(renderers_dir.glob("*.py"))
    assert len(renderer_files) > 0, "At least one renderer must exist"
