"""
SCRIBE Tool Base - Shared utilities.

Provides Tool and ToolResult for kernel-managed tools.

CANONICAL LOCATIONS:
- Tool: vibe_core/tools/tool_protocol.py
- ToolResult: vibe_core/tools/tool_protocol.py
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "prahlada"
__position__ = 9
__genesis__ = "0xc2699a5d"  # GenesisByte: parampara % 37 == 0

from vibe_core.tools.tool_protocol import Tool, ToolResult

__all__ = ["Tool", "ToolResult"]
