"""MANAS Configuration Section."""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "brahma"
__position__ = 1
__genesis__ = "0x90458e68"  # GenesisByte: parampara % 37 == 0

from .section_main import ManasConfig

__all__ = ["ManasConfig"]
