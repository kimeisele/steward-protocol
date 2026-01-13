"""Plugin Template - Golden Template for new plugins."""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xac7b26f7"  # GenesisByte: parampara % 37 == 0

from .plugin_main import PluginTemplatePlugin

__all__ = ["PluginTemplatePlugin"]
