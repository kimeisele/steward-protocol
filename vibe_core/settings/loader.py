#!/usr/bin/env python3
"""
SettingsSectionLoader - Auto-discovery for Settings Sections

Mirrors plugin_loader.py pattern for consistency.
Discovers sections from vibe_core/settings/sections/
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "manu"
__position__ = 7
__genesis__ = "0x13a4d915"  # GenesisByte: parampara % 37 == 0

import importlib
import logging
from pathlib import Path
from typing import Dict, List

from .protocol import SettingsSection

logger = logging.getLogger(__name__)

# Directory containing section implementations
SECTIONS_DIR = Path(__file__).parent / "sections"


class SettingsSectionLoader:
    """
    Auto-discovers and loads SettingsSection implementations.

    Usage:
        loader = SettingsSectionLoader()
        sections = loader.load_all()

        for section in sections:
            lines = section.render(context)
    """

    def __init__(self, sections_dir: Path = SECTIONS_DIR):
        self.sections_dir = sections_dir
        self._sections: Dict[str, SettingsSection] = {}
        self._loaded = False

    def discover(self) -> List[str]:
        """
        Discover available section modules.

        Returns:
            List of module names (without .py)
        """
        if not self.sections_dir.exists():
            logger.warning(f"Sections directory not found: {self.sections_dir}")
            return []

        modules = []
        for file in self.sections_dir.glob("*.py"):
            if file.name.startswith("_"):
                continue
            modules.append(file.stem)

        logger.debug(f"Discovered {len(modules)} section modules: {modules}")
        return modules

    def load_all(self) -> List[SettingsSection]:
        """
        Load all discovered sections, sorted by priority.

        Returns:
            List of SettingsSection instances (lowest priority first)
        """
        if self._loaded:
            return sorted(self._sections.values(), key=lambda s: s.priority)

        for module_name in self.discover():
            try:
                self._load_module(module_name)
            except Exception as e:
                logger.error(f"Failed to load section module '{module_name}': {e}")

        self._loaded = True
        sections = sorted(self._sections.values(), key=lambda s: s.priority)
        logger.info(f"Loaded {len(sections)} settings sections")
        return sections

    def _load_module(self, module_name: str) -> None:
        """Load a single section module and register its section class."""
        full_module = f"vibe_core.settings.sections.{module_name}"

        try:
            module = importlib.import_module(full_module)
        except ImportError as e:
            logger.warning(f"Could not import {full_module}: {e}")
            return

        # Find SettingsSection subclasses in module
        for attr_name in dir(module):
            if attr_name.startswith("_"):
                continue

            attr = getattr(module, attr_name)

            # Check if it's a SettingsSection subclass (not the base class)
            if isinstance(attr, type) and issubclass(attr, SettingsSection) and attr is not SettingsSection:
                try:
                    instance = attr()
                    self._sections[instance.section_id] = instance
                    logger.debug(f"Loaded section: {instance.section_id} (priority: {instance.priority})")
                except Exception as e:
                    logger.error(f"Failed to instantiate {attr_name}: {e}")

    def get_section(self, section_id: str) -> SettingsSection | None:
        """Get a specific section by ID."""
        if not self._loaded:
            self.load_all()
        return self._sections.get(section_id)

    def get_handler(self, command_key: str) -> SettingsSection | None:
        """
        Find the section that handles a given command key.

        Args:
            command_key: The SET command key (e.g., "provider")

        Returns:
            The section that handles this command, or None
        """
        if not self._loaded:
            self.load_all()

        for section in self._sections.values():
            if section.handles_command(command_key):
                return section

        return None


# Singleton instance
_loader: SettingsSectionLoader | None = None


def get_section_loader() -> SettingsSectionLoader:
    """Get the singleton SettingsSectionLoader instance."""
    global _loader
    if _loader is None:
        _loader = SettingsSectionLoader()
    return _loader


def reset_loader() -> None:
    """Reset the singleton (for testing)."""
    global _loader
    _loader = None
