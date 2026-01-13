"""
ENVOY Plugin - The System Shell.

Exposes: EnvoyPlugin
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x4d31a02e"  # GenesisByte: parampara % 37 == 0

from .plugin_main import EnvoyPlugin

__all__ = ["EnvoyPlugin"]
