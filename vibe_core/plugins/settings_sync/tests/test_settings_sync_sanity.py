"""Sanity tests for settings_sync plugin."""

import pytest


class TestSettingsSyncSanity:
    """Basic sanity checks for SettingsSyncPlugin."""

    def test_plugin_imports(self):
        """Plugin module can be imported."""
        from vibe_core.plugins.settings_sync.plugin_main import SettingsSyncPlugin

        assert SettingsSyncPlugin is not None

    def test_plugin_has_required_methods(self):
        """Plugin has required lifecycle methods."""
        from vibe_core.plugins.settings_sync.plugin_main import SettingsSyncPlugin

        plugin = SettingsSyncPlugin()
        assert hasattr(plugin, "on_boot")
        assert hasattr(plugin, "on_tick_post")
        assert callable(plugin.on_boot)
        assert callable(plugin.on_tick_post)

    def test_plugin_metadata(self):
        """Plugin has correct metadata."""
        from vibe_core.plugins.settings_sync.plugin_main import SettingsSyncPlugin

        plugin = SettingsSyncPlugin()
        assert plugin.id == "settings_sync"
        assert plugin.name == "Settings Sync"
