#!/usr/bin/env python3
"""
SCRIBE Tool Base - Shared boilerplate for all renderers

Eliminates DRY violation across renderer modules.
Provides Tool and ToolResult for both kernel-managed and standalone modes.
Includes template loading utilities.

Tool Protocol Compliant.
"""

from pathlib import Path
from typing import Any, Optional

from jinja2 import Environment, FileSystemLoader, Template

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


def get_template_dir() -> Path:
    """Get the SCRIBE templates directory path."""
    return Path(__file__).parent.parent / "templates"


def load_template(template_name: str, fallback: Optional[str] = None) -> Template:
    """Load a Jinja2 template from the templates directory.

    Args:
        template_name: Name of template file (e.g., 'readme.jinja2')
        fallback: Optional fallback template string if file not found

    Returns:
        Jinja2 Template object
    """
    template_dir = get_template_dir()
    template_file = template_dir / template_name

    if template_file.exists():
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        return env.get_template(template_name)
    elif fallback:
        return Template(fallback)
    else:
        raise FileNotFoundError(f"Template not found: {template_name}")


__all__ = [
    "Tool",
    "ToolResult",
    "TOOL_PROTOCOL_AVAILABLE",
    "get_template_dir",
    "load_template",
]
