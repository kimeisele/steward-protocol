"""
SCRIBE Tool Base - Shared utilities.

Provides Tool and ToolResult for kernel-managed tools.
"""

from typing import Any

# Tool Protocol import
try:
    from vibe_core.tools.tool_protocol import Tool, ToolResult

    TOOL_PROTOCOL_AVAILABLE = True
except ImportError:
    TOOL_PROTOCOL_AVAILABLE = False

    class Tool:
        """Base class for tools (standalone mode)."""

        @property
        def name(self) -> str:
            raise NotImplementedError

        @property
        def description(self) -> str:
            raise NotImplementedError

        @property
        def parameters_schema(self) -> dict[str, Any]:
            raise NotImplementedError

        def validate(self, parameters: dict[str, Any]) -> None:
            raise NotImplementedError

        def execute(self, parameters: dict[str, Any]) -> "ToolResult":
            raise NotImplementedError

    class ToolResult:
        """Result of tool execution (standalone mode)."""

        def __init__(self, success: bool, output: Any = None, error: str = None):
            self.success = success
            self.output = output
            self.error = error


__all__ = ["Tool", "ToolResult", "TOOL_PROTOCOL_AVAILABLE"]
