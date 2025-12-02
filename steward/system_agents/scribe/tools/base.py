#!/usr/bin/env python3
"""
SCRIBE Tool Base - Shared boilerplate for all renderers

Eliminates DRY violation across renderer modules.
Provides Tool and ToolResult for both kernel-managed and standalone modes.

Tool Protocol Compliant.
"""

from typing import Any

# Tool Protocol import - optional for standalone mode
try:
    from vibe_core.tools.tool_protocol import Tool as KernelTool
    from vibe_core.tools.tool_protocol import ToolResult as KernelToolResult

    TOOL_PROTOCOL_AVAILABLE = True

    # Use kernel versions
    Tool = KernelTool
    ToolResult = KernelToolResult

except ImportError:
    TOOL_PROTOCOL_AVAILABLE = False

    # Standalone fallback implementations
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

        def __repr__(self) -> str:
            if self.success:
                return f"ToolResult(success=True, output={self.output!r})"
            return f"ToolResult(success=False, error={self.error!r})"


__all__ = ["Tool", "ToolResult", "TOOL_PROTOCOL_AVAILABLE"]
