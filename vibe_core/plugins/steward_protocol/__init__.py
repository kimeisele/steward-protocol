"""
STEWARD Protocol Plugin - Fraktal Cartridge Structure.

This plugin follows the Universal Cartridge Pattern:
    manifest.json     ← SHABDA: Identity + Schema
    plugin_main.py    ← KARMA: Entry Point
    config.yaml       ← PRATYAYA: Local Config (optional)
    validators/       ← Sub-items (future)
"""

from .plugin_main import StewardProtocolPlugin

__all__ = ["StewardProtocolPlugin"]
