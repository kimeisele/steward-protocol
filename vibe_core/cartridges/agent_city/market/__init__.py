"""
MARKET - The Exchange Economy (Vaishya Function)
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xd83438f1"  # GenesisByte: parampara % 37 == 0

from .cartridge_main import MarketCartridge

__all__ = ["MarketCartridge"]
