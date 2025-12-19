#!/usr/bin/env python3
"""
Execution Mode Settings Section

Self-contained section for simulation/live_fire mode toggle.
"""

import logging
from typing import List, Optional

from ..protocol import SectionContext, SettingsResult, SettingsSection

logger = logging.getLogger(__name__)

VALID_MODES = {"simulation", "live_fire"}


class ExecutionModeSection(SettingsSection):
    """Execution mode (simulation/live_fire) configuration section."""

    @property
    def section_id(self) -> str:
        return "execution_mode"

    @property
    def priority(self) -> int:
        return 20  # After provider

    @property
    def title(self) -> str:
        return "## ⚡ Execution Mode"

    def render(self, context: SectionContext) -> List[str]:
        """Render execution mode section."""
        is_live = context.live_fire_enabled
        mode_emoji = "🔴" if is_live else "🟢"
        mode_name = "live_fire" if is_live else "simulation"

        lines = [
            "---",
            "",
            self.title,
            "",
            f"**Current Mode:** `{mode_name}` {mode_emoji}",
            "",
            "| Mode | Description |",
            "|------|-------------|",
            "| `simulation` | Dry-run mode - no real API calls, no file writes |",
            "| `live_fire` | Real execution - API calls, file writes enabled |",
            "",
        ]

        if is_live:
            lines.extend(
                [
                    "**⚠️ WARNING:** Live Fire mode is ACTIVE. Real changes will be made.",
                    "",
                    "**To disable:**",
                    "```",
                    "- SET mode=simulation",
                    "```",
                    "",
                ]
            )
        else:
            lines.extend(
                [
                    "**To enable Live Fire:**",
                    "```",
                    "- SET mode=live_fire",
                    "```",
                    "",
                    "**⚠️ WARNING:** Live Fire mode makes real changes. Use with caution.",
                    "",
                ]
            )

        return lines

    def handles_command(self, key: str) -> bool:
        return key == "mode"

    def validate(self, key: str, value: str) -> Optional[str]:
        """Validate execution mode."""
        if value.lower() not in VALID_MODES:
            return f"Invalid mode '{value}'. Use: simulation or live_fire"
        return None

    def execute(self, key: str, value: str, context: SectionContext) -> SettingsResult:
        """Execute mode change."""
        mode = value.lower().strip()

        # Validate
        error = self.validate(key, mode)
        if error:
            return SettingsResult(success=False, message=error)

        is_live = mode == "live_fire"

        try:
            # Update phoenix config
            from vibe_core.phoenix import get_config

            config = get_config()
            config.kernel.features.live_fire_enabled = is_live
            config.save()

            if is_live:
                logger.warning("⚠️  LIVE FIRE MODE ENABLED")
                message = "Live Fire mode ENABLED - Real API calls and writes are now active!"
            else:
                logger.info("🔒 Simulation mode enabled")
                message = "Simulation mode enabled - API calls and writes are simulated"

            return SettingsResult(
                success=True,
                message=message,
                side_effects={"live_fire_enabled": is_live},
            )

        except Exception as e:
            logger.error(f"Failed to change execution mode: {e}")
            return SettingsResult(success=False, message=str(e))
