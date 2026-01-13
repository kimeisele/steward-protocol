"""
OPUS Assistant Plugin - Active manager for OPUS.md ecosystem.

Transforms OPUS from passive renderer to active Agent OS plugin.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x06c3f2a9"  # GenesisByte: parampara % 37 == 0

from .plugin_main import OpusAssistantPlugin

__all__ = ["OpusAssistantPlugin"]
