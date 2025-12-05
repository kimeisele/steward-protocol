"""
Settings Renderer (Control Panel).
"""

import logging

from vibe_core.settings_sync import SettingsSync, get_executor

from .base import BaseRenderer

logger = logging.getLogger("RENDERER_SETTINGS")


class SettingsRenderer(BaseRenderer):
    """Renders SETTINGS.md and handles system configuration."""

    def __init__(self, kernel):
        super().__init__(kernel)
        self.sync = SettingsSync()

    @property
    def name(self) -> str:
        return "settings"

    def render(self) -> None:
        # Gather state
        state = {
            "paused_agents": [],
            "history": [],
            "stats": self.kernel.get_status(),
        }

        # Get paused agents from governance if available
        if hasattr(self.kernel, "governance") and self.kernel.governance:
            state["paused_agents"] = list(self.kernel.governance.get_paused_agents())

        # Sync to reality
        try:
            result = self.sync.sync_to_reality(state, ledger_callback=self.kernel.record_verified_event)

            # Execute side effects (RESTART, REFRESH, etc.)
            if result:
                executor = get_executor()
                executor.execute(result, self.kernel)

        except Exception as e:
            logger.error(f"Error rendering SETTINGS.md: {e}")
