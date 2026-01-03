"""
METAL TEST: Settings Sync Plugin (P0 SettingsExecutor Fix)

Tests that the settings_sync plugin:
1. Boots correctly
2. Initializes MarkdownUIManager
3. Can call sync_all() without crashing

OPUS-312: SettingsExecutor was orphaned - existed but never called.
Fix: Created settings_sync plugin that wires it into tick_post.
"""

from unittest.mock import MagicMock, patch

import pytest


class TestSettingsSyncPlugin:
    """Verify settings_sync plugin works."""

    def test_plugin_imports(self):
        """Plugin module must import without errors."""
        from vibe_core.plugins.settings_sync import SettingsSyncPlugin

        assert SettingsSyncPlugin is not None

    def test_plugin_has_correct_id(self):
        """Plugin ID must match manifest."""
        from vibe_core.plugins.settings_sync import SettingsSyncPlugin

        plugin = SettingsSyncPlugin()
        assert plugin.plugin_id == "settings_sync"

    def test_plugin_on_boot_initializes_ui_manager(self):
        """on_boot must create MarkdownUIManager."""
        from vibe_core.plugin_protocol import HookResult
        from vibe_core.plugins.settings_sync import SettingsSyncPlugin

        plugin = SettingsSyncPlugin()

        # Mock kernel
        mock_kernel = MagicMock()

        # Mock MarkdownUIManager (imported inside on_boot from vibe_core.markdown_ui_manager)
        with patch("vibe_core.markdown_ui_manager.MarkdownUIManager") as MockUIManager:
            MockUIManager.return_value = MagicMock()

            result = plugin.on_boot(mock_kernel)

            # Verify MarkdownUIManager was created
            MockUIManager.assert_called_once_with(mock_kernel)
            assert result == HookResult.ok()

    def test_plugin_on_tick_post_calls_sync_all(self):
        """on_tick_post must call sync_all()."""
        from vibe_core.plugin_protocol import HookResult
        from vibe_core.plugins.settings_sync import SettingsSyncPlugin

        plugin = SettingsSyncPlugin()

        # Mock kernel and UI manager
        mock_kernel = MagicMock()

        with patch("vibe_core.markdown_ui_manager.MarkdownUIManager") as MockUIManager:
            mock_ui_manager = MagicMock()
            MockUIManager.return_value = mock_ui_manager

            # Boot the plugin
            plugin.on_boot(mock_kernel)

            # Call tick_post
            result = plugin.on_tick_post(mock_kernel)

            # Verify sync_all was called
            mock_ui_manager.sync_all.assert_called_once()
            assert result == HookResult.ok()

    def test_plugin_survives_sync_all_error(self):
        """on_tick_post must not crash if sync_all raises."""
        from vibe_core.plugin_protocol import HookResult
        from vibe_core.plugins.settings_sync import SettingsSyncPlugin

        plugin = SettingsSyncPlugin()

        # Mock kernel and UI manager that raises
        mock_kernel = MagicMock()

        with patch("vibe_core.markdown_ui_manager.MarkdownUIManager") as MockUIManager:
            mock_ui_manager = MagicMock()
            mock_ui_manager.sync_all.side_effect = RuntimeError("Settings file corrupt")
            MockUIManager.return_value = mock_ui_manager

            # Boot the plugin
            plugin.on_boot(mock_kernel)

            # Call tick_post - should NOT raise
            result = plugin.on_tick_post(mock_kernel)

            # Should return ok() even on error (graceful degradation)
            assert result == HookResult.ok()

    def test_manifest_is_valid_json(self):
        """Manifest must be valid JSON with required fields."""
        import json
        from pathlib import Path

        manifest_path = Path(__file__).parent.parent.parent.parent / "vibe_core/plugins/settings_sync/manifest.json"
        manifest = json.loads(manifest_path.read_text())

        assert manifest["id"] == "settings_sync"
        assert "description" in manifest
        assert "version" in manifest
        assert "priority" in manifest
