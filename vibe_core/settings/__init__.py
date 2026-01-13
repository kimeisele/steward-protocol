"""
Settings Section Plugin System

Scalable architecture for SETTINGS.md configuration.
Each section is a self-contained plugin.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "manu"
__position__ = 7
__genesis__ = "0xaf841c45"  # GenesisByte: parampara % 37 == 0

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
