"""
AGORA - The Broadcast Channel (Parampara System)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x33a400c5"  # GenesisByte: parampara % 37 == 0

from .cartridge_main import AgoraCartridge

__all__ = ["AgoraCartridge"]
