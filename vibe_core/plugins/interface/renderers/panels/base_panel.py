"""
OpusPanel - Abstract base for OPUS renderer panels.

VEDA-4 Pattern: Each panel is auto-discovered and hot-swappable.
Panels are composed by OpusRenderer in priority order.

To create a new panel:
1. Create a new .py file in this directory
2. Extend OpusPanel
3. Implement panel_id, priority, render()
4. Done - auto-discovered on next render!
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict


class OpusPanel(ABC):
    """
    Abstract base class for OPUS dashboard panels.

    Each panel renders a section of OPUS.md independently.
    Panels are stateless - all state comes from config.
    """

    @property
    @abstractmethod
    def panel_id(self) -> str:
        """
        Unique panel identifier.

        Examples: 'visnu', 'candidates', 'blockers', 'activity'
        Used for config lookup and enable/disable.
        """
        pass

    @property
    @abstractmethod
    def priority(self) -> int:
        """
        Render order (lower = rendered first).

        Examples:
        - 0: Header/Status panels
        - 10: Main content panels
        - 20: Secondary panels
        - 100: Footer panels
        """
        pass

    @property
    def section_id(self) -> str:
        """
        Optional: Section ID for config lookup.
        Defaults to panel_id.
        """
        return self.panel_id

    def is_enabled(self, config: Dict[str, Any]) -> bool:
        """
        Check if this panel is enabled in config.

        Panels can be disabled via:
        - panels.<panel_id>.enabled: false
        - display.show_<panel_id>: false
        """
        panels_config = config.get("panels", {})
        panel_config = panels_config.get(self.panel_id, {})

        # Check explicit panel config
        if "enabled" in panel_config:
            return panel_config.get("enabled", True)

        # Check display flags (legacy support)
        display = config.get("display", {})
        display_key = f"show_{self.panel_id}"
        if display_key in display:
            return display.get(display_key, True)

        return True  # Enabled by default

    def get_panel_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get panel-specific config.

        Looks in config.panels.<panel_id> first,
        then falls back to config.<section_id>.
        """
        panels_config = config.get("panels", {})
        panel_config = panels_config.get(self.panel_id, {})

        if panel_config:
            return panel_config

        # Fallback to section config
        return config.get(self.section_id, {})

    @abstractmethod
    def render(self, config: Dict[str, Any], context: Dict[str, Any]) -> str:
        """
        Render this panel to Markdown.

        Args:
            config: Full OPUS config (from config/opus.yaml)
            context: Shared context between panels (for data sharing)

        Returns:
            Markdown string for this panel section.

        Note: Should include section header (## Panel Name)
        """
        pass

    def _count_loc(self, path: Path) -> int:
        """Utility: Count lines of code in a file."""
        try:
            if path.exists():
                return len(path.read_text().splitlines())
        except Exception:
            pass
        return 0
