"""
NodePulse Plugin - OPUS-166

Manages node.json lifecycle for all cartridges.
Creates on boot, updates on pulse with KALA state, deletes on shutdown.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x6b13fc46"  # GenesisByte: parampara % 37 == 0

from .plugin_main import NodePulsePlugin

__all__ = ["NodePulsePlugin"]
