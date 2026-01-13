"""Settings Sync Plugin - Wires SettingsExecutor into kernel tick."""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x6c3b8509"  # GenesisByte: parampara % 37 == 0

from .plugin_main import SettingsSyncPlugin

__all__ = ["SettingsSyncPlugin"]
