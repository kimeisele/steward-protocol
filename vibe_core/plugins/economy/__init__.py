"""Economy Plugin - CivicBank and CivicVault as a Service."""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x9e3e725b"  # GenesisByte: parampara % 37 == 0

from .plugin_main import EconomyPlugin

__all__ = ["EconomyPlugin"]
