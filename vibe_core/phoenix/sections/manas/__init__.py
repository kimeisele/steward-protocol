"""MANAS Configuration Section."""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "kapila"
__position__ = 6
__genesis__ = "0x90458e68"  # GenesisByte: parampara % 37 == 0

from .section_main import ManasConfig

__all__ = ["ManasConfig"]
