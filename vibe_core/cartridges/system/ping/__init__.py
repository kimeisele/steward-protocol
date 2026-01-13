"""PING Agent - Minimal test agent."""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x56360d88"  # GenesisByte: parampara % 37 == 0

from .cartridge_main import PingCartridge

__all__ = ["PingCartridge"]
