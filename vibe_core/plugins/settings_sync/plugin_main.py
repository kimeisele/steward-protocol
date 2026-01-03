"""
Settings Sync Plugin - OPUS-312 SettingsExecutor Wiring.

This plugin bridges the gap between SETTINGS.md and actual execution.
Previously MarkdownUIManager was commented out in kernel_impl.py with
incorrect "DEPRECATED: Handled by Plugins" note. Now it IS handled by
this plugin.

PATTERN: Plugin calls sync_all() on each tick_post, which:
  1. Reads SETTINGS.md for pending commands (RESTART, REFRESH, SET)
  2. Executes them via SettingsExecutor
  3. Syncs ENVOY.md for interface state
"""

import logging
from typing import Any, Dict, Optional

from vibe_core.plugin_protocol import HookResult, KernelPlugin
from vibe_core.protocols import VibeKernel

logger = logging.getLogger("SETTINGS_SYNC")


class SettingsSyncPlugin(KernelPlugin):
    """
    Wires MarkdownUIManager into the kernel tick cycle.
    Executes SETTINGS.md commands that were previously ignored.
    """

    @property
    def plugin_id(self) -> str:
        return "settings_sync"

    def on_boot(self, kernel: VibeKernel, config: Optional[Dict[str, Any]] = None) -> HookResult:
        """Initialize MarkdownUIManager on kernel boot."""
        from vibe_core.markdown_ui_manager import MarkdownUIManager

        self._kernel = kernel
        self._ui_manager = MarkdownUIManager(kernel)

        logger.info("🖥️  SETTINGS_SYNC: MarkdownUIManager initialized (SettingsExecutor ACTIVE)")
        return HookResult.ok()

    def on_tick_post(self, kernel: VibeKernel) -> HookResult:
        """Sync SETTINGS.md/ENVOY.md after each tick."""
        try:
            self._ui_manager.sync_all()
        except Exception as e:
            logger.warning(f"⚠️  SETTINGS_SYNC: sync_all() failed: {e}")
            # Don't crash the tick - settings sync is non-critical
        return HookResult.ok()


# Entry point for Loader
def get_plugin():
    return SettingsSyncPlugin()
