"""
CLEANER Tools

Dead code detection and cleanup.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0x4369ab08"  # GenesisByte: parampara % 37 == 0

from .dead_code_tool import DeadCodeTool
from .status_tool import StatusTool

__all__ = ["DeadCodeTool", "StatusTool"]
