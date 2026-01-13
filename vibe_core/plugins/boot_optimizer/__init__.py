"""Boot Optimizer Plugin - Collects and analyzes boot performance metrics."""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x9006fc96"  # GenesisByte: parampara % 37 == 0

from .plugin_main import BootOptimizerPlugin

__all__ = ["BootOptimizerPlugin"]
