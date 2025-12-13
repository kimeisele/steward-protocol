"""
Control Cables Parser - OPUS-031 Layer 1.5

Transforms OPUS.md into a bidirectional control surface.
The document IS the API.

Architecture:
    ┌─────────────────────────────────────────────────────────────┐
    │                   OPUS.md                                   │
    │   ## 🎛️ Control Plane                                      │
    │   - [x] Tests                                               │
    │   - [ ] Debug                                               │
    │   - [x] Auto-Heal Mode: ON                                  │
    │   - [ ] Budget Limit: $5.00                                 │
    └────────────────────────┬────────────────────────────────────┘
                             │ human edits
                             ▼
    ┌─────────────────────────────────────────────────────────────┐
    │               ControlCablesParser                           │
    │   parse_control_plane(content) → Dict[str, Any]             │
    │   apply_to_state(state_manager, settings)                   │
    └────────────────────────┬────────────────────────────────────┘
                             │ persists to
                             ▼
    ┌─────────────────────────────────────────────────────────────┐
    │               .opus_state/session.json                      │
    │   { "view_preferences": { "show_tests": true, ... } }       │
    └─────────────────────────────────────────────────────────────┘

Design Decisions (OPUS-031):
- DD4: Bidirectional Control Surface - OPUS.md is INPUT, not just OUTPUT
- DD5: Configuration, Not Commands - Settings persist until changed
"""

import logging
import re
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from vibe_core.plugins.opus_assistant.core.state_manager import OpusStateManager

logger = logging.getLogger("CONTROL_CABLES")


class ControlCablesParser:
    """
    Parse Control Plane section from OPUS.md back into StateManager.

    This closes the feedback loop:
    OPUS.md (human edit) → Parser → StateManager → Next Render
    """

    # Schema: Maps markdown label → (state_key, type, default)
    # Label is what appears in OPUS.md, key is stored in view_preferences
    SCHEMA = {
        # Panel toggles (existing from control_plane.md.j2)
        "Tests": {"key": "show_tests", "type": bool, "default": True},
        "Code Health": {"key": "show_code_health", "type": bool, "default": True},
        "Debug": {"key": "show_debug", "type": bool, "default": False},
        # Layer 1.5 Settings (new)
        "Auto-Heal Mode": {"key": "auto_heal", "type": bool, "default": False},
        "Simulation Mode": {"key": "simulation_mode", "type": bool, "default": True},
        "Aggressive Refactoring": {"key": "aggressive_refactoring", "type": bool, "default": False},
        "Budget Limit": {"key": "budget_limit", "type": float, "default": 5.0},
    }

    def parse_control_plane(self, opus_content: str) -> Dict[str, Any]:
        """
        Extract settings from ## 🎛️ Control Plane section.

        Supports two checkbox formats:
        1. Simple toggle: `- [x] Tests` or `- [ ] Tests`
        2. With value: `- [x] Budget Limit: $5.00` or `- [ ] Budget Limit: $5.00`

        Args:
            opus_content: Full OPUS.md content

        Returns:
            Dict of {state_key: value} with defaults for missing entries
        """
        settings = {}

        # Find Control Plane section
        match = re.search(r"## 🎛️ Control Plane\n(.*?)(?=\n##|\n---|\Z)", opus_content, re.DOTALL)

        if not match:
            logger.debug("No Control Plane section found in OPUS.md")
            return self._get_defaults()

        section_content = match.group(1)

        # Parse each line for checkboxes
        # Pattern: - [x] Label or - [ ] Label: Value
        # Note: Label may have trailing emoji/styling that we need to strip
        checkbox_pattern = re.compile(r"- \[(x| )\] ([^:\n]+?)(?:\s*[🔧⚠️]*)?(?::\s*(.+))?$")

        for line in section_content.split("\n"):
            line = line.strip()
            if not line:
                continue

            m = checkbox_pattern.match(line)
            if not m:
                continue

            is_checked = m.group(1) == "x"
            # Strip trailing whitespace, underscores, and common markdown formatting
            label = m.group(2).strip().rstrip("_").strip()
            value_str = m.group(3).strip() if m.group(3) else None

            # Also try without trailing parenthetical hints like "_(hidden)_" or "_(live!)_"
            label = re.sub(r"\s*_?\([^)]+\)_?$", "", label).strip()

            # Skip labels not in schema (e.g., section headers)
            if label not in self.SCHEMA:
                continue

            schema_entry = self.SCHEMA[label]
            key = schema_entry["key"]
            expected_type = schema_entry["type"]
            default = schema_entry["default"]

            # Parse value based on type
            if expected_type is bool:
                settings[key] = is_checked
            elif expected_type is float and value_str:
                try:
                    # Handle "$5.00" or "5.00" format
                    clean_val = value_str.replace("$", "").strip()
                    settings[key] = float(clean_val)
                except ValueError:
                    logger.warning(f"Invalid float for '{label}': {value_str}, using default")
                    settings[key] = default
            elif expected_type is int and value_str:
                try:
                    settings[key] = int(value_str)
                except ValueError:
                    logger.warning(f"Invalid int for '{label}': {value_str}, using default")
                    settings[key] = default
            elif expected_type is str and value_str:
                settings[key] = value_str
            else:
                settings[key] = default

        # Merge with defaults for any missing settings
        final_settings = self._get_defaults()
        final_settings.update(settings)

        logger.debug(f"Parsed {len(settings)} settings from Control Plane")
        return final_settings

    def _get_defaults(self) -> Dict[str, Any]:
        """Get default values for all settings."""
        return {v["key"]: v["default"] for v in self.SCHEMA.values()}

    def apply_to_state(self, state_manager: "OpusStateManager", settings: Dict[str, Any]) -> bool:
        """
        Apply parsed settings to OpusStateManager.

        This persists the settings to .opus_state/session.json
        so they survive across renders.

        Args:
            state_manager: OpusStateManager instance
            settings: Dict from parse_control_plane()

        Returns:
            True if all settings applied successfully
        """
        success = True
        changed_count = 0

        for key, value in settings.items():
            current = state_manager.get_preference(key)
            if current != value:
                if state_manager.set_preference(key, value):
                    changed_count += 1
                else:
                    success = False

        if changed_count > 0:
            logger.info(f"🔌 Control Cables: Applied {changed_count} setting changes")

        return success

    def get_changed_settings(
        self, state_manager: "OpusStateManager", new_settings: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Compare new settings with current state and return changes.

        Useful for detecting human edits between renders.

        Args:
            state_manager: OpusStateManager instance
            new_settings: Dict from parse_control_plane()

        Returns:
            List of {key, old_value, new_value} dicts for changed settings
        """
        changes = []

        for key, new_value in new_settings.items():
            current = state_manager.get_preference(key)
            if current != new_value:
                changes.append({"key": key, "old_value": current, "new_value": new_value})

        return changes


def parse_and_apply(opus_content: str, state_manager: Optional["OpusStateManager"] = None) -> Dict[str, Any]:
    """
    Convenience function: Parse OPUS.md and apply to state in one call.

    Args:
        opus_content: Full OPUS.md content
        state_manager: Optional StateManager (auto-detected if None)

    Returns:
        The parsed settings dict
    """
    parser = ControlCablesParser()
    settings = parser.parse_control_plane(opus_content)

    if state_manager is None:
        from vibe_core.plugins.opus_assistant.core.state_manager import get_state_manager

        state_manager = get_state_manager()

    parser.apply_to_state(state_manager, settings)
    return settings
