"""
STEWARD Protocol Plugin - Fraktal Cartridge Structure.

This plugin follows the Universal Cartridge Pattern:
    manifest.json     ← SHABDA: Identity + Schema
    plugin_main.py    ← KARMA: Entry Point
    config.yaml       ← PRATYAYA: Local Config (optional)
    validators/       ← Sub-items (future)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x31962bd5"  # GenesisByte: parampara % 37 == 0

from .plugin_main import StewardProtocolPlugin

__all__ = ["StewardProtocolPlugin"]
