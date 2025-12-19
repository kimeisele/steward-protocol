"""
Settings Section Plugin System

Scalable architecture for SETTINGS.md configuration.
Each section is a self-contained plugin.
"""

from .loader import SettingsSectionLoader, get_section_loader, reset_loader
from .protocol import SectionContext, SettingsResult, SettingsSection

__all__ = [
    "SettingsSection",
    "SectionContext",
    "SettingsResult",
    "SettingsSectionLoader",
    "get_section_loader",
    "reset_loader",
]
