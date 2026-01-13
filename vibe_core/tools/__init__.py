"""
Tool system for vibe-agency OS.

Provides a clean protocol for agents to execute actions (file operations,
API calls, etc.) without dirty hacks like exec() or string parsing.
"""

# === MAHAJANA DECLARATION (machine-readable) ===
__mahajana__ = "janaka"
__position__ = 10
__genesis__ = "0x5d040658"  # GenesisByte: parampara % 37 == 0

from vibe_core.tools.agenda_tools import AddTaskTool, CompleteTaskTool, ListTasksTool
from vibe_core.tools.delegate_tool import DelegateTool
from vibe_core.tools.file_tools import ReadFileTool, WriteFileTool
from vibe_core.tools.tool_protocol import Tool, ToolCall, ToolResult
from vibe_core.tools.tool_registry import ToolRegistry

__all__ = [
    "AddTaskTool",
    "CompleteTaskTool",
    "DelegateTool",
    "ListTasksTool",
    "ReadFileTool",
    "Tool",
    "ToolCall",
    "ToolRegistry",
    "ToolResult",
    "WriteFileTool",
]
